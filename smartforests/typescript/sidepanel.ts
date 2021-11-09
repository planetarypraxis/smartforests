const init = () => {
  document
    .querySelectorAll<HTMLElement>("[data-smartforests-sidepanel-open]")
    .forEach((el) => {
      const sidepanel = document.querySelector(
        el.dataset.smartforestsSidepanelOpen
      );

      el.addEventListener("click", () => {
        if (sidepanel) {
          const instance =
            bootstrap.Offcanvas.getInstance(sidepanel) ||
            new bootstrap.Offcanvas(sidepanel);
          instance.show();
        }
      });
    });
};

window.addEventListener("turbo:load", init);
init();
