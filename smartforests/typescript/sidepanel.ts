const init = () => {
  // Clean up
  document
    .querySelectorAll<HTMLElement>("[data-smartforests-sidepanel-open]")
    .forEach((el) => {
      el.removeEventListener("click", onClickSidepanelLink)
    })
  // Set up
  document
    .querySelectorAll<HTMLElement>("[data-smartforests-sidepanel-open]")
    .forEach((el) => {
      el.addEventListener("click", onClickSidepanelLink);
    });
};

function onClickSidepanelLink(e) {
  const sidepanel = document.querySelector(
    e.target.dataset.smartforestsSidepanelOpen
  );
  if (sidepanel) {
    // Close all other sidepanels
    const sidepanels = Array.from(document.querySelectorAll(".offcanvas"))
    for (const sidepanel of sidepanels) {
      const instance = bootstrap.Offcanvas.getInstance(sidepanel) || new bootstrap.Offcanvas(sidepanel);
      instance.hide()
    }

    // Then open this `sidepanel`
    const instance =
      bootstrap.Offcanvas.getInstance(sidepanel) ||
      new bootstrap.Offcanvas(sidepanel);
    instance.show();
  }
}

window.addEventListener("turbo:load", init);
window.addEventListener("turbo:frame-render", init)
