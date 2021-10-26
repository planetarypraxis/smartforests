(() => {
  const init = () => {
    const filters = document.getElementById("filters");
    if (!filters) {
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const showFilters = document.getElementById("sidebar-show");

    filters.addEventListener("show.bs.collapse", () => {
      showFilters.classList.add("collapse");
    });
    filters.addEventListener("hidden.bs.collapse", () => {
      showFilters.classList.remove("collapse");
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
