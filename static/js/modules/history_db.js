/**
 * Persistent IndexedDB field-testing history with desktop table, mobile cards, CSV export, and modal viewer.
 */

const DB_NAME = "MusaVisionDB";
const DB_VERSION = 1;
const STORE_NAME = "detection_history";

export function cleanText(str) {
  if (!str) return "";
  return String(str)
    .replace(
      /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2300}-\u{23FF}\u{2B50}\u{200D}\u{FE0F}]/gu,
      ""
    )
    .replace(/\u2014/g, ": ")
    .replace(/\u2013/g, "-")
    .trim();
}

function openIndexedDB() {
  return new Promise((resolve, reject) => {
    if (!window.indexedDB) {
      reject(new Error("IndexedDB tidak didukung oleh browser ini."));
      return;
    }
    const req = window.indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
        store.createIndex("timestamp", "timestamp", { unique: false });
        store.createIndex("dominant_class", "dominant_class", { unique: false });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function createThumbnailBase64(sourceUrlOrBase64, maxSide = 140) {
  return new Promise((resolve) => {
    if (!sourceUrlOrBase64) {
      resolve("");
      return;
    }
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const canvas = document.createElement("canvas");
        let w = img.width;
        let h = img.height;
        if (w > h) {
          if (w > maxSide) {
            h = Math.round((h * maxSide) / w);
            w = maxSide;
          }
        } else if (h > maxSide) {
          w = Math.round((w * maxSide) / h);
          h = maxSide;
        }
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL("image/jpeg", 0.72));
      } catch (err) {
        resolve("");
      }
    };
    img.onerror = () => resolve("");
    img.src = sourceUrlOrBase64;
  });
}

async function saveDetectionToIndexedDB(record) {
  try {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      const req = store.add(record);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    try {
      const backup = JSON.parse(localStorage.getItem("musa_vision_backup_hist") || "[]");
      backup.unshift(record);
      localStorage.setItem("musa_vision_backup_hist", JSON.stringify(backup.slice(0, 30)));
    } catch (e) {
      // Ignore storage quota errors
    }
    return null;
  }
}

async function getAllHistoryFromIndexedDB() {
  try {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const store = tx.objectStore(STORE_NAME);
      const req = store.getAll();
      req.onsuccess = () => {
        const list = req.result || [];
        list.sort((a, b) => b.id - a.id);
        resolve(list);
      };
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    try {
      return JSON.parse(localStorage.getItem("musa_vision_backup_hist") || "[]");
    } catch (e) {
      return [];
    }
  }
}

async function deleteHistoryItemFromIndexedDB(id) {
  try {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      const req = store.delete(Number(id));
      req.onsuccess = () => resolve(true);
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    return false;
  }
}

async function clearAllHistoryFromIndexedDB() {
  try {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      const req = store.clear();
      req.onsuccess = () => resolve(true);
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    localStorage.removeItem("musa_vision_backup_hist");
    return true;
  }
}

export async function saveToIndexedDBHistory(data, clientRoundtripMs, currentFile, currentLocalPreviewUrl) {
  try {
    const now = new Date();
    const timeFormatted =
      now.toLocaleDateString("id-ID", {
        day: "numeric",
        month: "short",
        year: "numeric",
      }) +
      " " +
      now.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });

    let thumbB64 = "";
    if (data.images && data.images.annotated_b64) {
      thumbB64 = await createThumbnailBase64(data.images.annotated_b64, 140);
    } else if (currentLocalPreviewUrl) {
      thumbB64 = await createThumbnailBase64(currentLocalPreviewUrl, 140);
    }

    let maxConf = 0;
    if (data.detections && data.detections.length > 0) {
      maxConf = Math.max(...data.detections.map((d) => d.confidence_pct));
    }

    const record = {
      timestamp: now.toISOString(),
      timeFormatted,
      filename: currentFile ? cleanText(currentFile.name) : "sampel.jpg",
      dominant_class: cleanText(data.dominant_class || "Daun Sehat"),
      scientific_name: cleanText(data.agronomy ? data.agronomy.scientific_name : "Musa spp."),
      severity: cleanText(data.agronomy ? data.agronomy.severity_category : "Sehat Optimal"),
      conf_pct: maxConf > 0 ? maxConf.toFixed(1) : "-",
      lesion_count: data.lesion_level_count !== undefined ? data.lesion_level_count : 0,
      leaf_count: data.leaf_level_count !== undefined ? data.leaf_level_count : 1,
      total_detections: data.total_detections !== undefined ? data.total_detections : 0,
      server_ms: data.telemetry ? data.telemetry.server_total_ms : "-",
      client_ms: clientRoundtripMs,
      use_clahe: data.use_clahe ? "Ya" : "Tidak",
      frac_summary:
        data.agronomy && data.agronomy.frac_codes
          ? cleanText(data.agronomy.frac_codes.join(", "))
          : "Tidak Diperlukan",
      thumbnail_b64: thumbB64,
    };

    await saveDetectionToIndexedDB(record);
    await renderHistoryTable();
  } catch (err) {
    console.error("Gagal mencatat ke IndexedDB:", err);
  }
}

