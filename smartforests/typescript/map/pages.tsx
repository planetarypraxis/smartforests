import React, { Fragment, memo } from 'react'
import { useWagtailSearch, Wagtail } from '../wagtail';
import { SmartForest } from './types';
import { Marker, Popup } from '@urbica/react-map-gl'
import { useFocusContext } from './state';

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
        <div
          // href={`/pages/inspect/${page.properties.id}`}
          className='cursor-pointer absolute bg-bright-yellow rounded-circle'
          style={{ transform: 'translate(-50%, -50%)', width: '15px', height: '15px' }}
          onMouseOver={() => setIsFocusing(true, 'map')}
          onMouseOut={() => setIsFocusing(false, 'map')}
        >
        </div>
      </Marker>
      {isFocusing && (
        <Popup
          className='mapbox-invisible-popup'
          longitude={page?.coordinates?.coordinates[0]}
          latitude={page?.coordinates?.coordinates[1]}
          offset={20}
        >
          <div
            // href={`/pages/inspect/${page.properties.id}`}
            style={{ width: 250 }}
            className='d-block p-2 rounded-1 bg-white'>
            <AtlasPageCard page={page} />
          </div>
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