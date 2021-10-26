(() => {
  const init = () => {
    const page = document.getElementById("filter-page");
    const filters = document.getElementById("filters");
    if (!filters || !page) {
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const showFilters = document.getElementById("sidebar-show");

    filters.addEventListener("show.bs.collapse", () => {
      page.classList.add("filters-visible");

      filters.dispatchEvent(new CustomEvent("sf:layout", { bubbles: true }));
    });
    filters.addEventListener("hidden.bs.collapse", () => {
      page.classList.remove("filters-visible");

      filters.dispatchEvent(new CustomEvent("sf:layout", { bubbles: true }));
    });

    $("#filters [data-filter-tag]").each((_, pill) => {
      $(pill).toggleClass(
        "active",
        params.getAll("filter").includes(pill.dataset.filterTag)
      );
    });
  };

  window.addEventListener("turbo:load", init);
  init();
})();
