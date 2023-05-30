import { useAtomValue } from "jotai/utils";
import React, { FC, Fragment, useEffect, useRef, useState } from "react";
import { languageCodeAtom } from "../pageContext";
import { MapViewport, useFeatures } from "./data";
import { AtlasPageMarker, ClusterMarker } from "./markers";
import { stringifyQuery, useFilterParam } from "./state";
import { SmartForest } from "./types";

export const AtlasPageFeatureLayer: FC<{
  size: DOMRectReadOnly;
  viewport: MapViewport;
}> = ({ size, viewport }) => {
  const tag = useFilterParam();

  // @ts-ignore
  const languageCode = useAtomValue(languageCodeAtom)

  const data = useFeatures<SmartForest.MapItem>(
    size,
    viewport,
    () => ({ tag, languageCode }),
    [tag, languageCode]
  );

  if (!data) {
    return (
      <div
      className="mapbox-loading-overlay position-absolute w-100 h-100 d-flex align-items-center justify-content-center">
      <div className="spinner-border" role="status">
        <span className="sr-only">Loading...</span>
      </div>
    </div>
    );
  }

  return (
    <Fragment>
      {data.map((feature) => {
        if (!feature.geometry) {
          return;
        }

        const properties = feature.properties;

        if (properties.cluster) {
          return (
            <ClusterMarker
              key={"cluster:" + properties.cluster_id}
              feature={{ ...feature, properties }}
            />
          );
        }

        const featureProperties = feature.properties as SmartForest.MapItem;

        return (
          <AtlasPageMarker
            key={"page:" + featureProperties.id}
            feature={{ ...feature, properties: featureProperties }}
          />
        );
      })}
    </Fragment>
  );
};