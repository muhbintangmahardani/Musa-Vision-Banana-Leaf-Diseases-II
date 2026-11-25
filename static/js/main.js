let currentFile = null;
let currentLocalPreviewUrl = "";
let currentLoadedSampleUrl = null;
let lastResponseData = null;
let currentVerdictView = "annotated";
let currentWorkspaceTab = "upload";
let lenisInstance = null;

const DB_NAME = "MusaVisionDB";
const DB_VERSION = 1;
const STORE_NAME = "detection_history";

const KEUNGGULAN_PHOTOS = [
  "/static/samples/pillar_canopy_management.jpg",
  "/static/samples/musavision_hero_bg.jpg",
  "/static/samples/pillar_sanitation_deleafing.jpg",
  "/static/samples/pillar_frac_spraying.jpg"
];

const FALLBACK_5_SAMPLES = [
  { filename: "sample_black_sigatoka.jpg", label: "Black Sigatoka", sub: "Ganas / Kritis", url: "/sample-file/samples/sample_black_sigatoka.jpg" },
  { filename: "sample_yellow_sigatoka.jpg", label: "Yellow Sigatoka", sub: "Bercak Kuning", url: "/sample-file/samples/sample_yellow_sigatoka.jpg" },
  { filename: "sample_cordana.jpg", label: "Cordana Leaf Spot", sub: "Bercak Oval", url: "/sample-file/samples/sample_cordana.jpg" },
  { filename: "sample_pestalotiopsis.jpg", label: "Pestalotiopsis", sub: "Bercak Tepi", url: "/sample-file/samples/sample_pestalotiopsis.jpg" },
  { filename: "sample_fresh.jpg", label: "Daun Sehat (Fresh)", sub: "Klorofil Optimal", url: "/sample-file/samples/sample_fresh.jpg" }
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
  "Saya perlu mempelajari banyak hal terlebih dahulu sebelum dapat menggunakan sistem ini."
];

function cleanText(str) {
  if (!str) return "";
  return String(str)
    .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2300}-\u{23FF}\u{2B50}\u{200D}\u{FE0F}]/gu, "")
    .replace(/\u2014/g, ": ")
    .replace(/\u2013/g, "-")
    .trim();
}

