setTimeout(() => {
  $("img[data-src]").each(function (i) {
    const $img = $(this);
    $img.attr("src", $img.attr("data-src"));
  });
}, 1);
