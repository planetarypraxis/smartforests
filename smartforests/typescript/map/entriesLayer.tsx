import React, { Fragment, memo } from 'react'
import { useWagtailSearch } from '../wagtail';
import { SmartForest } from './types';
import { Marker, Popup } from '@urbica/react-map-gl'

export function AtlasEntriesMapLayer() {
  const results = useWagtailSearch<SmartForest.LogbookPage>({
    type: 'logbooks.LogbookPage',
    limit: 1000
  })

  return (
    <Fragment>
      {results.data?.items?.filter(f => !!f.coordinates).map(page => (
        <AtlasEntryMarker key={page.id} page={page} />
      ))}
    </Fragment>
  )
}

export const AtlasEntryMarker: React.FC<{ page: SmartForest.LogbookPage }> = memo(({ page }) => {
  // const [isHovering, setIsHovering] = useHoverContext(page.properties.id, 'page')

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
        // onMouseOver={() => setIsHovering(true, 'map')}
        // onMouseOut={() => setIsHovering(false, 'map')}
        >
        </div>
      </Marker>
      {/* {isHovering && (
        <Popup
          className='mapbox-invisible-popup max-w-2xl'
          longitude={page?.geometry?.coordinates[0]}
          latitude={page?.geometry?.coordinates[1]}
          offset={20}
        >
          <A
            href={`/pages/inspect/${page.properties.id}`}
            className='block p-2 rounded-lg bg-white'>
            <pageCard page={page.properties} />
          </A>
        </Popup>
      )} */}
    </Fragment>
  )
})
