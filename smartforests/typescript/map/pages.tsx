import React, { Fragment, memo, useEffect, useRef } from 'react'
import { constructModelTypeName, pageToPath, initialPageURL, useWagtailSearch, Wagtail, TurboFrame } from '../wagtail';
import { SmartForest } from './types';
import { Marker, Popup } from '@urbica/react-map-gl'
import { useFocusContext } from './state';
import { Link, useRouteMatch, useHistory } from 'react-router-dom';
import type { Offcanvas } from 'bootstrap';

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

  return (
    <Fragment>
      <Marker
        longitude={page.coordinates.coordinates[0]}
        latitude={page.coordinates.coordinates[1]}
      >
        <Link
          to={pageToPath(page)}
          onMouseOver={() => setIsFocusing(true, 'map')}
          onMouseOut={() => setIsFocusing(false, 'map')}
        >
          <div
            className='cursor-pointer absolute bg-bright-yellow rounded-circle'
            style={{ transform: 'translate(-50%, -50%)', width: '15px', height: '15px' }}
          />
        </Link>
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

export function Sidepanel() {
  const history = useHistory()
  const { params: { app, model, id } } = useRouteMatch<{ app: string, model: string, id: string }>('/map/:app?/:model?/:id?')
  const pageSearch = useWagtailSearch<SmartForest.LogbookPage>({ id: parseInt(id), type: constructModelTypeName(app, model) })
  const page = pageSearch.data?.items?.[0]

  const offcanvasMapId = 'offcanvasMap'
  const offcanvasElement = useRef<HTMLElement>()
  const offcanvas = useRef<Offcanvas>()

  useEffect(() => {
    offcanvasElement.current ??= document.getElementById(offcanvasMapId)
    // @ts-ignore
    offcanvas.current ??= new bootstrap.Offcanvas(offcanvasElement.current)
    offcanvasElement.current?.addEventListener('hide.bs.offcanvas', function () {
      return history.push(initialPageURL().pathname)
    })
  }, [])

  useEffect(() => {
    if (page) {
      return offcanvas.current?.show()
    } else {
      return offcanvas.current?.hide()
    }
  }, [page])

  return <div
    className="offcanvas offcanvas-end flex flex-column h-100 overflow-hidden"
    tabIndex={-1}
    id={offcanvasMapId}
    aria-labelledby="offcanvasMapTitle"
    data-bs-scroll="true"
    data-bs-backdrop="false"
  >
    <div className='container gx-2 py-2 bg-warning' style={{
      mixBlendMode: 'multiply',
    }}>
      <button type="button" className="btn btn-link text-reset text-decoration-none" data-bs-dismiss="offcanvas" aria-label="Close">
        <span className='pe-2'>&larr;</span>
        <span className='border-bottom border-1 pb-1 border-dark-green'>Close</span>
      </button>
    </div>
    <div className='overflow-auto h-100'>
      {!!page ? (
        <TurboFrame id='metadata' page={page} template='logbooks/sidepanel.html' />
      ) : (
        <Fragment>
          <div className='offcanvas-header container gy-1 gx-3 py-3'>
            Loading
          </div>
          <div className='offcanvas-body container gy-1 gx-3 py-3'></div>
        </Fragment>
      )}
    </div>
  </div>
}