export async function renderHistoryTable() {
  const tbody = document.getElementById("historyTableBody");
  const mobileList = document.getElementById("historyListMobile");
  if (!tbody && !mobileList) return;

  try {
    const list = await getAllHistoryFromIndexedDB();
    if (list.length === 0) {
      if (tbody) {
        tbody.innerHTML =
          '<tr><td colspan="7" class="py-6 text-center text-[#4B524C]">Belum ada riwayat pengujian pada peramban ini.</td></tr>';
      }
      if (mobileList) {
        mobileList.innerHTML =
          '<div class="py-8 text-center text-xs text-[#4B524C]">Belum ada riwayat pengujian pada peramban ini.</div>';
      }
      return;
    }

    if (tbody) {
      tbody.innerHTML = list
        .map(
          (it) => `
        <tr class="hover:bg-slate-50 transition border-b border-[#ECEEEA]">
          <td class="py-2.5 px-3">
            ${
              it.thumbnail_b64
                ? `<img src="${it.thumbnail_b64}" alt="${cleanText(it.dominant_class)}" class="w-11 h-11 rounded-lg object-cover bg-[#ECEEEA] border border-[#E8EAE6] cursor-pointer transition-opacity hover:opacity-85" onclick="openHistoryDetailModal(${it.id})" title="Klik untuk lihat detail" />`
                : '<div class="w-11 h-11 rounded-lg bg-[#ECEEEA] flex items-center justify-center text-xs text-[#4B524C] font-mono">No Img</div>'
            }
          </td>
          <td class="py-2.5 px-3 font-mono text-[#4B524C] text-xs whitespace-nowrap">${it.timeFormatted || it.timestamp}</td>
          <td class="py-2.5 px-3 font-medium text-[#111812] truncate max-w-[130px]">${cleanText(it.filename)}</td>
          <td class="py-2.5 px-3">
            <span class="font-bold text-[#111812] block">${cleanText(it.dominant_class)}</span>
            <span class="text-xs text-[#4B524C] block">${cleanText(it.severity)}</span>
          </td>
          <td class="py-2.5 px-3 font-mono text-center">
            <span class="font-semibold text-[#111812]">${it.lesion_count}</span>
            <span class="text-xs text-[#4B524C] block">Lesi</span>
          </td>
          <td class="py-2.5 px-3 font-mono text-[#4B524C] text-xs whitespace-nowrap">${it.server_ms} ms</td>
          <td class="py-2.5 px-3 text-right whitespace-nowrap">
            <button type="button" onclick="openHistoryDetailModal(${it.id})" class="text-[#2F6B43] hover:text-[#245434] font-semibold text-xs mr-2.5 transition" title="Lihat Detail">
              Lihat
            </button>
            <button type="button" onclick="deleteHistoryRow(${it.id})" class="text-rose-600 hover:text-rose-800 text-xs transition" title="Hapus Entri">
              Hapus
            </button>
          </td>
        </tr>
      `
        )
        .join("");
    }

    if (mobileList) {
      mobileList.innerHTML = list
        .map((it) => {
          const domClass = cleanText(it.dominant_class || "Daun Sehat");
          const sevDesc = cleanText(it.severity || "Sehat Optimal");
          const fname = cleanText(it.filename || "foto_daun.jpg");
          const time = it.timeFormatted || it.timestamp || "-";
          const lesion = it.lesion_count !== undefined ? it.lesion_count : 0;
          const serverMs = it.server_ms !== undefined ? it.server_ms : "-";

          return `
            <div class="py-4 border-b border-[#E5E7E2] first:pt-1 last:border-b-0">
              <div class="flex items-center justify-between gap-3">
                <span class="text-base font-bold text-[#111812] tracking-tight">${domClass}</span>
                <div class="flex items-center gap-2 shrink-0">
                  <button type="button" onclick="openHistoryDetailModal(${it.id})" class="px-3.5 py-1.5 rounded-full border border-[#D8DCD5] bg-white text-[#163C24] font-semibold text-[0.8125rem] shadow-2xs hover:bg-[#F6F7F4] active:scale-95 transition" title="Lihat Detail">
                    Lihat
                  </button>
                  <button type="button" onclick="deleteHistoryRow(${it.id})" class="p-1.5 text-[#8A9086] hover:text-rose-600 transition" title="Hapus Entri" aria-label="Hapus Entri">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M3 6h18"></path>
                      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="text-[0.875rem] text-[#4B524C] leading-snug mt-1">
                ${sevDesc}
              </div>
              <div class="flex items-center gap-1.5 text-[0.8125rem] text-[#5A625B] font-mono mt-2 min-w-0">
                <span class="font-semibold text-[#111812] shrink-0">${lesion} Lesi</span>
                <span class="text-[#CCD0C7] shrink-0">&middot;</span>
                <span class="shrink-0">${serverMs} ms</span>
                <span class="text-[#CCD0C7] shrink-0">&middot;</span>
                <span class="truncate" title="${fname}">${fname}</span>
                <span class="text-[#CCD0C7] shrink-0">&middot;</span>
                <span class="shrink-0 text-[#7A8076]">${time}</span>
              </div>
            </div>
          `;
        })
        .join("");
    }
  } catch (err) {
    console.error("Gagal menampilkan tabel riwayat:", err);
  }
}

