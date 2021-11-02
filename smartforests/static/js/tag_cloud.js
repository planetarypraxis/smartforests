import webcola from "https://cdn.skypack.dev/webcola";
import * as d3 from "https://cdn.skypack.dev/d3@7";
import * as geo from "https://cdn.skypack.dev/geometric";
import * as chroma from "https://cdn.skypack.dev/chroma-js";
import concaveman from "https://cdn.skypack.dev/concaveman";
import debounce from "https://cdn.skypack.dev/lodash.debounce";

// Re-layout on window resize
let resizeHandlers = [];
window.addEventListener("resize", () => {
  resizeHandlers.forEach((fn) => fn());
});

const init = () => {
  // Downsample the canvas to produce the pixelated effect.
  const PIXEL_SIZE = 32;

  // Color configs for the background.
  const GRADIENT_INNER = "#63E364";
  const GRADIENT_OUTER = "#4A964A";
  const COLOR_SCALE = chroma.scale([GRADIENT_OUTER, GRADIENT_INNER]);

  // Reset the resize handlers on navigation
  resizeHandlers = [];

  // Bind to data-tags
  $("[data-tag-cloud-data]").each((_, el) => {
    const configElement = document.getElementById(el.dataset.tagCloudData);
    if (!configElement) {
      console.error("No config element found for tag cloud");
      return;
    }

    el.classList.add("tag-cloud");
    el.style.backgroundColor = GRADIENT_OUTER;

    // Prepare the data for d3
    const nodes = JSON.parse(configElement.innerHTML);
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
    const canvas = d3
      .select(el)
      .append("canvas")
      .attr("class", "w-100 h-100 position-absolute")
      .node();

    const ctx = canvas.getContext("2d");

    // Approximate a curve around a polygon by alternating its points as the control and targets of a quadratic bezier
    const drawPath = (path) => {
      const start = path[0];
      let i = 1;

      ctx.beginPath();
      ctx.moveTo(...start);

      while (i < path.length - 1) {
        const ctl = path[i];
        i += 1;

        const target = path[i] || start;
        i += 1;

        ctx.quadraticCurveTo(...ctl, ...target);
      }

      ctx.closePath();
    };

    // Produce the background elevation effect by taking the concave hull polygon of all tag locations, then repetedly
    // filling using the color scale getting lighter as we move in.

    // We can't do this with a gradient because it wouldn't trace the outlne of the polygon.
    const updateBackground = (nodes) => {
      const ctxWidth = Math.floor(el.clientWidth / PIXEL_SIZE);
      const ctxHeight = Math.floor(el.clientHeight / PIXEL_SIZE);

      canvas.width = ctxWidth;
      canvas.height = ctxHeight;

      const outerPolygon = concaveman(
        nodes.map((node) => [node.x / PIXEL_SIZE, node.y / PIXEL_SIZE])
      );

      ctx.clearRect(0, 0, ctxWidth, ctxHeight);

      for (let i = 0; i < 10; ++i) {
        const poly = geo.polygonScale(outerPolygon, 2 / (i + 1) + 1);
        const color = COLOR_SCALE(i / 10);

        drawPath(poly);
        ctx.fillStyle = color;
        ctx.fill();
      }
    };

    // Use webcola's constraint-based graph layout plugin for d3 to lay out the tags, ensuring that we respect the
    // following constrants:
    //
    // * Related tags are close togehter
    // * Tags are all within the bounds of the tag area.
    // * Tags do not overlap.
    const layout = () => {
      const width = el.clientWidth;
      const height = el.clientHeight;

      const container = d3.select(el);
      const cola = webcola.d3adaptor(d3).size([width, height]);

      const realGraphNodes = nodes.slice(0);
      const pageBounds = { x: 0, y: 0, width, height };
      const fixedNode = { fixed: true, fixedWeight: 100 };
      const topLeft = { ...fixedNode, x: pageBounds.x, y: pageBounds.y };
      const tlIndex = nodes.push(topLeft) - 1;
      const bottomRight = {
        ...fixedNode,
        x: pageBounds.x + pageBounds.width,
        y: pageBounds.y + pageBounds.height,
      };
      const brIndex = nodes.push(bottomRight) - 1;
      const constraints = [];

      // Render a tag for each node.
      const tags = container
        .selectAll(".related-tag")
        .data(realGraphNodes, (d) => d.slug)
        .join((enter) => {
          const a = enter.append("a").attr("class", "related-tag");

          a.append("span").attr("class", "tag-handle");

          a.append("span")
            .attr("class", "tag-label")
            .text((node) => node.name);

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
      for (let i = 0; i < realGraphNodes.length; i++) {
        const nodeEl = elements[i];
        const node = realGraphNodes[i];

        // Use the tag element's pixel size to drive the layout algorithm's constraints for avoiding overlaps.
        node.width = nodeEl.clientWidth;
        node.height = nodeEl.clientHeight;

        // Preserve relative positions if we're resizing.
        if (scaleFactor && node.x && node.y) {
          node.x = scaleFactor[0] * node.x;
          node.y = scaleFactor[1] * node.y;
        }

        // Add constraints to prevent going offscreen
        constraints.push({
          axis: "x",
          type: "separation",
          left: tlIndex,
          right: i,
          gap: 0,
        });
        constraints.push({
          axis: "y",
          type: "separation",
          left: tlIndex,
          right: i,
          gap: 0,
        });
        constraints.push({
          axis: "x",
          type: "separation",
          left: i,
          right: brIndex,
          gap: nodeEl.clientWidth,
        });
        constraints.push({
          axis: "y",
          type: "separation",
          left: i,
          right: brIndex,
          gap: nodeEl.clientHeight + 32,
        });
      }

      // If there's already an instance of the layout system (ie. after window resize), remove it so it doesn't
      // conflict with the new one
      if (el._cola) {
        el._cola.stop();
      }

      // Configure and start the layout
      cola
        .nodes(nodes)
        .links(links)
        .avoidOverlaps(true)
        .constraints(constraints)
        .jaccardLinkLengths(80, 0.7)
        .handleDisconnected(false)
        .start(30);

      // Store the things we need for re-layout
      el._prevBounds = [el.clientWidth, el.clientHeight];
      el._cola = cola;

      // Animate the layout.
      cola.on("tick", () => {
        tags.style("transform", (d) => `translate(${px(d.x)},${px(d.y)})`);
        updateBackground(nodes);
      });
    };

    layout();
    resizeHandlers.push(debounce(layout, 200));
  });
};

const px = (val) => Math.round(val) + "px";

$().on("turbo:load", init);
init();
