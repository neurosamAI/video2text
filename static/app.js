const $ = (sel) => document.querySelector(sel);

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : String(str);
  return div.innerHTML;
}

let selectedFile = null;
const expandedRelabelPanels = new Set();

const READ_SCRIPT =
  "안녕하세요. 제 목소리를 등록하기 위해 이 문장을 읽고 있습니다. " +
  "오늘 회의에서는 프로젝트 진행 상황과 다음 분기 계획에 대해 이야기하려고 합니다. " +
  "날씨가 좋아서 그런지 오늘따라 기분이 좋네요. 하나, 둘, 셋, 넷, 다섯까지 세어 보겠습니다.";

$("#readScript").textContent = READ_SCRIPT;

// ---------- Settings ----------

async function loadSettings() {
  const res = await fetch("/api/settings");
  const s = await res.json();

  const status = $("#settingsStatus");
  const form = $("#settingsForm");
  if (s.hf_token_set) {
    status.textContent = `✅ 화자 분리 사용 가능 (토큰 ${s.hf_token_preview})`;
  } else {
    status.textContent = "⚠️ 토큰이 설정되지 않았습니다. 화자 분리 없이는 변환이 되지 않습니다.";
  }
  form.style.display = "flex";

  $("#saveDirInput").placeholder = s.result_save_dir;
  $("#saveDirCurrent").textContent = `현재: ${s.result_save_dir}`;

  $("#thresholdInput").value = s.speaker_match_threshold;
  $("#thresholdValue").textContent = Math.round(s.speaker_match_threshold * 100) + "%";

  $("#consolidationThresholdInput").value = s.speaker_consolidation_threshold;
  $("#consolidationThresholdValue").textContent = Math.round(s.speaker_consolidation_threshold * 100) + "%";
}

$("#saveTokenBtn").addEventListener("click", async () => {
  const token = $("#hfTokenInput").value.trim();
  if (!token) return;
  const fd = new FormData();
  fd.append("hf_token", token);
  const res = await fetch("/api/settings", { method: "POST", body: fd });
  if (!res.ok) {
    alert("저장 실패");
    return;
  }
  $("#hfTokenInput").value = "";
  loadSettings();
});

$("#saveDirBtn").addEventListener("click", async () => {
  const dir = $("#saveDirInput").value.trim();
  if (!dir) return;
  const fd = new FormData();
  fd.append("result_save_dir", dir);
  const res = await fetch("/api/settings", { method: "POST", body: fd });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "저장 실패" }));
    alert(err.detail || "저장 실패");
    return;
  }
  $("#saveDirInput").value = "";
  loadSettings();
});

$("#thresholdInput").addEventListener("change", async (e) => {
  const value = parseFloat(e.target.value);
  $("#thresholdValue").textContent = Math.round(value * 100) + "%";
  const fd = new FormData();
  fd.append("speaker_match_threshold", value);
  await fetch("/api/settings", { method: "POST", body: fd });
});
$("#consolidationThresholdInput").addEventListener("change", async (e) => {
  const value = parseFloat(e.target.value);
  $("#consolidationThresholdValue").textContent = Math.round(value * 100) + "%";
  const fd = new FormData();
  fd.append("speaker_consolidation_threshold", value);
  await fetch("/api/settings", { method: "POST", body: fd });
});
$("#consolidationThresholdInput").addEventListener("input", (e) => {
  $("#consolidationThresholdValue").textContent = Math.round(parseFloat(e.target.value) * 100) + "%";
});

$("#thresholdInput").addEventListener("input", (e) => {
  $("#thresholdValue").textContent = Math.round(parseFloat(e.target.value) * 100) + "%";
});

// ---------- Speaker profiles ----------

const expandedProfiles = new Set();

