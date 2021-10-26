import React, { Fragment, memo, useEffect, useMemo, useState } from "react";
import {
  pageToPath,
  useWagtailSearch,
  Wagtail,
  pageToFrameURL,
} from "../wagtail";
import { SmartForest } from "./types";
import { Marker, Popup } from "@urbica/react-map-gl";
import { useFocusContext } from "./state";
import { Link } from "react-router-dom";
import { equalUrls, useFrameSrc, useOffcanvas } from "../bootstrap";

export function AtlasPagesMapLayer() {
  return (
    <Fragment>
      <LogbookPageMarkers />
      <LogbookEntryPageMarkers />
      <StoryPageMarkers />
    </Fragment>
  );
}

export function LogbookPageMarkers() {
  const results = useWagtailSearch<SmartForest.LogbookPage>({
    type: "logbooks.LogbookPage",
    limit: 1000,
  });

  return (
    <Fragment>
      {results.data?.items
        ?.filter((f) => !!f.coordinates)
        .map((page, i) => (
          <AtlasPageMarker key={i + page.id} page={page} />
        ))}
    </Fragment>
  );
}

export function LogbookEntryPageMarkers() {
  const results = useWagtailSearch<SmartForest.LogbookEntryPage>({
    type: "logbooks.LogbookEntryPage",
    limit: 1000,
  });

  return (
    <Fragment>
      {results.data?.items
        ?.filter((f) => !!f.coordinates)
        .map((page, i) => (
          <AtlasPageMarker key={i + page.id} page={page} />
        ))}
    </Fragment>
  );
}

export function StoryPageMarkers() {
  const results = useWagtailSearch<SmartForest.StoryPage>({
    type: "logbooks.StoryPage",
    limit: 1000,
  });

  return (
    <Fragment>
      {results.data?.items
        ?.filter((f) => !!f.coordinates)
        .map((page, i) => (
          <AtlasPageMarker key={i + page.id} page={page} />
        ))}
    </Fragment>
  );
}

export const AtlasPageMarker: React.FC<{
  page: Wagtail.Item<SmartForest.GeocodedMixin>;
}> = memo(({ page }) => {
  const [isFocusing, setIsFocusing] = useFocusContext(page.id, page.meta.type);
  const [offcanvas] = useOffcanvas<any>("sidepanel-offcanvas");

  const frameUrl = pageToFrameURL(
    "sidepanel-turboframe",
    page,
    "logbooks/sidepanel.html"
  );

  const activeUrl = useFrameSrc("sidepanel-turboframe");

  const active = equalUrls(frameUrl, activeUrl);
  const iconClass = active ? `icon-30 icon-cursor` : page.icon_class;

  return (
    <Fragment>
      <Marker
        longitude={page.coordinates.coordinates[0]}
        latitude={page.coordinates.coordinates[1]}
      >
        <a
          data-turbo-action="advance"
          data-turbo-frame="sidepanel-turboframe"
          href={frameUrl}
          onMouseOver={() => setIsFocusing(true, "map")}
          onMouseOut={() => setIsFocusing(false, "map")}
          onClick={() => {
            // data-bs-toggle does not open/close things appropriately
            // data-bs-[*] attributes interfere with data-turbo-action
            // So we do this programatically instead.
            // An alternative would be to control this at the URL level, coordinated by some kind of routing library.
            offcanvas.show();
            // NB: Currently the TurboFrame sidepanel will not respond to back/forward navigation, so this is not in use.
            // Update the window URL to allow navigation back to this sidepanel on share/refresh.
            // (supported by server-side rendering at smartforests.models.MapPage.subpages).
            // (There is an open PR to do this via data-turbo-[attr] at https://github.com/hotwired/turbo/pull/167 / https://github.com/hotwired/turbo/pull/398)
            //
            // history.push(pageToPath(page))
          }}
        >
          <div
            className={`${
              !active ? "cursor-pointer" : ""
            } translate-middle position-absolute bg-bright-yellow icon ${iconClass}`}
          />
        </a>
      </Marker>
      {isFocusing && !active && (
        <Popup
          className="mapbox-invisible-popup"
          longitude={page?.coordinates?.coordinates[0]}
          latitude={page?.coordinates?.coordinates[1]}
          offset={20}
        >
          <AtlasPageCard page={page} />
        </Popup>
      )}
    </Fragment>
  );
});

function AtlasPageCard({
  page,
}: {
  page: Wagtail.Item<SmartForest.GeocodedMixin>;
}) {
  return (
    <div className="p-3 w-popover bg-white elevated">
      <div className="caption text-dark-grey">{page.label}</div>

      <h5 id="offcanvasMapTitle" className="text-dark-green fw-bold mt-1 mb-0">
        <i
          className={`icon icon-20 bg-primary ms-2 align-bottom float-end ${page.icon_class}`}
        />
        {page.title}
      </h5>

      {page.geographical_location && (
        <div className="mt-1 caption text-dark-grey">
          {page.geographical_location}
        </div>
      )}
    </div>
  );
}
