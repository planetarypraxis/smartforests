import { Feature, Point } from "geojson";
import React, { FC, Fragment } from "react";
import { Cluster, MapViewport, useClusteredMapData } from "./data";
import { AtlasPageMarker, ClusterMarker } from "./markers";
import { stringifyQuery, useFilterParam } from "./state";
import { SmartForest } from "./types";

export const AtlasPageFeatureLayer: FC<{
  size: DOMRectReadOnly;
  viewport: MapViewport;
}> = ({ size, viewport }) => {
  const tag = useFilterParam();

  const data = useClusteredMapData<SmartForest.MapItem>(
    size,
    viewport,
    () => getFeaturesUrl({ tag }),
    [tag]
  );

  if (!data) {
    return null;
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
            key={"page:" + featureProperties.page.id}
            feature={{ ...feature, properties: featureProperties }}
          />
        );
      })}
    </Fragment>
  );
};

const getFeaturesUrl = (opts: { tag?: string }) => {
  const q = stringifyQuery({
    ...(opts.tag ? { tag: opts.tag } : {}),
  });

  return [window.location.host, "/api/v2/geo/", q ? "?" : ""].join("");
};
