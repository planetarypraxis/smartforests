import React from 'react'
import { render } from 'react-dom'
import { Provider as StateContext } from 'jotai';
import { MapVisual } from './mapbox';
import {
  BrowserRouter as Router,
  Route
} from "react-router-dom";

function MapApp() {
  return (
    <Router>
      <StateContext>
        <MapVisual />
      </StateContext>
    </Router>
  )
}

export function main() {
  const rootNode = document.getElementById('MAP_APP')
  if (rootNode) {
    render(<MapApp />, rootNode)
  }
}