import qs from 'query-string'
import { getLanguageCode } from './pageContext';

const SEARCH_ID = "searchToggle"
const SEARCH_BACKDROP_ID = 'search-backdrop'

const init = () => {
  const search = document.getElementById("search-box");
  const searchResults = document.getElementById("search-results");
  const searchToggle = document.getElementById(SEARCH_ID);
  const modal = new window.bootstrap.Modal(searchToggle);
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

  function getBackdropElement() {
    return document.getElementById(SEARCH_BACKDROP_ID)
  }

  function getSearchElement() {
    return document.getElementById(SEARCH_ID)
  }

  function closeBootstrapSearchOnOutsideClicks(event) {
    const modalElement = getSearchElement().querySelector('.modal-dialog')
    const isClickingOutside = !event.composedPath().includes(modalElement)
    if (isClickingOutside) {
      // @ts-ignore
      bootstrap.Modal.getInstance(document.getElementById(SEARCH_ID)).hide()
    }
  }

  document.addEventListener("show.bs.modal", showBackdrop)
  document.addEventListener("hidden.bs.modal", hideBackdrop)
  document.addEventListener("turbo:before-cache", hideBackdrop)

  function showBackdrop() {
    document.body.classList.toggle('modal-open', true)
    //
    let backdrop = getBackdropElement()
    if (!backdrop) {
      backdrop = document.createElement('div')
      backdrop.classList.add('modal-backdrop')
      backdrop.classList.add('fade')
      backdrop.classList.add('show')
      backdrop.setAttribute('id', SEARCH_BACKDROP_ID)
      backdrop.setAttribute('data-turbo-cache', 'false')
      document.body.appendChild(backdrop)
    }
    document.addEventListener('click', closeBootstrapSearchOnOutsideClicks)
  }

  function hideBackdrop() {
    // Kill the outside click listener
    document.removeEventListener('click', closeBootstrapSearchOnOutsideClicks)
    //
    document.body.classList.toggle('modal-open', false)
    //
    const backdrop = getBackdropElement()
    if (!backdrop) return
    backdrop.classList.remove('show')
    backdrop.addEventListener('transitionend', () => {
      backdrop.remove()
    });
  }
};

window.addEventListener("turbo:load", init);
