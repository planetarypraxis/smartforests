// Replace <img src=""> with the value in data-src=""
// which is a better quality image.
setTimeout(() => {
  $("img[data-src]").each(function (i) {
    const $img = $(this);
    $img.attr("src", $img.attr("data-src"));
  });
}, 1);
