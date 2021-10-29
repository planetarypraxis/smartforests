import React, { FC, Fragment } from "react";
import { MapViewport, useMapData } from "./data";
import { AtlasPageMarker } from "./markers";
import { stringifyQuery, useFilterParam } from "./state";
import { SmartForest } from "./types";

export const AtlasPageFeatureLayer: FC<{
  size: DOMRectReadOnly;
  viewport: MapViewport;
}> = ({ size, viewport }) => {
  const tag = useFilterParam();
  const data = useMapData<SmartForest.MapItem>(
    size,
    viewport,
    () =>
      "/api/v2/geo/?" +
      stringifyQuery({
        tag,
      }),
    [tag]
  );

  if (!data) {
    return null;
  }

  return (
    <Fragment>
      {data.features.map((feature) => {
        if (!feature.geometry) {
          return;
        }

        return (
          <AtlasPageMarker key={feature.properties.page.id} feature={feature} />
        );
      })}
    </Fragment>
  );
};
