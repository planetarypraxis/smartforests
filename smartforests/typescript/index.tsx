import "./sidepanel";
import "./mainmenu";
import { Offcanvas } from "bootstrap"

load();

document.addEventListener("turbo:load", async (event) => {
  load();
  resetJSForTurboFrame();
});

function getModelInfo() {
  const modelInfoInDOM = document.getElementById("model-info");

  if (!modelInfoInDOM) {
    return;
  }

  const modelInfo = JSON.parse(modelInfoInDOM.innerHTML) as {
    app_label: string;
    model: string;
    page_id: string
  };

  return modelInfo
}

const PAGE_ID_REGEX = /pages\/[0-9]+/gim
document.addEventListener("turbo:render", () => {
  const btns = document.getElementById("wagtail-userbar-items")
  // get the page ID from the HTML
  const modelInfo = getModelInfo()
  if (!modelInfo || !btns) return
  // find all the anchor links
  const links = btns.querySelectorAll<HTMLAnchorElement>("a[role='menuitem']");
  // loop over them, replace `page/oldID/` with `page/newID/`
  for (const link of links) {
    link.setAttribute("href", link.href.replace(PAGE_ID_REGEX, `pages/${modelInfo.page_id}`));
  }
})

async function load() {
  const modelInfo = getModelInfo()
  if (!modelInfo) return

  const modelName = modelInfo.model?.toLowerCase();

  let modules: Array<() => void> = []

  switch (modelName) {
    case "mappage":
      const { main } = await import("./map")
      modules.push(main)
      break;
  }

  // Load radio player on all pages
  {
    const { main } = await import("./radio")
    modules.push(main)
  }

  modules.forEach(fn => fn());
}

function resetJSForTurboFrame() {
  // Ensure Boostrap Offcanvases (sidepanels) are in the correct state
  // according to the Turbo Frame cache'd history. If going back in the history
  // and the Offcanvas was previously open, then re-open it
  const offcanvas = document.querySelectorAll(".offcanvas")

  for (const el of offcanvas) {
    const visible = window.getComputedStyle(el)['visibility'] === 'visible'
    let offcanvas = new Offcanvas(el)
    offcanvas.show()
    if (!visible) offcanvas.hide()
  }
}