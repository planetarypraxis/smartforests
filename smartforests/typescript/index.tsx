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

  let main = () => {};

  switch (modelName) {
    case "mappage":
      ({ main } = await import("./map"));
      break;

    case "radioindexpage":
    case "episodepage":
      ({ main } = await import("./radio"));
      break;
  }

  main();
}
