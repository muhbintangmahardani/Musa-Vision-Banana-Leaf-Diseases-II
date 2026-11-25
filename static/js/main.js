/**
 * Main ES module orchestrator initializing UI behaviors conditionally per active route.
 */

import { initFaqAccordion, initKeunggulanAccordion } from "./modules/accordion.js";
import {
  bindAnimationGlobals,
  initHeroSlideshow,
  initOptionalAnimations,
} from "./modules/animations.js";
import { bindCatalogGlobals, initPathogenCatalog } from "./modules/catalog.js";
import {
  bindDetectorGlobals,
  closeLightbox,
  initFileInputListeners,
  initResearcherPanelRefresh,
  initSliderCounters,
  initWorkspaceTabs,
  loadSampleGallery,
  renderSusQuestions,
  resetDetectorSessionState,
} from "./modules/detector.js";
import {
  bindHistoryGlobals,
  closeHistoryDetailModal,
  renderHistoryTable,
} from "./modules/history_db.js";
import {
  bindNavigationGlobals,
  initAnchorClickInterceptors,
  initBackToTop,
  initHashJumpHandler,
  initInitialNavState,
  initNavbarScroll,
} from "./modules/navigation.js";

// Bind window globals before HTML click handlers can fire
bindNavigationGlobals();
bindAnimationGlobals();
bindDetectorGlobals();
bindHistoryGlobals();
bindCatalogGlobals();

document.addEventListener("DOMContentLoaded", () => {
  resetDetectorSessionState();

  initNavbarScroll();
  initAnchorClickInterceptors();
  initHeroSlideshow();
  initBackToTop();
  initKeunggulanAccordion();
  initFaqAccordion();

  if (document.getElementById("workspace-deteksi") || document.querySelector(".mode-tab-btn")) {
    initWorkspaceTabs();
    initSliderCounters();
    initFileInputListeners();
    initResearcherPanelRefresh();
    loadSampleGallery();
    renderHistoryTable();
  }

  renderSusQuestions();
  initPathogenCatalog();
  initOptionalAnimations();
  initInitialNavState();
  initHashJumpHandler();

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeLightbox();
      closeHistoryDetailModal();
    }
  });
});