async function loadProfiles() {
  const res = await fetch("/api/speakers");
  const profiles = await res.json();

  const list = $("#profileList");
  list.innerHTML = "";
  if (profiles.length === 0) {
    list.innerHTML = '<span class="muted">등록된 프로필이 없습니다.</span>';
  }
  for (const p of profiles) {
    const row = document.createElement("div");
    row.className = "profile-row";
    const sampleNote = p.samples > 1 ? ` (${p.samples}개 샘플)` : "";
    row.innerHTML = `
      <div class="profile-row-top">
        <span>👤 ${escapeHtml(p.name)}${escapeHtml(sampleNote)}</span>
        <span>
          <button class="secondary manage-btn" data-id="${escapeHtml(p.id)}">샘플 관리</button>
          <span class="del" data-id="${escapeHtml(p.id)}">✕</span>
        </span>
      </div>
      <div class="sample-list" data-id="${escapeHtml(p.id)}" hidden></div>
    `;
    row.querySelector(".del").addEventListener("click", async () => {
      if (!confirm(`"${p.name}" 프로필을 삭제할까요? (등록된 샘플 ${p.samples}개 전부 삭제됩니다)`)) return;
      await fetch(`/api/speakers/${p.id}`, { method: "DELETE" });
      loadProfiles();
    });
    const manageBtn = row.querySelector(".manage-btn");
    if (manageBtn) {
      manageBtn.addEventListener("click", () => toggleSampleList(p.id, manageBtn));
    }
    list.appendChild(row);
    if (manageBtn && expandedProfiles.has(p.id)) {
      showSampleList(p.id, manageBtn);
    }
  }

  const match = $("#matchProfiles");
  match.innerHTML = "";
  if (profiles.length > 0) {
    const label = document.createElement("div");
    label.className = "muted";
    label.style.width = "100%";
    label.textContent = "이번 변환에서 자동 매칭할 프로필:";
    match.appendChild(label);
  }
  for (const p of profiles) {
    const chip = document.createElement("label");
    chip.className = "chip";
    chip.innerHTML = `<input type="checkbox" value="${escapeHtml(p.id)}" checked /> ${escapeHtml(p.name)}`;
    match.appendChild(chip);
  }
}

function toggleSampleList(profileId, btn) {
  const el = document.querySelector(`.sample-list[data-id="${profileId}"]`);
  if (!el) return;
  if (!el.hidden) {
    hideSampleList(profileId, btn);
  } else {
    showSampleList(profileId, btn);
  }
}

function hideSampleList(profileId, btn) {
  const el = document.querySelector(`.sample-list[data-id="${profileId}"]`);
  if (el) el.hidden = true;
  if (btn) btn.textContent = "샘플 관리 ▾";
  expandedProfiles.delete(profileId);
}

async function showSampleList(profileId, btn) {
  const el = document.querySelector(`.sample-list[data-id="${profileId}"]`);
  if (!el) return;
  expandedProfiles.add(profileId);
  if (btn) btn.textContent = "샘플 관리 ▴ (접기)";

  const res = await fetch(`/api/speakers/${profileId}/samples`);
  const samples = await res.json();
  el.innerHTML = samples
    .map((s) => {
      const label = s.original_filename ? escapeHtml(s.original_filename) : `샘플 ${escapeHtml(s.index + 1)}`;
      const audio = s.has_audio
        ? `<audio controls preload="none" src="/api/speakers/${escapeHtml(encodeURIComponent(profileId))}/samples/${escapeHtml(s.index)}/audio"></audio>`
        : "";
      return `
      <div class="sample-item">
        <div class="sample-item-info">
          <span>${label} · ${escapeHtml(s.created_at || "")}</span>
          ${audio}
        </div>
        <span class="del sample-del" data-id="${escapeHtml(profileId)}" data-index="${escapeHtml(s.index)}">✕</span>
      </div>`;
    })
    .join("");
  el.hidden = false;

  el.querySelectorAll(".sample-del").forEach((delBtn) => {
    delBtn.addEventListener("click", async () => {
      if (!confirm("이 샘플을 삭제할까요?")) return;
      await fetch(`/api/speakers/${delBtn.dataset.id}/samples/${delBtn.dataset.index}`, { method: "DELETE" });
      loadProfiles();
    });
  });
}

function getSelectedProfileIds() {
  return Array.from(document.querySelectorAll("#matchProfiles input:checked")).map((el) => el.value);
}

async function enrollFromBlob(blob, filename, name) {
  const fd = new FormData();
  fd.append("name", name);
  fd.append("file", blob, filename);
  const res = await fetch("/api/speakers", { method: "POST", body: fd });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "등록 실패" }));
    alert(err.detail || "등록 실패");
    return;
  }
  $("#profileName").value = "";
  loadProfiles();
}

$("#profileFile").addEventListener("change", (e) => {
  const name = $("#profileName").value.trim();
  if (!name) {
    alert("먼저 이름을 입력하세요.");
    e.target.value = "";
    return;
  }
  const file = e.target.files[0];
  if (!file) return;
  enrollFromBlob(file, file.name, name);
  e.target.value = "";
});

