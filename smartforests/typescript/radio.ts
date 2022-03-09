import { findAncestor, formatDuration } from "./util";

const radioPlayerAudio = new Audio();

export function main() {
  /**
   * Control the audio player from any number of play buttons in the UI
   */
  const playButtons = document.querySelectorAll(
    "[data-smartforests-radio-play-button]"
  );
  console.log(`Found ${playButtons.length} play buttons on page.`);

  /**
   * Define the actual radio player
   */
  const radioPlayer = document.getElementById("radioPlayer");
  const radioPlayerPlayButton = document.getElementById("radioPlayerPlayButton");
  const radioPlayerOffCanvasElement = document.getElementById("radioPlayer");
  const radioPlayerSeeker = document.getElementById('radioPlayerSeeker')
  // @ts-ignore
  const radioPlayerOffCanvas = new bootstrap.Offcanvas(radioPlayerOffCanvasElement);

  /**
   * Update all play buttons in response to radioPlayerAudio status
   */
  radioPlayerAudio.addEventListener('ended', updateButtonState)
  radioPlayerAudio.addEventListener('pause', updateButtonState)
  radioPlayerAudio.addEventListener('play', updateButtonState)
  radioPlayerAudio.addEventListener('playing', updateButtonState)

  function isPlayerButtonActive(somePlayButton) {
    if (!somePlayButton.dataset.smartforestsAudio || !radioPlayerAudio.src) return false
    // (We rebuild the URL because one might be a relative URL, the other might be absolute)
    const buttonURL = new URL(somePlayButton.dataset.smartforestsAudio, radioPlayerAudio.src).toString()
    const playerURL = new URL(radioPlayerAudio.src).toString()
    return buttonURL === playerURL
  }

  function updateButtonState() {
    // Main radio player
    radioPlayerPlayButton.querySelector(radioPlayerAudio.paused ? ".pause-button" : ".play-button").classList.add("d-none");
    radioPlayerPlayButton.querySelector(radioPlayerAudio.paused ? ".play-button" : ".pause-button").classList.remove("d-none");

    // Other play/pause buttons in the UI
    Array.from(playButtons).forEach((somePlayButton) => {
      // Default all buttons to pause, just in case
      somePlayButton.querySelector(".pause-button").classList.add("d-none");
      somePlayButton.querySelector(".play-button").classList.remove("d-none");

      // If the button refers to the same audio, then sync its visual state to the radio player
      if (isPlayerButtonActive(somePlayButton)) {
        somePlayButton.querySelector(radioPlayerAudio.paused ? ".pause-button" : ".play-button").classList.add("d-none");
        somePlayButton.querySelector(radioPlayerAudio.paused ? ".play-button" : ".pause-button").classList.remove("d-none");
      }
    });
  }

  /**
   * Update the current time / bar / etc. according to current status
   */
  radioPlayerAudio.addEventListener('timeupdate', updatePlayerTime)
  function updatePlayerTime(e) {
    requestAnimationFrame(() => {
      radioPlayer.querySelector(
        "[data-smartforests-radio-episode-elapsed-time]"
      ).innerHTML = formatDuration(radioPlayerAudio.currentTime);
      // @ts-ignore
      radioPlayerSeeker.value = (radioPlayerAudio.currentTime / radioPlayerAudio.duration).toString()
    })
  }

  radioPlayerAudio.addEventListener('durationchange', updatePlayerDuration)
  function updatePlayerDuration() {
    requestAnimationFrame(() => {
      radioPlayer.querySelector(
        "[data-smartforests-radio-episode-duration]"
      ).innerHTML = formatDuration(radioPlayerAudio.duration);
    })
  }

  /**
   * Control the radio player with the buttons
   */

  radioPlayerPlayButton.addEventListener("click", (event) => {
    event.stopImmediatePropagation();
    if (radioPlayerAudio.paused) {
      radioPlayerAudio.play()
    } else {
      radioPlayerAudio.pause()
    }
  });

  /**
   * Control the current time via the seeker
   */
  radioPlayerSeeker.addEventListener('click', (event) => {
    event.stopImmediatePropagation()
    const percent = event.offsetX / radioPlayerSeeker.offsetWidth;
    radioPlayerAudio.currentTime = percent * radioPlayerAudio.duration;
  })

  /**
   * Load audio into player from any 'play' button in the UI
   */

  function startRadioPlayer(audioUrl, title, owner, lastPublishedAt, image, pageURL, play = true) {
    radioPlayer.querySelector(
      "[data-smartforests-radio-episode-title]"
    ).innerHTML = title;
    radioPlayer.querySelector(
      "[data-smartforests-radio-episode-owner]"
    ).innerHTML = owner;
    radioPlayer.querySelector(
      "[data-smartforests-radio-episode-last-published-at]"
    ).innerHTML = lastPublishedAt;
    Array.from(radioPlayer.querySelectorAll<HTMLAnchorElement>(
      "[data-smartforests-radio-episode-page-url]"
    )).map(el => el.href = pageURL)

    // @ts-ignore
    radioPlayer.querySelector("[data-smartforests-radio-episode-image]").src =
      image;

    radioPlayerAudio.src = audioUrl;
    if (play) {
      radioPlayerAudio.play();
    }
  }

  Array.from(playButtons).forEach((playButton) => {
    // Load featured episode at pageload
    if (
      // Don't override an explicit user interaction
      !isPlayerButtonActive(playButton)
      // @ts-ignore
      // Only listen for radio things marked preloadable
      && playButton.dataset.smartforestsShouldPreloadEpisode !== undefined
    ) {
      startRadioPlayerViaButton(playButton, false);
    }

    // Listen for subsequent 'play' requests
    playButton.addEventListener("click", (event) => {
      event.stopImmediatePropagation();

      // If this audio track was already playing,
      // then treat this as a normal play/pause button
      if (isPlayerButtonActive(playButton)) {
        if (radioPlayerAudio.paused) {
          radioPlayerAudio.play();
        } else {
          radioPlayerAudio.pause();
        }
        return
      }

      // Else treat this as a "load new track" button
      let buttonElement

      // @ts-ignore
      if (!event.target.dataset.smartforestsAudio) {
        buttonElement = findAncestor(
          event.target,
          "[data-smartforests-radio-play-button]"
        );
      } else {
        buttonElement = event.target;
      }

      startRadioPlayerViaButton(buttonElement);
    });
  });

  function startRadioPlayerViaButton(buttonElement, play = true) {
    const audioUrl = buttonElement.dataset.smartforestsAudio;
    const title = buttonElement.dataset.smartforestsTitle;
    const lastPublishedAt = buttonElement.dataset.smartforestsLastPublishedAt;
    const owner = buttonElement.dataset.smartforestsOwner;
    const image = buttonElement.dataset.smartforestsImage;
    const pageURL = buttonElement.dataset.smartforestsPageUrl;

    radioPlayerAudio.pause();
    radioPlayerOffCanvas.show();

    console.log(`Loading ${audioUrl}`);
    startRadioPlayer(audioUrl, title, owner, lastPublishedAt, image, pageURL, play);
  }

  // Update the button state on each new visit
  // in case something is already playing
  updateButtonState()
}
