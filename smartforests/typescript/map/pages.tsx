import React, { Fragment, memo, useEffect, useRef } from 'react'
import { constructModelTypeName, pageToPath, initialPageURL, useWagtailSearch, Wagtail, TurboFrame, pageToFrameURL } from '../wagtail';
import { SmartForest } from './types';
import { Marker, Popup } from '@urbica/react-map-gl'
import { useFocusContext } from './state';
import { Link, useRouteMatch, useHistory } from 'react-router-dom';
import { useOffcanvas } from '../bootstrap';

export function AtlasPagesMapLayer() {
  return (
    <Fragment>
      <LogbookPageMarkers />
      <LogbookEntryPageMarkers />
      <StoryPageMarkers />
    </Fragment>
  )
}

export function LogbookPageMarkers() {
  const results = useWagtailSearch<SmartForest.LogbookPage>({
    type: 'logbooks.LogbookPage',
    limit: 1000
  })

  return (
    <Fragment>
      {results.data?.items?.filter(f => !!f.coordinates).map((page, i) => (
        <AtlasPageMarker key={i + page.id} page={page} />
      ))}
    </Fragment>
  )
}

export function LogbookEntryPageMarkers() {
  const results = useWagtailSearch<SmartForest.LogbookEntryPage>({
    type: 'logbooks.LogbookEntryPage',
    limit: 1000
  })

  return (
    <Fragment>
      {results.data?.items?.filter(f => !!f.coordinates).map((page, i) => (
        <AtlasPageMarker key={i + page.id} page={page} />
      ))}
    </Fragment>
  )
}

export function StoryPageMarkers() {
  const results = useWagtailSearch<SmartForest.StoryPage>({
    type: 'logbooks.StoryPage',
    limit: 1000
  })

  return (
    <Fragment>
      {results.data?.items?.filter(f => !!f.coordinates).map((page, i) => (
        <AtlasPageMarker key={i + page.id} page={page} />
      ))}
    </Fragment>
  )
}

export const AtlasPageMarker: React.FC<{ page: Wagtail.Item<SmartForest.GeocodedMixin> }> = memo(({ page }) => {
  const [isFocusing, setIsFocusing] = useFocusContext(page.id, page.meta.type)
  const history = useHistory()
  const [offcanvas] = useOffcanvas('sidepanel-offcanvas')

  return (
    <Fragment>
      <Marker
        longitude={page.coordinates.coordinates[0]}
        latitude={page.coordinates.coordinates[1]}
      >
        <a
          // data-bs-toggle="offcanvas"
          // data-bs-target="#sidepanel-offcanvas"
          data-turbo-action="advance"
          data-turbo-frame="sidepanel-turboframe"
          href={pageToFrameURL("sidepanel-turboframe", page, 'logbooks/sidepanel.html')}
          onMouseOver={() => setIsFocusing(true, 'map')}
          onMouseOut={() => setIsFocusing(false, 'map')}
          onClick={() => {
            // data-bs-toggle does not open/close things appropriately
            // data-bs-[*] attributes interfere with data-turbo-action
            // So we do this programatically instead.
            // An alternative would be to control this at the URL level, coordinated by some kind of routing library.
            offcanvas.show()
            // NB: Currently the TurboFrame sidepanel will not respond to back/forward navigation, so this is not in use.
            // Update the window URL to allow navigation back to this sidepanel on share/refresh.
            // (supported by server-side rendering at smartforests.models.MapPage.subpages).
            // (There is an open PR to do this via data-turbo-[attr] at https://github.com/hotwired/turbo/pull/167 / https://github.com/hotwired/turbo/pull/398)
            //
            // history.push(pageToPath(page))
          }}
        >
          <div
            className='cursor-pointer absolute bg-bright-yellow rounded-circle'
            style={{ transform: 'translate(-50%, -50%)', width: '15px', height: '15px' }}
          />
        </a>
      </Marker>
      {isFocusing && (
        <Popup
          className='mapbox-invisible-popup'
          longitude={page?.coordinates?.coordinates[0]}
          latitude={page?.coordinates?.coordinates[1]}
          offset={20}
        >
          <Link to={pageToPath(page)}>
            <div className='d-block p-2 rounded-1 bg-white' style={{ width: 250 }}>
              <AtlasPageCard page={page} />
            </div>
          </Link>
        </Popup>
      )}
    </Fragment>
  )
})

function AtlasPageCard({ page }: { page: Wagtail.Item<SmartForest.GeocodedMixin> }) {
  return (
    <div className='row gy-1'>
      <div className='caption text-muted'>{page.label}</div>
      <div className='fs-6 text-dark-green fw-bold'>{page.title}</div>
      {!!page.geographical_location && (
        <div className='caption text-muted'>{page.geographical_location}</div>
      )}
    </div>
  )
}