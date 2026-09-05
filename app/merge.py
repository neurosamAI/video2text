def _overlap(a_start, a_end, b_start, b_end) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def assign_speakers(transcript_segments: list[dict], diarization_segments: list[dict]) -> list[dict]:
    """Assign a speaker label to each transcript segment by total overlapping
    duration per speaker — summed across all of that speaker's diarization
    segments within the transcript segment's span, not just whichever single
    diarization segment overlaps the most. A speaker's turn is sometimes split
    into several short diarization fragments right at a sentence's edges;
    comparing only the single best fragment can hand the whole segment to a
    different speaker whose one fragment is locally larger, even though the
    first speaker's fragments add up to more total time in that span."""
    result = []
    for seg in transcript_segments:
        overlap_by_speaker: dict[str, float] = {}
        for d in diarization_segments:
            ov = _overlap(seg["start"], seg["end"], d["start"], d["end"])
            if ov > 0:
                overlap_by_speaker[d["speaker"]] = overlap_by_speaker.get(d["speaker"], 0.0) + ov

        best_speaker = max(overlap_by_speaker, key=overlap_by_speaker.get) if overlap_by_speaker else None

        if best_speaker is None and diarization_segments:
            # no overlap found (e.g. gap) - fall back to nearest diarization segment
            mid = (seg["start"] + seg["end"]) / 2
            nearest = min(diarization_segments, key=lambda d: min(abs(d["start"] - mid), abs(d["end"] - mid)))
            best_speaker = nearest["speaker"]

        result.append({**seg, "speaker": best_speaker or "SPEAKER_00"})
    return result


def group_by_speaker(assigned_segments: list[dict]) -> list[dict]:
    """Merge consecutive segments from the same speaker into blocks."""
    blocks = []
    for seg in assigned_segments:
        if blocks and blocks[-1]["speaker"] == seg["speaker"]:
            blocks[-1]["end"] = seg["end"]
            blocks[-1]["text"] += " " + seg["text"]
            blocks[-1]["segments"].append(seg)
        else:
            blocks.append(
                {
                    "speaker": seg["speaker"],
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"],
                    "segments": [seg],
                }
            )
    return blocks
