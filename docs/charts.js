// Small SVG chart helpers for docs/*.html: profile (line + error bars), scatter, horizontal bars.
// Colors come from CSS tokens (style.css) so light and dark mode follow the page.
(function () {
  const NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    const node = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  }

  function niceStep(raw) {
    const p = Math.pow(10, Math.floor(Math.log10(raw)));
    const m = raw / p;
    return (m < 1.5 ? 1 : m < 3 ? 2 : m < 7 ? 5 : 10) * p;
  }

  function ticks(a, b, n) {
    const step = niceStep((b - a) / n);
    const out = [];
    for (let v = Math.ceil(a / step - 1e-9) * step; v <= b + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }

  function scale(d0, d1, r0, r1) {
    return (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  }

  // Marker shapes, so identity never rests on color alone.
  function marker(shape, cx, cy, r, cls, parent) {
    if (shape === "square") return el("rect", { x: cx - r, y: cy - r, width: 2 * r, height: 2 * r, rx: 1, class: cls }, parent);
    if (shape === "triangle") {
      const h = r * 1.25;
      return el("polygon", { points: `${cx},${cy - h} ${cx + h},${cy + h * 0.8} ${cx - h},${cy + h * 0.8}`, class: cls }, parent);
    }
    if (shape === "diamond") {
      const h = r * 1.3;
      return el("polygon", { points: `${cx},${cy - h} ${cx + h},${cy} ${cx},${cy + h} ${cx - h},${cy}`, class: cls }, parent);
    }
    return el("circle", { cx, cy, r, class: cls }, parent);
  }

  function legend(container, series) {
    const box = document.createElement("div");
    box.className = "legend";
    for (const s of series) {
      const item = document.createElement("span");
      const svg = el("svg", { viewBox: "0 0 22 12", "aria-hidden": "true" });
      el("line", { x1: 0, y1: 6, x2: 22, y2: 6, stroke: `var(${s.color})`, "stroke-width": 2, "stroke-dasharray": s.dash || "" }, svg);
      marker(s.marker || "circle", 11, 6, 3.6, "", svg).setAttribute("style", `fill:var(${s.fill === "none" ? "--surface" : s.color});stroke:var(${s.color});stroke-width:1.5`);
      item.appendChild(svg);
      item.appendChild(document.createTextNode(s.name));
      box.appendChild(item);
    }
    container.appendChild(box);
  }

  function tooltip(container) {
    const tip = document.createElement("div");
    tip.className = "tooltip";
    container.appendChild(tip);
    return {
      show(evt, html) {
        tip.innerHTML = html;
        const r = container.getBoundingClientRect();
        let x = evt.clientX - r.left + 12, y = evt.clientY - r.top - 34;
        if (x + 180 > r.width) x = evt.clientX - r.left - 190;
        tip.style.left = `${x}px`; tip.style.top = `${Math.max(0, y)}px`;
        tip.classList.add("on");
      },
      hide() { tip.classList.remove("on"); },
    };
  }

  // Axes, grid and labels; returns the scales and the plot group.
  function frame(svg, o) {
    const { W, H, m } = o;
    const x = scale(o.xd[0], o.xd[1], m.l, W - m.r);
    const y = scale(o.yd[0], o.yd[1], H - m.b, m.t);
    const g = el("g", {}, svg);
    for (const v of ticks(o.yd[0], o.yd[1], o.yTicks || 6)) {
      el("line", { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), class: v === 0 ? "c-zero" : "c-grid" }, g);
      el("text", { x: m.l - 6, y: y(v) + 4, "text-anchor": "end", class: "c-tick" }, g).textContent = v;
    }
    for (const v of ticks(o.xd[0], o.xd[1], o.xTicks || 8)) {
      el("line", { x1: x(v), x2: x(v), y1: H - m.b, y2: H - m.b + 4, class: "c-axis" }, g);
      el("text", { x: x(v), y: H - m.b + 17, "text-anchor": "middle", class: "c-tick" }, g).textContent = v;
    }
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, class: "c-axis" }, g);
    el("text", { x: (m.l + W - m.r) / 2, y: H - 6, "text-anchor": "middle", class: "c-label" }, g).textContent = o.xLabel;
    el("text", { x: 14, y: (m.t + H - m.b) / 2, "text-anchor": "middle", class: "c-label", transform: `rotate(-90 14 ${(m.t + H - m.b) / 2})` }, g).textContent = o.yLabel;
    return { x, y, g: el("g", {}, svg) };
  }

  // series: [{name, color: "--c-ref", marker, fill, dash, x: [], y: [], err: [], label, labelDy}]
  window.profileChart = function (container, o) {
    const W = o.W || 660, H = o.H || 360, m = { l: 58, r: o.rightMargin || 150, t: 14, b: 44 };
    legend(container, o.series);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.aria }, container);
    const tip = tooltip(container);
    const { x, y, g } = frame(svg, { W, H, m, xd: o.xd, yd: o.yd, xLabel: o.xLabel, yLabel: o.yLabel });
    for (const s of o.series) {
      const pts = s.x.map((xv, i) => [x(xv), y(s.y[i])]);
      el("polyline", { points: pts.map((p) => p.join(",")).join(" "), fill: "none", stroke: `var(${s.color})`, "stroke-width": s.width || 2, "stroke-dasharray": s.dash || "" }, g);
      s.x.forEach((xv, i) => {
        if (s.err) el("line", { x1: x(xv), x2: x(xv), y1: y(s.y[i] - s.err[i]), y2: y(s.y[i] + s.err[i]), stroke: `var(${s.color})`, "stroke-width": 1.5 }, g);
        marker(s.marker || "circle", x(xv), y(s.y[i]), 4.2, "", g).setAttribute(
          "style", `fill:var(${s.fill === "none" ? "--surface" : s.color});stroke:var(${s.fill === "none" ? s.color : "--surface"});stroke-width:${s.fill === "none" ? 1.6 : 1.5}`);
        const hit = el("circle", { cx: x(xv), cy: y(s.y[i]), r: 9, fill: "transparent" }, g);
        hit.addEventListener("pointerenter", (e) => tip.show(e, `<b>${s.name}</b><br>${o.xName} ${xv.toFixed(1)} ${o.xUnit}: ${s.y[i].toFixed(1)} ± ${(s.err ? s.err[i] : 0).toFixed(1)} ${o.yUnit}`));
        hit.addEventListener("pointerleave", () => tip.hide());
      });
      if (s.label) {
        const [lx, ly] = pts[pts.length - 1];
        el("text", { x: lx + 10, y: ly + 4 + (s.labelDy || 0), class: "c-point-label" }, g).textContent = s.label;
      }
    }
    return svg;
  };

  // points: {x: [], y: []}; overlays: profile series drawn on top
  window.scatterChart = function (container, o) {
    const W = o.W || 330, H = o.H || 300, m = { l: 52, r: 12, t: 12, b: 44 };
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.aria }, container);
    const { x, y, g } = frame(svg, { W, H, m, xd: o.xd, yd: o.yd, xLabel: o.xLabel, yLabel: o.yLabel, xTicks: 5, yTicks: 6 });
    const pts = el("g", { style: "fill:var(--muted);fill-opacity:0.38" }, g);
    o.points.x.forEach((xv, i) => {
      const yv = o.points.y[i];
      if (xv < o.xd[0] || xv > o.xd[1] || yv < o.yd[0] || yv > o.yd[1]) return;
      el("circle", { cx: x(xv), cy: y(yv), r: 1.7 }, pts);
    });
    for (const s of o.overlays || []) {
      el("polyline", { points: s.x.map((xv, i) => `${x(xv)},${y(s.y[i])}`).join(" "), fill: "none", stroke: `var(${s.color})`, "stroke-width": 2.5, "stroke-dasharray": s.dash || "" }, g);
    }
    if (o.note) el("text", { x: m.l + 8, y: m.t + 14, class: "c-point-label" }, g).textContent = o.note;
    return svg;
  };

  // bars: [{label, value, color, note}]
  window.barChart = function (container, o) {
    const rowH = 34, W = o.W || 660, m = { l: o.leftMargin || 230, r: 70, t: 6, b: 36 };
    const H = m.t + m.b + rowH * o.bars.length;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.aria }, container);
    const tip = tooltip(container);
    const x = scale(0, o.max, m.l, W - m.r);
    for (const v of ticks(0, o.max, 6)) {
      el("line", { x1: x(v), x2: x(v), y1: m.t, y2: H - m.b, class: "c-grid" }, svg);
      el("text", { x: x(v), y: H - m.b + 16, "text-anchor": "middle", class: "c-tick" }, svg).textContent = v;
    }
    el("text", { x: (m.l + W - m.r) / 2, y: H - 4, "text-anchor": "middle", class: "c-label" }, svg).textContent = o.xLabel;
    o.bars.forEach((b, i) => {
      const yc = m.t + rowH * i + rowH / 2;
      el("text", { x: m.l - 10, y: yc + 4, "text-anchor": "end", class: "c-point-label" }, svg).textContent = b.label;
      const w = Math.max(2, x(b.value) - m.l);
      // 4 px rounded data end, square at the baseline
      el("path", { d: `M${m.l},${yc - 8} h${w - 4} a4,4 0 0 1 4,4 v8 a4,4 0 0 1 -4,4 h${-(w - 4)} z`, style: `fill:var(${b.color})` }, svg);
      el("text", { x: m.l + w + 6, y: yc + 4, class: "c-point-label" }, svg).textContent = `${b.value.toFixed(1)} ps`;
      const hit = el("rect", { x: m.l, y: yc - 14, width: Math.max(w, 40), height: 28, fill: "transparent" }, svg);
      hit.addEventListener("pointerenter", (e) => tip.show(e, `<b>${b.label}</b><br>σ(t0) = ${b.value.toFixed(1)} ps${b.note ? "<br>" + b.note : ""}`));
      hit.addEventListener("pointerleave", () => tip.hide());
    });
    el("line", { x1: m.l, x2: m.l, y1: m.t, y2: H - m.b, class: "c-axis" }, svg);
    return svg;
  };
})();
