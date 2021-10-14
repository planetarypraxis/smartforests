console.debug("Initial page load.")
load();

document.addEventListener('turbo:load', async (event) => {
  console.debug('TURBO page navigation', event)
  load();
})

async function load() {
  if (window.location.pathname.startsWith('/map')) {
    const { main } = await import('./map');
    main();
  }
}