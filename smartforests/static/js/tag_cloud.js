import webcola from "https://cdn.skypack.dev/webcola";
import * as d3 from "https://cdn.skypack.dev/d3@7.6";
import * as chroma from "https://cdn.skypack.dev/chroma-js";
import debounce from "https://cdn.skypack.dev/lodash.debounce";
import uniqBy from "https://cdn.skypack.dev/lodash.uniqby";
import * as StackBlur from "https://cdn.skypack.dev/stackblur-canvas@2.5"

function getPageElements() {
  const parentEl = document.querySelector("[data-tag-cloud-data]")
  if (!parentEl) return
  const dict = Object.entries(parentEl.dataset).reduce((dict, [key, value]) => {
    dict[key] = value ? document.getElementById(value) : null
    return dict
  }, {})
  dict.tagOffcanvasInstance = bootstrap.Offcanvas.getInstance(dict.tagOffcanvas) || new bootstrap.Offcanvas(dict.tagOffcanvas);
  return dict
}

// Re-layout on window resize
let resizeHandlers = [];
window.addEventListener("resize", () => {
  resizeHandlers.forEach((fn) => fn());
});

// Manage highlighted tag state

let selectedTag = null

function isTagSelected(slug) {
  if (slug) {
    return selectedTag === slug
  } else {
    return !!selectedTag
  }
}

function setSelectedTag(slug) {
  if (slug) {
    selectedTag = slug
  } else {
    selectedTag = null
  }
  syncState()
}

function resetSelectedTag() {
  if (!isTagSelected()) return
  setSelectedTag(null)
}

function showTagSidepanel() {
  const elements = getPageElements()
  if (!elements || !elements.tagOffcanvasInstance) return
  elements.tagOffcanvasInstance.show();
}

function hideTagSidepanel() {
  const elements = getPageElements()
  if (!elements || !elements.tagOffcanvasInstance) return
  elements.tagOffcanvasInstance.hide();
}

// Offcanvas close handler should update state

window.addEventListener('hide.bs.offcanvas', e => {
  const elements = getPageElements()
  if (!elements || !elements.tagOffcanvas || e.target.id !== elements.tagOffcanvas.id) return
  resetSelectedTag()
})

// Sync the tag / sidepanel state on first load

function syncState() {
  if (isTagSelected()) {
    showTagSidepanel()
  } else {
    hideTagSidepanel()
  }
  updateSelectedTagStyle()
}

window.addEventListener('turbo:visit', () => {
  selectedTag = false
  syncState()
})

syncState()

// Styling derived from state

function tagStyleFn(d) {
  if (!d) return ''
  return d.fixed ? "layout-tag" : `related-tag fade-in ${isTagSelected(d.slug) && 'related-tag--selected'}`
}

function updateSelectedTagStyle() {
  d3.selectAll('.related-tag').attr('class', tagStyleFn)
}

export const getLanguageCode = () => {
  try {
    const requestInfoElement = document.getElementById('request-info')
    if (!requestInfoElement) throw new Error("Request info was not provided by Django")
    const { languageCode } = JSON.parse(requestInfoElement.innerHTML)
    if (!languageCode || typeof languageCode !== 'string') throw new Error("Language code was not defined")
    return languageCode
  } catch (e) {
    // In case of malformed JSON
    return 'en'
  }
}

