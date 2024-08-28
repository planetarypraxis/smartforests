import * as d3 from "https://cdn.skypack.dev/d3@7.9.0";
import "https://cdn.skypack.dev/d3-force@3.0.0";
import forceBoundary from "https://cdn.skypack.dev/d3-force-boundary@0.0.1";

let initialOffCanvasContent = "";
document.addEventListener("turbo:load", () => {
  initTagCloud();
});
document.addEventListener("turbo:frame-load", (e) => {
  if (e.target && e.target.getAttribute("id") === "tagcloud-turboframe") {
    initTagCloud();
  }
});

function initTagCloud() {
  document.querySelectorAll("[data-tag-cloud-data]").forEach(($parent) => {
    const dataElementId = $parent.getAttribute("data-tag-cloud-data");
    const $data = document.getElementById(dataElementId);
    if (!$data) {
      return;
    }

    const tagOffCanvasId = $parent.getAttribute("data-tag-offcanvas");
    let tagOffcanvas = null;
    if (tagOffCanvasId) {
      tagOffcanvas = document.getElementById(tagOffCanvasId);
    }
    if (!initialOffCanvasContent) {
      initialOffCanvasContent = tagOffcanvas?.innerHTML || "";
    }

    // Specify the dimensions of the chart.
    const { width, height } = calculateCanvasDimensions();
    const data = JSON.parse(document.getElementById(dataElementId).innerText);

    const $container = document.createElement("div");
    $container.setAttribute("id", new Date().toISOString());
    $parent.innerHTML = "";
    $parent.appendChild($container);

    doTagCloud($container, width, height, data, tagOffcanvas);

    window.addEventListener("resize", () => {
      const { width, height } = calculateCanvasDimensions();
      doTagCloud($container, width, height, data, tagOffcanvas);
    });
  });
}

function calculateCanvasDimensions() {
  const width = window.innerWidth;
  let height = window.innerHeight;

  const nav = document.querySelector("nav");
  height -= nav.getBoundingClientRect().height;

  const radio = document.querySelector("#radioPlayer");
  height -= radio.getBoundingClientRect().height;

  return { width, height };
}

function doTagCloud($container, width, height, data, tagOffcanvas) {
  const margin = 50; 
  $container.innerHTML = "";

  let focusedNode = null;

  // Specify the color scale.
  const interpolateColors = d3.interpolateRgbBasis([
    "#C7EAC6",
    "#71B340",
    "#026302",
  ]);

  const color = d3.scaleSequential(interpolateColors);

  // The force simulation mutates links and nodes, so create a copy
  // so that re-evaluating this function
  const links = data.links.map((d) => ({ ...d }));
  const nodes = data.nodes.map((d) => ({ ...d }));
  nodes.sort(() => (Math.random() < 0.5 ? -1 : 1));

  const maxCount = data.max_count;

  const simulation = d3.forceSimulation(nodes)
  .force(
    "link",
    d3.forceLink(links).id((d) => d.id)
  )
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(30));

  // Apply boundary force only on medium screens up
  if (width > 768) {
    simulation.force("boundary", forceBoundary(margin, margin, width - margin, height - margin));
  }