export async function openHistoryDetailModal(id) {
  try {
    const list = await getAllHistoryFromIndexedDB();
    const item = list.find((it) => it.id === Number(id));
    if (!item) return;

    const modal = document.getElementById("historyDetailModal");
    const title = document.getElementById("hdmTitle");
    const sci = document.getElementById("hdmSci");
    const time = document.getElementById("hdmTime");
    const file = document.getElementById("hdmFile");
    const img = document.getElementById("hdmImg");
    const severity = document.getElementById("hdmSeverity");
    const counts = document.getElementById("hdmCounts");
    const frac = document.getElementById("hdmFrac");
    const latency = document.getElementById("hdmLatency");

    if (title) title.textContent = cleanText(item.dominant_class);
    if (sci) sci.textContent = cleanText(item.scientific_name || "Musa spp.");
    if (time) time.textContent = item.timeFormatted || item.timestamp;
    if (file) file.textContent = cleanText(item.filename);
    if (img) img.src = item.thumbnail_b64 || "";
    if (severity) severity.textContent = cleanText(item.severity);
    if (counts) counts.textContent = `${item.lesion_count} Lesi Bercak, ${item.leaf_count} Helai Daun (Keyakinan: ${item.conf_pct}%)`;
    if (frac) frac.textContent = cleanText(item.frac_summary);
    if (latency) latency.textContent = `Server: ${item.server_ms} ms | Client Roundtrip: ${item.client_ms} ms`;

    if (modal) {
      modal.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
    }
  } catch (err) {
    console.error("Gagal membuka detail riwayat:", err);
  }
}

export function closeHistoryDetailModal() {
  const modal = document.getElementById("historyDetailModal");
  if (modal) modal.classList.add("hidden");
  document.body.classList.remove("overflow-hidden");
}

export async function deleteHistoryRow(id) {
  if (confirm("Hapus entri riwayat pengujian ini?")) {
    await deleteHistoryItemFromIndexedDB(id);
    await renderHistoryTable();
  }
}

export async function clearDetectionHistory() {
  if (confirm("Apakah Anda yakin ingin menghapus seluruh log riwayat pengujian pada peramban ini?")) {
    await clearAllHistoryFromIndexedDB();
    await renderHistoryTable();
  }
}

export async function exportHistoryCsv() {
  const list = await getAllHistoryFromIndexedDB();
  if (list.length === 0) {
    alert("Tidak ada data riwayat pengujian untuk diekspor.");
    return;
  }

  const headers = [
    "ID",
    "Waktu",
    "Nama File",
    "Vonis Dominan",
    "Keparahan",
    "Keyakinan (%)",
    "Lesi",
    "Daun",
    "Rekomendasi FRAC",
    "Server Latensi (ms)",
    "Client Roundtrip (ms)",
  ];
  const rows = list.map((item) => [
    item.id,
    `"${item.timeFormatted || item.timestamp}"`,
    `"${cleanText(item.filename)}"`,
    `"${cleanText(item.dominant_class)}"`,
    `"${cleanText(item.severity)}"`,
    `"${item.conf_pct}"`,
    item.lesion_count,
    item.leaf_count,
    `"${cleanText(item.frac_summary)}"`,
    item.server_ms,
    item.client_ms,
  ]);

  const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.setAttribute("href", url);
  a.setAttribute("download", "musavision_riwayat_deteksi.csv");
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

export function bindHistoryGlobals() {
  window.openHistoryDetailModal = openHistoryDetailModal;
  window.closeHistoryDetailModal = closeHistoryDetailModal;
  window.deleteHistoryRow = deleteHistoryRow;
  window.clearDetectionHistory = clearDetectionHistory;
  window.exportHistoryCsv = exportHistoryCsv;
}
