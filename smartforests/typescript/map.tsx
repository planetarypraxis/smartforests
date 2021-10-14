import React from 'react'
import { render } from 'react-dom'

function MapApp() {
  return (
    <div>
      Map goes here.
    </div>
  )
}

export function main() {
  const rootNode = document.getElementById('MAP_APP')
  if (rootNode) {
    render(<MapApp />, rootNode)
  }
}