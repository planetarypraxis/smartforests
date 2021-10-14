import React from 'react'
import { render } from 'react-dom'
import { Provider as StateContext } from 'jotai';
import { MapVisual } from './mapbox';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import { AtlasPage } from './pages';

function MapApp() {
  return (
    <Router>
      <StateContext>
        <MapVisual />
        <Route path='/map/:app/:model/:id'>
          <div className='position-absolute top-0 end-0 h-100 bg-white overflow-auto' style={{
            width: 360,
            boxShadow: '0px 0px 20px 0px #02630233'
          }}>
            <Link to='/map'>&larr; Map</Link>
            <AtlasPage />
          </div>
        </Route>
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