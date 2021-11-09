(() => {
  /**
   * When a page has the .filter-page class applied, set relevant body classes when the sidebar is visible/invisible.
   */
  const initSidebarExpand = () => {
    const page = document.querySelector(".filter-page");
    const filters = document.getElementById("filters");
    if (!page || !filters) {
      return;
    }

    filters.addEventListener("show.bs.collapse", () => {
      page.classList.add("filters-visible");

      filters.dispatchEvent(new CustomEvent("sf:layout", { bubbles: true }));
    });
    filters.addEventListener("hidden.bs.collapse", () => {
      page.classList.remove("filters-visible");

      filters.dispatchEvent(new CustomEvent("sf:layout", { bubbles: true }));
    });
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
    initSidebarExpand();
  };

  const handleVisit = () => {
    initFilters();
  };

  window.addEventListener("turbo:visit", handleVisit);
  window.addEventListener("turbo:load", init);
  window.addEventListener("turbo:frame-load", init);
  init();
})();