// ---------- Upload / transcribe ----------

const dropzone = $("#dropzone");
const fileInput = $("#fileInput");

dropzone.addEventListener("click", () => fileInput.click());
["dragenter", "dragover"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag");
  })
);
["dragleave", "drop"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag");
  })
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) setSelectedFile(file);
});
fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) setSelectedFile(e.target.files[0]);
});

let selectedLocalPath = null;

function setSelectedFile(file) {
  selectedFile = file;
  selectedLocalPath = null;
  $("#dropzoneText").textContent = `선택됨: ${file.name}`;
  $("#selectedFile").textContent = `${(file.size / 1e6).toFixed(1)} MB (복사됨)`;
  $("#uploadBtn").disabled = false;
}

function setSelectedLocalPath(path) {
  selectedFile = null;
  selectedLocalPath = path;
  const name = path.split("/").pop();
  $("#dropzoneText").textContent = `선택됨: ${name}`;
  $("#selectedFile").textContent = "복사 없이 원본 위치에서 바로 사용";
  $("#uploadBtn").disabled = false;
}

// pywebview's JS bridge (window.pywebview.api) is injected asynchronously
// after the native window finishes loading — only a real desktop-app
// window has it at all (a plain browser tab never will), which is also how
// we gate showing the "no-copy" picker button to when it'll actually work.
window.addEventListener("pywebviewready", () => {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.pick_video) {
    $("#pickNativeBtn").hidden = false;
  }
});

$("#pickNativeBtn").addEventListener("click", async () => {
  try {
    const path = await window.pywebview.api.pick_video();
    if (path) setSelectedLocalPath(path);
  } catch (e) {
    alert("파일 선택 실패: " + e.message);
  }
});

$("#uploadBtn").addEventListener("click", async () => {
  if (!selectedFile && !selectedLocalPath) return;
  $("#uploadBtn").disabled = true;
  const fd = new FormData();
  if (selectedLocalPath) {
    fd.append("local_path", selectedLocalPath);
  } else {
    fd.append("file", selectedFile);
  }
  fd.append("profile_ids", getSelectedProfileIds().join(","));
  const minSpeakers = $("#minSpeakersInput").value.trim();
  const maxSpeakers = $("#maxSpeakersInput").value.trim();
  if (minSpeakers) fd.append("min_speakers", minSpeakers);
  if (maxSpeakers) fd.append("max_speakers", maxSpeakers);
  try {
    const res = await fetch("/api/jobs", { method: "POST", body: fd });
    if (!res.ok) throw new Error(await res.text());
    selectedFile = null;
    selectedLocalPath = null;
    $("#dropzoneText").textContent = "mp4 파일을 여기로 드래그하거나 클릭해서 선택하세요";
    $("#selectedFile").textContent = "";
    fileInput.value = "";
    loadJobs();
  } catch (e) {
    alert("업로드 실패: " + e.message);
  } finally {
    $("#uploadBtn").disabled = false;
  }
});

// ---------- Jobs ----------

const STATUS_LABEL = {
  queued: "대기 중",
  extracting_audio: "오디오 추출 중",
  diarizing: "화자 분리 중",
  transcribing: "전사 중",
  matching_speakers: "화자 매칭 중",
  merging: "정리 중",
  done: "완료",
  error: "오류",
  cancelled: "취소됨",
};

const ACTIVE_STATUSES = new Set([
  "queued",
  "extracting_audio",
  "diarizing",
  "transcribing",
  "matching_speakers",
  "merging",
]);

const STEPS = [
  { key: "extracting_audio", icon: "🎧", label: "오디오 추출" },
  { key: "diarizing", icon: "🗣️", label: "화자 분리" },
  { key: "transcribing", icon: "✍️", label: "음성 인식" },
  { key: "matching_speakers", icon: "🪪", label: "화자 매칭" },
  { key: "done", icon: "✅", label: "완료" },
];

