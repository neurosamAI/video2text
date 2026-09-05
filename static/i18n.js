// Tiny key-based i18n for the frontend. Mirrors app/i18n.py's approach:
// a flat dict per language, values are either plain strings or functions
// (for anything that needs interpolation). `t(key, ...args)` looks up the
// current language (set by main.js via setLang()) and calls the value if
// it's a function.

const I18N = {
  ko: {
    appSubtitle: "mp4를 넣으면 화자 분리된 텍스트 전사본을 만들어줍니다 (Webex 녹화 기준, 완전 로컬 처리)",
    settingsTitle: "⚙️ 설정",
    settingsHfSubhead: "화자 분리 모델 접근 권한",
    settingsChecking: "확인 중...",
    hfTokenPlaceholder: "hf_로 시작하는 HuggingFace 토큰",
    btnSave: "저장",
    hfHelpHtml:
      '토큰이 없다면 ' +
      '<a href="https://huggingface.co/settings/tokens" target="_blank" style="color:var(--accent)">huggingface.co/settings/tokens</a>' +
      ' 에서 무료로 발급받으세요 (Read 권한). 발급 전, 아래 두 모델 페이지에서 각각 라이선스 동의가 필요합니다: ' +
      '<a href="https://huggingface.co/pyannote/speaker-diarization-3.1" target="_blank" style="color:var(--accent)">speaker-diarization-3.1</a>, ' +
      '<a href="https://huggingface.co/pyannote/segmentation-3.0" target="_blank" style="color:var(--accent)">segmentation-3.0</a>',
    saveDirSubhead: "결과 저장 위치",
    currentPrefix: (dir) => `현재: ${dir}`,
    thresholdSubhead: "화자 매칭 민감도",
    thresholdHelp:
      "값을 낮추면 등록한 프로필과 조금만 비슷해도 이름으로 매칭됩니다 (대신 다른 사람과 헷갈릴 위험이 커집니다). " +
      '등록된 프로필이 있는데 계속 "화자 N"으로만 나온다면 낮춰보세요.',
    consolidationSubhead: "화자 그룹 통합 민감도",
    consolidationHelp:
      "화자 분리가 같은 사람을 여러 번호로 쪼개놓은 경우, 목소리가 서로 이 값 이상 비슷하면 자동으로 하나로 합칩니다. " +
      "값을 낮추면 더 적극적으로 합치지만 실제로 다른 두 사람을 잘못 합칠 위험이 커집니다 (합쳐진 후에는 다시 나눌 수 없으니 신중하게).",
    voiceProfileTitle: "🎙️ 내 목소리 프로필",
    voiceProfileHelp1:
      "등록해두면 전사 결과에서 해당 화자가 자동으로 이름으로 표시됩니다. macOS 음성 메모 등으로 조용한 곳에서 10~20초 정도 또렷하게 녹음한 뒤 업로드하세요.",
    voiceProfileHelp2html:
      "💡 매칭이 잘 안 되면, <b>같은 이름으로 한 번 더 등록</b>해보세요 (다른 마이크나 실제 회의 녹화에서 발췌한 샘플이면 더 좋습니다). 같은 이름의 샘플이 여러 개면 그중 가장 잘 맞는 것으로 비교합니다.",
    profileNamePlaceholder: "이름 (예: 홍길동, 나)",
    uploadFileLabel: "파일 업로드",
    scriptBoxLabel: "📝 녹음할 때 아래 문장을 또렷하게 읽으면 좋습니다 (10~20초 분량)",
    readScript:
      "안녕하세요. 제 목소리를 등록하기 위해 이 문장을 읽고 있습니다. " +
      "오늘 회의에서는 프로젝트 진행 상황과 다음 분기 계획에 대해 이야기하려고 합니다. " +
      "날씨가 좋아서 그런지 오늘따라 기분이 좋네요. 하나, 둘, 셋, 넷, 다섯까지 세어 보겠습니다.",
    convertTitle: "📼 mp4 변환하기",
    dropzoneDefault: "mp4 파일을 여기로 드래그하거나 클릭해서 선택하세요",
    pickNativeBtn: "📂 Finder에서 선택 (복사 없이, 더 빠름)",
    expectedSpeakersLabel: "예상 화자 수 (선택, 모르면 비워두세요)",
    expectedSpeakersHelp:
      "화자 분리가 한 사람을 여러 명으로 쪼개는 경우가 있는데, 대략적인 인원 범위를 알려주면 도움이 됩니다. " +
      "정확한 수를 모르면 최소/최대만 대충 넣어도 되고, 하나만 넣어도 됩니다.",
    minPlaceholder: "최소",
    maxPlaceholder: "최대",
    uploadBtn: "변환 시작",
    jobsTitle: "📄 작업 내역",
    uiLanguageSubhead: "화면 언어",
    uiLanguageSystem: "시스템 설정 따름",
    uiLanguageKo: "한국어",
    uiLanguageEn: "English",

    statusAvailable: (preview) => `✅ 화자 분리 사용 가능 (토큰 ${preview})`,
    statusNotSet: "⚠️ 토큰이 설정되지 않았습니다. 화자 분리 없이는 변환이 되지 않습니다.",
    alertSaveFailed: "저장 실패",
    alertRegisterFailed: "등록 실패",
    alertUploadFailedPrefix: "업로드 실패: ",
    alertFileSelectFailedPrefix: "파일 선택 실패: ",
    alertEnterNameFirst: "먼저 이름을 입력하세요.",
    noProfilesRegistered: "등록된 프로필이 없습니다.",
    samplesCountSuffix: (n) => ` (${n}개 샘플)`,
    manageSamplesBtn: "샘플 관리",
    manageSamplesBtnExpanded: "샘플 관리 ▴ (접기)",
    manageSamplesBtnCollapsed: "샘플 관리 ▾",
    confirmDeleteProfile: (name, samples) => `"${name}" 프로필을 삭제할까요? (등록된 샘플 ${samples}개 전부 삭제됩니다)`,
    matchProfilesLabel: "이번 변환에서 자동 매칭할 프로필:",
    samplePrefix: (n) => `샘플 ${n}`,
    confirmDeleteSample: "이 샘플을 삭제할까요?",
    selectedPrefix: (name) => `선택됨: ${name}`,
    mbCopiedSuffix: (mb) => `${mb} MB (복사됨)`,
    noCopyLocalUse: "복사 없이 원본 위치에서 바로 사용",

    statusLabel: {
      queued: "대기 중",
      extracting_audio: "오디오 추출 중",
      diarizing: "화자 분리 중",
      transcribing: "전사 중",
      matching_speakers: "화자 매칭 중",
      merging: "정리 중",
      done: "완료",
      error: "오류",
      cancelled: "취소됨",
    },
    stepLabel: {
      extracting_audio: "오디오 추출",
      diarizing: "화자 분리",
      transcribing: "음성 인식",
      matching_speakers: "화자 매칭",
      done: "완료",
    },
    noJobsYet: "아직 작업이 없습니다.",
    revealInFinderBtn: "Finder에서 보기",
    savedLocationPrefix: (dir) => `📁 저장 위치: ${dir}`,
    unmatchedSpeakerLine: (profile, score, threshold) =>
      `가장 가까운 후보 "${profile}"와 ${score}% 유사 (기준 ${threshold}% 미달)`,
    unmatchedSpeakersBlock: (lines) =>
      `⚠️ 자동 매칭 안 된 화자가 있습니다:<br>${lines}<br>비슷한데 안 붙는다면 위 "설정 → 화자 매칭 민감도"를 낮춰보세요.`,
    mergeLine: (canonical, count, list) => `"${canonical}"로 원시 라벨 ${count}개(${list}) 통합됨`,
    mergeBlock: (lines) =>
      `🔗 같은 사람인데 화자 분리가 여러 번호로 쪼갠 것을 자동으로 합쳤습니다:<br>${lines}<br>잘못 합쳐진 것 같으면 위 "설정 → 화자 그룹 통합 민감도"를 높여서 다시 매칭해보세요.`,
    cancelJobBtn: "작업 취소",
    rematchBtn: "현재 설정으로 재매칭",
    relabelBtn: "화자 이름 수정",
    deleteBtn: "삭제",
    prevPageBtn: "이전",
    nextPageBtn: "다음",
    pageInfo: (current, total, totalCount) => `${current} / ${total} 페이지 (총 ${totalCount}개)`,
    relabelHelpText:
      "화자분리가 같은 사람을 서로 다른 번호로 나눠놨다면, 여기서 이름을 직접 맞춰주세요. " +
      "원본 화자 번호(SPEAKER_XX)는 이 작업 안에서는 고정이지만, 다른 작업(다시 변환/재매칭)에서는 서로 다른 사람을 가리킬 수 있으니 " +
      "화면에 보이는 발언 내용으로 확인하시는 게 안전합니다.",
    relabelBtnExpanded: "화자 이름 수정 ▴ (접기)",
    scoreNote: (score, profile) => ` (${score}% 유사 · ${profile})`,
    relabelSaveBtn: "저장하고 다시 생성",
    relabelSaving: "적용 중...",
    alertApplyFailed: "적용 실패",
    confirmCancelJob: "진행 중인 작업을 취소할까요?",
    cancellingBtn: "취소 중...",
    confirmDeleteJob: "이 작업 기록을 삭제할까요? (저장 위치에 이미 저장된 결과 파일은 그대로 남습니다)",
    confirmRematch: "현재 화자 매칭 민감도 / 선택된 프로필로 다시 매칭할까요? 화자 분리·전사는 재사용하므로 빠르게 끝납니다.",
    rematchStartingBtn: "재매칭 시작 중...",
    alertRematchFailed: "재매칭 실패",
  },

  en: {
    appSubtitle: "Feed it an mp4 and get a speaker-diarized transcript (built for Webex recordings, fully local processing)",
    settingsTitle: "⚙️ Settings",
    settingsHfSubhead: "Speaker Diarization Model Access",
    settingsChecking: "Checking...",
    hfTokenPlaceholder: "HuggingFace token starting with hf_",
    btnSave: "Save",
    hfHelpHtml:
      "No token yet? Get one for free (Read access) at " +
      '<a href="https://huggingface.co/settings/tokens" target="_blank" style="color:var(--accent)">huggingface.co/settings/tokens</a>' +
      ". Before that, accept the license on both model pages: " +
      '<a href="https://huggingface.co/pyannote/speaker-diarization-3.1" target="_blank" style="color:var(--accent)">speaker-diarization-3.1</a>, ' +
      '<a href="https://huggingface.co/pyannote/segmentation-3.0" target="_blank" style="color:var(--accent)">segmentation-3.0</a>',
    saveDirSubhead: "Result Save Location",
    currentPrefix: (dir) => `Current: ${dir}`,
    thresholdSubhead: "Speaker Match Sensitivity",
    thresholdHelp:
      "Lower this and a segment only needs to be a little similar to a registered profile to get matched by name (but the risk of confusing it with someone else goes up). " +
      'If you have profiles registered but transcripts still just show "Speaker N", try lowering this.',
    consolidationSubhead: "Speaker Group Merge Sensitivity",
    consolidationHelp:
      "When diarization splits the same person across several numbers, voices this similar to each other get automatically merged into one. " +
      "Lower this to merge more aggressively — but the risk of wrongly merging two actually-different people goes up (merges can't be split back apart, so be careful).",
    voiceProfileTitle: "🎙️ My Voice Profile",
    voiceProfileHelp1:
      "Register your voice and that speaker shows up under their real name automatically in future transcripts. Record 10-20 seconds clearly in a quiet room (e.g. with macOS Voice Memos) and upload it.",
    voiceProfileHelp2html:
      "💡 If matching isn't working well, try <b>registering the same name again</b> (ideally with a different mic, or a clip from a real meeting recording). With multiple samples under one name, the best-matching one is used for comparison.",
    profileNamePlaceholder: "Name (e.g. Alex, Me)",
    uploadFileLabel: "Upload File",
    scriptBoxLabel: "📝 Read the sentence below clearly while recording (about 10-20 seconds)",
    readScript:
      "Hello. I'm reading this sentence to register my voice. " +
      "Today's meeting is about project progress and plans for next quarter. " +
      "It's a nice day, so I'm in a good mood. Let me count: one, two, three, four, five.",
    convertTitle: "📼 Convert mp4",
    dropzoneDefault: "Drag an mp4 file here, or click to choose one",
    pickNativeBtn: "📂 Choose via Finder (no copy, faster)",
    expectedSpeakersLabel: "Expected Speaker Count (optional — leave blank if unsure)",
    expectedSpeakersHelp:
      "Diarization sometimes splits one person into several. Giving it a rough headcount helps. " +
      "If you don't know the exact number, a rough min/max — or just one number — is fine too.",
    minPlaceholder: "Min",
    maxPlaceholder: "Max",
    uploadBtn: "Start Conversion",
    jobsTitle: "📄 Job History",
    uiLanguageSubhead: "Interface Language",
    uiLanguageSystem: "Follow System",
    uiLanguageKo: "한국어",
    uiLanguageEn: "English",

    statusAvailable: (preview) => `✅ Speaker diarization available (token ${preview})`,
    statusNotSet: "⚠️ No token set. Conversion won't work without speaker diarization.",
    alertSaveFailed: "Save failed",
    alertRegisterFailed: "Registration failed",
    alertUploadFailedPrefix: "Upload failed: ",
    alertFileSelectFailedPrefix: "File selection failed: ",
    alertEnterNameFirst: "Enter a name first.",
    noProfilesRegistered: "No profiles registered yet.",
    samplesCountSuffix: (n) => ` (${n} samples)`,
    manageSamplesBtn: "Manage Samples",
    manageSamplesBtnExpanded: "Manage Samples ▴ (Collapse)",
    manageSamplesBtnCollapsed: "Manage Samples ▾",
    confirmDeleteProfile: (name, samples) => `Delete the "${name}" profile? (All ${samples} registered sample(s) will be deleted)`,
    matchProfilesLabel: "Profiles to auto-match for this conversion:",
    samplePrefix: (n) => `Sample ${n}`,
    confirmDeleteSample: "Delete this sample?",
    selectedPrefix: (name) => `Selected: ${name}`,
    mbCopiedSuffix: (mb) => `${mb} MB (copied)`,
    noCopyLocalUse: "Used directly in place, no copy",

    statusLabel: {
      queued: "Queued",
      extracting_audio: "Extracting Audio",
      diarizing: "Diarizing",
      transcribing: "Transcribing",
      matching_speakers: "Matching Speakers",
      merging: "Finalizing",
      done: "Done",
      error: "Error",
      cancelled: "Cancelled",
    },
    stepLabel: {
      extracting_audio: "Extract Audio",
      diarizing: "Diarize",
      transcribing: "Transcribe",
      matching_speakers: "Match Speakers",
      done: "Done",
    },
    noJobsYet: "No jobs yet.",
    revealInFinderBtn: "Show in Finder",
    savedLocationPrefix: (dir) => `📁 Saved to: ${dir}`,
    unmatchedSpeakerLine: (profile, score, threshold) =>
      `${score}% similar to closest candidate "${profile}" (below the ${threshold}% threshold)`,
    unmatchedSpeakersBlock: (lines) =>
      `⚠️ Some speakers weren't auto-matched:<br>${lines}<br>If it seems close but isn't matching, try lowering "Settings → Speaker Match Sensitivity" above.`,
    mergeLine: (canonical, count, list) => `${count} raw label(s) (${list}) merged into "${canonical}"`,
    mergeBlock: (lines) =>
      `🔗 Diarization split the same person into multiple numbers, so they were automatically merged:<br>${lines}<br>If this merged incorrectly, raise "Settings → Speaker Group Merge Sensitivity" above and rematch.`,
    cancelJobBtn: "Cancel Job",
    rematchBtn: "Rematch with Current Settings",
    relabelBtn: "Edit Speaker Names",
    deleteBtn: "Delete",
    prevPageBtn: "Previous",
    nextPageBtn: "Next",
    pageInfo: (current, total, totalCount) => `${current} / ${total} (${totalCount} total)`,
    relabelHelpText:
      "If diarization split the same person across different numbers, match up the names here yourself. " +
      "Raw speaker labels (SPEAKER_XX) are fixed within this job, but can refer to different people in other jobs (a re-conversion or rematch) — " +
      "it's safest to check against what's actually said on screen.",
    relabelBtnExpanded: "Edit Speaker Names ▴ (Collapse)",
    scoreNote: (score, profile) => ` (${score}% similar · ${profile})`,
    relabelSaveBtn: "Save & Regenerate",
    relabelSaving: "Applying...",
    alertApplyFailed: "Apply failed",
    confirmCancelJob: "Cancel this running job?",
    cancellingBtn: "Cancelling...",
    confirmDeleteJob: "Delete this job's history entry? (Result files already saved to your save location will stay put)",
    confirmRematch: "Rematch with the current match sensitivity / selected profiles? Diarization and transcription are reused, so this finishes quickly.",
    rematchStartingBtn: "Starting rematch...",
    alertRematchFailed: "Rematch failed",
  },
};

let _lang = "ko";

function setLang(lang) {
  _lang = lang === "en" ? "en" : "ko";
  document.documentElement.lang = _lang;
}

function getLang() {
  return _lang;
}

function t(key, ...args) {
  const dict = I18N[_lang] || I18N.ko;
  const val = dict[key];
  if (typeof val === "function") return val(...args);
  if (val !== undefined) return val;
  return key;
}

// Apply translations to every static element in the document tagged with
// data-i18n (textContent), data-i18n-html (innerHTML, for text with
// embedded links/markup), or data-i18n-placeholder (input placeholder).
function applyStaticI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.title = "video2text";
}