function smoothScrollTo(targetEl) {
  if (!targetEl) return;
  if (window.lenis && typeof window.lenis.scrollTo === "function") {
    window.lenis.scrollTo(targetEl, { offset: -76, duration: 1.15 });
  } else {
    targetEl.scrollIntoView({ behavior: "smooth" });
  }
}
window.smoothScrollTo = smoothScrollTo;

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
        } else {
          if (h > maxSide) {
            w = Math.round((w * maxSide) / h);
            h = maxSide;
          }
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
      // Ignored
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

document.addEventListener("DOMContentLoaded", () => {
  currentFile = null;
  currentLocalPreviewUrl = "";
  lastResponseData = null;

  initNavbarScroll();
  initAnchorClickInterceptors();
  initHeroSlideshow();
  initBackToTop();
  initKeunggulanAccordion();
  initFaqAccordion();
  initWorkspaceTabs();
  initSliderCounters();
  initFileInputListeners();
  initResearcherPanelRefresh();
  loadSampleGallery();
  renderHistoryTable();
  renderSusQuestions();

  initOptionalAnimations();

  // Inisialisasi status aktif navigasi desktop & mobile terpadu
  if (window.location.pathname.includes("/deteksi")) {
    if (typeof window.setActiveNav === "function") window.setActiveNav("deteksi");
  } else if (window.location.pathname.includes("/katalog-patogen")) {
    if (typeof window.setActiveNav === "function") window.setActiveNav("katalog");
  } else if (window.location.hash) {
    const hashKey = window.location.hash.replace("#", "").replace("-preview", "").replace("-section", "");
    if (typeof window.setActiveNav === "function") window.setActiveNav(hashKey || "beranda");
  } else {
    if (typeof window.setActiveNav === "function") window.setActiveNav("beranda");
  }

  // Anti-Flash Curtain Handler: Kunci posisi target instan lalu buka tirai
  if (document.documentElement.classList.contains("hash-jumping")) {
    const unlockCurtain = () => {
      document.documentElement.classList.remove("hash-jumping");
    };

    // Failsafe timeout 500ms agar halaman mustahil terjebak tersembunyi
    const failsafe = setTimeout(unlockCurtain, 500);

    try {
      if (window.location.hash) {
        const target = document.querySelector(window.location.hash);
        if (target) {
          const y = Math.max(0, target.getBoundingClientRect().top + window.scrollY - 88);
          window.scrollTo(0, y);
          if (window.lenis && typeof window.lenis.scrollTo === "function") {
            window.lenis.scrollTo(y, { immediate: true, force: true });
          }
          const hashKey = window.location.hash.replace("#", "").replace("-preview", "").replace("-section", "");
          if (typeof window.setActiveNav === "function") {
            window.setActiveNav(hashKey || "beranda");
          }
          if (typeof window.updateNavbarScrollState === "function") {
            window.updateNavbarScrollState(y);
          }
          if (typeof ScrollTrigger !== "undefined") {
            ScrollTrigger.refresh();
          }
        }
      }
    } catch (e) {
      console.warn("Hash jump calculation error:", e);
    }

    requestAnimationFrame(() => {
      clearTimeout(failsafe);
      unlockCurtain();
      if (typeof window.updateNavbarScrollState === "function") {
        window.updateNavbarScrollState(window.scrollY);
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeLightbox();
      closeHistoryDetailModal();
    }
  });
});

function initNavbarScroll() {
  const nav = document.getElementById("mainNavbar");
  if (!nav) return;

  // Khusus halaman statis katalog dengan background terang
  if (nav.dataset.navbarStatic === "light" || nav.classList.contains("navbar--light")) {
    nav.classList.add("is-scrolled");
    return;
  }

  let ticking = false;

  const updateNavbarScrollState = (customY) => {
    const scrollY = typeof customY === "number"
      ? customY
      : (window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0);

    // Dynamic threshold: scrollY > 40 sesuai spesifikasi user
    const threshold = 40;

    if (scrollY > threshold) {
      nav.classList.add("is-scrolled");
    } else {
      nav.classList.remove("is-scrolled");
    }
    ticking = false;
  };

  window.updateNavbarScrollState = updateNavbarScrollState;

  const onScroll = () => {
    updateNavbarScrollState();
  };

  // Jalankan segera saat inisialisasi agar posisi scrollY = 0 tidak memiliki class is-scrolled
  updateNavbarScrollState();

  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        window.requestAnimationFrame(onScroll);
        ticking = true;
      }
    },
    { passive: true }
  );

  // Jalankan juga saat window load dan resize selesai
  window.addEventListener("load", () => {
    updateNavbarScrollState();
  });
  window.addEventListener("resize", () => {
    updateNavbarScrollState();
  });

  // Expose ke global window agar sinkron saat Lenis smooth scroll diinisialisasi
  window.updateNavbarScrollState = updateNavbarScrollState;

  // Sinkronkan juga dengan listener Lenis jika sudah aktif
  if (window.lenis) {
    window.lenis.on("scroll", (e) => {
      const scrollY = e && typeof e.scroll === "number" ? e.scroll : window.scrollY;
      updateNavbarScrollState(scrollY);
      if (typeof window.trackActiveSection === "function") {
        window.trackActiveSection();
      }
    });
  }

  // Pelacakan Menu Aktif (Pill Active Auto-Move via Scroll Spy)
  initNavbarActiveTracker();

  // Close mobile drawer saat klik di luar atau tombol Escape
  document.addEventListener("click", (e) => {
    const overlay = document.getElementById("mobileMenuOverlay") || document.getElementById("mobileMenuDrawer");
    const btn = document.getElementById("hamburgerBtn") || document.getElementById("deteksiHamburgerBtn") || document.getElementById("katalogHamburgerBtn");
    if (overlay && btn && btn.classList.contains("is-open") && !overlay.contains(e.target) && !btn.contains(e.target)) {
      toggleMobileMenu(true);
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      toggleMobileMenu(true);
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 860) {
      toggleMobileMenu(true);
    }
  });
}

function setActiveNav(sectionKey) {
  if (!sectionKey) return;
  let key = sectionKey.toLowerCase().trim();
  if (key.startsWith("#")) key = key.substring(1);
  if (key === "katalog-preview" || key === "katalog-patogen") key = "katalog";
  if (key === "workspace-deteksi") key = "deteksi";
  if (key === "faq-section") key = "beranda";

  // 1. Bersihkan is-active dari semua desktop links
  const desktopLinks = document.querySelectorAll("#desktopNavPill .nav-item-link, .nav-center-pill .nav-item-link");
  desktopLinks.forEach((link) => {
    link.classList.remove("is-active");
    const dot = link.querySelector(".nav-dot-active");
    if (dot) dot.remove();
  });

  // 2. Bersihkan is-active dari semua mobile links
  const mobileLinks = document.querySelectorAll(".mobile-nav-link");
  mobileLinks.forEach((link) => {
    link.classList.remove("is-active");
  });

  // 3. Tambahkan is-active ke desktop link yang cocok
  desktopLinks.forEach((link) => {
    const linkKey = link.getAttribute("data-nav-key") || link.getAttribute("data-section");
    if (linkKey === key) {
      link.classList.add("is-active");
      if (!link.querySelector(".nav-dot-active")) {
        const dot = document.createElement("span");
        dot.className = "nav-dot-active";
        link.prepend(dot);
      }
    }
  });

  // 4. Tambahkan is-active ke mobile link yang cocok
  mobileLinks.forEach((link) => {
    const linkKey = link.getAttribute("data-nav-key");
    if (linkKey === key) {
      link.classList.add("is-active");
    }
  });
}
window.setActiveNav = setActiveNav;