function renderStepTracker(job) {
  // "merging" belongs conceptually between matching_speakers and done
  const effectiveStatus = job.status === "merging" ? "matching_speakers" : job.status;
  const currentIdx = STEPS.findIndex((s) => s.key === effectiveStatus);

  return `<div class="step-tracker">${STEPS.map((s, i) => {
    let cls = "step";
    let icon = s.icon;
    if (job.status === "error" && i === Math.max(currentIdx, 0)) {
      cls += " error";
      icon = "⚠️";
    } else if (currentIdx === -1 && job.status === "queued") {
      // nothing done yet
    } else if (i < currentIdx || (job.status === "done" && i <= currentIdx)) {
      cls += " done";
      icon = "✓";
    } else if (i === currentIdx) {
      cls += " active";
    }
    return `<div class="${cls}"><div class="dot">${icon}</div><div class="label">${s.label}</div></div>`;
  }).join("")}</div>`;
}

const JOBS_PAGE_SIZE = 10;
let jobsOffset = 0;

async function loadJobs() {
  // loadJobs() rebuilds the whole list from scratch every call. If the user
  // is actively focused in a relabel-panel text input, tearing down and
  // recreating that DOM node mid-keystroke steals focus and makes typing
  // impossible (the input loses focus every ~2s poll). Skip the rebuild
  // entirely for as long as that focus holds — it resumes on the very next
  // poll once the user blurs (clicks elsewhere, tabs out, or hits save), so
  // this never blocks new jobs from appearing for more than a keystroke or
  // two at a time.
  const activeEl = document.activeElement;
  if (activeEl && activeEl.classList && activeEl.classList.contains("relabel-input")) {
    return;
  }

  // For a relabel panel that's open but not currently focused (e.g. the user
  // looked away mid-edit), capture its current (possibly unsaved) input
  // values before the rebuild below, then restore them into the
  // freshly-rebuilt panel so a stray poll never silently discards an edit.
  const savedRelabelEdits = {};
  for (const jobId of expandedRelabelPanels) {
    const panel = document.querySelector(`.relabel-panel[data-id="${CSS.escape(jobId)}"]`);
    if (!panel) continue;
    const edits = {};
    panel.querySelectorAll(".relabel-input").forEach((input) => {
      edits[input.dataset.label] = input.value;
    });
    savedRelabelEdits[jobId] = edits;
  }

  const res = await fetch(`/api/jobs?offset=${jobsOffset}&limit=${JOBS_PAGE_SIZE}`);
  const { jobs, total } = await res.json();
  const container = $("#jobs");
  container.innerHTML = "";
  if (total === 0) {
    container.innerHTML = '<span class="muted">아직 작업이 없습니다.</span>';
    $("#jobsPagination").innerHTML = "";
    return;
  }
  if (jobs.length === 0 && jobsOffset > 0) {
    // the page we were on emptied out (e.g. last item deleted) - go back one page
    jobsOffset = Math.max(0, jobsOffset - JOBS_PAGE_SIZE);
    return loadJobs();
  }
  for (const job of jobs) {
    const el = document.createElement("div");
    el.className = "job";
    const badgeClass =
      job.status === "done" ? "done" : job.status === "error" ? "error" : job.status === "cancelled" ? "cancelled" : "running";
    const isActive = ACTIVE_STATUSES.has(job.status);

    let savedInfo = "";
    if (job.status === "done" && job.result) {
      const savedPaths = job.result.saved_paths || {};
      const fileRows = Object.entries(savedPaths)
        .map(([ext, path]) => {
          const filename = path.split("/").pop();
          return `<div class="saved-file">
            <span>${escapeHtml(filename)}</span>
            <button class="secondary reveal-btn" data-path="${escapeHtml(path)}">Finder에서 보기</button>
          </div>`;
        })
        .join("");
      savedInfo = `<div class="saved-info">
        📁 저장 위치: ${escapeHtml(job.result.saved_dir)}
        ${fileRows}
      </div>`;

      const debug = job.result.match_debug || {};
      const unmatched = Object.values(debug).filter((d) => !d.matched);
      if (unmatched.length > 0) {
        const lines = unmatched
          .map((d) => `가장 가까운 후보 "${escapeHtml(d.closest_profile)}"와 ${Math.round(d.score * 100)}% 유사 (기준 ${Math.round(d.threshold * 100)}% 미달)`)
          .join("<br>");
        savedInfo += `<div class="match-note">⚠️ 자동 매칭 안 된 화자가 있습니다:<br>${lines}<br>비슷한데 안 붙는다면 위 "설정 → 화자 매칭 민감도"를 낮춰보세요.</div>`;
      }

      const merges = job.result.speaker_merges || {};
      const mergeEntries = Object.entries(merges);
      if (mergeEntries.length > 0) {
        const speakers = job.result.speakers || {};
        const lines = mergeEntries
          .map(([canonical, absorbed]) => `"${escapeHtml(speakers[canonical] || canonical)}"로 원시 라벨 ${absorbed.length}개(${escapeHtml(absorbed.join(", "))}) 통합됨`)
          .join("<br>");
        savedInfo += `<div class="match-note">🔗 같은 사람인데 화자 분리가 여러 번호로 쪼갠 것을 자동으로 합쳤습니다:<br>${lines}<br>잘못 합쳐진 것 같으면 위 "설정 → 화자 그룹 통합 민감도"를 높여서 다시 매칭해보세요.</div>`;
      }
    }

    const showTracker = isActive;
    el.innerHTML = `
      <div class="job-top">
        <div class="job-name">${escapeHtml(job.filename)}</div>
        <div class="status-badge ${badgeClass}">${STATUS_LABEL[job.status] || job.status}</div>
      </div>
      ${showTracker ? renderStepTracker(job) : ""}
      <div class="progress-bar"><div style="width:${job.progress || 0}%"></div></div>
      <div class="job-message">${escapeHtml(job.error ? job.error.split("\n")[0] : job.message || "")} (${job.progress || 0}%)</div>
      <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
        ${isActive ? `<button class="danger cancel-btn" data-job-id="${escapeHtml(job.id)}">작업 취소</button>` : ""}
        ${job.status === "done" && job.result && job.result.can_rematch ? `<button class="secondary rematch-btn" data-job-id="${escapeHtml(job.id)}">현재 설정으로 재매칭</button>` : ""}
        ${job.status === "done" && job.result && job.result.can_rematch ? `<button class="secondary relabel-btn" data-job-id="${escapeHtml(job.id)}">화자 이름 수정</button>` : ""}
        ${!isActive ? `<button class="secondary delete-job-btn" data-job-id="${escapeHtml(job.id)}">삭제</button>` : ""}
      </div>
      <div class="relabel-panel" data-id="${escapeHtml(job.id)}" hidden></div>
      ${savedInfo}
    `;
    container.appendChild(el);

    const relabelBtn = el.querySelector(".relabel-btn");
    if (relabelBtn) {
      relabelBtn.addEventListener("click", () => toggleRelabelPanel(job, relabelBtn));
      if (expandedRelabelPanels.has(job.id)) {
        openRelabelPanel(job, relabelBtn, savedRelabelEdits[job.id]);
      }
    }
  }

  renderJobsPagination(jobsOffset, total);
}

