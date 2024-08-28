import { findAncestor, formatDuration } from "./util";
import { snakeCase } from "lodash";

type RadioState = {
  loaded: boolean;
  playing: boolean;
  episode?: string;
};

type EpisodeMeta = {
  audioUrl: string;
  title: string;
  owner: string;
  lastPublishedAt: string;
  image: string;
  pageURL: string;
};

type PlayButton = HTMLButtonElement & { dataset: PlayButtonDataset };

interface PlayButtonDataset {
  smartforestsAudio: string;
  smartforestsTitle: string;
  smartforestsLastPublishedAt: string;
  smartforestsOwner: string;
  smartforestsImage: string;
  smartforestsPageUrl: string;
}

const episode = new Audio();
let radio: RadioState = {
  loaded: false,
  playing: false,
};

export function main() {
  /**
   * Define the actual radio player
   */
  const radioUI = document.getElementById("radioPlayer") as HTMLElement;
  const radioPlayButton = document.getElementById("radioPlayerPlayButton") as HTMLElement;
  const radioSeeker = document.getElementById("radioPlayerSeeker") as HTMLProgressElement;
  const radioOffCanvasElement = document.getElementById("radioPlayer") as HTMLElement;
  const radioOffCanvas = new window.bootstrap.Offcanvas(radioOffCanvasElement);
  
  /**
   * Force ticker title animation to play on pageload 
   */

  const tickerElements = document.querySelectorAll('.ticker');

  tickerElements.forEach(function(element) {
    const htmlElement = element as HTMLElement;

    htmlElement.style.display = 'none';
    htmlElement.offsetHeight;
    htmlElement.style.display = 'inline-block'; 
  
    htmlElement.style.animation = 'ticker 30s linear infinite';
});

  /**
   * Update all play buttons in response to radioPlayerAudio status
   */
  episode.addEventListener("ended", updateButtonState);
  episode.addEventListener("pause", updateButtonState);
  episode.addEventListener("play", updateButtonState);
  episode.addEventListener("playing", updateButtonState);

  /**
   * Control the audio player from any number of play buttons in the UI
   */
  function getEpisodeButtons(): NodeListOf<PlayButton> {
    return document.querySelectorAll<PlayButton>("[data-smartforests-radio-play-button]");
  }

  function isEpisodeActive(playButton: PlayButton) {
    if (!playButton.dataset.smartforestsAudio || !episode.src) return false;
    // (We rebuild the URL because one might be a relative URL, the other might be absolute)
    const buttonURL = new URL(playButton.dataset.smartforestsAudio, episode.src).toString();
    const playerURL = new URL(episode.src).toString();
    return buttonURL === playerURL;
  }

  function updateButtonState() {
    const episodeLoadButtons = getEpisodeButtons();

    // Main radio player
    radioPlayButton
      .querySelector(episode.paused ? ".pause-button" : ".play-button")
      ?.classList.add("d-none");
    radioPlayButton
      .querySelector(episode.paused ? ".play-button" : ".pause-button")
      ?.classList.remove("d-none");

    // Other play/pause buttons in the UI
    (Array.from(episodeLoadButtons) as PlayButton[]).forEach((loadEpisodeButton) => {
      // Default all buttons to pause, just in case
      loadEpisodeButton.querySelector(".pause-button")?.classList.add("d-none");
      loadEpisodeButton.querySelector(".play-button")?.classList.remove("d-none");

      // If the button refers to the same audio, then sync its visual state to the radio player
      if (isEpisodeActive(loadEpisodeButton)) {
        loadEpisodeButton
          .querySelector(episode.paused ? ".pause-button" : ".play-button")
          ?.classList.add("d-none");
        loadEpisodeButton
          .querySelector(episode.paused ? ".play-button" : ".pause-button")
          ?.classList.remove("d-none");
      }
    });
  }

  /**
   * Update the current time / bar / etc. according to current status
   */
  episode.addEventListener("timeupdate", updatePlayerTime);
  function updatePlayerTime() {
    requestAnimationFrame(() => {
      const elapsed = radioUI.querySelector("[data-smartforests-radio-episode-elapsed-time]");
      if (elapsed) elapsed.innerHTML = formatDuration(episode.currentTime);
      if (episode.currentTime && episode.duration && episode?.duration > 0) {
        radioSeeker.value = parseFloat((episode.currentTime / episode.duration).toString());
      }
    });
  }

  episode.addEventListener("durationchange", updateEpisodeDuration);
  function updateEpisodeDuration() {
    requestAnimationFrame(() => {
      const duration = radioUI.querySelector("[data-smartforests-radio-episode-duration]");
      if (duration) duration.innerHTML = formatDuration(episode.duration);
    });
  }

  /**
   * Control the radio player with the buttons
   */
  radioPlayButton.addEventListener("click", (event) => {
    event.stopImmediatePropagation();
    if (episode.paused) {
      episode.play();
    } else {
      episode.pause();
    }
  });

  /**
   * Control the current time via the seeker
   */
  radioSeeker.addEventListener("click", (event) => {
    event.stopImmediatePropagation();
    const percent = event.offsetX / radioSeeker.offsetWidth;
    episode.currentTime = percent * episode.duration;
  });

  /**
   * Load audio into player from any 'play' button in the UI
   */

  function loadEpisode(episodeMeta: EpisodeMeta, play = false) {
    (["title", "owner", "lastPublishedAt"] as Array<keyof EpisodeMeta>).forEach((prop) => {
      const element = radioUI.querySelector(`[data-smartforests-radio-episode-${snakeCase(prop)}]`);
      if (element) element.innerHTML = episodeMeta[prop];
    });

    Array.from(
      radioUI.querySelectorAll<HTMLAnchorElement>("[data-smartforests-radio-episode-page-url]")
    ).map((el) => {
      el.href = episodeMeta.pageURL;
    });

    (radioUI.querySelector("img[data-smartforests-radio-episode-image]") as HTMLImageElement).src =
      episodeMeta.image;

    episode.src = episodeMeta.audioUrl;

    if (play) {
      episode.play();
    }
  }

  function addButtonListeners() {
    const episodeLoadButtons = getEpisodeButtons();
    Array.from(episodeLoadButtons).forEach((loadEpisodeButton) => {
      // Listen for clicks
      loadEpisodeButton.addEventListener("click", (event) => {
        event.stopImmediatePropagation();

        // If this audio track was already playing,
        // then treat this as a normal play/pause button
        if (isEpisodeActive(loadEpisodeButton)) {
          if (episode.paused) {
            episode.play();
          } else {
            episode.pause();
          }
          return;
        }

        // Else treat this as a "load new track" button
        let buttonElement;

        // Capture click events on child elements
        if (!(event.target as HTMLElement).dataset.smartforestsAudio) {
          buttonElement = findAncestor(event.target, "[data-smartforests-radio-play-button]");
        } else {
          buttonElement = event.target;
        }

        loadEpisodeViaButton(buttonElement, true);
      });
    });
  }

  function loadEpisodeViaButton(buttonElement: PlayButton, play = false): EpisodeMeta {
    const audioUrl = buttonElement.dataset.smartforestsAudio;
    const title = buttonElement.dataset.smartforestsTitle;
    const lastPublishedAt = buttonElement.dataset.smartforestsLastPublishedAt;
    const owner = buttonElement.dataset.smartforestsOwner;
    const image = buttonElement.dataset.smartforestsImage;
    const pageURL = buttonElement.dataset.smartforestsPageUrl;

    episode.pause();
    radioOffCanvas.show();
    const episodeMeta: EpisodeMeta = {
      audioUrl,
      title,
      owner,
      lastPublishedAt,
      image,
      pageURL,
    };

    loadEpisode(episodeMeta, play);

    return episodeMeta;
  }

  async function loadRadio() {
    if (!radio.loaded) {
      const featuredEpisode = document.querySelectorAll<PlayButton>(
        ".featured-episode[data-smartforests-radio-play-button]"
      )[0];

      if (!featuredEpisode) throw "Unable to load the Radio - no featured episode was found";

      const { pageURL } = loadEpisodeViaButton(featuredEpisode);

      radio.loaded = true;
      radio.episode = pageURL;
    }
    addButtonListeners();
    updateButtonState();
  }

  loadRadio();
}
