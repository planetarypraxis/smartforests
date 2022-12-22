(() => {
  const initSidebar = () => {
    const page = document.querySelector(".filter-page");
    const filters = document.getElementById("filters");
    if (!page || !filters) {
      return;
    }

    // When a tag is clicked, `hide.bs.offcanvas` does not fire,
    // so do this manually to prevent glitchy behaviour on subsequent Turbo visits.
    let offcanvas = bootstrap.Offcanvas.getInstance(filters)
    if (offcanvas) offcanvas.hide()
  };

  /**
   * Bind filter params to the current url.
   */
  const initFilters = () => {
    const filters = document.getElementById("filters");
    if (!filters) {
      return;
    }

    const params = new URLSearchParams(window.location.search);

    $("#filters [data-filter-tag]").each((_, pill) => {
      $(pill).toggleClass(
        "active",
        params.getAll("filter").includes(pill.dataset.filterTag)
      );
    });
  };

  const init = () => {
    initFilters();
    initSidebar();
  };

  const handleVisit = () => {
    initFilters();
    initSidebar();
  };

  window.addEventListener("turbo:visit", handleVisit);
  window.addEventListener("turbo:load", init);
  window.addEventListener("turbo:frame-load", init);
  init();

  window.resetJSForTurboFrame = () => {
    // Ensure Boostrap Offcanvases (sidepanels) are in the correct state
    // according to the Turbo Frame cache'd history. If going back in the history
    // and the Offcanvas was previously open, then re-open it
    const offcanvas = document.querySelectorAll(".offcanvas")
  
    for (const el of offcanvas) {
      const visible = window.getComputedStyle(el)['visibility'] === 'visible'
      let offcanvas = new window.bootstrap.Offcanvas(el)
      offcanvas.show()
      if (!visible) offcanvas.hide()
    }
  }
})();
