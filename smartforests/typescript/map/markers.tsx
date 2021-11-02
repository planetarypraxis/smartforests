import React, { Fragment, memo, useEffect, useMemo, useState } from "react";
import {
  pageToPath,
  useWagtailSearch,
  Wagtail,
  pageToFrameURL,
} from "../wagtail";
import { SmartForest } from "./types";
import { Marker, Popup } from "@urbica/react-map-gl";
import { useFocusContext, viewportAtom } from "./state";
import { equalUrls, useFrameSrc, useOffcanvas } from "../bootstrap";
import { Feature, Point } from "geojson";
import { TurboFrameElement } from "../turbo";
import { Cluster } from "./data";
import { useAtomCallback } from "jotai/utils";
import { useAtom } from "jotai";

export const ClusterMarker: React.FC<{
  feature: Feature<Point, Cluster>;
}> = ({ feature }) => {
  const size = Math.round(
    Math.max(20, Math.min(Math.log(feature.properties.point_count), 75))
  );
  const [_, updateViewport] = useAtom(viewportAtom);

  const [longitude, latitude] = feature.geometry.coordinates;

  return (
    <Marker
      longitude={longitude}
      latitude={latitude}
      onClick={() => {
        updateViewport({
          longitude,
          latitude,
          zoom: 6,
        });
      }}
    >
      <div
        className="bg-bright-yellow position-absolute rounded-circle overflow-hidden d-flex flex-row justify-content-center translate-middle align-items-center"
        style={{
          width: size,
          height: size,
          cursor: "pointer",
        }}
      >
        <div
          className={`${
            size > 30 ? "heading-medium" : ""
          } p-1 font-monospace center-screen`}
        >
          {feature.properties.point_count}
        </div>
      </div>
    </Marker>
  );
};

export const AtlasPageMarker: React.FC<{
  feature: Feature<Point, SmartForest.MapItem>;
}> = memo(({ feature }) => {
  const {
    properties: { page },
    geometry,
  } = feature;
  const [isFocusing, setIsFocusing] = useFocusContext(page.id, "");
  const [offcanvas, sidebarEl] = useOffcanvas("sidepanel-offcanvas");
  const frame = useMemo(
    () => document.querySelector<TurboFrameElement>("#sidepanel-turboframe"),
    []
  );

  const frameUrl = pageToFrameURL(page);
  const activeUrl = useFrameSrc(frame);

  const active = equalUrls(frameUrl, activeUrl);
  const iconClass = active ? `icon-30 icon-cursor` : page.icon_class;

  return (
    <Fragment>
      <Marker
        longitude={geometry.coordinates[0]}
        latitude={geometry.coordinates[1]}
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
          longitude={geometry.coordinates[0]}
          latitude={geometry.coordinates[1]}
          offset={20}
        >
          <AtlasPageCard feature={feature} />
        </Popup>
      )}
    </Fragment>
  );
});

function AtlasPageCard({
  feature,
}: {
  feature: Feature<Point, SmartForest.MapItem>;
}) {
  const {
    properties: { page },
  } = feature;

  return (
    <div className="p-3 w-popover bg-white elevated">
      <div className="caption text-dark-grey">{page.title}</div>

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
