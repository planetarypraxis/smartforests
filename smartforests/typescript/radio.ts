import { findAncestor, formatDuration } from "./util";

const episode = new Audio();

export function main() {
  /**
   * Control the audio player from any number of play buttons in the UI
   */
  const loadEpisodeButtons = document.querySelectorAll<HTMLElement>(
    "[data-smartforests-radio-play-button]"
  );

  /**
   * Define the actual radio player
   */
  const radio = document.getElementById("radioPlayer") as HTMLElement;
  const radioPlayButton = document.getElementById("radioPlayerPlayButton") as HTMLElement;
  const radioOffCanvasElement = document.getElementById("radioPlayer") as HTMLElement;
  const radioSeeker = document.getElementById('radioPlayerSeeker') as HTMLProgressElement
  const radioOffCanvas = new window.bootstrap.Offcanvas(radioOffCanvasElement);

  /**
   * Update all play buttons in response to radioPlayerAudio status
   */
  episode.addEventListener('ended', updateButtonState)
  episode.addEventListener('pause', updateButtonState)
  episode.addEventListener('play', updateButtonState)
  episode.addEventListener('playing', updateButtonState)

  function isEpisodeActive(somePlayButton) {
    if (!somePlayButton.dataset.smartforestsAudio || !episode.src) return false
    // (We rebuild the URL because one might be a relative URL, the other might be absolute)
    const buttonURL = new URL(somePlayButton.dataset.smartforestsAudio, episode.src).toString()
    const playerURL = new URL(episode.src).toString()
    return buttonURL === playerURL
  }

  function updateButtonState() {
    // Main radio player
    radioPlayButton.querySelector(episode.paused ? ".pause-button" : ".play-button").classList.add("d-none");
    radioPlayButton.querySelector(episode.paused ? ".play-button" : ".pause-button").classList.remove("d-none");

    // Other play/pause buttons in the UI
    Array.from(loadEpisodeButtons).forEach((loadEpisodeButton) => {
      // Default all buttons to pause, just in case
      loadEpisodeButton.querySelector(".pause-button").classList.add("d-none");
      loadEpisodeButton.querySelector(".play-button").classList.remove("d-none");

      // If the button refers to the same audio, then sync its visual state to the radio player
      if (isEpisodeActive(loadEpisodeButton)) {
        loadEpisodeButton.querySelector(episode.paused ? ".pause-button" : ".play-button").classList.add("d-none");
        loadEpisodeButton.querySelector(episode.paused ? ".play-button" : ".pause-button").classList.remove("d-none");
      }
    });
  }

  /**
   * Update the current time / bar / etc. according to current status
   */
  episode.addEventListener('timeupdate', updatePlayerTime)
  function updatePlayerTime(e) {
    requestAnimationFrame(() => {
      radio.querySelector(
        "[data-smartforests-radio-episode-elapsed-time]"
      ).innerHTML = formatDuration(episode.currentTime);
      radioSeeker.value = parseFloat((episode.currentTime / episode.duration).toString())
    })
  }

  episode.addEventListener('durationchange', updateEpisodeDuration)
  function updateEpisodeDuration() {
    requestAnimationFrame(() => {
      radio.querySelector(
        "[data-smartforests-radio-episode-duration]"
      ).innerHTML = formatDuration(episode.duration);
    })
  }

  /**
   * Control the radio player with the buttons
   */

  radioPlayButton.addEventListener("click", (event) => {
    event.stopImmediatePropagation();
    if (episode.paused) {
      episode.play()
    } else {
      episode.pause()
    }
  });

  /**
   * Control the current time via the seeker
   */
  radioSeeker.addEventListener('click', (event) => {
    event.stopImmediatePropagation()
    const percent = event.offsetX / radioSeeker.offsetWidth;
    episode.currentTime = percent * episode.duration;
  })

  /**
   * Load audio into player from any 'play' button in the UI
   */

  function loadRadioPlayer(audioUrl, title, owner, lastPublishedAt, image, pageURL, play = true) {
    radio.querySelector(
      "[data-smartforests-radio-episode-title]"
    ).innerHTML = title;
    radio.querySelector(
      "[data-smartforests-radio-episode-owner]"
    ).innerHTML = owner;
    radio.querySelector(
      "[data-smartforests-radio-episode-last-published-at]"
    ).innerHTML = lastPublishedAt;
    Array.from(radio.querySelectorAll<HTMLAnchorElement>(
      "[data-smartforests-radio-episode-page-url]"
    )).map(el => { el.href = pageURL });

    (radio.querySelector("img[data-smartforests-radio-episode-image]") as HTMLImageElement).src =
      image;

    episode.src = audioUrl;
    if (play) {
      episode.play();
    }
  }

  Array.from(loadEpisodeButtons).forEach((playButton) => {
    // Load featured episode at pageload
    if (
      // Don't override an explicit user interaction
      !isEpisodeActive(playButton)
      // Only listen for radio things marked preloadable
      && playButton.dataset.smartforestsShouldPreloadEpisode !== undefined
    ) {
      loadEpisodeViaButton(playButton, false);
    }

    // Listen for subsequent 'play' requests
    playButton.addEventListener("click", (event) => {
      event.stopImmediatePropagation();

      // If this audio track was already playing,
      // then treat this as a normal play/pause button
      if (isEpisodeActive(playButton)) {
        if (episode.paused) {
          episode.play();
        } else {
          episode.pause();
        }
        return
      }

      // Else treat this as a "load new track" button
      let buttonElement

      // Capture click events on child elements
      if (!(event.target as HTMLElement).dataset.smartforestsAudio) {
        buttonElement = findAncestor(
          event.target,
          "[data-smartforests-radio-play-button]"
        );
      } else {
        buttonElement = event.target;
      }

      loadEpisodeViaButton(buttonElement);
    });
  });

  function loadEpisodeViaButton(buttonElement, play = true) {
    const audioUrl = buttonElement.dataset.smartforestsAudio;
    const title = buttonElement.dataset.smartforestsTitle;
    const lastPublishedAt = buttonElement.dataset.smartforestsLastPublishedAt;
    const owner = buttonElement.dataset.smartforestsOwner;
    const image = buttonElement.dataset.smartforestsImage;
    const pageURL = buttonElement.dataset.smartforestsPageUrl;

    episode.pause();
    radioOffCanvas.show();

    loadRadioPlayer(audioUrl, title, owner, lastPublishedAt, image, pageURL, play);
  }

  // Update the button state on each new visit
  // in case something is already playing
  updateButtonState()
}
