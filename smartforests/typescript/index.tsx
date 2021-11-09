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

  if (modelInfo?.model?.toLowerCase() === "mappage") {
    const { main } = await import("./map");
    main();
  }

  if (modelInfo?.model?.toLowerCase() === "radiopage") {
    const { main } = await import("./radio");
    main();
  }
}
