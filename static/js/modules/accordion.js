/**
 * Accordion controllers for System Excellence (#keunggulan) and Farmer FAQ (#faq-section).
 */

const KEUNGGULAN_PHOTOS = [
  "/static/samples/pillar_canopy_management.jpg",
  "/static/samples/musavision_hero_bg.jpg",
  "/static/samples/pillar_sanitation_deleafing.jpg",
  "/static/samples/pillar_frac_spraying.jpg",
];

export function initKeunggulanAccordion() {
  const items = document.querySelectorAll(".keunggulan-accordion-item");
  if (!items.length) return;
  const photo = document.getElementById("keunggulanPhoto");

  items.forEach((item, index) => {
    const trigger = item.querySelector(".accordion-trigger") || item;
    trigger.addEventListener("click", (e) => {
      e.preventDefault();

      items.forEach((it) => {
        it.classList.remove("is-active");
        const btn = it.querySelector(".accordion-trigger");
        if (btn) btn.setAttribute("aria-expanded", "false");
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

export function initFaqAccordion() {
  const items = document.querySelectorAll(".faq-card-item");
  if (!items.length) return;

  items.forEach((item) => {
    const btn = item.querySelector(".faq-trigger-btn") || item.querySelector(".accordion-trigger");
    if (!btn) return;

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const isOpen = item.classList.contains("is-open");

      items.forEach((it) => {
        it.classList.remove("is-open");
        const b = it.querySelector(".faq-trigger-btn") || it.querySelector(".accordion-trigger");
        if (b) b.setAttribute("aria-expanded", "false");
      });

      if (!isOpen) {
        item.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      }

      if (window.ScrollTrigger) {
        setTimeout(() => window.ScrollTrigger.refresh(), 320);
      }
    });
  });
}