function renderJobsPagination(offset, total) {
  const el = $("#jobsPagination");
  const totalPages = Math.max(1, Math.ceil(total / JOBS_PAGE_SIZE));
  const currentPage = Math.floor(offset / JOBS_PAGE_SIZE) + 1;
  if (totalPages <= 1) {
    el.innerHTML = "";
    return;
  }
  el.innerHTML = `
    <button class="secondary" id="jobsPrevBtn" ${offset === 0 ? "disabled" : ""}>이전</button>
    <span class="muted">${currentPage} / ${totalPages} 페이지 (총 ${total}개)</span>
    <button class="secondary" id="jobsNextBtn" ${offset + JOBS_PAGE_SIZE >= total ? "disabled" : ""}>다음</button>
  `;
  $("#jobsPrevBtn").addEventListener("click", () => {
    jobsOffset = Math.max(0, jobsOffset - JOBS_PAGE_SIZE);
    loadJobs();
  });
  $("#jobsNextBtn").addEventListener("click", () => {
    jobsOffset += JOBS_PAGE_SIZE;
    loadJobs();
  });
}

function openRelabelPanel(job, btn, savedEdits) {
  const el = document.querySelector(`.relabel-panel[data-id="${CSS.escape(job.id)}"]`);
  if (!el) return;
  btn.textContent = "화자 이름 수정 ▴ (접기)";
  expandedRelabelPanels.add(job.id);

  const speakers = job.result.speakers || {};
  const debug = job.result.match_debug || {};
  const rawLabels = Object.keys(speakers).sort();
  el.innerHTML = `
    <p class="muted" style="margin:0 0 8px;">
      화자분리가 같은 사람을 서로 다른 번호로 나눠놨다면, 여기서 이름을 직접 맞춰주세요.
      원본 화자 번호(SPEAKER_XX)는 이 작업 안에서는 고정이지만, 다른 작업(다시 변환/재매칭)에서는 서로 다른 사람을 가리킬 수 있으니
      화면에 보이는 발언 내용으로 확인하시는 게 안전합니다.
    </p>
    ${rawLabels
      .map((label) => {
        const scoreNote = debug[label] ? ` <span class="muted">(${Math.round(debug[label].score * 100)}% 유사 · ${escapeHtml(debug[label].closest_profile)})</span>` : "";
        const value = savedEdits && Object.prototype.hasOwnProperty.call(savedEdits, label) ? savedEdits[label] : speakers[label];
        return `<div class="relabel-row">
          <span class="muted" style="font-family:monospace;">${escapeHtml(label)}</span>
          <input type="text" class="relabel-input" data-label="${escapeHtml(label)}" value="${escapeHtml(value)}" />
          ${scoreNote}
        </div>`;
      })
      .join("")}
    <button class="relabel-save-btn" data-job-id="${escapeHtml(job.id)}" style="margin-top:10px;">저장하고 다시 생성</button>
  `;
  el.hidden = false;
}