const init = () => {
  const languageCode = getLanguageCode()

  // Downsample the canvas to produce the pixelated effect.
  const DEBUG_NETWORK = false;
  const PIXEL_SIZE = DEBUG_NETWORK ? 1 : 12;
  const MOBILE_BREAKPOINT = 540;
  const GRID_BORDERS = false;

  // Color configs for the background.
  const GRADIENT_LINE = '#B9FFA6';
  const GRADIENT_LIME = '#8DFF85';
  const GRADIENT_INNER = "#63E364";
  const GRADIENT_MIDDLE = "#4A964A";
  const GRADIENT_OUTER = "#1F6B1F";
  const COLOR_SCALE = chroma.scale([GRADIENT_OUTER, GRADIENT_MIDDLE, GRADIENT_INNER, GRADIENT_LIME]);

  // Reset the resize handlers on navigation
  resizeHandlers = [];

  // Bind to data-tags
  $("[data-tag-cloud-data]").each((_, parentEl) => {
    const configElement = document.getElementById(
      parentEl.dataset.tagCloudData
    );

    if (!configElement) {
      console.error("No config element found for tag cloud");
      return;
    }

    // Get the sidepanel elements for navigation
    const sidepanelFrame = parentEl.dataset.tagFrame ?? "_top";

    parentEl.classList.add("tag-cloud");

    const el = d3
      .select(parentEl)
      .append("div")
      .attr("class", "tag-cloud-content")
      .node();

    el.style.backgroundColor = GRADIENT_OUTER;

    // Prepare the data for d3
    const rawData = JSON.parse(configElement.innerHTML);
    const nodes = uniqBy(rawData, "id");

    const nodeMap = d3.index(nodes, (x) => x.id);

    const links = nodes.flatMap((node) => {
      return node.links.flatMap((target) => {
        const targetNode = nodeMap.get(target);
        if (!targetNode) {
          return [];
        }

        return [
          {
            source: node.index,
            target: targetNode.index,
            value: targetNode.score,
          },
        ];
      });
    });

    // Canvas element for rendering the background 'elevation effect'
    /** @type HTMLCanvasElement */
    const canvas = d3
      .select(el)
      .append("canvas")
      .attr("class", "w-100 h-100 position-absolute")
      .attr("style", "image-rendering: crisp-edges;")
      .node();

    const ctx = canvas.getContext("2d");

    // Disable image smoothing soe we can achieve the pixelly effect
    ctx.msImageSmoothingEnabled = false;
    ctx.mozImageSmoothingEnabled = false;
    ctx.webkitImageSmoothingEnabled = false;
    ctx.imageSmoothingEnabled = false;

    const updateBackground = (nodes, links) => {
      if (!parentEl || !parentEl.isConnected) return

      /**
       * Set up the canvas
       */

      const ctxWidth = Math.floor(el.clientWidth / PIXEL_SIZE);
      const ctxHeight = Math.floor(el.clientHeight / PIXEL_SIZE);

      canvas.width = ctxWidth;
      canvas.height = ctxHeight;

      ctx.clearRect(0, 0, ctxWidth, ctxHeight);

      // Default dark green background
      ctx.fillStyle = COLOR_SCALE(0);
      ctx.fillRect(0, 0, ctxWidth, ctxHeight);

      /**
       * Node heat map
       */

      // Keeps a count of how many nodes have been in each cell during a "tick"
      for (const _GRID_SIZE of (new Array(30).fill(0).map((_, i) => (i + 1) * 6)).reverse()) {
        const GRID_SIZE = _GRID_SIZE / PIXEL_SIZE;
        var grid = d3.range(0, ctxHeight / GRID_SIZE).map(function () {
          return d3.range(0, ctxWidth / GRID_SIZE).map(function () { return 0 });
        });

        // Increment the counts
        nodes.forEach(function (d) {
          if (d.score !== undefined) {
            var row = Math.max(0, Math.min(Math.floor((d.y / PIXEL_SIZE) / GRID_SIZE), grid.length - 1));
            var col = Math.max(0, Math.min(Math.floor((d.x / PIXEL_SIZE) / GRID_SIZE), grid[0].length - 1));
            // console.log(row, col, d, grid)
            grid[row][col] += Math.max(0, Math.sqrt(d.score) * 0.05) || 0;
          }
        });

        // Max cell value, for normalizing
        var gridMax = d3.max(grid, function (row) {
          return d3.max(row);
        });

        // Draw the grid
        grid.forEach(function (row, i) {
          row.forEach(function (cell, j) {
            if (cell <= 0) return
            ctx.beginPath();
            ctx.fillStyle = COLOR_SCALE(cell / gridMax);
            ctx.rect(j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE);
            ctx.fill();
            ctx.closePath();
            if (GRID_BORDERS) {
              ctx.strokeStyle = 'white';
              ctx.strokeRect(j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE);
            }
          });
        });
      }

      /**
       * Draw lines between nodes
      */
      var linkMax = d3.max(links, l => l.value);
      const MIN_LINE_WIDTH = 1.5;
      const MAX_LINE_WIDTH = 25;
      links.slice().sort(
        (a, b) => a.value - b.value
      ).forEach((d) => {
        ctx.beginPath()
        ctx.strokeStyle = COLOR_SCALE(1)
        ctx.lineWidth = Math.max(MIN_LINE_WIDTH / PIXEL_SIZE, Math.min(MAX_LINE_WIDTH / PIXEL_SIZE,
          ((d.value / (linkMax ** 0.5))) * (MAX_LINE_WIDTH / PIXEL_SIZE)
        ))
        ctx.lineCap = 'round';
        ctx.moveTo(d.source.x / PIXEL_SIZE, d.source.y / PIXEL_SIZE);
        ctx.lineTo(d.target.x / PIXEL_SIZE, d.target.y / PIXEL_SIZE);
        ctx.closePath();
        ctx.stroke();
      });

      // Blur

      if (!DEBUG_NETWORK) {
        StackBlur.canvasRGB(canvas, 0, 0, ctxWidth, ctxHeight, 3);
      }

      // Then it is zoomed in by the PIXEL_SIZE ratio
      // without smoothing to achieve the pixelly effect
    };

    let usingMobileLayout = false;

    // Use webcola's constraint-based graph layout plugin for d3 to lay out the tags
    // ensuring that we respect the following constrants:
    //
    // * Related tags are close together
    // * Tags are all within the bounds of the tag area.
    // * Tags do not overlap.
    const layout = () => {
      const container = d3.select(el);
      const realGraphNodes = nodes.slice();

      // Define canvas boundaries
      const PADDING = responsive({
        "default": 15,
        "(min-width: 480px)": 25,
        "(min-width: 640px)": 50,
        "(min-width: 1024px)": 66
      })
      const width = Math.max(PADDING, el.clientWidth - (2 * PADDING));
      const height = Math.max(PADDING, el.clientHeight - (2 * PADDING));

      // Add boundary points in the top left / bottom right to constrain the other points
      // see: https://github.com/tgdwyer/WebCola/issues/139#issuecomment-136937699
      const fixedNodeProperties = { fixed: true, fixedWeight: 100000 };
      const pageBounds = { x: PADDING, y: PADDING, width, height };
      const topLeft = {
        ...fixedNodeProperties,
        x: pageBounds.x,
        y: pageBounds.y
      };
      const topLeftBoundary = realGraphNodes.push(topLeft) - 1;
      const bottomRight = {
        ...fixedNodeProperties,
        x: pageBounds.x + pageBounds.width,
        y: pageBounds.y + pageBounds.height,
      };
      const bottomRightBoundary = realGraphNodes.push(bottomRight) - 1;

      // Scroll reset
      if (window.innerWidth <= MOBILE_BREAKPOINT) {
        // Center the scroll position on entering mobile view

        if (!usingMobileLayout) {
          parentEl.scroll({
            left: Math.round(el.clientWidth / 2 - parentEl.clientWidth / 2),
            top: Math.round(el.clientHeight / 2 - parentEl.clientHeight / 2),
          });
        }

        usingMobileLayout = true;
      } else {
        usingMobileLayout = false;
      }

      // Render a tag for each node.
      const tags = container
        .selectAll(".related-tag")
        .data(realGraphNodes, (d) => d.slug)
        .join((enter) => {
          const a = enter
            .append("a")
            .attr("class", tagStyleFn)
            .attr("data-filter", (d) => d.slug)
            .attr("data-turbo-frame", sidepanelFrame)
            .attr("href", (d) => `/${languageCode}/_tags/${d.slug}/`)

          a.append("span").attr("class", "tag-handle");

          a.append("span")
            .attr("class", "tag-label")
            .text((node) => node.name)
            .attr("data-filter", (d) => d.slug)
            .on('click', (e) => {
              if (isTagSelected(e.target.dataset.filter)) {
                resetSelectedTag() // Toggle off
              } else {
                setSelectedTag(e.target.dataset.filter)
              }
            })

          return a;
        });

      const elements = tags.nodes();

      // This is used to initialize the tag locations on resize so that they start in the (scaled) same location as
      // before. Otherwise, they might start offscreen, which causes the layout algorithm to get stuck.
      let scaleFactor = el._prevBounds && [
        (1 / el._prevBounds[0]) * el.clientWidth,
        (1 / el._prevBounds[1]) * el.clientHeight,
      ];

      // Initialize constraints.
      const constraints = [];
      for (let i = 0; i < realGraphNodes.length; i++) {
        const nodeEl = elements[i];
        const node = realGraphNodes[i];

        // Use the tag element's pixel size to drive the layout algorithm's constraints for avoiding overlaps.
        node.width = nodeEl.clientWidth * 1;
        node.height = nodeEl.clientHeight * 1;

        // Preserve relative positions if we're resizing.
        if (scaleFactor && node.x && node.y) {
          node.x = scaleFactor[0] * node.x;
          node.y = scaleFactor[1] * node.y;
        }

        // Add constraints to prevent going offscreen
        constraints.push({
          axis: "x",
          type: "separation",
          left: topLeftBoundary,
          right: i,
          gap: 0,
        });
        constraints.push({
          axis: "y",
          type: "separation",
          left: topLeftBoundary,
          right: i,
          gap: 0,
        });
        constraints.push({
          axis: "x",
          type: "separation",
          left: i,
          right: bottomRightBoundary,
          gap: nodeEl.clientWidth,
        });
        constraints.push({
          axis: "y",
          type: "separation",
          left: i,
          right: bottomRightBoundary,
          gap: nodeEl.clientHeight,
        });
      }

      // If there's already an instance of the layout system (ie. after window resize), remove it so it doesn't
      // conflict with the new one
      if (el._cola) {
        el._cola.stop();
      }

      // Configure and start the layout
      // DOCS: https://ialab.it.monash.edu/webcola/

      /** @type {import('webcola').d3adaptor} */
      const d3adaptor = webcola.d3adaptor

      const cola = d3adaptor(d3)
        .nodes(realGraphNodes)
        .links(links)
        .size([width, height])
        .constraints(constraints)
        .jaccardLinkLengths(responsive({
          "default": 40,
          "(min-width: 640px)": 80,
          "(min-width: 1140px)": 90
        }), 0.7)
        .avoidOverlaps(true)
        .handleDisconnected(true)
        .start(15, 15, 15);

      // Store the things we need for re-layout
      el._prevBounds = [el.clientWidth, el.clientHeight];
      el._cola = cola;

      // Animate the layout.
      cola.on("tick", () => {
        requestAnimationFrame(() => {
          tags.style("transform", ({ x, y }) => {
            x = Math.max(pageBounds.x, Math.min(pageBounds.width, x))
            y = Math.max(pageBounds.y, Math.min(pageBounds.height, y))
            return `translate(${px(x)},${px(y)})`
          });
          updateBackground(realGraphNodes, links);
        })
      });

      // Stop animation after converged
      setTimeout(() => {
        cola.on("tick", null)
      }, 2000)

    };

    layout();
    resizeHandlers.push(debounce(layout, 200));
  });
};

const px = (val) => Math.round(val) + "px";

window.addEventListener("turbo:load", init);

init()


/**
 * @param {{ query: Number }} breakpointValues 
 */
function responsive(breakpointValues) {
  if (!breakpointValues) return 0
  const entries = Object.entries(breakpointValues)
  if (!entries.length) return 0
  let cascadeValue = entries[0][1]
  for (const [breakpoint, value] of entries) {
    if (breakpoint === 'default' || window.matchMedia(breakpoint).matches) {
      cascadeValue = value
    }
  }
  // Backup
  return cascadeValue
}