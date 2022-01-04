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
})();
