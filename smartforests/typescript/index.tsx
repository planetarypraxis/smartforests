load();

import { Offcanvas } from "bootstrap";

document.addEventListener("turbo:load", async (event) => {
  load();
});

async function load() {
  if (window.location.pathname.startsWith("/map")) {
    const { main } = await import("./map");
    main();
  }

  const playButtons = document.querySelectorAll(
    "[data-smartforests-radio-play-button]"
  );

  console.log(`Found ${playButtons.length} play buttons on page.`);

  const radioPlayerAudio = document.getElementById("radioPlayerAudio");
  const radioPlayerPlayButton = document.getElementById(
    "radioPlayerPlayButton"
  );

  let radioIsPlaying = false;

  const radioPlayerOffCanvasElement = document.getElementById("radioPlayer");
  const radioPlayerOffCanvas = new Offcanvas(radioPlayerOffCanvasElement);

  radioPlayerPlayButton.addEventListener("click", (event) => {
    event.stopImmediatePropagation();

    if (!radioIsPlaying) {
      console.log("Starting radio");
      radioPlayerAudio.play();
      radioIsPlaying = true;

      radioPlayerPlayButton
        .querySelector(".play-button")
        .classList.add("d-none");
      radioPlayerPlayButton
        .querySelector(".pause-button")
        .classList.remove("d-none");
      return;
    }

    console.log("Stopping radio");
    radioIsPlaying = false;
    radioPlayerAudio.pause();

    radioPlayerPlayButton
      .querySelector(".play-button")
      .classList.remove("d-none");
    radioPlayerPlayButton
      .querySelector(".pause-button")
      .classList.add("d-none");

    Array.from(playButtons).forEach((otherPlaybutton) => {
      otherPlaybutton.querySelector(".pause-button").classList.add("d-none");
      otherPlaybutton.querySelector(".play-button").classList.remove("d-none");
    });
  });

  function findAncestor(element, selector) {
    while (
      (element = element.parentElement) &&
      !(element.matches || element.matchesSelector).call(element, selector)
    );

    return element;
  }

  Array.from(playButtons).forEach((playButton) => {
    playButton.addEventListener("click", (event) => {
      event.stopImmediatePropagation();

      if (radioIsPlaying) {
        radioPlayerAudio.pause();
      }

      let buttonElement;

      if (!event.target.dataset.smartforestsAudio) {
        buttonElement = findAncestor(
          event.target,
          "[data-smartforests-radio-play-button]"
        );
      } else {
        buttonElement = event.target;
      }

      const audioUrl = buttonElement.dataset.smartforestsAudio;

      buttonElement.querySelector(".play-button").classList.add("d-none");
      buttonElement.querySelector(".pause-button").classList.remove("d-none");

      Array.from(playButtons).forEach((otherPlaybutton) => {
        if (otherPlaybutton === buttonElement) {
          console.log("Our element, skipping");
          return;
        }

        otherPlaybutton.querySelector(".pause-button").classList.add("d-none");
        otherPlaybutton
          .querySelector(".play-button")
          .classList.remove("d-none");
      });

      console.log(`Loading ${audioUrl}`);

      radioPlayerAudio.src = audioUrl;

      radioPlayerOffCanvas.show();
      radioPlayerAudio.play();

      radioPlayerPlayButton
        .querySelector(".play-button")
        .classList.add("d-none");
      radioPlayerPlayButton
        .querySelector(".pause-button")
        .classList.remove("d-none");

      radioIsPlaying = true;
    });
  });
}
