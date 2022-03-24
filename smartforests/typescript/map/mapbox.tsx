import "@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css";
import "mapbox-gl/dist/mapbox-gl.css";

import React, { FC } from "react";
import MapGL, { MapContext, NavigationControl } from "@urbica/react-map-gl";
import MapboxGeocoder from "@mapbox/mapbox-gl-geocoder";
import mapboxgl, { Evented } from "mapbox-gl";
import { useContext, useEffect, useRef, useState } from "react";
import * as ReactDOM from "react-dom";

import { useSize } from "./data";
import { AtlasPageFeatureLayer } from "./layers";
import { unmountComponentAtNode } from "react-dom";
import { useAtom } from "jotai";
import { viewportAtom } from "./state";
import { TurboURLParamsContextProvider, useTurboURLParams } from "../turbo";

const MAPBOX_TOKEN = document.getElementById("MAP_APP")?.dataset.mapboxToken;

export function MapVisual() {
  const [viewport, setViewport] = useAtom(viewportAtom);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const size = useSize(mapContainerRef);
  const [params, _] = useTurboURLParams()

  return (
    <div style={{ width: "100%", height: "100%" }} ref={mapContainerRef}>
      <MapGL
        {...viewport}
        accessToken={MAPBOX_TOKEN}
        mapStyle="mapbox://styles/smartforests/ckziehr6u001e14ohgl2brzlu"
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
        minZoom={0}
        maxZoom={16}
      >
        <NavigationControl showCompass={false} showZoom position='top-left' />
        <GeocodeControl position="top-left" accessToken={MAPBOX_TOKEN} />
        <FilterControl />
        <AtlasPageFeatureLayer size={size} viewport={viewport} />
      </MapGL>
      {!!params['filter'] && (
        <a href={window.location.pathname} className='d-none d-sm-block font-monospace bg-white selected-tag fs-7'>
          {params['filter']}
          <button className="icon-btn" aria-label="Close">
            {/* @ts-ignore */}
            <i className="icon icon-8 bg-mid-green icon-close ms-1"></i>
          </button>
        </a>
      )}
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
    ReactDOM.render(
      <TurboURLParamsContextProvider>
        <FilterPopover />
      </TurboURLParamsContextProvider>,
      this._container
    );
    return this._container;
  }

  onRemove() {
    if (this._container) {
      unmountComponentAtNode(this._container);
    }
  }
}

function FilterIcon({ className = "" }) {
  return (
    <svg
      width="24"
      height="16"
      viewBox="0 0 24 16"
      fill="none"
      className={`center-screen d-inline-block fade-inout ${className}`}
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
    <div
      className={`mapboxgl-ctrl-filters-content top-0 fade-inout p-3 ${open ? "" : "hidden"
        }`}
    >
      <div className="position-sticky top-0 bg-white d-flex flex-row justify-content-start pb-4">
        <h2 className="heading-small fw-bold flex-grow-1 font-sans-serif">Filter by tag</h2>

        <a href={window.location.pathname} className='font-monospace text-uppercase px-2 cursor-pointer'>
          Clear All
        </a>

        <button onClick={onClose} className="icon-btn" style={{ marginTop: -5 }} aria-label="Close">
          <i className="icon bg-dark icon-close"></i>
        </button>
      </div>

      <div>
        {/* @ts-ignore */}
        <turbo-frame
          id="filters"
          target="_top"
          loading="lazy"
          src={`/_filters/`}
        />
      </div>
    </div>
  );
};

function FilterPopover() {
  const [open, setOpen] = useState(false);
  const [params, _] = useTurboURLParams()

  return (
    <div
      id="filter-popover"
      aria-label={open ? undefined : "Show filters"}
      role={open ? undefined : "button"}
      className={`mapboxgl-ctrl mapboxgl-ctrl-filters fade-inout ${open ? "" : "mapboxgl-ctrl-filters--collapsed"
        }`}
      onClick={open ? undefined : () => setOpen(true)}
    >
      <FilterView
        open={open}
        onClose={() => {
          setOpen(false);
        }}
      />
      <FilterIcon className={open ? "hidden" : ""} />
      {!!params['filter'] && <div className='filter-counter bg-dark-green text-white'>1</div>}
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
