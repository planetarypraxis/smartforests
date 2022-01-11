import qs from 'query-string'
import { getLanguageCode } from './pageContext';

const init = () => {
  const search = document.getElementById("search-box");
  const searchResults = document.getElementById("search-results");
  const searchToggle = document.getElementById("searchToggle");
  const modal = new bootstrap.Modal(searchToggle);
  const languageCode = getLanguageCode()

  searchToggle.addEventListener("submit", (e) => e.preventDefault());

  search.addEventListener(
    "input",
    _.debounce(() => {
      searchResults.src = qs.stringifyUrl({
        url: '/search/',
        query: {
          query: search.value,
          language_code: languageCode
        }
      })
    }, 300)
  );

  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "s") {
      event.preventDefault();
      modal.show();
    }
  });

  searchToggle.addEventListener("turbo:frame-load", (event) => {
    let index = 0;

    const down = 40;
    const up = 38;
    const enter = 13;

    const moveSelection = (delta) => {
      searchResults.children[index].classList.remove("active");
      searchResults.children[index + delta].classList.add("active");
      index += delta;
    };

    search.addEventListener("keydown", (event) => {
      if (event.keyCode == down) {
        if (index < searchResults.children.length - 1) {
          moveSelection(+1);
          event.preventDefault();
        }
      } else if (event.keyCode == up) {
        if (index > 0) {
          moveSelection(-1);
          event.preventDefault();
        }
      } else if (event.keyCode == enter) {
        if (searchResults.children[index].href) {
          modal.hide();
          Turbo.visit(searchResults.children[index].href);
        }
      }
    });
  });
};

window.addEventListener("turbo:load", init);
