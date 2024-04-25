const tagOffcanvasId = "tagpanel-turboframe";
let initialOffCanvasContent = "";

window.addEventListener("load", () => {
  const tagOffcanvas = document.getElementById(tagOffcanvasId);
  initialOffCanvasContent = tagOffcanvas?.innerHTML || "";

  window.addEventListener("turbo:load", () => {
    setupLoadingOnTagClick();
  });
  setupLoadingOnTagClick();
});

let $tags = [];
function setupLoadingOnTagClick() {
  $tags.forEach(($tag) => {
    $tag.removeEventListener("click", showLoading);
  });
  $tags = document.querySelectorAll('[data-turbo-frame="tagpanel-turboframe"]');
  $tags.forEach(($tag) => {
    $tag.addEventListener("click", showLoading);
  });
}

function showLoading() {
  const tagOffcanvas = document.getElementById(tagOffcanvasId);
  if (tagOffcanvas) {
    tagOffcanvas.innerHTML = initialOffCanvasContent;
  }
}
