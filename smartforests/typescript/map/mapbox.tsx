import React from 'react'
import MapGL, { MapContext, Marker, Popup, NavigationControl, GeolocateControl } from '@urbica/react-map-gl'
import { WebMercatorViewport } from '@math.gl/web-mercator';
import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';
import mapboxgl from 'mapbox-gl';
import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useContext, useEffect, useRef, useState } from 'react';

export function MapVisual({ className }: { className?: string }) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const [viewport, setViewport] = useState({
    latitude: 0,
    longitude: 0,
    zoom: 2
  })

  return (
    <div ref={mapContainerRef} className={className}>
      <MapGL
        accessToken={process.env.MAPBOX_API_PUBLIC_TOKEN}
        mapStyle='mapbox://styles/smartforests/ckuquky9r2o3v18lkxddvri76'
        style={{ width: '100%', height: '80vh' }}
        viewportChangeMethod='flyTo'
        {...viewport}
        onViewportChange={setViewport}
      >
        {/* <NavigationControl showCompass showZoom position='top-left' />
        <GeolocateControl position='top-left' /> */}
        <GeocodeControl position='top-left' accessToken={process.env.MAPBOX_API_PUBLIC_TOKEN} />
      </MapGL>
      <div className='position-absolute bottom-0 end-0 me-3 mb-5 p-4 bg-white opacity-75'>
        <pre className='font-monospace mono monospace'>{JSON.stringify(viewport, null, 2)}</pre>
      </div>
    </div>
  )
}

function GeocodeControl({ position, accessToken }: {
  accessToken: string,
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right',
}) {
  const map: mapboxgl.Map = useContext(MapContext)

  useEffect(() => {
    const control = new MapboxGeocoder({
      accessToken,
      mapboxgl
    })

    map?.addControl(
      control as any,
      position
    )

    return () => {
      map?.removeControl(control as any)
    }
  }, [map, position])

  return null
}