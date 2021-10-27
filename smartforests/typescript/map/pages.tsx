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
import { equalUrls, useFrameSrc, useOffcanvas } from "../bootstrap";

interface TurboFrameElement extends HTMLElement {
  src?: string;
}

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
  const [offcanvas, sidebarEl] = useOffcanvas("sidepanel-offcanvas");
  const frame = useMemo(
    () => document.querySelector<TurboFrameElement>("#sidepanel-turboframe"),
    []
  );

  const frameUrl = pageToFrameURL(page);
  const activeUrl = useFrameSrc(frame);

  console.log(frameUrl, activeUrl);

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
            // Remove children from frame before showing to prevent flash of stale content
            if (sidebarEl.style.visibility !== "visible") {
              Array.from(frame.children).forEach((x) => x.remove());
            }
            offcanvas.show();
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
