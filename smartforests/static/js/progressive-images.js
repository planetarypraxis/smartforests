$("img[data-src]").each(function () {
  const $img = $(this);
  $img.attr("src", $img.attr("data-src"));
});
