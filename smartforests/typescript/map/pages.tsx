import React, { Fragment, memo } from 'react'
import { useWagtailSearch, Wagtail } from '../wagtail';
import { SmartForest } from './types';
import { Marker, Popup } from '@urbica/react-map-gl'
import { useFocusContext } from './state';
import { Link, useParams } from 'react-router-dom';

export function AtlasPagesMapLayer() {
  const results = useWagtailSearch<SmartForest.LogbookPage>({
    type: 'logbooks.LogbookPage',
    limit: 1000
  })

  return (
    <Fragment>
      {results.data?.items?.filter(f => !!f.coordinates).map(page => (
        <AtlasPageMarker key={page.id} page={page} />
      ))}
    </Fragment>
  )
}

export const AtlasPageMarker: React.FC<{ page: Wagtail.Item<SmartForest.LogbookPage> }> = memo(({ page }) => {
  const [isFocusing, setIsFocusing] = useFocusContext(page.id, page.meta.type)

  return (
    <Fragment>
      <Marker
        longitude={page.coordinates.coordinates[0]}
        latitude={page.coordinates.coordinates[1]}
      >
        <Link
          to={`/map/${page.meta.type}/${page.id}`}
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
          <Link to={`/map/${page.meta.type}/${page.id}`}>
            <div className='d-block p-2 rounded-1 bg-white' style={{ width: 250 }}>
              <AtlasPageCard page={page} />
            </div>
          </Link>
        </Popup>
      )}
    </Fragment>
  )
})

function AtlasPageCard({ page }: { page: Wagtail.Item<SmartForest.LogbookPage> }) {
  return (
    <div className='row gy-1'>
      <div className='caption text-muted'>{page.meta.type}</div>
      <div className='fs-6 text-dark-green fw-bold'>{page.title}</div>
      {!!page.geographical_location && (
        <div className='caption text-muted'>{page.geographical_location}</div>
      )}
    </div>
  )
}

export function AtlasPage() {
  const { type, pageId } = useParams<{ type: string, pageId: string }>()
  const page = useWagtailSearch({ id: parseInt(pageId), type })
  return (
    <div className='w-100 h-100'>
      <h1>{pageId}</h1>
      <pre className='font-monospace'>
        {JSON.stringify(page.data, null, 2)}
      </pre>
    </div>
  )
}