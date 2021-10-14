import * as Turbo from "@hotwired/turbo"

console.log("Page navigation handled by Turbo.", Turbo)

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