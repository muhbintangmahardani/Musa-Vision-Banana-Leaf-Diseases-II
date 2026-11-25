/**
 * Navigation, scroll-spy, full-screen mobile menu, hash anti-flash handler, and Back-to-Top.
 */

export function smoothScrollTo(targetEl) {
  if (!targetEl) return;
  if (window.lenis && typeof window.lenis.scrollTo === "function") {
    window.lenis.scrollTo(targetEl, { offset: -76, duration: 1.15 });
  } else {
    targetEl.scrollIntoView({ behavior: "smooth" });
  }
}

export function switchView() {
  const target = document.getElementById("deteksi");
  if (target) smoothScrollTo(target);
}

export function setActiveNav(sectionKey) {
  if (!sectionKey) return;
  let key = sectionKey.toLowerCase().trim();
  if (key.startsWith("#")) key = key.substring(1);
  if (key === "katalog-preview" || key === "katalog-patogen") key = "katalog";
  if (key === "workspace-deteksi") key = "deteksi";
  if (key === "faq-section") key = "beranda";

  const desktopLinks = document.querySelectorAll(
    "#desktopNavPill .nav-item-link, .nav-center-pill .nav-item-link"
  );
  desktopLinks.forEach((link) => {
    link.classList.remove("is-active");
    const dot = link.querySelector(".nav-dot-active");
    if (dot) dot.remove();
  });

  const mobileLinks = document.querySelectorAll(".mobile-nav-link");
  mobileLinks.forEach((link) => {
    link.classList.remove("is-active");
  });

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

  mobileLinks.forEach((link) => {
    const linkKey = link.getAttribute("data-nav-key");
    if (linkKey === key) {
      link.classList.add("is-active");
    }
  });
}

export function toggleMobileMenu(forceClose = false) {
  const overlay =
    document.getElementById("mobileMenuOverlay") ||
    document.getElementById("mobileMenuDrawer");
  const btn =
    document.getElementById("hamburgerBtn") ||
    document.getElementById("deteksiHamburgerBtn") ||
    document.getElementById("katalogHamburgerBtn");
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

export function handleNavClick(key) {
  setActiveNav(key);
  toggleMobileMenu(true);
}

function initNavbarActiveTracker() {
  const nav = document.getElementById("mainNavbar");
  if (!nav || nav.dataset.navbarStatic === "light" || nav.classList.contains("navbar--light")) {
    return;
  }

  const sections = [
    "beranda",
    "misi",
    "keunggulan",
    "deteksi",
    "performa",
    "sanitasi",
    "katalog-preview",
    "faq-section",
  ];

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

    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 60) {
      currentActive = "faq-section";
    }

    setActiveNav(currentActive);
  };

  window.trackActiveSection = trackActiveSection;
  window.addEventListener("scroll", trackActiveSection, { passive: true });
  trackActiveSection();
}

export function initNavbarScroll() {
  const nav = document.getElementById("mainNavbar");
  if (!nav) return;

  if (nav.dataset.navbarStatic === "light" || nav.classList.contains("navbar--light")) {
    nav.classList.add("is-scrolled");
  } else {
    let ticking = false;

    const updateNavbarScrollState = (customY) => {
      const scrollY =
        typeof customY === "number"
          ? customY
          : window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;

      if (scrollY > 40) {
        nav.classList.add("is-scrolled");
      } else {
        nav.classList.remove("is-scrolled");
      }
      ticking = false;
    };

    window.updateNavbarScrollState = updateNavbarScrollState;
    updateNavbarScrollState();

    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          window.requestAnimationFrame(() => updateNavbarScrollState());
          ticking = true;
        }
      },
      { passive: true }
    );

    window.addEventListener("load", () => updateNavbarScrollState());
    window.addEventListener("resize", () => updateNavbarScrollState());

    if (window.lenis) {
      window.lenis.on("scroll", (e) => {
        const scrollY = e && typeof e.scroll === "number" ? e.scroll : window.scrollY;
        updateNavbarScrollState(scrollY);
        if (typeof window.trackActiveSection === "function") {
          window.trackActiveSection();
        }
      });
    }

    initNavbarActiveTracker();
  }

  document.addEventListener("click", (e) => {
    const overlay =
      document.getElementById("mobileMenuOverlay") ||
      document.getElementById("mobileMenuDrawer");
    const btn =
      document.getElementById("hamburgerBtn") ||
      document.getElementById("deteksiHamburgerBtn") ||
      document.getElementById("katalogHamburgerBtn");
    if (
      overlay &&
      btn &&
      btn.classList.contains("is-open") &&
      !overlay.contains(e.target) &&
      !btn.contains(e.target)
    ) {
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

export function initAnchorClickInterceptors() {
  document.querySelectorAll('a[href^="#"], a[href^="/#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (!href) return;

      const targetUrl = new URL(this.href, window.location.origin);
      const isSamePage = targetUrl.pathname === window.location.pathname;
      if (!isSamePage) {
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
          setActiveNav(navKey);
        }
      }
    });
  });
}

export function initInitialNavState() {
  if (window.location.pathname.includes("/deteksi")) {
    setActiveNav("deteksi");
  } else if (window.location.pathname.includes("/katalog-patogen")) {
    setActiveNav("katalog");
  } else if (window.location.hash) {
    const hashKey = window.location.hash
      .replace("#", "")
      .replace("-preview", "")
      .replace("-section", "");
    setActiveNav(hashKey || "beranda");
  } else {
    setActiveNav("beranda");
  }
}

export function initHashJumpHandler() {
  if (document.documentElement.classList.contains("hash-jumping")) {
    const unlockCurtain = () => {
      document.documentElement.classList.remove("hash-jumping");
    };

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
          const hashKey = window.location.hash
            .replace("#", "")
            .replace("-preview", "")
            .replace("-section", "");
          setActiveNav(hashKey || "beranda");
          if (typeof window.updateNavbarScrollState === "function") {
            window.updateNavbarScrollState(y);
          }
          if (typeof ScrollTrigger !== "undefined") {
            ScrollTrigger.refresh();
          }
        }
      }
    } catch (err) {
      console.warn("Hash jump calculation error:", err);
    }

    requestAnimationFrame(() => {
      clearTimeout(failsafe);
      unlockCurtain();
      if (typeof window.updateNavbarScrollState === "function") {
        window.updateNavbarScrollState(window.scrollY);
      }
    });
  }

  window.addEventListener("load", () => {
    if (window.location.hash) {
      try {
        const hash = window.location.hash;
        const target = document.querySelector(hash);
        if (target) {
          if (typeof ScrollTrigger !== "undefined") {
            ScrollTrigger.refresh();
          }
          const hashKey = hash
            .replace("#", "")
            .replace("-preview", "")
            .replace("-section", "");
          setActiveNav(hashKey);
        }
      } catch (err) {
        // Ignore invalid selector hashes
      }
    }
  });
}

export function scrollToTop() {
  if (window.lenis && typeof window.lenis.scrollTo === "function") {
    window.lenis.scrollTo(0, { duration: 1.2 });
  } else {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

export function initBackToTop() {
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

export function bindNavigationGlobals() {
  window.smoothScrollTo = smoothScrollTo;
  window.switchView = switchView;
  window.setActiveNav = setActiveNav;
  window.handleNavClick = handleNavClick;
  window.toggleMobileMenu = toggleMobileMenu;
  window.toggleDeteksiMobileMenu = toggleMobileMenu;
  window.toggleKatalogMobileMenu = toggleMobileMenu;
  window.scrollToTop = scrollToTop;
}