simulation.on("tick", draw);


  // Create the canvas.
  const dpi = devicePixelRatio; // _e.g._, 2 for retina screens
  const canvas = d3
    .create("canvas")
    .attr("width", dpi * width)
    .attr("height", dpi * height)
    .attr("style", `width: ${width}px; max-width: 100%; height: auto;`)
    .node();

  const context = canvas.getContext("2d");
  context.scale(dpi, dpi);
  context.font = "12px Monaco";

  function draw() {
    context.clearRect(0, 0, width, height);

    drawBackground();
    drawNodes(nodes);
  }

  function drawBackground() {
    context.save();
    context.fillStyle =  "rgba(31, 107, 31, 0.2)"
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.restore();

    const heatSquareSize = 50;
    const heatSquareStep = heatSquareSize / 2;
    const widths = new Array(Math.ceil(canvas.width / heatSquareStep))
      .fill(0)
      .map((_, i) => i * heatSquareStep);
    const heights = new Array(Math.ceil(canvas.height / (heatSquareSize / 2)))
      .fill(0)
      .map((_, i) => i * heatSquareStep);

    context.save();
    for (const width of widths) {
      for (const height of heights) {
        const count = nodes.reduce((c, node) => {
          if (
            node.x >= width &&
            node.x < width + heatSquareSize &&
            node.y >= height &&
            node.y < height + heatSquareSize
          ) {
            return c + 1;
          }
          return c;
        }, 0);
        if (count > 0) {
          context.globalAlpha = 0.1;
          context.fillStyle = color(1 - count / 5);
          context.fillRect(width, height, heatSquareSize, heatSquareSize);
        }
      }
    }
    context.restore();
  }

  function drawNodes(nodes) {
    const padding = 8;

    context.save();
    context.strokeStyle = "#fff";
    context.globalAlpha = 1;

    nodes.forEach((node) => {
      drawNode(node);
    });

    // Keep track of expanded nodes to prevent overlap
    const expandedNodes = {};
    const overlapPadding = 32;
    nodes.forEach((node) => {
      const text = node.name.toUpperCase();
      const textWidth = context.measureText(text).width;

      node.top = node.y - padding;
      node.bottom = node.y + padding;

      if (node.x + textWidth + padding <= width) {
        node.left = node.x - padding * 2;
        node.right = node.x + textWidth + padding * 2;
      } else {
        node.left = node.x - textWidth - padding * 2;
        node.right = node.x + padding + padding * 2;
      }

      node.overlapLeft = node.left - overlapPadding;
      node.overlapRight = node.right + overlapPadding;
      node.overlapTop = node.y - overlapPadding;
      node.overlapBottom = node.y + overlapPadding;

      const overlaps = Object.keys(expandedNodes).filter((id) => {
        const expandedNode = expandedNodes[id];
        if (
          node.overlapRight >= expandedNode.overlapLeft &&
          node.overlapLeft <= expandedNode.overlapRight &&
          node.overlapBottom >= expandedNode.overlapTop &&
          node.overlapTop <= expandedNode.overlapBottom
        ) {
          return true;
        }
      });

      if (!overlaps.length) {
        expandedNodes[node.id] = node;
        node.expanded = true;
        // Draw focused node at the end
        if (node.id !== focusedNode?.id) {
          drawLabelContainer(node.x, node.y, textWidth, padding);
          drawLabel(node.x, node.y, text, textWidth, padding);
        }
      } else {
        node.expanded = false;
      }
    });

    nodes.forEach((node) => {
      // Make sure node circle is on top of the label
      // Draw focused node at the end (below)
      if (expandedNodes[node.id] && node.id !== focusedNode?.id) {
        drawNode(node);
      }
    });

    if (focusedNode) {
      // Make sure focused node is on top of everything
      focusedNode.expanded = true;
      const text = focusedNode.name.toUpperCase();
      const textWidth = context.measureText(text).width;
      drawLabelContainer(
        focusedNode.x,
        focusedNode.y,
        textWidth,
        padding,
        true
      );
      drawLabel(focusedNode.x, focusedNode.y, text, textWidth, padding, true);
      drawNode(focusedNode);
    }

    context.restore();
  }

  function drawLabelContainer(x, y, textWidth, padding, invert = false) {
    context.save();

    context.strokeStyle = "#fff";
    context.globalAlpha = 0.8;
    context.fillStyle = invert ? "#043003" : "#fff";

    context.beginPath();

    // Draw to the right of the node if fits on screen
    if (x + textWidth + padding <= width) {
      context.arc(x, y, padding, Math.PI / 2, (3 * Math.PI) / 2);
      context.lineTo(x + textWidth + padding, y - padding);
      context.arc(
        x + textWidth + padding,
        y,
        padding,
        (3 * Math.PI) / 2,
        Math.PI / 2
      );
      context.lineTo(x, y + padding);
    }
    // Otherwise draw to the left of the node
    else {
      context.arc(x, y, padding, (3 * Math.PI) / 2, Math.PI / 2);
      context.lineTo(x - textWidth - padding, y + padding);
      context.arc(
        x - textWidth - padding,
        y,
        padding,
        Math.PI / 2,
        (3 * Math.PI) / 2
      );
      context.lineTo(x, y - padding);
    }

    context.fill();
    context.stroke();
    context.restore();
  }

  function drawNode(node) {
    context.globalAlpha = 1;
    context.strokeStyle = "#fff";
    context.fillStyle = color(1 - node.count / maxCount);
    context.beginPath();
    context.moveTo(node.x + 5, node.y);
    context.arc(node.x, node.y, 5, 0, 2 * Math.PI);
    context.fill();
    context.stroke();
  }

  function drawLabel(x, y, text, textWidth, padding, invert = false) {
    context.fillStyle = invert ? "#fff" : "#026302";
    if (x + textWidth + padding <= width) {
      context.fillText(text, x + 10, y + 4);
    } else {
      context.fillText(text, x - textWidth - 10, y + 4);
    }
  }

  // Add a drag behavior. The _subject_ identifies the closest node to the pointer,
  // conditional on the distance being less than 20 pixels.
  d3.select(canvas).call(
    d3
      .drag()
      .subject((event) => {
        const [px, py] = d3.pointer(event, canvas);
        return d3.least(nodes, ({ x, y }) => {
          const dist2 = (x - px) ** 2 + (y - py) ** 2;
          if (dist2 < 400) return dist2;
        });
      })
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended)
  );

  // Reheat the simulation when drag starts, and fix the subject position.
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  // Update the subject (dragged node) position during drag.
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  // Restore the target alpha so the simulation cools after dragging ends.
  // Unfix the subject position now that it’s no longer being dragged.
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  const findFocusedNode = (px, py) => {
    for (const node of nodes) {
      if (
        node.expanded &&
        node.left <= px &&
        node.right >= px &&
        node.top <= py &&
        node.bottom >= py
      ) {
        return node;
      }
    }

    return d3.least(nodes, ({ x, y }) => {
      const dist2 = (x - px) ** 2 + (y - py) ** 2;
      if (dist2 < 400) return dist2;
    });
  };

  canvas.addEventListener("mousemove", (event) => {
    const [px, py] = d3.pointer(event, canvas);

    let hoveredNode = findFocusedNode(px, py);
    if (hoveredNode) {
      canvas.style.cursor = "pointer";
      focusedNode = hoveredNode;
    } else {
      canvas.style.removeProperty("cursor");
      focusedNode = null;
    }
    draw();
  });

  canvas.addEventListener("click", (event) => {
    const [px, py] = d3.pointer(event, canvas);
    const node = findFocusedNode(px, py);
    if (node && tagOffcanvas) {
      // Show loading indicator
      tagOffcanvas.innerHTML = initialOffCanvasContent;
      window.Turbo.visit(`/${getLanguageCode()}/_tags/${node.slug}/`, {
        frame: "tagpanel-turboframe",
      });
      const tagOffcanvasInstance =
        bootstrap.Offcanvas.getInstance(tagOffcanvas) ||
        new bootstrap.Offcanvas(tagOffcanvas);
      tagOffcanvasInstance.show();
    }
  });

  $container.appendChild(canvas);
}

function getLanguageCode() {
  return window.LANGUAGE_CODE || "en";
}
