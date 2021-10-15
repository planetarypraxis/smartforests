import React, { Fragment, memo } from 'react'
import { constructModelTypeName, pageToPath, useWagtailSearch, Wagtail } from '../wagtail';
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
  const { app, model, id } = useParams<{ app: string, model: string, id: string }>()
  const pageSearch = useWagtailSearch<SmartForest.LogbookPage>({ id: parseInt(id), type: constructModelTypeName(app, model) })
  const page = pageSearch.data?.items?.[0]
  return (
    <div className='w-100 h-100 bg-white'>
      {!!page ? (
        <div className='container row gy-1 py-3'>
          <div className='caption text-muted'>{page.meta.type}</div>
          <div className='fs-6 text-dark-green fw-bold'>{page.title}</div>
          {!!page.geographical_location && (
            <div className='caption text-muted'>{page.geographical_location}</div>
          )}
          <div>
            {page.tags.map(tag => (
              <span className='badge rounded-pill bg-offwhite text-mid-green caption align-baseline mx-1'>
                {tag}
              </span>
            ))}
          </div>
          <hr className='mx-2 mt-3 mb-2' />
          <div className='py-2' dangerouslySetInnerHTML={{ __html: page.description }} />
        </div>
      ) : (
        "Loading"
      )}
    </div>
  )
}