function handleNavClick(key, el, event) {
  setActiveNav(key);
  toggleMobileMenu(true);
}
window.handleNavClick = handleNavClick;

function initNavbarActiveTracker() {
  const nav = document.getElementById("mainNavbar");
  if (!nav || nav.dataset.navbarStatic === "light" || nav.classList.contains("navbar--light")) {
    return;
  }
  const sections = ["beranda", "misi", "keunggulan", "deteksi", "performa", "sanitasi", "katalog-preview", "faq-section"];

  // Pelacakan presisi tinggi menggunakan getBoundingClientRect
  const trackActiveSection = () => {
    let currentActive = "beranda";
    const headerThreshold = 140;

    for (let i = 0; i < sections.length; i++) {
      const secEl = document.getElementById(sections[i]);
      if (secEl) {
        const rect = secEl.getBoundingClientRect();
        if (rect.top <= headerThreshold && rect.bottom > headerThreshold) {
          currentActive = sections[i];
          break;
        }
      }
    }

    if ((window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 60)) {
      currentActive = "faq-section";
    }

    setActiveNav(currentActive);
  };

  window.trackActiveSection = trackActiveSection;
  window.addEventListener("scroll", trackActiveSection, { passive: true });
  trackActiveSection();
}

function toggleMobileMenu(forceClose = false) {
  const overlay = document.getElementById("mobileMenuOverlay") || document.getElementById("mobileMenuDrawer");
  const btn = document.getElementById("hamburgerBtn") || document.getElementById("deteksiHamburgerBtn") || document.getElementById("katalogHamburgerBtn");
  const navbar = document.getElementById("mainNavbar");

  if (!overlay || !btn) return;

  const isOpen = btn.classList.contains("is-open");
  const shouldClose = forceClose || isOpen;

  if (shouldClose) {
    overlay.classList.remove("is-open");
    btn.classList.remove("is-open");
    btn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("overflow-hidden");
    if (navbar) {
      navbar.classList.remove("drawer-open");
      navbar.classList.remove("is-menu-open");
    }
    if (window.lenis && typeof window.lenis.start === "function") {
      window.lenis.start();
    }
  } else {
    // Sinkronkan active nav sebelum membuka overlay
    if (window.location.pathname.includes("/deteksi")) {
      setActiveNav("deteksi");
    } else if (window.location.pathname.includes("/katalog-patogen")) {
      setActiveNav("katalog");
    } else if (typeof window.trackActiveSection === "function") {
      window.trackActiveSection();
    }

    overlay.classList.add("is-open");
    btn.classList.add("is-open");
    btn.setAttribute("aria-expanded", "true");
    document.body.classList.add("overflow-hidden");
    if (navbar) {
      navbar.classList.add("drawer-open");
      navbar.classList.add("is-menu-open");
    }
    if (window.lenis && typeof window.lenis.stop === "function") {
      window.lenis.stop();
    }
  }
  if (typeof window.updateNavbarScrollState === "function") {
    window.updateNavbarScrollState();
  }
}
window.toggleMobileMenu = toggleMobileMenu;
window.toggleDeteksiMobileMenu = toggleMobileMenu;
window.toggleKatalogMobileMenu = toggleMobileMenu;

function initAnchorClickInterceptors() {
  document.querySelectorAll('a[href^="#"], a[href^="/#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (!href) return;

      const targetUrl = new URL(this.href, window.location.origin);
      const isSamePage = targetUrl.pathname === window.location.pathname;
      if (!isSamePage) {
        // JANGAN preventDefault! Biarkan browser berpindah halaman ke /#deteksi atau /#katalog
        return;
      }

      const hash = href.startsWith("/#") ? href.substring(1) : href;
      if (hash && hash !== "#" && hash.startsWith("#")) {
        const target = document.querySelector(hash);
        if (target) {
          e.preventDefault();
          smoothScrollTo(target);
          toggleMobileMenu(true);
          const navKey = this.getAttribute("data-nav-key") || hash.substring(1);
          if (typeof window.setActiveNav === "function") {
            window.setActiveNav(navKey);
          }
        }
      }
    });
  });
}

// Penanganan otomatis sinkronisasi saat gambar & asset halaman termuat penuh
window.addEventListener("load", () => {
  if (window.location.hash) {
    try {
      const hash = window.location.hash;
      const target = document.querySelector(hash);
      if (target) {
        if (typeof ScrollTrigger !== "undefined") {
          ScrollTrigger.refresh();
        }
        const hashKey = hash.replace("#", "").replace("-preview", "").replace("-section", "");
        if (typeof window.setActiveNav === "function") {
          window.setActiveNav(hashKey);
        }
      }
    } catch (e) {
      // Abaikan kesalahan selektor tidak valid
    }
  }
});

