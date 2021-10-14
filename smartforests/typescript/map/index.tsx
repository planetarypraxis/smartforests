import React from 'react'
import { render } from 'react-dom'
import { Provider as StateContext } from 'jotai';
import { MapVisual } from './mapbox';

function MapApp() {
  return (
    <StateContext>
      <MapVisual />
    </StateContext>
  )
}

export function main() {
  const rootNode = document.getElementById('MAP_APP')
  if (rootNode) {
    render(<MapApp />, rootNode)
  }
}