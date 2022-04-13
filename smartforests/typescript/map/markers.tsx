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
import { equalUrls, useOffcanvas } from "../bootstrap";
import { Feature, Point } from "geojson";
import { useAtomValue } from "jotai/utils";
import { useAtom } from "jotai";
import { frameAtomFamily } from "../pageContext";
import type { Cluster } from "superclusterd";

export const ClusterMarker: React.FC<{
  feature: Feature<Point, Cluster>;
}> = ({ feature }) => {
  const size = Math.round(
    Math.max(20, Math.min(Math.log(feature.properties.point_count), 75))
  );
  const [_, updateViewport] = useAtom(viewportAtom);
  const [longitude, latitude] = feature.geometry.coordinates;
  const [isFocusing, setIsFocusing] = useFocusContext(`cluster-${feature.properties.cluster_id}`, "cluster");
  const [offcanvas, sidebarEl] = useOffcanvas("sidepanel-offcanvas");
  const sidebarFrame = useAtomValue(frameAtomFamily("#sidepanel-turboframe"));

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
          className={`${size > 30 ? "heading-medium" : ""} p-1 font-monospace center-screen`}
          onMouseOver={() => setIsFocusing(true, "map")}
        >
          {feature.properties.point_count}
        </div>
        {isFocusing && feature.properties?.features?.length ? (
          <Popup
            className="mapbox-invisible-popup w-popover"
            longitude={longitude}
            latitude={latitude}
            offset={20}
            onClose={() => setIsFocusing(false, "map")}
          >
            <div className='caption text-dark-grey p-2 cursor-pointer hover-bg-light-grey' onClick={() => setIsFocusing(false, "map")}>
              Close
            </div>
            {feature.properties.features.map(properties =>
              <a
                className='outline-none text-decoration-none bordered-child'
                data-turbo-frame="sidepanel-turboframe"
                href={pageToFrameURL(properties)}
                onClick={() => {
                  // Remove children from frame before showing to prevent flash of stale content
                  if (sidebarEl.style.visibility !== "visible") {
                    Array.from(sidebarFrame.el.children).forEach((x) => x.remove());
                  }
                  offcanvas.show();
                }}
              >
                <AtlasPageCard key={feature.id} properties={properties} elevated={false} />
              </a>
            )}
          </Popup>
        ) : null}
      </div>
    </Marker>
  );
};

export const AtlasPageMarker: React.FC<{
  feature: Feature<Point, SmartForest.MapItem>;
}> = memo(({ feature }) => {
  const { properties, geometry } = feature;
  const [isFocusing, setIsFocusing] = useFocusContext(properties.id, "map");
  const [offcanvas, sidebarEl] = useOffcanvas("sidepanel-offcanvas");

  const frameUrl = pageToFrameURL(properties);
  const sidebarFrame = useAtomValue(frameAtomFamily("#sidepanel-turboframe"));

  const active = equalUrls(frameUrl, sidebarFrame.src);

  const iconClass = (active ? `icon-30` : '') + " " + properties.icon_class;

  return (
    <Fragment>
      <Marker
        longitude={geometry.coordinates[0]}
        latitude={geometry.coordinates[1]}
      >
        <a
          data-turbo-frame="sidepanel-turboframe"
          href={frameUrl}
          onMouseOver={() => setIsFocusing(true, "map")}
          onMouseOut={() => setIsFocusing(false, "map")}
          onClick={() => {
            // Remove children from frame before showing to prevent flash of stale content
            if (sidebarEl.style.visibility !== "visible") {
              Array.from(sidebarFrame.el.children).forEach((x) => x.remove());
            }
            offcanvas.show();
          }}
        >
          <div
            className={`${!active ? "cursor-pointer" : ""
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
          onClose={() => setIsFocusing(false, "map")}
        >
          <AtlasPageCard properties={feature.properties} />
        </Popup>
      )}
    </Fragment>
  );
});

export function AtlasPageCard({
  properties,
  elevated = true
}: {
  properties: Feature<Point, SmartForest.MapItem>['properties'];
  elevated?: boolean
}) {
  return (
    <div className={`p-2 w-popover bg-white ${elevated ? "br-3" : ""}`}>
      <div className="caption text-dark-grey">{properties.page_type}</div>

      <h5 id="offcanvasMapTitle" className="text-dark-green fw-bold mt-1 mb-0">
        <i
          className={`icon icon-20 bg-primary ms-2 align-bottom float-end ${properties.icon_class}`}
        />
        <span className='font-sans-serif'>{properties.title}</span>
      </h5>

      {properties.geographical_location && (
        <div className="mt-1 caption text-dark-grey">
          {properties.geographical_location}
        </div>
      )}
    </div>
  );
}
