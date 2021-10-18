import React from 'react'
import { render } from 'react-dom'
import { Provider as StateContext } from 'jotai';
import { MapVisual } from './mapbox';
import {
  BrowserRouter as Router,
  Route,
  Link
} from "react-router-dom";
import { AtlasPage } from './pages';
import { pageURL } from '../wagtail';

function MapApp() {
  return (
    <Router>
      <StateContext>
        <MapVisual />
        <Route path='/map/:app/:model/:id'>
          <div className='position-absolute top-0 end-0 h-100 overflow-auto' style={{
            width: 360,
            boxShadow: '0px 0px 20px 0px #02630233'
          }}>
            <div className='container opacity-50 py-3 bg-dark-green-transparent bg-md-white' style={{
              mixBlendMode: 'multiply',
            }}>
              <div className='row gy-1'>
                <Link to={pageURL().pathname} className='text-decoration-none'>
                  <span className='text-white'>&larr;</span>
                  <span className='text-white text-decoration-underline'>Map</span>
                </Link>
              </div>
            </div>
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