// 2. HERO SLIDESHOW 3 GAMBAR (Auto-Crossfade & Controls)
let currentHeroSlide = 0;
const totalHeroSlides = 3;
let heroSlideshowTimer = null;

function updateHeroSlide(index) {
  currentHeroSlide = (index + totalHeroSlides) % totalHeroSlides;
  for (let i = 0; i < totalHeroSlides; i++) {
    const slide = document.getElementById(`heroSlide${i}`);
    if (slide) {
      if (i === currentHeroSlide) {
        slide.classList.add("active");
      } else {
        slide.classList.remove("active");
      }
    }
  }

  const counter = document.getElementById("heroSlideCounter");
  if (counter) {
    counter.textContent = `0${currentHeroSlide + 1} / 0${totalHeroSlides}`;
  }

  const dotsContainer = document.getElementById("heroSlideDots");
  if (dotsContainer) {
    const dots = dotsContainer.querySelectorAll(".hero-dot");
    dots.forEach((dot, idx) => {
      if (idx === currentHeroSlide) {
        dot.classList.add("active");
      } else {
        dot.classList.remove("active");
      }
    });
  }
}

function goToHeroSlide(index) {
  updateHeroSlide(index);
  startHeroSlideshow();
}
window.goToHeroSlide = goToHeroSlide;

function startHeroSlideshow() {
  if (heroSlideshowTimer) clearInterval(heroSlideshowTimer);
  heroSlideshowTimer = setInterval(() => {
    updateHeroSlide(currentHeroSlide + 1);
  }, 5500);
}

function initHeroSlideshow() {
  const container = document.querySelector(".hero-slideshow-container");
  if (!container) return;
  updateHeroSlide(0);
  startHeroSlideshow();
}

// 4. FLOATING BACK TO TOP BUTTON
function initBackToTop() {
  const btn = document.getElementById("backToTopBtn");
  if (!btn) return;

  const handleScroll = () => {
    const scrollY = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollY > window.innerHeight * 0.75) {
      btn.classList.remove("opacity-0", "pointer-events-none");
      btn.classList.add("opacity-100", "pointer-events-auto");
    } else {
      btn.classList.add("opacity-0", "pointer-events-none");
      btn.classList.remove("opacity-100", "pointer-events-auto");
    }
  };

  window.addEventListener("scroll", handleScroll, { passive: true });
  if (window.lenis) {
    window.lenis.on("scroll", handleScroll);
  }
}

function scrollToTop() {
  if (window.lenis && typeof window.lenis.scrollTo === "function") {
    window.lenis.scrollTo(0, { duration: 1.2 });
  } else {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}
window.scrollToTop = scrollToTop;

function initKeunggulanAccordion() {
  const items = document.querySelectorAll(".keunggulan-accordion-item");
  const photo = document.getElementById("keunggulanPhoto");

  items.forEach((item, index) => {
    const trigger = item.querySelector(".accordion-trigger") || item;
    trigger.addEventListener("click", (e) => {
      e.preventDefault();

      items.forEach((it) => {
        it.classList.remove("is-active");
        const b = it.querySelector(".accordion-trigger");
        if (b) b.setAttribute("aria-expanded", "false");
      });

      item.classList.add("is-active");
      const btn = item.querySelector(".accordion-trigger");
      if (btn) btn.setAttribute("aria-expanded", "true");

      if (photo && KEUNGGULAN_PHOTOS[index]) {
        photo.style.opacity = "0.5";
        setTimeout(() => {
          photo.src = KEUNGGULAN_PHOTOS[index];
          photo.style.opacity = "1";
        }, 150);
      }

      if (window.ScrollTrigger) {
        setTimeout(() => window.ScrollTrigger.refresh(), 300);
      }
    });
  });
}

function initFaqAccordion() {
  const items = document.querySelectorAll(".faq-card-item");
  items.forEach((item) => {
    const btn = item.querySelector(".faq-trigger-btn") || item.querySelector(".accordion-trigger");
    if (btn) {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const isOpen = item.classList.contains("is-open");
        
        // Tutup semua item lain
        items.forEach((it) => {
          it.classList.remove("is-open");
          const b = it.querySelector(".faq-trigger-btn") || it.querySelector(".accordion-trigger");
          if (b) b.setAttribute("aria-expanded", "false");
        });

        // Toggle item yang diklik
        if (!isOpen) {
          item.classList.add("is-open");
          btn.setAttribute("aria-expanded", "true");
        }

        if (window.ScrollTrigger) {
          setTimeout(() => window.ScrollTrigger.refresh(), 320);
        }
      });
    }
  });
}

function initWorkspaceTabs() {
  const tabBtns = document.querySelectorAll(".mode-tab-btn");
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabTarget = btn.getAttribute("data-tab");
      switchWorkspaceTab(tabTarget);
    });
  });
}

