import "./sidepanel";
import "./mainmenu";

load();

const SEARCH_BACKDROP_ID = 'search-backdrop'
const SEARCH_ID = 'searchToggle'

function getBackdropElement() {
  return document.getElementById(SEARCH_BACKDROP_ID)
}

function getSearchElement() {
  return document.getElementById(SEARCH_ID)
}

function closeBootstrapSearchOnOutsideClicks(event) {
  const modalElement = getSearchElement().querySelector('.modal-dialog')
  const isClickingOutside = !event.composedPath().includes(modalElement)
  if (isClickingOutside) {
    // @ts-ignore
    bootstrap.Modal.getInstance(document.getElementById(SEARCH_ID)).hide()
  }
}

document.addEventListener("show.bs.modal", showBackdrop)
document.addEventListener("hidden.bs.modal", hideBackdrop)

document.addEventListener("turbo:before-cache", () => {
  hideBackdrop()
})

function showBackdrop() {
  document.body.classList.toggle('modal-open', true)
  //
  const backdrop = document.createElement('div')
  backdrop.classList.add('modal-backdrop')
  backdrop.classList.add('fade')
  backdrop.classList.add('show')
  backdrop.setAttribute('id', SEARCH_BACKDROP_ID)
  document.body.appendChild(backdrop)
  document.addEventListener('click', closeBootstrapSearchOnOutsideClicks)
}

function hideBackdrop() {
  // Kill the outside click listener
  document.removeEventListener('click', closeBootstrapSearchOnOutsideClicks)
  //
  document.body.classList.toggle('modal-open', false)
  //
  const backdrop = getBackdropElement()
  if (!backdrop) return
  backdrop.classList.remove('show')
  backdrop.addEventListener('transitionend', () => {
    backdrop.remove()
  });
}

document.addEventListener("turbo:load", async (event) => {
  load();
});

async function load() {
  const modelInfoInDOM = document.getElementById("model-info");

  if (!modelInfoInDOM) {
    return;
  }

  const modelInfo = JSON.parse(modelInfoInDOM.innerHTML) as {
    app_label: string;
    model: string;
  };

  const modelName = modelInfo?.model?.toLowerCase();

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
