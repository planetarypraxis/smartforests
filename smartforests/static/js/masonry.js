(() => {
  const init = () => {
    if ($(".grid").data("masonry")) {
      return;
    }

    const $grid = $(".grid").masonry({
      itemSelector: "none", // select none at first
      columnWidth: ".grid__col-sizer",
      gutter: ".grid__gutter-sizer",
      percentPosition: true,
      stagger: 30,
      // nicer reveal transition
      visibleStyle: { opacity: 1 },
      hiddenStyle: { opacity: 0 },
    });

    // get Masonry instance
    const msnry = $grid.data("masonry");

    // initial items reveal
    $grid.imagesLoaded(function () {
      $grid.removeClass("are-images-unloaded");
      $grid.masonry("option", { itemSelector: ".grid__item" });
      const $items = $grid.find(".grid__item");
      $grid.masonry("appended", $items);
    });
  };

  window.addEventListener("sf:layout", () => {
    $(".grid").each((_, el) => {
      const msnry = $(".grid").data("masonry");
      if (msnry) {
        msnry.layout();
      }
    });
  });

  window.addEventListener("turbo:load", init);
  init();
})();
