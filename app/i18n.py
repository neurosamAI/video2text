"""Tiny key-based i18n for backend-generated user-facing text (job
progress/status messages, error details returned to the frontend).

The UI language setting is one of "system", "ko", "en" (persisted like any
other setting — see config.UI_LANGUAGE). "system" resolves via macOS's
actual preferred-language list (NSLocale), which reflects System Settings >
General > Language & Region rather than a possibly-unset shell locale env
var — falling back to the POSIX locale on non-macOS/dev environments.
"""
from __future__ import annotations

from . import config

STRINGS: dict[str, dict[str, str]] = {
    "ko": {
        "queued": "대기 중...",
        "app_restarted_interrupted": "앱이 종료되어 작업이 중단되었습니다.",
        "cancel_requested": "취소 요청됨... (진행 중인 단계가 끝나는 대로 중단됩니다)",
        "cancelled_by_user": "사용자가 취소했습니다.",
        "error_occurred": "오류 발생: {error}",
        "rematch_suffix": "(재매칭)",
        "relabel_suffix": "(이름 수정)",
        "rematch_missing_audio": "재매칭에 필요한 오디오가 없습니다 (원본 작업이 이 기능이 생기기 전에 만들어졌을 수 있습니다).",
        "extracting_audio": "오디오 추출 중...",
        "diarizing": "화자 분리 중... (파일 길이에 따라 시간이 걸릴 수 있습니다)",
        "diarizing_progress": "화자 분리 중... {pct}% ({step})",
        "consolidating_speakers": "화자 그룹 정리 중...",
        "transcribing_start": "음성 인식(전사) 중... 0%",
        "transcribing_progress": "음성 인식(전사) 중... {pct}% ({elapsed} / {total})",
        "matching_speakers": "화자 매칭 중...",
        "recomputing_match": "화자 매칭 재계산 중...",
        "applying_names": "이름 반영 중...",
        "merging_results": "결과 정리 중...",
        "done": "완료",
        "raw_segments_missing": "이 작업에 필요한 원본 데이터가 없습니다 (예전 버전에서 만든 작업이거나 이미 삭제된 작업입니다).",
        "rematch_audio_missing_file": "재매칭에 필요한 오디오 파일을 찾을 수 없습니다 ({filename}이 결과 저장 위치에서 옮겨졌거나 삭제된 것 같습니다).",
        "speaker_n": "화자 {n}",
        "sample_too_short": "샘플 오디오가 너무 짧거나 무음입니다. 최소 5~10초 분량의 음성이 필요합니다.",
        "ffmpeg_not_found": "{name}를 찾을 수 없습니다. `brew install ffmpeg`로 설치해주세요.",
        "hf_token_not_set": "HF_TOKEN이 설정되지 않았습니다. .env 파일에 HuggingFace 토큰을 설정하세요 (README.md의 화자분리 모델 접근 권한 안내를 참고하세요).",
        "file_not_found": "파일을 찾을 수 없습니다.",
        "file_or_local_path_required": "file 또는 local_path 중 하나가 필요합니다.",
        "cannot_delete_running_job": "진행 중인 작업은 삭제할 수 없습니다. 먼저 취소해주세요.",
        "cannot_cancel_job": "취소할 수 없는 작업입니다 (이미 끝났거나 존재하지 않음).",
        "rematch_requires_done": "완료된 작업만 재매칭할 수 있습니다.",
        "relabel_requires_done": "완료된 작업만 이름을 수정할 수 있습니다.",
        "overrides_must_be_object": "overrides는 JSON 객체여야 합니다.",
        "cannot_create_folder": "폴더를 만들 수 없습니다: {error}",
        "threshold_range": "임계값은 0~1 사이여야 합니다.",
        "path_not_found": "경로를 찾을 수 없습니다.",
        "file_picker_media_types": "동영상 오디오 (*.mp4;*.mov;*.m4v;*.mkv;*.wav;*.m4a;*.mp3)",
        "file_picker_all_types": "모든 파일 (*.*)",
    },
    "en": {
        "queued": "Queued...",
        "app_restarted_interrupted": "The app quit, so this job was interrupted.",
        "cancel_requested": "Cancellation requested... (stops as soon as the current step finishes)",
        "cancelled_by_user": "Cancelled by user.",
        "error_occurred": "Error: {error}",
        "rematch_suffix": "(rematch)",
        "relabel_suffix": "(relabel)",
        "rematch_missing_audio": "No audio available for rematching (the source job may predate this feature).",
        "extracting_audio": "Extracting audio...",
        "diarizing": "Diarizing speakers... (may take a while depending on file length)",
        "diarizing_progress": "Diarizing speakers... {pct}% ({step})",
        "consolidating_speakers": "Consolidating speaker groups...",
        "transcribing_start": "Transcribing... 0%",
        "transcribing_progress": "Transcribing... {pct}% ({elapsed} / {total})",
        "matching_speakers": "Matching speakers...",
        "recomputing_match": "Recomputing speaker match...",
        "applying_names": "Applying names...",
        "merging_results": "Finalizing results...",
        "done": "Done",
        "raw_segments_missing": "The source data for this job is missing (it may be from an older version, or was already deleted).",
        "rematch_audio_missing_file": "Couldn't find the audio file needed for rematching ({filename} may have been moved or deleted from the save location).",
        "speaker_n": "Speaker {n}",
        "sample_too_short": "The sample audio is too short or silent. At least 5-10 seconds of speech is required.",
        "ffmpeg_not_found": "Couldn't find {name}. Install it with `brew install ffmpeg`.",
        "hf_token_not_set": "HF_TOKEN is not set. Set your HuggingFace token in the .env file (see the model-access instructions in README.md).",
        "file_not_found": "File not found.",
        "file_or_local_path_required": "Either file or local_path is required.",
        "cannot_delete_running_job": "Can't delete a job that's still running. Cancel it first.",
        "cannot_cancel_job": "This job can't be cancelled (it's already finished, or doesn't exist).",
        "rematch_requires_done": "Only completed jobs can be rematched.",
        "relabel_requires_done": "Only completed jobs can have names edited.",
        "overrides_must_be_object": "overrides must be a JSON object.",
        "cannot_create_folder": "Couldn't create the folder: {error}",
        "threshold_range": "The threshold must be between 0 and 1.",
        "path_not_found": "Path not found.",
        "file_picker_media_types": "Video/Audio (*.mp4;*.mov;*.m4v;*.mkv;*.wav;*.m4a;*.mp3)",
        "file_picker_all_types": "All Files (*.*)",
    },
}


def _detect_system_language() -> str:
    """Best-effort read of the Mac's preferred UI language (System Settings >
    General > Language & Region), independent of shell locale env vars —
    those are frequently unset for a GUI-launched .app."""
    try:
        from Foundation import NSLocale

        preferred = NSLocale.preferredLanguages()
        if preferred and str(preferred[0]).lower().startswith("ko"):
            return "ko"
        if preferred:
            return "en"
    except Exception:
        pass

    try:
        import locale

        loc = locale.getlocale()[0] or locale.getdefaultlocale()[0] or ""
        if loc.lower().startswith("ko"):
            return "ko"
    except Exception:
        pass

    return "en"


def effective_language() -> str:
    setting = config.UI_LANGUAGE
    if setting in ("ko", "en"):
        return setting
    return _detect_system_language()


def t(key: str, **kwargs) -> str:
    lang = effective_language()
    template = STRINGS.get(lang, {}).get(key) or STRINGS["en"].get(key) or key
    return template.format(**kwargs) if kwargs else template
