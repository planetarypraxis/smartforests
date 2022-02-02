import "./sidepanel";
import "./mainmenu";

load();

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
