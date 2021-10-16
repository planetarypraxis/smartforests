load();

document.addEventListener("turbo:load", async (event) => {
  load();
});

async function load() {
  if (window.location.pathname.startsWith("/map")) {
    const { main } = await import("./map");
    main();
  }
}
