import "@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css";
import "mapbox-gl/dist/mapbox-gl.css";

import React, { FC } from "react";
import MapGL, { MapContext } from "@urbica/react-map-gl";
import MapboxGeocoder from "@mapbox/mapbox-gl-geocoder";
import mapboxgl, { Evented } from "mapbox-gl";
import { Fragment, useContext, useEffect, useRef, useState } from "react";
import * as ReactDOM from "react-dom";

import { useSize } from "./data";
import { AtlasPageFeatureLayer } from "./layers";
import { unmountComponentAtNode } from "react-dom";
import { useAtom } from "jotai";
import { viewportAtom } from "./state";

const MAPBOX_TOKEN = document.getElementById("MAP_APP")?.dataset.mapboxToken;

export function MapVisual() {
  const [viewport, setViewport] = useAtom(viewportAtom);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const size = useSize(mapContainerRef);

  return (
    <div style={{ width: "100%", height: "100%" }} ref={mapContainerRef}>
      <MapGL
        {...viewport}
        accessToken={MAPBOX_TOKEN}
        mapStyle="mapbox://styles/smartforests/ckuquky9r2o3v18lkxddvri76/draft?v2"
        style={{ width: "100%", height: "100%" }}
        viewportChangeMethod="flyTo"
        onViewportChange={(viewport) =>
          setViewport({
            ...viewport,
            // no 3D controls
            bearing: 0,
            pitch: 0,
          })
        }
        minZoom={2}
        maxZoom={6}
      >
        <GeocodeControl position="top-left" accessToken={MAPBOX_TOKEN} />
        <FilterControl />
        <AtlasPageFeatureLayer size={size} viewport={viewport} />
      </MapGL>
    </div>
  );
}

function GeocodeControl({
  position,
  accessToken,
}: {
  accessToken: string;
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right";
}) {
  const map: mapboxgl.Map = useContext(MapContext);

  useEffect(() => {
    // Docs: https://github.com/mapbox/mapbox-gl-geocoder/blob/master/API.md#mapboxgeocoder
    const control = new MapboxGeocoder({
      accessToken,
      mapboxgl,
      zoom: 14,
      placeholder: "Search by location",
      collapsed: true,
      marker: false,
      types: [
        "country",
        "region",
        "district",
        "place",
        "locality",
        "neighborhood",
      ].join(","),
    });

    map?.addControl(control as any, position);

    return () => {
      map?.removeControl(control as any);
    };
  }, [map, position]);

  return null;
}

class FilterControlRenderer extends Evented {
  private _map?: mapboxgl.Map;
  private _container?: HTMLElement;

  onAdd(map) {
    this._map = map;
    this._container = document.createElement("div");
    ReactDOM.render(<FilterPopover />, this._container);
    return this._container;
  }

  onRemove() {
    if (this._container) {
      unmountComponentAtNode(this._container);
    }
  }
}

function FilterIcon() {
  return (
    <svg
      width="24"
      height="16"
      viewBox="0 0 24 16"
      fill="none"
      className="d-inline-block"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M9.33333 16H14.6667V13.3333H9.33333V16ZM0 0V2.66667H24V0H0ZM4 9.33333H20V6.66667H4V9.33333Z"
        fill="#043003"
      />
    </svg>
  );
}
const FilterView: FC<{ onClose: () => void; open: boolean }> = ({
  onClose,
  open,
}) => {
  return (
    <div className={`mapbox-ctl-filters-content ${open ? "" : "hidden"}`}>
      <div className="position-sticky bg-white p-3 d-flex flex-row justify-content-start">
        <h2 className="heading-small fw-normal flex-grow-1">Filter by tag</h2>

        <button onClick={onClose} className="icon-btn" aria-label="Close">
          <i className="icon icon-close"></i>
        </button>
      </div>

      <div className="p-3 pt-0">
        {/* @ts-ignore */}
        <turbo-frame
          id="filters"
          target="_top"
          loading="lazy"
          src={`/_tags`}
          data-turbo-permanent=""
        />
      </div>
    </div>
  );
};

function FilterPopover() {
  const [open, setOpen] = useState(false);

  return (
    <div
      id="filter-popover"
      data-turbo-permanent
      aria-label={open ? undefined : "Show filters"}
      role={open ? undefined : "button"}
      className={`mapboxgl-ctrl-geocoder mapboxgl-ctrl overflow-hidden ${
        open
          ? "mapbox-ctl-filters"
          : "p-1 py-2 mapboxgl-ctrl-geocoder--collapsed text-center cursor-pointer"
      }`}
      onClick={open ? undefined : () => setOpen(true)}
    >
      <FilterView
        open={open}
        onClose={() => {
          setOpen(false);
        }}
      />
      {!open && <FilterIcon />}
    </div>
  );
}

export function FilterControl() {
  const map: mapboxgl.Map = useContext(MapContext);
  useEffect(() => {
    const control = new FilterControlRenderer();
    // @ts-ignore
    map?.addControl(control, "top-left");
    return () => void map?.removeControl(control as any);
  }, [map]);
  return null;
}