function switchWorkspaceTab(tabId) {
  currentWorkspaceTab = tabId;
  const tabBtns = document.querySelectorAll(".mode-tab-btn");
  tabBtns.forEach((btn) => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("is-active");
    } else {
      btn.classList.remove("is-active");
    }
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
window.switchWorkspaceTab = switchWorkspaceTab;

function initSliderCounters() {
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

function initResearcherPanelRefresh() {
  const researcherPanel = document.getElementById("researcherPanel");
  if (researcherPanel) {
    researcherPanel.addEventListener("toggle", () => {
      if (window.ScrollTrigger) {
        window.ScrollTrigger.refresh();
      }
    });
  }
}

function initFileInputListeners() {
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

function handleFileSelection(file) {
  currentFile = file;
  currentLoadedSampleUrl = null;
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

function clearSelectedFile() {
  currentFile = null;
  currentLocalPreviewUrl = "";
  currentLoadedSampleUrl = null;

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
window.clearSelectedFile = clearSelectedFile;

async function loadSampleGallery() {
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
              url: s.url
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

async function selectAndRunSample(url, filename, el) {
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
window.selectAndRunSample = selectAndRunSample;

async function runPrediction() {
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
      if (rTitle) {
        rTitle.textContent = cleanText(data.title || "Objek Bukan Daun Pisang");
      }

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

    await saveToIndexedDBHistory(data, clientRoundtripMs);

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
window.runPrediction = runPrediction;

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

  const phImgOrig = document.getElementById("phImgOrig");
  const imgOrig = document.getElementById("imgOrig");
  const badgeImgOrig = document.getElementById("badgeImgOrig");
  if (imgOrig && images.original_b64) {
    imgOrig.src = images.original_b64;
    imgOrig.classList.remove("hidden");
    if (phImgOrig) phImgOrig.classList.add("hidden");
    if (badgeImgOrig) badgeImgOrig.classList.remove("hidden");
  }

  const phImgClahe = document.getElementById("phImgClahe");
  const imgClahe = document.getElementById("imgClahe");
  const badgeImgClahe = document.getElementById("badgeImgClahe");
  if (imgClahe && images.clahe_b64) {
    imgClahe.src = images.clahe_b64;
    imgClahe.classList.remove("hidden");
    if (phImgClahe) phImgClahe.classList.add("hidden");
    if (badgeImgClahe) badgeImgClahe.classList.remove("hidden");
  }

  const phImgAnnotated = document.getElementById("phImgAnnotated");
  const imgAnnotated = document.getElementById("imgAnnotated");
  const badgeImgAnnotated = document.getElementById("badgeImgAnnotated");
  if (imgAnnotated && images.annotated_b64) {
    imgAnnotated.src = images.annotated_b64;
    imgAnnotated.classList.remove("hidden");
    if (phImgAnnotated) phImgAnnotated.classList.add("hidden");
    if (badgeImgAnnotated) badgeImgAnnotated.classList.remove("hidden");
  }
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
    } else if (sevCategory.includes("Sedang") || sevCategory.includes("Ringan") || data.dominant_class === "Cordana" || data.dominant_class === "Pestalotiopsis") {
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
    const totalMs = data.telemetry && data.telemetry.server_total_ms ? `${data.telemetry.server_total_ms} ms` : `${data.total_detections !== undefined ? data.total_detections : 0} Deteksi`;
    totalDetCount.textContent = totalMs;
  }

  if (data.telemetry) {
    if (latServer) latServer.innerHTML = `${data.telemetry.server_total_ms} <span class="text-xs font-sans font-medium text-[#4B524C]">ms</span>`;
    if (latPre) latPre.textContent = `${data.telemetry.preprocess_ms} ms`;
    if (latInf) latInf.textContent = `${data.telemetry.inference_nms_ms} ms`;
    if (latPost) latPost.textContent = `${data.telemetry.postprocess_ms} ms`;
  }
  if (latClient) latClient.textContent = `${clientRoundtripMs} ms`;

  if (agroDeleafing) agroDeleafing.textContent = cleanText(agro.deleafing_protocol || "Pertahankan minimal 6 sampai 8 daun fungsional sehat.");
  if (agroFracText) agroFracText.textContent = cleanText(agro.frac_recommendation || "Penyemprotan fungisida tidak diperlukan untuk daun sehat.");
  if (agroDisclaimer) agroDisclaimer.textContent = cleanText(agro.ppl_disclaimer || "Lakukan pengamatan kebun secara berkala.");

  if (agroFracShort) {
    const codes = agro.frac_codes || [];
    agroFracShort.innerHTML = codes
      .map((raw) => {
        const text = cleanText(raw);
        const match = text.match(/^(FRAC\s+[^\s(]+)\s*\((.+)\)$/i);
        if (match) {
          const code = match[1];
          const rest = match[2];
          return `
            <div class="flex items-start gap-2 text-xs sm:text-[0.8125rem] text-[#111812]">
              <span class="font-mono font-bold text-[0.7rem] text-[#163C24] bg-[#F7F8F5] border border-[#E8ECE6] px-1.5 py-0.5 rounded shrink-0">${code}</span>
              <span class="font-medium text-[#111812] leading-snug">${rest}</span>
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
          const code = match[1];
          const rest = match[2];
          let group = rest;
          let active = "";
          if (rest.includes(":")) {
            const parts = rest.split(":");
            group = parts[0].trim();
            active = parts.slice(1).join(":").trim();
          }
          return `
            <div class="flex items-center justify-between gap-2.5 p-3 sm:py-2.5 sm:px-3.5 rounded-xl bg-[#F7F8F5] border border-[#E8ECE6] text-sm">
              <div class="flex items-center gap-2.5 min-w-0">
                <span class="font-mono font-bold text-xs sm:text-sm text-[#163C24] bg-white border border-[#E2E6DE] px-2.5 py-1 rounded shadow-2xs shrink-0">${code}</span>
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
      tbody.innerHTML = `<tr><td colspan="6" class="py-4 text-center text-[#4B524C]">Tidak ada kotak terdeteksi.</td></tr>`;
    }
  }
}

function switchVerdictView(mode) {
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
window.switchVerdictView = switchVerdictView;

function updateSwitcherActiveBtn(mode) {
  const btnAnn = document.getElementById("btnSwitchAnnotated");
  const btnCla = document.getElementById("btnSwitchClahe");
  const btnOri = document.getElementById("btnSwitchOrig");

  [btnAnn, btnCla, btnOri].forEach((btn) => {
    if (btn) {
      btn.className = "detection-tab-btn";
    }
  });

  const activeBtn = mode === "clahe" ? btnCla : (mode === "orig" ? btnOri : btnAnn);
  if (activeBtn) {
    activeBtn.className = "detection-tab-btn active";
  }
}

function resetDetectionState() {
  currentFile = null;
  currentLocalPreviewUrl = "";
  currentLoadedSampleUrl = null;
  lastResponseData = null;

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

  const phImgOrig = document.getElementById("phImgOrig");
  const imgOrig = document.getElementById("imgOrig");
  const badgeImgOrig = document.getElementById("badgeImgOrig");
  if (imgOrig) {
    imgOrig.src = "";
    imgOrig.classList.add("hidden");
  }
  if (phImgOrig) phImgOrig.classList.remove("hidden");
  if (badgeImgOrig) badgeImgOrig.classList.add("hidden");

  const phImgClahe = document.getElementById("phImgClahe");
  const imgClahe = document.getElementById("imgClahe");
  const badgeImgClahe = document.getElementById("badgeImgClahe");
  if (imgClahe) {
    imgClahe.src = "";
    imgClahe.classList.add("hidden");
  }
  if (phImgClahe) phImgClahe.classList.remove("hidden");
  if (badgeImgClahe) badgeImgClahe.classList.add("hidden");

  const phImgAnnotated = document.getElementById("phImgAnnotated");
  const imgAnnotated = document.getElementById("imgAnnotated");
  const badgeImgAnnotated = document.getElementById("badgeImgAnnotated");
  if (imgAnnotated) {
    imgAnnotated.src = "";
    imgAnnotated.classList.add("hidden");
  }
  if (phImgAnnotated) phImgAnnotated.classList.remove("hidden");
  if (badgeImgAnnotated) badgeImgAnnotated.classList.add("hidden");

  switchWorkspaceTab("upload");
}
window.resetDetectionState = resetDetectionState;

async function saveToIndexedDBHistory(data, clientRoundtripMs) {
  try {
    const now = new Date();
    const timeFormatted = now.toLocaleDateString("id-ID", {
      day: "numeric",
      month: "short",
      year: "numeric"
    }) + " " + now.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });

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
      frac_summary: data.agronomy && data.agronomy.frac_codes ? cleanText(data.agronomy.frac_codes.join(", ")) : "Tidak Diperlukan",
      thumbnail_b64: thumbB64
    };

    await saveDetectionToIndexedDB(record);
    await renderHistoryTable();
  } catch (err) {
    console.error("Gagal mencatat ke IndexedDB:", err);
  }
}

async function renderHistoryTable() {
  const tbody = document.getElementById("historyTableBody");
  const mobileList = document.getElementById("historyListMobile");
  if (!tbody && !mobileList) return;

  try {
    const list = await getAllHistoryFromIndexedDB();
    if (list.length === 0) {
      if (tbody) {
        tbody.innerHTML = `<tr><td colspan="7" class="py-6 text-center text-[#4B524C]">Belum ada riwayat pengujian pada peramban ini.</td></tr>`;
      }
      if (mobileList) {
        mobileList.innerHTML = `<div class="py-8 text-center text-xs text-[#4B524C]">Belum ada riwayat pengujian pada peramban ini.</div>`;
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
                : `<div class="w-11 h-11 rounded-lg bg-[#ECEEEA] flex items-center justify-center text-xs text-[#4B524C] font-mono">No Img</div>`
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
              <!-- Baris 1: Header Item (Nama Penyakit di kiri + Tombol Lihat & Hapus di kanan) -->
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

              <!-- Baris 2: Substatus Kategori Penyakit -->
              <div class="text-[0.875rem] text-[#4B524C] leading-snug mt-1">
                ${sevDesc}
              </div>

              <!-- Baris 3: Metadata 1 Baris (Lesi · Latensi · Nama Berkas / Waktu) -->
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

async function openHistoryDetailModal(id) {
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
window.openHistoryDetailModal = openHistoryDetailModal;

function closeHistoryDetailModal() {
  const modal = document.getElementById("historyDetailModal");
  if (modal) modal.classList.add("hidden");
  document.body.classList.remove("overflow-hidden");
}
window.closeHistoryDetailModal = closeHistoryDetailModal;

async function deleteHistoryRow(id) {
  if (confirm("Hapus entri riwayat pengujian ini?")) {
    await deleteHistoryItemFromIndexedDB(id);
    await renderHistoryTable();
  }
}
window.deleteHistoryRow = deleteHistoryRow;

async function clearDetectionHistory() {
  if (confirm("Apakah Anda yakin ingin menghapus seluruh log riwayat pengujian pada peramban ini?")) {
    await clearAllHistoryFromIndexedDB();
    await renderHistoryTable();
  }
}
window.clearDetectionHistory = clearDetectionHistory;

async function exportHistoryCsv() {
  const list = await getAllHistoryFromIndexedDB();
  if (list.length === 0) {
    alert("Tidak ada data riwayat pengujian untuk diekspor.");
    return;
  }

  const headers = ["ID", "Waktu", "Nama File", "Vonis Dominan", "Keparahan", "Keyakinan (%)", "Lesi", "Daun", "Rekomendasi FRAC", "Server Latensi (ms)", "Client Roundtrip (ms)"];
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
    item.client_ms
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
window.exportHistoryCsv = exportHistoryCsv;

function openLightboxFullscreen() {
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
window.openLightboxFullscreen = openLightboxFullscreen;

function closeLightbox() {
  const modal = document.getElementById("lightboxModal");
  if (modal) modal.classList.add("hidden");
  document.body.classList.remove("overflow-hidden");
}
window.closeLightbox = closeLightbox;

function switchLightboxTab(mode) {
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
window.switchLightboxTab = switchLightboxTab;

function downloadDetectionResult() {
  if (lastResponseData && lastResponseData.images && lastResponseData.images.annotated_b64) {
    const dominant = (lastResponseData.dominant_class || "Patogen").replace(/\s+/g, "_");
    const filename = `MusaVision_Deteksi_${dominant}.jpg`;
    const link = document.createElement("a");
    link.href = lastResponseData.images.annotated_b64;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } else {
    alert("Belum ada citra hasil deteksi untuk diunduh.");
  }
}
window.downloadDetectionResult = downloadDetectionResult;

function renderSusQuestions() {
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

function calculateSusScore() {
  let answers = [];
  for (let i = 0; i < 10; i++) {
    const selected = document.querySelector(`input[name="sus_q_${i}"]:checked`);
    if (!selected) {
      alert("Harap jawab seluruh 10 pertanyaan kuesioner SUS terlebih dahulu.");
      return;
    }
    answers.push(parseInt(selected.value));
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
window.calculateSusScore = calculateSusScore;

function switchView(viewName) {
  const target = document.getElementById("deteksi");
  if (target) smoothScrollTo(target);
}
window.switchView = switchView;

function initOptionalAnimations() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  try {
    if (typeof Lenis !== "undefined") {
      lenisInstance = new Lenis({
        duration: 1.15,
        smoothWheel: true,
        touchMultiplier: 1.5,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t))
      });
      window.lenis = lenisInstance;

      // Sinkronkan instan posisi hash jika mendarat dari halaman lain
      if (window.location.hash) {
        try {
          const hashTarget = document.querySelector(window.location.hash);
          if (hashTarget) {
            lenisInstance.scrollTo(hashTarget, { offset: -88, immediate: true, force: true });
          }
        } catch (e) {}
      }

      // Hubungkan listener Lenis dengan status navbar is-scrolled dan trackActiveSection
      if (typeof window.updateNavbarScrollState === "function") {
        lenisInstance.on("scroll", (e) => {
          const scrollY = e && typeof e.scroll === "number" ? e.scroll : window.scrollY;
          window.updateNavbarScrollState(scrollY);
          if (typeof window.trackActiveSection === "function") {
            window.trackActiveSection();
          }
        });
      }

      if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
        gsap.registerPlugin(ScrollTrigger);
        lenisInstance.on("scroll", ScrollTrigger.update);
        gsap.ticker.add((time) => {
          lenisInstance.raf(time * 1000);
        });
        gsap.ticker.lagSmoothing(0);
      } else {
        function raf(time) {
          lenisInstance.raf(time);
          requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);
      }
    }
  } catch (err) {
    console.warn("Lenis animation init skipped:", err);
  }

  try {
    if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
      const splitHeading = (el) => {
        if (!el || el.dataset.wordsSplit === "true") return [];
        el.dataset.wordsSplit = "true";
        const childNodes = Array.from(el.childNodes);
        const createdWords = [];

        childNodes.forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent;
            if (!text.trim()) return;
            const parts = text.split(/(\s+)/);
            const frag = document.createDocumentFragment();

            parts.forEach((p) => {
              if (!p) return;
              if (/^\s+$/.test(p)) {
                frag.appendChild(document.createTextNode(p));
              } else {
                const mask = document.createElement("span");
                mask.className = "word-mask";
                const inner = document.createElement("span");
                inner.className = "word-inner";
                inner.textContent = p;
                mask.appendChild(inner);
                frag.appendChild(mask);
                createdWords.push(inner);
              }
            });
            el.replaceChild(frag, node);
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            createdWords.push(...splitHeading(node));
          }
        });
        return createdWords;
      };

      const heroH1 = document.getElementById("heroHeadline");
      if (heroH1) {
        const words = splitHeading(heroH1);
        if (words.length > 0) {
          gsap.fromTo(
            words,
            { yPercent: 110, opacity: 0 },
            { yPercent: 0, opacity: 1, duration: 0.8, stagger: 0.05, ease: "power3.out", delay: 0.1 }
          );
        }
      }

      const otherHeadings = document.querySelectorAll('[data-reveal="words"]');
      otherHeadings.forEach((h) => {
        if (h.id === "heroHeadline") return;
        const words = splitHeading(h);
        if (words && words.length > 0) {
          gsap.fromTo(
            words,
            { yPercent: 110, opacity: 0 },
            {
              scrollTrigger: { trigger: h, start: "top 85%", once: true },
              yPercent: 0,
              opacity: 1,
              duration: 0.7,
              stagger: 0.04,
              ease: "power3.out"
            }
          );
        }
      });

      // 3. Misi Text Highlight Berjalan (Scroll Scrub Reveal)
      const scrubContainers = document.querySelectorAll(".misi-scrub-text");
      scrubContainers.forEach((container) => {
        if (container.dataset.scrubSplit === "true") return;
        container.dataset.scrubSplit = "true";
        const text = container.textContent.trim();
        const words = text.split(/\s+/);
        container.innerHTML = words
          .map((w) => `<span class="misi-word text-[#4B524C] opacity-35">${w}</span>`)
          .join(" ");
      });

      const misiWords = document.querySelectorAll(".misi-word");
      if (misiWords.length > 0) {
        gsap.to(misiWords, {
          scrollTrigger: {
            trigger: "#misi",
            start: "top 78%",
            end: "bottom 55%",
            scrub: 0.5
          },
          color: "#111812",
          opacity: 1,
          stagger: 0.05,
          ease: "none"
        });
      }
    } else {
      // Fallback jika GSAP belum tersedia: pastikan teks misi terbaca jelas
      const scrubContainers = document.querySelectorAll(".misi-scrub-text");
      scrubContainers.forEach((container) => {
        if (container.dataset.scrubSplit === "true") return;
        container.dataset.scrubSplit = "true";
        const text = container.textContent.trim();
        const words = text.split(/\s+/);
        container.innerHTML = words
          .map((w) => `<span class="misi-word text-[#111812] opacity-100">${w}</span>`)
          .join(" ");
      });
    }
  } catch (err) {
    console.warn("GSAP word reveal / scrub skipped:", err);
  }

  import("https://cdn.jsdelivr.net/npm/motion@11.15.0/+esm")
    .then(({ animate, inView, stagger, hover }) => {
      try {
        inView(".pillar-grid-3", () => {
          animate(
            ".pillar-editorial-card",
            { opacity: [0, 1], y: [24, 0] },
            { duration: 0.6, delay: stagger(0.08), easing: [0.22, 1, 0.36, 1] }
          );
        });

        if (window.matchMedia("(hover: hover)").matches) {
          document.querySelectorAll(".pillar-editorial-card, .metric-card-stat").forEach((card) => {
            hover(card, (el) => {
              animate(el, { y: -4 }, { type: "spring", stiffness: 350, damping: 25 });
              return () => animate(el, { y: 0 }, { type: "spring", stiffness: 350, damping: 25 });
            });
          });
        }
      } catch (e) {
        console.warn("Motion entrance/hover skipped:", e);
      }
    })
    .catch((err) => {
      console.warn("Motion CDN import skipped:", err);
    });
}
