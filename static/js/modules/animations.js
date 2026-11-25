/**
 * Hero three-slide carousel, Lenis smooth scroll, GSAP heading reveals, and Mission scrub animation.
 */

let lenisInstance = null;
let currentHeroSlide = 0;
const totalHeroSlides = 3;
let heroSlideshowTimer = null;

function updateHeroSlide(index) {
  currentHeroSlide = (index + totalHeroSlides) % totalHeroSlides;
  for (let i = 0; i < totalHeroSlides; i++) {
    const slide = document.getElementById(`heroSlide${i}`);
    if (slide) {
      slide.classList.toggle("active", i === currentHeroSlide);
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
      dot.classList.toggle("active", idx === currentHeroSlide);
    });
  }
}

function startHeroSlideshow() {
  if (heroSlideshowTimer) clearInterval(heroSlideshowTimer);
  heroSlideshowTimer = setInterval(() => {
    updateHeroSlide(currentHeroSlide + 1);
  }, 5500);
}

export function goToHeroSlide(index) {
  updateHeroSlide(index);
  startHeroSlideshow();
}

export function initHeroSlideshow() {
  const container = document.querySelector(".hero-slideshow-container");
  if (!container) return;
  updateHeroSlide(0);
  startHeroSlideshow();
}

export function initOptionalAnimations() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  try {
    if (typeof Lenis !== "undefined") {
      lenisInstance = new Lenis({
        duration: 1.15,
        smoothWheel: true,
        touchMultiplier: 1.5,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      });
      window.lenis = lenisInstance;

      if (window.location.hash) {
        try {
          const hashTarget = document.querySelector(window.location.hash);
          if (hashTarget) {
            lenisInstance.scrollTo(hashTarget, { offset: -88, immediate: true, force: true });
          }
        } catch (err) {
          // Ignore malformed URL fragments
        }
      }

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
        const raf = (time) => {
          lenisInstance.raf(time);
          requestAnimationFrame(raf);
        };
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

            parts.forEach((part) => {
              if (!part) return;
              if (/^\s+$/.test(part)) {
                frag.appendChild(document.createTextNode(part));
              } else {
                const mask = document.createElement("span");
                mask.className = "word-mask";
                const inner = document.createElement("span");
                inner.className = "word-inner";
                inner.textContent = part;
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

      document.querySelectorAll('[data-reveal="words"]').forEach((h) => {
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
              ease: "power3.out",
            }
          );
        }
      });

      const scrubContainers = document.querySelectorAll(".misi-scrub-text");
      scrubContainers.forEach((container) => {
        if (container.dataset.scrubSplit === "true") return;
        container.dataset.scrubSplit = "true";
        const words = container.textContent.trim().split(/\s+/);
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
            scrub: 0.5,
          },
          color: "#111812",
          opacity: 1,
          stagger: 0.05,
          ease: "none",
        });
      }
    } else {
      document.querySelectorAll(".misi-scrub-text").forEach((container) => {
        if (container.dataset.scrubSplit === "true") return;
        container.dataset.scrubSplit = "true";
        const words = container.textContent.trim().split(/\s+/);
        container.innerHTML = words
          .map((w) => `<span class="misi-word text-[#111812] opacity-100">${w}</span>`)
          .join(" ");
      });
    }
  } catch (err) {
    console.warn("GSAP word reveal / scrub skipped:", err);
  }

  const pillarGrid = document.querySelector(".pillar-grid-3");
  if (pillarGrid) {
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
        } catch (err) {
          console.warn("Motion entrance/hover skipped:", err);
        }
      })
      .catch((err) => {
        console.warn("Motion CDN import skipped:", err);
      });
  }
}

export function bindAnimationGlobals() {
  window.goToHeroSlide = goToHeroSlide;
}
