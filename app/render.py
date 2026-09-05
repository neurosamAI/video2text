import json
from pathlib import Path


def _fmt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_srt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_txt(blocks: list[dict], speaker_names: dict[str, str], out_path: Path) -> Path:
    lines = []
    for b in blocks:
        name = speaker_names.get(b["speaker"], b["speaker"])
        lines.append(f"[{_fmt_ts(b['start'])}] {name}: {b['text'].strip()}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def write_srt(assigned_segments: list[dict], speaker_names: dict[str, str], out_path: Path) -> Path:
    lines = []
    for i, seg in enumerate(assigned_segments, start=1):
        name = speaker_names.get(seg["speaker"], seg["speaker"])
        lines.append(str(i))
        lines.append(f"{_fmt_srt_ts(seg['start'])} --> {_fmt_srt_ts(seg['end'])}")
        lines.append(f"{name}: {seg['text'].strip()}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def write_json(blocks: list[dict], speaker_names: dict[str, str], out_path: Path) -> Path:
    data = {
        "speakers": speaker_names,
        "blocks": [
            {
                "speaker": b["speaker"],
                "speaker_name": speaker_names.get(b["speaker"], b["speaker"]),
                "start": b["start"],
                "end": b["end"],
                "text": b["text"].strip(),
            }
            for b in blocks
        ],
    }
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path
