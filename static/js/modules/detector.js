/**
 * Leaf detection workspace: file/camera upload, drag-drop, sample gallery, /predict fetch, result renderer, and lightbox.
 */

import { cleanText, renderHistoryTable, saveToIndexedDBHistory } from "./history_db.js";

let currentFile = null;
let currentLocalPreviewUrl = "";
let lastResponseData = null;
let currentVerdictView = "annotated";
let currentWorkspaceTab = "upload";

const FALLBACK_5_SAMPLES = [
  {
    filename: "sample_black_sigatoka.jpg",
    label: "Black Sigatoka",
    sub: "Ganas / Kritis",
    url: "/sample-file/samples/sample_black_sigatoka.jpg",
  },
  {
    filename: "sample_yellow_sigatoka.jpg",
    label: "Yellow Sigatoka",
    sub: "Bercak Kuning",
    url: "/sample-file/samples/sample_yellow_sigatoka.jpg",
  },
  {
    filename: "sample_cordana.jpg",
    label: "Cordana Leaf Spot",
    sub: "Bercak Oval",
    url: "/sample-file/samples/sample_cordana.jpg",
  },
  {
    filename: "sample_pestalotiopsis.jpg",
    label: "Pestalotiopsis",
    sub: "Bercak Tepi",
    url: "/sample-file/samples/sample_pestalotiopsis.jpg",
  },
  {
    filename: "sample_fresh.jpg",
    label: "Daun Sehat (Fresh)",
    sub: "Klorofil Optimal",
    url: "/sample-file/samples/sample_fresh.jpg",
  },
];

const SUS_QUESTIONS = [
  "Saya berpikir akan sering menggunakan sistem deteksi penyakit daun pisang ini.",
  "Saya merasa sistem ini terlalu rumit untuk digunakan secara mandiri.",
  "Saya merasa sistem ini sangat mudah untuk digunakan dalam proses deteksi kebun.",
  "Saya membutuhkan bantuan orang lain atau teknisi ahli untuk menggunakan sistem ini.",
  "Saya merasa fungsi dan fitur pada sistem ini terintegrasi dengan sangat baik.",
  "Saya merasa ada terlalu banyak hal yang tidak konsisten pada sistem ini.",
  "Saya merasa kebanyakan petani atau pengguna umum akan cepat memahami sistem ini.",
  "Saya merasa sistem ini sangat membingungkan saat pertama kali dioperasikan.",
  "Saya merasa sangat percaya diri saat menggunakan sistem ini di lapangan.",
  "Saya perlu mempelajari banyak hal terlebih dahulu sebelum dapat menggunakan sistem ini.",
];

export function resetDetectorSessionState() {
  currentFile = null;
  currentLocalPreviewUrl = "";
  lastResponseData = null;
}

export function switchWorkspaceTab(tabId) {
  currentWorkspaceTab = tabId;
  document.querySelectorAll(".mode-tab-btn").forEach((btn) => {
    btn.classList.toggle("is-active", btn.getAttribute("data-tab") === tabId);
  });

  const viewUpload = document.getElementById("tabViewUpload");
  const viewSamples = document.getElementById("tabViewSamples");
  const viewResult = document.getElementById("tabViewResult");
  const viewHistory = document.getElementById("tabViewHistory");

  [viewUpload, viewSamples, viewResult, viewHistory].forEach((v) => {
    if (v) v.classList.add("hidden");
  });

  if (tabId === "upload" && viewUpload) viewUpload.classList.remove("hidden");
  else if (tabId === "samples" && viewSamples) viewSamples.classList.remove("hidden");
  else if (tabId === "result" && viewResult) viewResult.classList.remove("hidden");
  else if (tabId === "history" && viewHistory) {
    viewHistory.classList.remove("hidden");
    renderHistoryTable();
  }

  if (window.ScrollTrigger) {
    window.ScrollTrigger.refresh();
  }
}

export function initWorkspaceTabs() {
  const tabBtns = document.querySelectorAll(".mode-tab-btn");
  if (!tabBtns.length) return;
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      switchWorkspaceTab(btn.getAttribute("data-tab"));
    });
  });
}

