import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np

from . import config, i18n
from .embedding import cosine_similarity, embed_segment


def _load_all() -> list[dict]:
    if not config.PROFILES_FILE.exists():
        return []
    profiles = json.loads(config.PROFILES_FILE.read_text())
    for p in profiles:
        # migrate from either older format to samples: [{embedding, created_at}, ...]
        if "samples" in p:
            continue
        if "embeddings" in p:
            p["samples"] = [{"embedding": e, "created_at": p.get("created_at")} for e in p.pop("embeddings")]
        elif "embedding" in p:
            p["samples"] = [{"embedding": p.pop("embedding"), "created_at": p.get("created_at")}]
    return profiles


def _save_all(profiles: list[dict]) -> None:
    config.PROFILES_FILE.write_text(json.dumps(profiles, ensure_ascii=False, indent=2))


def list_profiles() -> list[dict]:
    return [
        {"id": p["id"], "name": p["name"], "created_at": p["created_at"], "samples": len(p["samples"])}
        for p in _load_all()
    ]


def list_samples(profile_id: str) -> list[dict] | None:
    profiles = _load_all()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        return None
    return [
        {
            "index": i,
            "created_at": s.get("created_at"),
            "original_filename": s.get("original_filename"),
            "has_audio": bool(s.get("audio_file")),
        }
        for i, s in enumerate(profile["samples"])
    ]


def get_sample_audio_path(profile_id: str, index: int) -> Path | None:
    profiles = _load_all()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile or not (0 <= index < len(profile["samples"])):
        return None
    audio_file = profile["samples"][index].get("audio_file")
    if not audio_file:
        return None
    path = config.SPEAKERS_SAMPLES_DIR / audio_file
    return path if path.exists() else None


def add_profile(name: str, wav_path: Path, original_filename: str | None = None) -> dict:
    """Enroll a voice sample under `name`. If a profile with that name already
    exists, the sample is added to it (matching is then done against
    whichever of that profile's samples scores highest) instead of creating
    a duplicate profile — enrolling multiple samples, ideally recorded in
    different conditions, measurably improves match reliability since
    speaker-embedding models are sensitive to microphone/channel differences.

    The (16kHz mono) audio itself is kept alongside the embedding — purely so
    a person managing their profile can play a sample back and tell which
    recording is which; it plays no part in matching.
    """
    embedding = embed_segment(wav_path)
    if embedding is None:
        raise ValueError(i18n.t("sample_too_short"))

    now = datetime.now().isoformat(timespec="seconds")
    audio_filename = f"{uuid.uuid4().hex}.wav"
    shutil.copyfile(wav_path, config.SPEAKERS_SAMPLES_DIR / audio_filename)

    sample = {
        "embedding": embedding.tolist(),
        "created_at": now,
        "audio_file": audio_filename,
        "original_filename": original_filename,
    }

    profiles = _load_all()
    existing = next((p for p in profiles if p["name"].strip().lower() == name.strip().lower()), None)

    if existing:
        existing["samples"].append(sample)
        _save_all(profiles)
        return {
            "id": existing["id"],
            "name": existing["name"],
            "created_at": existing["created_at"],
            "samples": len(existing["samples"]),
        }

    profile = {
        "id": uuid.uuid4().hex[:12],
        "name": name,
        "created_at": now,
        "samples": [sample],
    }
    profiles.append(profile)
    _save_all(profiles)
    return {"id": profile["id"], "name": profile["name"], "created_at": profile["created_at"], "samples": 1}


def _delete_sample_audio(sample: dict) -> None:
    audio_file = sample.get("audio_file")
    if audio_file:
        (config.SPEAKERS_SAMPLES_DIR / audio_file).unlink(missing_ok=True)


def delete_profile(profile_id: str) -> bool:
    profiles = _load_all()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        return False
    for sample in profile["samples"]:
        _delete_sample_audio(sample)
    _save_all([p for p in profiles if p["id"] != profile_id])
    return True


def delete_sample(profile_id: str, index: int) -> str | None:
    """Delete one sample from a profile. Returns "sample_deleted",
    "profile_deleted" (if that was its last sample), or None if not found."""
    profiles = _load_all()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile or not (0 <= index < len(profile["samples"])):
        return None

    _delete_sample_audio(profile["samples"][index])
    profile["samples"].pop(index)
    if not profile["samples"]:
        profiles = [p for p in profiles if p["id"] != profile_id]
        _save_all(profiles)
        return "profile_deleted"

    _save_all(profiles)
    return "sample_deleted"


def match_speakers(
    wav_path: Path,
    diarization_segments: list[dict],
    profile_ids: list[str] | None = None,
    threshold: float | None = None,
) -> dict[str, str]:
    """Convenience wrapper — see `match_speakers_debug` for the per-speaker
    score/threshold breakdown this discards."""
    mapping, _debug = match_speakers_debug(wav_path, diarization_segments, profile_ids, threshold)
    return mapping


def _compute_label_embeddings(
    wav_path: Path, diarization_segments: list[dict], raw_labels: list[str]
) -> dict[str, np.ndarray]:
    """Compute one L2-normalized average speaker embedding per raw
    diarization label, from up to its 5 longest segments (long segments
    give a more stable embedding than short ones, and 5 is enough to average
    out per-segment noise without much added cost). Labels with no usable
    audio (e.g. all segments too short to embed) are simply absent from the
    returned dict."""
    label_embs: dict[str, np.ndarray] = {}
    for label in raw_labels:
        segs = [s for s in diarization_segments if s["speaker"] == label]
        segs.sort(key=lambda s: s["end"] - s["start"], reverse=True)
        sample_embeddings = []
        for seg in segs[:5]:
            emb = embed_segment(wav_path, seg["start"], seg["end"])
            if emb is not None:
                sample_embeddings.append(emb)
        if not sample_embeddings:
            continue
        avg = np.mean(sample_embeddings, axis=0)
        label_embs[label] = avg / np.linalg.norm(avg)
    return label_embs