function closeRelabelPanel(jobId, btn) {
  const el = document.querySelector(`.relabel-panel[data-id="${CSS.escape(jobId)}"]`);
  if (el) el.hidden = true;
  if (btn) btn.textContent = "화자 이름 수정";
  expandedRelabelPanels.delete(jobId);
}

function toggleRelabelPanel(job, btn) {
  const el = document.querySelector(`.relabel-panel[data-id="${CSS.escape(job.id)}"]`);
  if (!el) return;
  if (!el.hidden) {
    closeRelabelPanel(job.id, btn);
    return;
  }
  openRelabelPanel(job, btn);
}

$("#jobs").addEventListener("click", async (e) => {
  const relabelSaveBtn = e.target.closest(".relabel-save-btn");
  if (relabelSaveBtn) {
    const panel = relabelSaveBtn.closest(".relabel-panel");
    const overrides = {};
    panel.querySelectorAll(".relabel-input").forEach((input) => {
      overrides[input.dataset.label] = input.value.trim();
    });
    relabelSaveBtn.disabled = true;
    relabelSaveBtn.textContent = "적용 중...";
    const fd = new FormData();
    fd.append("overrides", JSON.stringify(overrides));
    const res = await fetch(`/api/jobs/${relabelSaveBtn.dataset.jobId}/relabel`, { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "적용 실패" }));
      alert(err.detail || "적용 실패");
    }
    expandedRelabelPanels.delete(relabelSaveBtn.dataset.jobId);
    loadJobs();
    return;
  }

  const revealBtn = e.target.closest(".reveal-btn");
  if (revealBtn) {
    const fd = new FormData();
    fd.append("path", revealBtn.dataset.path);
    await fetch("/api/reveal", { method: "POST", body: fd });
    return;
  }

  const cancelBtn = e.target.closest(".cancel-btn");
  if (cancelBtn) {
    if (!confirm("진행 중인 작업을 취소할까요?")) return;
    cancelBtn.disabled = true;
    cancelBtn.textContent = "취소 중...";
    await fetch(`/api/jobs/${cancelBtn.dataset.jobId}/cancel`, { method: "POST" });
    loadJobs();
    return;
  }

  const deleteBtn = e.target.closest(".delete-job-btn");
  if (deleteBtn) {
    if (!confirm("이 작업 기록을 삭제할까요? (저장 위치에 이미 저장된 결과 파일은 그대로 남습니다)")) return;
    deleteBtn.disabled = true;
    await fetch(`/api/jobs/${deleteBtn.dataset.jobId}`, { method: "DELETE" });
    loadJobs();
    return;
  }

  const rematchBtn = e.target.closest(".rematch-btn");
  if (rematchBtn) {
    if (!confirm("현재 화자 매칭 민감도 / 선택된 프로필로 다시 매칭할까요? 화자 분리·전사는 재사용하므로 빠르게 끝납니다.")) return;
    rematchBtn.disabled = true;
    rematchBtn.textContent = "재매칭 시작 중...";
    const fd = new FormData();
    fd.append("profile_ids", getSelectedProfileIds().join(","));
    const res = await fetch(`/api/jobs/${rematchBtn.dataset.jobId}/rematch`, { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "재매칭 실패" }));
      alert(err.detail || "재매칭 실패");
    }
    loadJobs();
  }
});

loadSettings();
loadProfiles();
loadJobs();
setInterval(loadJobs, 2000);