export function initSliderCounters() {
  const confSlider = document.getElementById("confSlider");
  const confValue = document.getElementById("confValue");
  if (confSlider && confValue) {
    confSlider.addEventListener("input", (e) => {
      confValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
  }

  const iouSlider = document.getElementById("iouSlider");
  const iouValue = document.getElementById("iouValue");
  if (iouSlider && iouValue) {
    iouSlider.addEventListener("input", (e) => {
      iouValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
  }
}

export function initResearcherPanelRefresh() {
  const researcherPanel = document.getElementById("researcherPanel");
  if (researcherPanel) {
    researcherPanel.addEventListener("toggle", () => {
      if (window.ScrollTrigger) {
        window.ScrollTrigger.refresh();
      }
    });
  }
}

function handleFileSelection(file) {
  currentFile = file;
  const url = URL.createObjectURL(file);
  currentLocalPreviewUrl = url;

  const fileNameText = document.getElementById("fileNameText");
  const selectedBadge = document.getElementById("selectedFileName");
  if (fileNameText) fileNameText.textContent = cleanText(file.name);
  if (selectedBadge) selectedBadge.classList.remove("hidden");

  const previewImg = document.getElementById("controlPreviewImg");
  const emptyPrompt = document.getElementById("controlEmptyPrompt");
  const previewOverlay = document.getElementById("controlPreviewOverlay");
  const previewBadge = document.getElementById("controlPreviewBadge");

  if (previewImg) {
    previewImg.src = url;
    previewImg.classList.remove("hidden");
  }
  if (emptyPrompt) emptyPrompt.classList.add("hidden");
  if (previewOverlay) previewOverlay.classList.remove("hidden");
  if (previewBadge) previewBadge.textContent = cleanText(file.name);

  const wsPlaceholder = document.getElementById("workspacePlaceholder");
  const activeDisplayImg = document.getElementById("activeDisplayImg");
  const verdictActiveImg = document.getElementById("verdictActiveImg");

  if (wsPlaceholder) wsPlaceholder.classList.add("hidden");
  if (activeDisplayImg) {
    activeDisplayImg.src = url;
    activeDisplayImg.classList.remove("hidden");
  }
  if (verdictActiveImg) verdictActiveImg.src = url;

  document.querySelectorAll(".sample-thumb-box").forEach((box) => {
    box.classList.remove("is-selected");
  });
}

export function initFileInputListeners() {
  const imageInput = document.getElementById("imageInput");
  const cameraInput = document.getElementById("cameraInput");

  if (imageInput) {
    imageInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  if (cameraInput) {
    cameraInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }

  const dropArea = document.getElementById("dropzoneArea");
  if (dropArea) {
    dropArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropArea.classList.add("border-[#2F6B43]");
    });
    dropArea.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dropArea.classList.remove("border-[#2F6B43]");
    });
    dropArea.addEventListener("drop", (e) => {
      e.preventDefault();
      dropArea.classList.remove("border-[#2F6B43]");
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });
  }
}

export function clearSelectedFile() {
  currentFile = null;
  currentLocalPreviewUrl = "";

  const imageInput = document.getElementById("imageInput");
  const cameraInput = document.getElementById("cameraInput");
  if (imageInput) imageInput.value = "";
  if (cameraInput) cameraInput.value = "";

  const selectedFileName = document.getElementById("selectedFileName");
  if (selectedFileName) selectedFileName.classList.add("hidden");

  const previewImg = document.getElementById("controlPreviewImg");
  const emptyPrompt = document.getElementById("controlEmptyPrompt");
  const previewOverlay = document.getElementById("controlPreviewOverlay");
  if (previewImg) {
    previewImg.src = "";
    previewImg.classList.add("hidden");
  }
  if (emptyPrompt) emptyPrompt.classList.remove("hidden");
  if (previewOverlay) previewOverlay.classList.add("hidden");

  const wsPlaceholder = document.getElementById("workspacePlaceholder");
  const activeDisplayImg = document.getElementById("activeDisplayImg");
  if (wsPlaceholder) wsPlaceholder.classList.remove("hidden");
  if (activeDisplayImg) {
    activeDisplayImg.src = "";
    activeDisplayImg.classList.add("hidden");
  }
}

export async function loadSampleGallery() {
  const grid = document.getElementById("sampleGalleryGrid");
  const countEl = document.getElementById("sampleGalleryCount");
  if (!grid) return;

  let samplesToRender = FALLBACK_5_SAMPLES;

  try {
    const res = await fetch("/api/samples");
    if (res.ok) {
      const data = await res.json();
      if (data && data.samples && data.samples.length > 0) {
        const filtered = data.samples.filter((s) => {
          const name = (s.name || s.filename || "").toLowerCase();
          return name.startsWith("sample_") && !name.includes("hero") && !name.includes("pillar");
        });

        if (filtered.length > 0) {
          samplesToRender = filtered.map((s) => {
            const fname = s.name || s.filename;
            let label = "Sampel Daun";
            let sub = "Uji Cepat";

            if (fname.includes("black_sigatoka")) {
              label = "Black Sigatoka";
              sub = "Ganas / Kritis";
            } else if (fname.includes("yellow_sigatoka")) {
              label = "Yellow Sigatoka";
              sub = "Bercak Kuning";
            } else if (fname.includes("cordana")) {
              label = "Cordana Leaf Spot";
              sub = "Bercak Oval";
            } else if (fname.includes("pestalotiopsis")) {
              label = "Pestalotiopsis";
              sub = "Bercak Tepi";
            } else if (fname.includes("fresh")) {
              label = "Daun Sehat (Fresh)";
              sub = "Klorofil Optimal";
            }

            return {
              filename: fname,
              label,
              sub,
              url: s.url,
            };
          });
        }
      }
    }
  } catch (err) {
    console.warn("Gagal memuat sampel dari API, menggunakan fallback lokal:", err);
  }

  if (countEl) {
    countEl.textContent = "Uji Instan";
  }

  grid.innerHTML = samplesToRender
    .map(
      (s) => `
      <div class="sample-card-item bg-white border border-[#ECEEEA] rounded-2xl p-3 cursor-pointer hover:border-[#2F6B43] transition shadow-xs group" onclick="selectAndRunSample('${s.url}', '${s.filename}', this)">
        <div class="w-full aspect-[4/3] rounded-xl overflow-hidden bg-[#ECEEEA] relative">
          <img src="${s.url}" alt="${s.label}" class="w-full h-full object-cover transition-opacity duration-300 group-hover:opacity-90" loading="lazy" />
        </div>
        <div class="mt-2.5 text-left">
          <div class="text-xs font-bold text-[#111812] leading-tight truncate">${s.label}</div>
          <div class="text-xs text-[#4B524C] truncate font-mono mt-0.5">${s.sub}</div>
        </div>
      </div>
    `
    )
    .join("");
}

export async function selectAndRunSample(url, filename) {
  try {
    switchWorkspaceTab("upload");

    const res = await fetch(url);
    if (!res.ok) throw new Error("Gagal mengambil file sampel: " + filename);
    const blob = await res.blob();
    const file = new File([blob], filename, { type: blob.type || "image/jpeg" });

    handleFileSelection(file);
    await runPrediction();
  } catch (err) {
    console.error("Gagal menjalankan sampel:", err);
    alert("Gagal memuat citra sampel: " + err.message);
  }
}

function updateCanvasImages(images) {
  const activeDisplayImg = document.getElementById("activeDisplayImg");
  const verdictActiveImg = document.getElementById("verdictActiveImg");

  let targetSrc = images.annotated_b64;
  if (currentVerdictView === "clahe") targetSrc = images.clahe_b64;
  else if (currentVerdictView === "orig") targetSrc = images.original_b64;

  if (activeDisplayImg) {
    activeDisplayImg.src = targetSrc;
    activeDisplayImg.classList.remove("hidden");
  }
  if (verdictActiveImg) verdictActiveImg.src = targetSrc;

  const wsPlaceholder = document.getElementById("workspacePlaceholder");
  if (wsPlaceholder) wsPlaceholder.classList.add("hidden");

  const slots = [
    { imgId: "imgOrig", phId: "phImgOrig", badgeId: "badgeImgOrig", src: images.original_b64 },
    { imgId: "imgClahe", phId: "phImgClahe", badgeId: "badgeImgClahe", src: images.clahe_b64 },
    { imgId: "imgAnnotated", phId: "phImgAnnotated", badgeId: "badgeImgAnnotated", src: images.annotated_b64 },
  ];

  slots.forEach(({ imgId, phId, badgeId, src }) => {
    const imgEl = document.getElementById(imgId);
    const phEl = document.getElementById(phId);
    const badgeEl = document.getElementById(badgeId);
    if (imgEl && src) {
      imgEl.src = src;
      imgEl.classList.remove("hidden");
      if (phEl) phEl.classList.add("hidden");
      if (badgeEl) badgeEl.classList.remove("hidden");
    }
  });
}

function renderDiagnosisResults(data, clientRoundtripMs) {
  const agro = data.agronomy || {};

  const agroName = document.getElementById("agroName");
  const agroSci = document.getElementById("agroSci");
  const agroSeverity = document.getElementById("agroSeverity");
  const agroDeleafing = document.getElementById("agroDeleafing");
  const agroFracText = document.getElementById("agroFracText");
  const agroDisclaimer = document.getElementById("agroDisclaimer");
  const agroFracShort = document.getElementById("agroFracShort");
  const agroFracBadges = document.getElementById("agroFracBadges");

  const lesionCount = document.getElementById("lesionCount");
  const leafCount = document.getElementById("leafCount");
  const latServer = document.getElementById("latServer");
  const totalDetCount = document.getElementById("totalDetCount");

  const latPre = document.getElementById("latPre");
  const latInf = document.getElementById("latInf");
  const latPost = document.getElementById("latPost");
  const latClient = document.getElementById("latClient");

  const verdictConfPct = document.getElementById("verdictConfPct");
  const verdictConfBar = document.getElementById("verdictConfBar");
  const severityMarker = document.getElementById("severityMarker");

  if (agroName) {
    const rawName = cleanText(agro.display_name || data.dominant_class || "Daun Sehat (Fresh)");
    const match = rawName.match(/^([^(]+)(?:\s*\(([^)]+)\))?$/);
    if (match && match[2]) {
      const primary = match[1].trim();
      const secondary = match[2].trim();
      agroName.innerHTML = `
        <span class="block">${primary}</span>
        <span class="block text-sm sm:text-base font-normal text-[#4B524C] font-sans mt-0.5">(${secondary})</span>
      `;
    } else {
      agroName.textContent = rawName;
    }
  }
  if (agroSci) agroSci.textContent = cleanText(agro.scientific_name || "Musa spp.");

  const sevCategory = agro.severity_category || "Sehat Optimal";
  if (agroSeverity) {
    let badgeText = "Optimal";
    let detailText = "Kanopi fungsional normal tanpa gejala infeksi jamur.";
    let sevBadgeColor = "bg-[#DCFCE7] text-[#14532D] border border-[#BBF7D0]";
    let sevPosition = "12%";

    if (sevCategory.includes("Ganas") || sevCategory.includes("Kritis") || data.dominant_class === "Black Sigatoka") {
      badgeText = "Ganas Utama";
      detailText = "Risiko kehilangan hasil panen hingga 50% jika kanopi daun aktif rusak.";
      sevBadgeColor = "bg-[#FEE2E2] text-[#991B1B] border border-[#FECACA]";
      sevPosition = "88%";
    } else if (data.dominant_class === "Yellow Sigatoka") {
      badgeText = "Ganas (Moderat)";
      detailText = "Menurunkan luas fotosintesis fungsional secara bertahap.";
      sevBadgeColor = "bg-[#FEF3C7] text-[#78350F] border border-[#FDE68A]";
      sevPosition = "72%";
    } else if (
      sevCategory.includes("Sedang") ||
      sevCategory.includes("Ringan") ||
      data.dominant_class === "Cordana" ||
      data.dominant_class === "Pestalotiopsis"
    ) {
      badgeText = "Ringan - Sedang";
      detailText = "Penyakit jamur sekunder pada helai daun tua atau luka robekan angin.";
      sevBadgeColor = "bg-[#FEF3C7] text-[#78350F] border border-[#FDE68A]";
      sevPosition = "50%";
    }

    agroSeverity.textContent = badgeText;
    agroSeverity.className = `font-bold text-xs ${sevBadgeColor} px-2.5 py-0.5 rounded-full shadow-xs whitespace-nowrap shrink-0`;

    const sevDetailEl = document.getElementById("agroSeverityDetail");
    if (sevDetailEl) {
      sevDetailEl.textContent = detailText;
    }

    if (severityMarker) severityMarker.style.left = sevPosition;
  }

  let maxConf = 0;
  if (data.detections && data.detections.length > 0) {
    maxConf = Math.max(...data.detections.map((d) => d.confidence_pct));
  }
  if (verdictConfPct) verdictConfPct.textContent = maxConf > 0 ? `${maxConf.toFixed(1)}%` : "N/A";
  if (verdictConfBar) {
    const scale = maxConf > 0 ? Math.min(Math.max(maxConf / 100, 0), 1) : 0;
    verdictConfBar.style.transform = `scaleX(${scale})`;
  }

  if (lesionCount) lesionCount.textContent = data.lesion_level_count !== undefined ? data.lesion_level_count : 0;
  if (leafCount) leafCount.textContent = data.leaf_level_count !== undefined ? data.leaf_level_count : 0;
  if (totalDetCount) {
    const totalMs =
      data.telemetry && data.telemetry.server_total_ms
        ? `${data.telemetry.server_total_ms} ms`
        : `${data.total_detections !== undefined ? data.total_detections : 0} Deteksi`;
    totalDetCount.textContent = totalMs;
  }

  if (data.telemetry) {
    if (latServer) {
      latServer.innerHTML = `${data.telemetry.server_total_ms} <span class="text-xs font-sans font-medium text-[#4B524C]">ms</span>`;
    }
    if (latPre) latPre.textContent = `${data.telemetry.preprocess_ms} ms`;
    if (latInf) latInf.textContent = `${data.telemetry.inference_nms_ms} ms`;
    if (latPost) latPost.textContent = `${data.telemetry.postprocess_ms} ms`;
  }
  if (latClient) latClient.textContent = `${clientRoundtripMs} ms`;

  if (agroDeleafing) {
    agroDeleafing.textContent = cleanText(
      agro.deleafing_protocol || "Pertahankan minimal 6 sampai 8 daun fungsional sehat."
    );
  }
  if (agroFracText) {
    agroFracText.textContent = cleanText(
      agro.frac_recommendation || "Penyemprotan fungisida tidak diperlukan untuk daun sehat."
    );
  }
  if (agroDisclaimer) {
    agroDisclaimer.textContent = cleanText(
      agro.ppl_disclaimer || "Lakukan pengamatan kebun secara berkala."
    );
  }

  if (agroFracShort) {
    const codes = agro.frac_codes || [];
    agroFracShort.innerHTML = codes
      .map((raw) => {
        const text = cleanText(raw);
        const match = text.match(/^(FRAC\s+[^\s(]+)\s*\((.+)\)$/i);
        if (match) {
          return `
            <div class="flex items-start gap-2 text-xs sm:text-[0.8125rem] text-[#111812]">
              <span class="font-mono font-bold text-[0.7rem] text-[#163C24] bg-[#F7F8F5] border border-[#E8ECE6] px-1.5 py-0.5 rounded shrink-0">${match[1]}</span>
              <span class="font-medium text-[#111812] leading-snug">${match[2]}</span>
            </div>
          `;
        }
        return `
          <div class="flex items-center gap-2 text-xs sm:text-[0.8125rem] text-[#111812]">
            <span class="w-1.5 h-1.5 rounded-full bg-[#2F6B43] shrink-0"></span>
            <span class="font-semibold">${text}</span>
          </div>
        `;
      })
      .join("");
  }

  if (agroFracBadges) {
    const codes = agro.frac_codes || [];
    agroFracBadges.innerHTML = codes
      .map((raw, idx) => {
        const text = cleanText(raw);
        const match = text.match(/^(FRAC\s+[^\s(]+)\s*\((.+)\)$/i);
        if (match) {
          const rest = match[2];
          let group = rest;
          if (rest.includes(":")) {
            group = rest.split(":")[0].trim();
          }
          return `
            <div class="flex items-center justify-between gap-2.5 p-3 sm:py-2.5 sm:px-3.5 rounded-xl bg-[#F7F8F5] border border-[#E8ECE6] text-sm">
              <div class="flex items-center gap-2.5 min-w-0">
                <span class="font-mono font-bold text-xs sm:text-sm text-[#163C24] bg-white border border-[#E2E6DE] px-2.5 py-1 rounded shadow-2xs shrink-0">${match[1]}</span>
                <span class="font-semibold text-xs sm:text-sm text-[#111812] truncate">${group}</span>
              </div>
              <span class="text-xs font-mono font-medium text-[#4B524C] bg-white px-2.5 py-1 rounded border border-[#E8ECE6] shrink-0">Giliran ${idx + 1}</span>
            </div>
          `;
        }

        return `
          <div class="flex items-center gap-2.5 p-3 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] text-sm">
            <span class="w-2 h-2 rounded-full bg-[#16a34a] shrink-0"></span>
            <span class="font-semibold text-[#14532D] text-xs sm:text-sm">${text} (Kondisi Kanopi Sehat)</span>
          </div>
        `;
      })
      .join("");
  }

  const tbody = document.getElementById("bboxTableBody");
  if (tbody) {
    if (data.detections && data.detections.length > 0) {
      tbody.innerHTML = data.detections
        .map(
          (d) => `
        <tr class="hover:bg-slate-50 transition border-b border-[#ECEEEA]">
          <td class="py-2.5 px-3 font-bold text-[#111812]">#${d.id}</td>
          <td class="py-2.5 px-3 font-semibold text-[#111812]">${cleanText(d.class_name)}</td>
          <td class="py-2.5 px-3 font-bold text-[#2F6B43]">${d.confidence_pct}%</td>
          <td class="py-2.5 px-3 text-[#4B524C]">${d.box_area_ratio_pct}%</td>
          <td class="py-2.5 px-3 text-[#4B524C]">${cleanText(d.granularity)}</td>
          <td class="py-2.5 px-3 text-[#4B524C] text-xs">[${d.bbox.join(", ")}]</td>
        </tr>
      `
        )
        .join("");
    } else {
      tbody.innerHTML =
        '<tr><td colspan="6" class="py-4 text-center text-[#4B524C]">Tidak ada kotak terdeteksi.</td></tr>';
    }
  }
}

export async function runPrediction() {
  if (!currentFile) {
    alert("Silakan pilih salah satu sampel daun atau unggah foto daun pisang terlebih dahulu.");
    return;
  }

  const predictBtn = document.getElementById("predictBtn");
  if (predictBtn) {
    predictBtn.disabled = true;
    predictBtn.classList.add("opacity-75", "cursor-wait");
    predictBtn.innerHTML = `
      <div class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
      <span>Menganalisis...</span>
    `;
  }

  const loadingBox = document.getElementById("loadingBox");
  const rejectedBox = document.getElementById("rejectedBox");
  const noDetectionBox = document.getElementById("noDetectionBox");
  const initialEmptyBox = document.getElementById("initialEmptyBox");
  const visualResultBox = document.getElementById("visualResultBox");

  if (initialEmptyBox) initialEmptyBox.classList.add("hidden");
  if (visualResultBox) visualResultBox.classList.add("hidden");
  if (rejectedBox) rejectedBox.classList.add("hidden");
  if (noDetectionBox) noDetectionBox.classList.add("hidden");
  if (loadingBox) loadingBox.classList.remove("hidden");

  const formData = new FormData();
  formData.append("image", currentFile);

  const confSlider = document.getElementById("confSlider");
  const iouSlider = document.getElementById("iouSlider");
  const useClaheToggle = document.getElementById("useClaheToggle");

  formData.append("conf_threshold", confSlider ? confSlider.value : "0.25");
  formData.append("iou_threshold", iouSlider ? iouSlider.value : "0.45");
  formData.append("use_clahe", useClaheToggle && useClaheToggle.checked ? "true" : "false");

  const tStartClient = performance.now();

  try {
    const res = await fetch("/predict", { method: "POST", body: formData });
    const data = await res.json();
    const clientRoundtripMs = (performance.now() - tStartClient).toFixed(2);

    if (loadingBox) loadingBox.classList.add("hidden");

    if (data.status === "error") {
      alert(data.message || "Terjadi kesalahan pada pemrosesan server.");
      return;
    }

    lastResponseData = data;

    if (data.status === "rejected") {
      if (rejectedBox) rejectedBox.classList.remove("hidden");
      if (visualResultBox) visualResultBox.classList.add("hidden");

      const rTitle = document.getElementById("rejectedTitle");
      if (rTitle) rTitle.textContent = cleanText(data.title || "Objek Bukan Daun Pisang");

      const rReason = document.getElementById("rejectedReason");
      if (rReason) {
        rReason.textContent = cleanText(
          data.reason ||
            "Citra yang diunggah teridentifikasi sebagai objek bukan daun pisang. Mohon fokuskan kamera pada permukaan helai daun pisang (Musa spp.) tanpa menyertakan pot, manusia, atau objek lain."
        );
      }

      const rMetrics = document.getElementById("rejectedMetrics");
      if (rMetrics && data.metrics) {
        const gy = data.metrics.green_yellow_pct !== undefined ? data.metrics.green_yellow_pct : 0;
        const bot = data.metrics.botanical_pct || 0;
        rMetrics.textContent = `Validasi: Objek Bukan Daun Pisang | Klorofil: ${gy}% | Lamina: ${bot}%`;
      }

      switchWorkspaceTab("result");
      return;
    }

    if (data.status === "no_detection" || (data.detections && data.detections.length === 0)) {
      if (noDetectionBox) noDetectionBox.classList.remove("hidden");
      if (visualResultBox) visualResultBox.classList.add("hidden");

      if (data.images) {
        updateCanvasImages(data.images);
      }

      switchWorkspaceTab("result");
      return;
    }

    if (data.images) {
      updateCanvasImages(data.images);
    }

    renderDiagnosisResults(data, clientRoundtripMs);
    await saveToIndexedDBHistory(data, clientRoundtripMs, currentFile, currentLocalPreviewUrl);

    if (visualResultBox) {
      visualResultBox.classList.remove("hidden");
    }

    switchWorkspaceTab("result");

    if (window.ScrollTrigger) {
      window.ScrollTrigger.refresh();
    }
  } catch (err) {
    console.error("Gagal melakukan prediksi:", err);
    alert("Koneksi gagal atau pemrosesan terputus: " + err.message);
    if (loadingBox) loadingBox.classList.add("hidden");
  } finally {
    if (predictBtn) {
      predictBtn.disabled = false;
      predictBtn.classList.remove("opacity-75", "cursor-wait");
      predictBtn.innerHTML = `
        <span>Analisis Daun Pisang</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      `;
    }
  }
}

function updateSwitcherActiveBtn(mode) {
  const btnAnn = document.getElementById("btnSwitchAnnotated");
  const btnCla = document.getElementById("btnSwitchClahe");
  const btnOri = document.getElementById("btnSwitchOrig");

  [btnAnn, btnCla, btnOri].forEach((btn) => {
    if (btn) btn.className = "detection-tab-btn";
  });

  const activeBtn = mode === "clahe" ? btnCla : mode === "orig" ? btnOri : btnAnn;
  if (activeBtn) {
    activeBtn.className = "detection-tab-btn active";
  }
}

export function switchVerdictView(mode) {
  currentVerdictView = mode;
  updateSwitcherActiveBtn(mode);

  const activeDisplayImg = document.getElementById("activeDisplayImg");
  const verdictActiveImg = document.getElementById("verdictActiveImg");

  if (lastResponseData && lastResponseData.images) {
    let targetSrc = lastResponseData.images.annotated_b64;
    if (mode === "clahe") targetSrc = lastResponseData.images.clahe_b64;
    else if (mode === "orig") targetSrc = lastResponseData.images.original_b64;

    if (activeDisplayImg) activeDisplayImg.src = targetSrc;
    if (verdictActiveImg) verdictActiveImg.src = targetSrc;
  }
}

export function resetDetectionState() {
  resetDetectorSessionState();
  clearSelectedFile();

  const visualResultBox = document.getElementById("visualResultBox");
  const initialEmptyBox = document.getElementById("initialEmptyBox");
  const loadingBox = document.getElementById("loadingBox");
  const rejectedBox = document.getElementById("rejectedBox");
  const noDetectionBox = document.getElementById("noDetectionBox");

  if (visualResultBox) visualResultBox.classList.add("hidden");
  if (loadingBox) loadingBox.classList.add("hidden");
  if (rejectedBox) rejectedBox.classList.add("hidden");
  if (noDetectionBox) noDetectionBox.classList.add("hidden");
  if (initialEmptyBox) initialEmptyBox.classList.remove("hidden");

  [
    { imgId: "imgOrig", phId: "phImgOrig", badgeId: "badgeImgOrig" },
    { imgId: "imgClahe", phId: "phImgClahe", badgeId: "badgeImgClahe" },
    { imgId: "imgAnnotated", phId: "phImgAnnotated", badgeId: "badgeImgAnnotated" },
  ].forEach(({ imgId, phId, badgeId }) => {
    const imgEl = document.getElementById(imgId);
    const phEl = document.getElementById(phId);
    const badgeEl = document.getElementById(badgeId);
    if (imgEl) {
      imgEl.src = "";
      imgEl.classList.add("hidden");
    }
    if (phEl) phEl.classList.remove("hidden");
    if (badgeEl) badgeEl.classList.add("hidden");
  });

  switchWorkspaceTab("upload");
}

export function openLightboxFullscreen() {
  const modal = document.getElementById("lightboxModal");
  const img = document.getElementById("lightboxImg");
  const cap = document.getElementById("lightboxCaption");

  let src = "";
  let caption = "Pratinjau Citra Resolusi Penuh";

  if (lastResponseData && lastResponseData.images) {
    if (currentVerdictView === "clahe") {
      src = lastResponseData.images.clahe_b64;
      caption = "Prapemrosesan Penajaman CIE-LAB CLAHE (Kanal L)";
    } else if (currentVerdictView === "orig") {
      src = lastResponseData.images.original_b64;
      caption = "Citra Asli Helai Daun Pisang (Raw RGB)";
    } else {
      src = lastResponseData.images.annotated_b64;
      caption = `Hasil Deteksi YOLO26n: ${cleanText(lastResponseData.dominant_class || "Bercak Daun")}`;
    }
  } else if (currentLocalPreviewUrl) {
    src = currentLocalPreviewUrl;
    caption = "Pratinjau Citra Helai Daun Pisang";
  } else {
    alert("Silakan pilih citra daun atau jalankan analisis terlebih dahulu.");
    return;
  }

  if (img) img.src = src;
  if (cap) cap.textContent = caption;
  if (modal) {
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
  }
}

export function closeLightbox() {
  const modal = document.getElementById("lightboxModal");
  if (modal) modal.classList.add("hidden");
  document.body.classList.remove("overflow-hidden");
}

export function switchLightboxTab(mode) {
  currentVerdictView = mode;
  switchVerdictView(mode);

  const img = document.getElementById("lightboxImg");
  const cap = document.getElementById("lightboxCaption");

  if (lastResponseData && lastResponseData.images) {
    let src = lastResponseData.images.annotated_b64;
    let caption = `Hasil Deteksi YOLO26n: ${cleanText(lastResponseData.dominant_class || "Bercak Daun")}`;

    if (mode === "clahe") {
      src = lastResponseData.images.clahe_b64;
      caption = "Prapemrosesan Penajaman CIE-LAB CLAHE (Kanal L)";
    } else if (mode === "orig") {
      src = lastResponseData.images.original_b64;
      caption = "Citra Asli Helai Daun Pisang (Raw RGB)";
    }

    if (img) img.src = src;
    if (cap) cap.textContent = caption;
  }
}

export function downloadDetectionResult() {
  if (lastResponseData && lastResponseData.images && lastResponseData.images.annotated_b64) {
    const dominant = (lastResponseData.dominant_class || "Patogen").replace(/\s+/g, "_");
    const link = document.createElement("a");
    link.href = lastResponseData.images.annotated_b64;
    link.download = `MusaVision_Deteksi_${dominant}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } else {
    alert("Belum ada citra hasil deteksi untuk diunduh.");
  }
}

export function renderSusQuestions() {
  const container = document.getElementById("susContainer");
  if (!container) return;

  container.innerHTML = SUS_QUESTIONS.map(
    (q, idx) => `
    <div class="sus-question-row flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 rounded-xl border border-[#ECEEEA] bg-[#F6F7F4]">
      <div class="text-xs sm:text-sm font-medium text-[#111812] leading-relaxed flex-1 pr-2">
        <span class="font-bold font-mono text-[#2F6B43] mr-1">${idx + 1}.</span> ${q}
      </div>
      <div class="sus-scale-radios grid grid-cols-5 gap-1.5 w-full md:w-64 shrink-0">
        ${[1, 2, 3, 4, 5]
          .map(
            (val) => `
          <label class="cursor-pointer flex flex-col items-center justify-center py-2 px-1 rounded-lg border border-[#E8EAE6] hover:border-[#2F6B43] hover:bg-white transition text-center min-h-[44px]">
            <input type="radio" name="sus_q_${idx}" value="${val}" ${val === (idx % 2 === 0 ? 5 : 1) ? "checked" : ""} class="accent-[#2F6B43] cursor-pointer mb-1" />
            <span class="font-mono text-xs font-bold text-[#111812]">${val}</span>
            <span class="text-xs text-[#4B524C] leading-none">${val === 1 ? "STS" : val === 5 ? "SS" : ""}</span>
          </label>
        `
          )
          .join("")}
      </div>
    </div>
  `
  ).join("");
}

export function calculateSusScore() {
  const answers = [];
  for (let i = 0; i < 10; i++) {
    const selected = document.querySelector(`input[name="sus_q_${i}"]:checked`);
    if (!selected) {
      alert("Harap jawab seluruh 10 pertanyaan kuesioner SUS terlebih dahulu.");
      return;
    }
    answers.push(parseInt(selected.value, 10));
  }

  let oddSum = 0;
  for (let i = 0; i < 10; i += 2) oddSum += answers[i] - 1;

  let evenSum = 0;
  for (let i = 1; i < 10; i += 2) evenSum += 5 - answers[i];

  const score = (oddSum + evenSum) * 2.5;
  const scoreDisplay = document.getElementById("susScoreDisplay");
  const gradeBadge = document.getElementById("susGradeBadge");
  const adjBadge = document.getElementById("susAdjectiveBadge");

  if (scoreDisplay) scoreDisplay.textContent = score.toFixed(1);

  let grade = "Grade A";
  let adj = "Excellent";
  if (score < 51.0) {
    grade = "Grade F";
    adj = "Poor";
  } else if (score < 68.0) {
    grade = "Grade C";
    adj = "Marginal";
  } else if (score < 80.3) {
    grade = "Grade B";
    adj = "Good";
  }

  if (gradeBadge) gradeBadge.textContent = grade;
  if (adjBadge) adjBadge.textContent = adj;
}

export function bindDetectorGlobals() {
  window.switchWorkspaceTab = switchWorkspaceTab;
  window.clearSelectedFile = clearSelectedFile;
  window.selectAndRunSample = selectAndRunSample;
  window.runPrediction = runPrediction;
  window.switchVerdictView = switchVerdictView;
  window.resetDetectionState = resetDetectionState;
  window.openLightboxFullscreen = openLightboxFullscreen;
  window.closeLightbox = closeLightbox;
  window.switchLightboxTab = switchLightboxTab;
  window.downloadDetectionResult = downloadDetectionResult;
  window.calculateSusScore = calculateSusScore;
}