def consolidate_fragmented_speakers(
    wav_path: Path, diarization_segments: list[dict], threshold: float | None = None
) -> tuple[list[dict], dict[str, list[str]]]:
    """Merge raw diarization labels that are almost certainly the same
    person split across multiple labels — a common diarization artifact,
    especially around brief pauses or tone/volume shifts, and one that no
    amount of profile-matching tuning can fix on its own (each merged-away
    label just keeps losing its one shot at matching a profile to whichever
    label happens to score highest).

    Labels are merged when their voice embeddings are at least `threshold`
    similar to each other (transitively — if A~B and B~C both clear the
    threshold, A/B/C all merge together even if A~C alone would not). Each
    merged group keeps the label with the most total speaking time as its
    canonical name, so the dominant instance's identity doesn't change.

    Returns the diarization segments with merged labels' `speaker` fields
    rewritten to their group's canonical label, plus a
    {canonical_label: [absorbed_label, ...]} map for surfacing to the user.
    Returns the input unchanged (and an empty map) when there's nothing to
    merge.
    """
    threshold = threshold if threshold is not None else config.SPEAKER_CONSOLIDATION_THRESHOLD
    raw_labels = sorted({s["speaker"] for s in diarization_segments})
    if len(raw_labels) <= 1:
        return diarization_segments, {}

    label_embs = _compute_label_embeddings(wav_path, diarization_segments, raw_labels)
    embedded_labels = [l for l in label_embs]

    parent = {label: label for label in raw_labels}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, a in enumerate(embedded_labels):
        for b in embedded_labels[i + 1 :]:
            if cosine_similarity(label_embs[a], label_embs[b]) >= threshold:
                union(a, b)

    groups: dict[str, list[str]] = {}
    for label in raw_labels:
        groups.setdefault(find(label), []).append(label)

    durations = {
        label: sum(s["end"] - s["start"] for s in diarization_segments if s["speaker"] == label)
        for label in raw_labels
    }

    remap: dict[str, str] = {}
    merge_info: dict[str, list[str]] = {}
    for members in groups.values():
        if len(members) <= 1:
            continue
        canonical = max(members, key=lambda l: durations[l])
        absorbed = [m for m in members if m != canonical]
        for m in absorbed:
            remap[m] = canonical
        merge_info[canonical] = absorbed

    if not remap:
        return diarization_segments, {}

    updated = [{**s, "speaker": remap.get(s["speaker"], s["speaker"])} for s in diarization_segments]
    return updated, merge_info


def match_speakers_debug(
    wav_path: Path,
    diarization_segments: list[dict],
    profile_ids: list[str] | None = None,
    threshold: float | None = None,
) -> tuple[dict[str, str], dict[str, dict]]:
    threshold = threshold if threshold is not None else config.SPEAKER_MATCH_THRESHOLD
    profiles = _load_all()
    if profile_ids is not None:
        profiles = [p for p in profiles if p["id"] in profile_ids]

    raw_labels = sorted({s["speaker"] for s in diarization_segments})
    mapping: dict[str, str] = {}
    debug: dict[str, dict] = {}

    if profiles:
        # each profile can hold multiple reference embeddings (multiple
        # enrolled samples); a speaker matches if it's close enough to ANY
        # one of them, which is the standard way to make matching robust to
        # per-recording variation (mic, noise, channel) between samples.
        profile_vecs = {
            p["id"]: (p["name"], [np.array(s["embedding"]) for s in p["samples"]]) for p in profiles
        }

        speaker_embs = _compute_label_embeddings(wav_path, diarization_segments, raw_labels)

        # score every (speaker, profile) pair, and remember each speaker's
        # single closest profile for the debug/"why didn't this match" view
        candidates = []  # (score, label, profile_id)
        for label, semb in speaker_embs.items():
            best_pid, best_score = None, -1.0
            for pid, (_, pvecs) in profile_vecs.items():
                score = max(cosine_similarity(semb, pvec) for pvec in pvecs)
                candidates.append((score, label, pid))
                if score > best_score:
                    best_pid, best_score = pid, score
            debug[label] = {
                "closest_profile": profile_vecs[best_pid][0],
                "score": round(best_score, 3),
                "threshold": threshold,
                "matched": False,
            }

        # greedy MAXIMUM-score assignment: consider the best-scoring pairs
        # first, not whichever speaker happens to sort first by label. Taking
        # the first pair that merely clears the threshold (in raw_label
        # order) lets an unrelated speaker who barely clears it "steal" a
        # profile before the far better-matching real speaker is even
        # considered — this is what actually caused matches to get *less*
        # reliable as more reference samples were enrolled, not the
        # max-per-sample scoring itself (which can only ever help).
        candidates.sort(key=lambda c: c[0], reverse=True)
        used_labels: set[str] = set()
        used_profiles: set[str] = set()
        for score, label, pid in candidates:
            if score < threshold:
                break
            if label in used_labels or pid in used_profiles:
                continue
            mapping[label] = profile_vecs[pid][0]
            debug[label]["matched"] = True
            debug[label]["score"] = round(score, 3)
            used_labels.add(label)
            used_profiles.add(pid)

    # remaining speakers get generic sequential labels
    counter = 1
    for label in raw_labels:
        if label not in mapping:
            mapping[label] = i18n.t("speaker_n", n=counter)
            counter += 1

    return mapping, debug
