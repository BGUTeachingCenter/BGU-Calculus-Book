
(function (global) {
  "use strict";

  // Palette. Read once from the shared stylesheet and kept as literal strings:
  // var() does NOT resolve inside SVG presentation attributes set via setAttribute,
  // so passing "var(--blue)" there silently yields black.
  var css = getComputedStyle(document.documentElement);
  function cssvar(name, fallback) {
    var s = css.getPropertyValue(name).trim();
    return s || fallback;
  }
  var INK   = cssvar("--ink",  "#1f2937");
  var BLUE  = cssvar("--blue", "#1f4e79");
  var RED   = cssvar("--red",  "#c0392b");
  var GREEN = "#2e7d32";

  // a_n = 1 + sin(n)/n, the sequence already used earlier in the chapter. It approaches
  // L from BOTH sides, so both sliders actually bite — a one-sided sequence would leave
  // one of them inert and teach the wrong thing.
  var L = 1, NMAX = 40;
  function a(n) { return 1 + Math.sin(n) / n; }

  // Slider ranges are chosen so that N stays inside the plotted window: the tightest
  // settings give N = 18 (from m) and N = 15 (from M). A wider range would send N off
  // the right edge, where the reader cannot see the thing the widget is about.
  var MLO = 0.70, MHI = 0.95, MSTEPS = 25;    // m, below L
  var ULO = 1.05, UHI = 1.50, USTEPS = 45;    // M, above L

  var VX0 = 0.3, VX1 = NMAX + 0.7, VY0 = 0.62, VY1 = 1.95;
  var PX0 = 52, PX1 = 622, PY0 = 26, PY1 = 244;
  var SVGNS = "http://www.w3.org/2000/svg";

  function sx(v) { return PX0 + (v - VX0) * (PX1 - PX0) / (VX1 - VX0); }
  function sy(v) { return PY1 - (v - VY0) * (PY1 - PY0) / (VY1 - VY0); }

  var svg = document.getElementById("plot");
  var dyn = document.createElementNS(SVGNS, "g");   // rebuilt on every update

  function make(parent, name, attrs, text) {
    var n = document.createElementNS(SVGNS, name);
    for (var k in attrs) { if (attrs[k] !== undefined) n.setAttribute(k, attrs[k]); }
    if (text !== undefined) n.textContent = text;
    parent.appendChild(n);
    return n;
  }

  // ---------- static layer ----------

  make(svg, "line", { x1: PX0 - 12, y1: sy(VY0), x2: PX1, y2: sy(VY0), "class": "axis" });
  make(svg, "line", { x1: PX0 - 12, y1: PY0 - 6, x2: PX0 - 12, y2: sy(VY0), "class": "axis" });

  for (var t = 5; t <= NMAX; t += 5) {
    make(svg, "line", { x1: sx(t), y1: sy(VY0), x2: sx(t), y2: sy(VY0) + 5, "class": "axis" });
    make(svg, "text", { x: sx(t), y: sy(VY0) + 19, "class": "axlbl" }, String(t));
  }
  make(svg, "text", { x: sx(NMAX / 2), y: sy(VY0) + 38, "class": "axlbl" }, "n");

  // the limit itself: dashed, so the solid m and M lines read as the movable pair
  make(svg, "line", { x1: PX0 - 12, y1: sy(L), x2: PX1, y2: sy(L), "class": "guide" });
  make(svg, "text", { x: PX1 - 6, y: sy(L) - 6, fill: INK, "class": "lbl",
                      "text-anchor": "end" }, "L = 1");

  svg.appendChild(dyn);                              // dynamic layer sits on top

  // ---------- dynamic layer ----------

  var mSl = document.getElementById("mr");
  var MSl = document.getElementById("Mr");
  var winEl = document.getElementById("win");
  var nEl = document.getElementById("nout");
  var verdict = document.getElementById("verdict");

  // The first index from which the whole TAIL stays inside. Scanning only the plotted
  // 40 terms would be a lie: it would report the first index that happens to work so
  // far, not the one the theorem promises. |a_n - L| <= 1/n, so beyond 1/gap nothing
  // can leave the window and the scan is exact.
  function tailIndex(m, M) {
    var gap = Math.min(L - m, M - L);
    var safe = Math.ceil(1 / gap) + 2;
    var last = 0;
    for (var n = 1; n <= safe; n++) {
      var v = a(n);
      if (v <= m || v >= M) { last = n; }
    }
    return last + 1;
  }

  function reportHeight() {
    requestAnimationFrame(function () {
      if (global.parent && global.parent !== global) {
        global.parent.postMessage({
          type: "widget-height",
          height: Math.ceil(document.documentElement.scrollHeight)
        }, "*");
      }
    });
  }

  function fmt(x) { return x.toFixed(2); }

  function update() {
    var m = MLO + (mSl.value / MSTEPS) * (MHI - MLO);
    var M = ULO + (MSl.value / USTEPS) * (UHI - ULO);
    var N = tailIndex(m, M);

    while (dyn.firstChild) { dyn.removeChild(dyn.firstChild); }

    // the window, drawn as a band so "inside" is a place rather than a pair of numbers
    make(dyn, "rect", { x: PX0 - 12, y: sy(M), width: PX1 - PX0 + 12,
                        height: sy(m) - sy(M), fill: GREEN, opacity: 0.10 });

    [[m, "m", BLUE], [M, "M", RED]].forEach(function (row) {
      make(dyn, "line", { x1: PX0 - 12, y1: sy(row[0]), x2: PX1, y2: sy(row[0]),
                          stroke: row[2], "stroke-width": 1.6 });
      make(dyn, "text", { x: PX0 - 16, y: sy(row[0]) + 5, fill: row[2], "class": "lbl",
                          "text-anchor": "end" }, row[1]);
    });

    // N, and the terms themselves: red before N, green from N on
    if (N <= NMAX) {
      make(dyn, "line", { x1: sx(N), y1: PY0 - 6, x2: sx(N), y2: sy(VY0),
                          stroke: INK, "stroke-width": 1.2, "stroke-dasharray": "4 3" });
      make(dyn, "text", { x: sx(N), y: PY0 - 10, fill: INK, "class": "axlbl" }, "N = " + N);
    }

    for (var n = 1; n <= NMAX; n++) {
      var v = a(n);
      if (v < VY0 || v > VY1) { continue; }
      var inside = (v > m && v < M);
      make(dyn, "circle", { cx: sx(n), cy: sy(v), r: 3.6,
                            fill: inside ? GREEN : RED, "class": "pt" });
    }

    winEl.textContent = fmt(m) + " < aₙ < " + fmt(M);
    nEl.textContent = "N = " + N;
    verdict.textContent = "החל מ-" + N + " כל האיברים בתוך החלון; לפניו " +
                          (N - 1) + " איברים, וחלקם בחוץ";

    reportHeight();
  }

  mSl.addEventListener("input", update);
  MSl.addEventListener("input", update);
  global.addEventListener("resize", reportHeight);
  update();
})(window);
