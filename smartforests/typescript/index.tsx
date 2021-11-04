load();

document.addEventListener("turbo:load", async (event) => {
  load();
});

async function load() {
  if (window.location.pathname.startsWith("/map")) {
    const { main } = await import("./map");
    main();
  }

  if (window.location.pathname.startsWith("/radio")) {
    const { main } = await import("./radio");
    main();
  }
}
