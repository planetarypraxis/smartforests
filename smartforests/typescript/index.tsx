load();

document.addEventListener("turbo:load", async (event) => {
  load();
});

async function load() {
  const modelInfo = JSON.parse(document.getElementById('model-info').innerHTML) as { app_label: string, model: string }

  if (modelInfo?.model?.toLowerCase() === 'mappage') {
    const { main } = await import("./map");
    main();
  }

  if (modelInfo?.model?.toLowerCase() === 'radiopage') {
    const { main } = await import("./radio");
    main();
  }
}
