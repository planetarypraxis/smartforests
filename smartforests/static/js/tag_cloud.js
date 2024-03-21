import * as d3 from "https://cdn.skypack.dev/d3@7.9.0";
import "https://cdn.skypack.dev/d3-force@3.0.0";
import forceBoundary from "https://cdn.skypack.dev/d3-force-boundary@0.0.1";

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

  // Specify the dimensions of the chart.
  const { width, height } = calculateCanvasDimensions();
  const data = JSON.parse(document.getElementById(dataElementId).innerText);

  const $container = document.createElement("div");
  $parent.appendChild($container);

  doTagCloud($container, width, height, data, tagOffcanvas);

  window.addEventListener("resize", () => {
    const { width, height } = calculateCanvasDimensions();
    doTagCloud($container, width, height, data, tagOffcanvas);
  });
});

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
  $container.innerHTML = "";

  let focusedNodeId = null;

  // Specify the color scale.
  const color = d3.scaleSequential(d3.interpolateGreens);

  // The force simulation mutates links and nodes, so create a copy
  // so that re-evaluating this function
  const links = data.links.map((d) => ({ ...d }));
  const nodes = data.nodes.map((d) => ({ ...d }));
  const maxCount = data.max_count;

  // Create a simulation with several forces.
  const simulation = d3
    .forceSimulation(nodes)
    .force(
      "link",
      d3.forceLink(links).id((d) => d.id)
    )
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("boundary", forceBoundary(10, 20, width - 10, height - 20))
    .on("tick", draw);

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

  function draw() {
    context.clearRect(0, 0, width, height);
    context.font = "12px Arial";

    drawBackground();
    drawNodes(nodes);
  }

  function drawBackground() {
    context.save();
    context.fillStyle = "#1f6b1f";
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
          context.globalAlpha = 0.6;
          context.fillStyle = color(1 - count / 5);
          context.fillRect(width, height, heatSquareSize, heatSquareSize);
        }
      }
    }
    context.restore();
  }

  function drawLinks(links) {
    // Draw lines
    context.save();
    context.globalAlpha = 0.6;
    context.strokeStyle = "#999";
    context.beginPath();
    links.forEach((d) => {
      context.moveTo(d.source.x, d.source.y);
      context.lineTo(d.target.x, d.target.y);
    });
    context.stroke();
    context.restore();
  }

  function drawNodes(nodes) {
    const padding = 8;

    context.save();
    context.strokeStyle = "#fff";
    context.globalAlpha = 1;

    let focusedNode = null;
    nodes.forEach((node) => {
      drawNode(node);
      if (node.id === focusedNodeId) {
        focusedNode = node;
      }
    });

    // Keep track of expanded nodes to prevent overlap
    const expandedNodes = {};
    const covered = [];

    // Start with focused node as this should always be shown
    // if (focusedNode) {
    //   expandedNodes[focusedNodeId] = true;
    //   const text = focusedNode.name.toUpperCase();
    //   const textWidth = context.measureText(text).width;
    //   covered.push({
    //     left: focusedNode.x - padding,
    //     right: focusedNode.x + textWidth + padding,
    //     top: focusedNode.y - padding,
    //     bottom: focusedNode.y + padding,
    //   });
    // }

    nodes.forEach((node) => {
      const text = node.name.toUpperCase();
      const textWidth = context.measureText(text).width;

      let nodeBounds;
      if (node.x + textWidth + padding <= width) {
        nodeBounds = {
          left: node.x - padding,
          right: node.x + textWidth + padding,
          top: node.y - padding,
          bottom: node.y + padding,
        };
      } else {
        nodeBounds = {
          left: node.x - padding - textWidth,
          right: node.x + padding,
          top: node.y - padding,
          bottom: node.y + padding,
        };
      }

      const overlaps = covered.filter((c) => {
        if (
          nodeBounds.right >= c.left &&
          nodeBounds.left <= c.right &&
          nodeBounds.bottom >= c.top &&
          nodeBounds.top <= c.bottom
        ) {
          return true;
        }
      });

      if (!overlaps.length) {
        expandedNodes[node.id] = true;
        // Draw focused node at the end
        if (node.id !== focusedNodeId) {
          drawLabelContainer(node.x, node.y, textWidth, padding);
          drawLabel(node.x, node.y, text, textWidth, padding);
        }
        covered.push(nodeBounds);
      }
    });

    nodes.forEach((node) => {
      // Make sure node circle is on top of the label
      // Draw focused node at the end
      if (expandedNodes[node.id] && node.id !== focusedNodeId) {
        drawNode(node);
      }
    });

    if (focusedNode) {
      // Make sure focused node is on top of everything
      const text = focusedNode.name.toUpperCase();
      const textWidth = context.measureText(text).width;
      drawLabelContainer(focusedNode.x, focusedNode.y, textWidth, padding);
      drawLabel(focusedNode.x, focusedNode.y, text, textWidth, padding);
      drawNode(focusedNode);
    }

    context.restore();
  }

  function drawLabelContainer(x, y, textWidth, padding) {
    context.save();

    context.strokeStyle = "#fff";
    context.globalAlpha = 0.8;
    context.fillStyle = color(1);

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
    context.fillStyle = color(1 - node.count / maxCount);
    context.beginPath();
    context.moveTo(node.x + 5, node.y);
    context.arc(node.x, node.y, 5, 0, 2 * Math.PI);
    context.fill();
    context.stroke();
  }

  function drawLabel(x, y, text, textWidth, padding) {
    context.fillStyle = color(0);
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

  function showLabel(text, x, y) {
    const label = document.getElementById("label");
    label.innerText = text;
    label.style.left = x;
    label.style.top = y;
    label.style.position = "absolute";
    label.style.display = "block";
  }

  function hideLabel() {
    const label = document.getElementById("label");
    label.style.display = "none";
  }

  canvas.addEventListener("mousemove", (event) => {
    const [px, py] = d3.pointer(event, canvas);
    const node = d3.least(nodes, ({ x, y }) => {
      const dist2 = (x - px) ** 2 + (y - py) ** 2;
      if (dist2 < 400) return dist2;
    });
    if (node) {
      canvas.style.cursor = "pointer";
      focusedNodeId = node.id;
    } else {
      canvas.style.removeProperty("cursor");
      focusedNodeId = null;
    }
    draw();
  });

  canvas.addEventListener("click", (event) => {
    const [px, py] = d3.pointer(event, canvas);
    const node = d3.least(nodes, ({ x, y }) => {
      const dist2 = (x - px) ** 2 + (y - py) ** 2;
      if (dist2 < 400) return dist2;
    });
    if (node && tagOffcanvas) {
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
  try {
    const requestInfoElement = document.getElementById("request-info");
    if (!requestInfoElement)
      throw new Error("Request info was not provided by Django");
    const { languageCode } = JSON.parse(requestInfoElement.innerHTML);
    if (!languageCode || typeof languageCode !== "string")
      throw new Error("Language code was not defined");
    return languageCode;
  } catch (e) {
    // In case of malformed JSON
    return "en";
  }
}
