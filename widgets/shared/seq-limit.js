/* Sequence-limit widgets.

   Only the interactive part lives here: a view switch, the sliders, one SVG
   and a short numeric readout. The sequence itself, its limit and every word
   of explanation stay in the .qmd as ordinary prose, so the book's LaTeX is
   never re-implemented in HTML.

   Two modes:
     convergent  — cfg.L is the limit. ε and N are both free; a button jumps N
                   to the minimal value for the current ε.
     divergent   — cfg.candidates given instead. The reader picks a candidate
                   limit; there is no N that works, so that control is absent.

   cfg = { f, L, candidates:[...], eps:{min,max,def}, scanMax }
*/
"use strict";
(function (global) {

  var BLUE = "#1f4e79", RED = "#c0392b", GRAY = "#94a3b8", SOFT = "#cbd5e1";
  var BAND = "rgba(31,78,121,.10)";

  /* ε runs over round values only — 1, 0.7, 0.5, 0.3, 0.2, 0.1, 0.07, …
     The slider is an index into this ladder, so it can never land on 0.79.
     Descending, so index 0 is the largest ε and dragging shrinks it. */
  function ladder(lo, hi) {
    var out = [], mant = [7, 5, 3, 2, 1];
    for (var k = 2; k >= -7; k--) {
      for (var i = 0; i < mant.length; i++) {
        var v = mant[i] * Math.pow(10, k);
        if (v <= hi * 1.000001 && v >= lo * 0.999999) out.push(+v.toPrecision(4));
      }
    }
    return out;
  }

  function mount(cfg) {
    var ec = cfg.eps || {};
    var EPS = ladder(ec.min != null ? ec.min : 0.01, ec.max != null ? ec.max : 1);
    var SCAN = cfg.scanMax || 3000;
    var divergent = !!cfg.candidates;

    var ei = 0;
    if (ec.def != null) {
      EPS.forEach(function (v, i) {
        if (Math.abs(v - ec.def) < Math.abs(EPS[ei] - ec.def)) ei = i;
      });
    }
    var st = { ei: ei, N: 1, L: cfg.L, view: "plot" };

    /* ---------- markup ---------- */
    var cands = divergent
      ? '<div class="row"><span class="key">מועמד לגבול</span>' +
        '<span class="seg" id="cands">' +
          cfg.candidates.map(function (c, i) {
            return '<button type="button" data-v="' + c.v + '" aria-pressed="' +
                   (i === 0) + '">' + c.label + '</button>';
          }).join("") +
        '</span></div>'
      : "";

    var nRow = divergent ? "" :
      '<div class="row">' +
        '<span class="key mathlbl">N</span>' +
        '<input type="range" id="nSl" min="1" step="1">' +
        '<span class="badge" id="nBadge"></span>' +
        '<button type="button" class="btn" id="nMinBtn">קפוץ ל‑N המינימלי</button>' +
      '</div>';

    (document.getElementById("app") || document.body).innerHTML =
      '<div class="demo">' +
        '<div class="row">' +
          '<span class="seg" id="views">' +
            '<button type="button" data-v="plot" aria-pressed="true">גרף הסדרה</button>' +
            '<button type="button" data-v="line">ציר המספרים</button>' +
          '</span>' +
        '</div>' +
        cands +
        '<div class="row">' +
          '<span class="key mathlbl">ε</span>' +
          '<input type="range" id="eSl" min="0" step="1">' +
          '<span class="badge" id="eBadge"></span>' +
        '</div>' +
        nRow +
        '<div id="plot"></div>' +
        '<div class="readout" id="readout"></div>' +
      '</div>';

    var $ = function (id) { return document.getElementById(id); };
    var eps = function () { return EPS[st.ei]; };

    /* ---------- the two numbers the widget has to know ---------- */
    function scan(e, L) {
      var last = 0, count = 0;
      for (var n = 1; n <= SCAN; n++) {
        if (Math.abs(cfg.f(n) - L) >= e) { last = n; count++; }
      }
      return { Nmin: last, count: count, endless: last > SCAN * 0.5 };
    }

    function decimals(half) {
      return Math.min(6, Math.max(2, Math.ceil(-Math.log10(Math.max(half, 1e-12))) + 2));
    }

    /* ---------- geometry shared by both views ---------- */
    function frame() {
      var e = eps();
      var s = scan(e, st.L);
      /* the view has to reach past both the chosen gate and the minimal one,
         otherwise picking a small N would hide the part of the tail that matters */
      var ref = s.endless ? st.N : Math.max(st.N, s.Nmin);
      var nMax = Math.max(60, Math.ceil((ref + 1) * 1.7));
      var stride = Math.max(1, Math.ceil(nMax / 320));
      var idx = [];
      for (var n = 1; n <= nMax; n += stride) idx.push(n);
      if (st.N >= 1 && idx.indexOf(st.N) < 0) idx.push(st.N);
      idx.sort(function (a, b) { return a - b; });

      /* keep the band a legible fraction of the view at every ε, without
         leaving a huge empty margin when the whole sequence is already close in */
      var dev = 0;
      idx.forEach(function (n) { dev = Math.max(dev, Math.abs(cfg.f(n) - st.L)); });
      var half = Math.max(e * 1.25, Math.min(e * 2.5, dev * 1.15));

      return { s: s, e: e, idx: idx, nMax: nMax, half: half };
    }

    /* grey = discarded by the gate; red = a term past the gate that still
       misses the band, so pressing "minimal N" visibly clears every red one */
    function colour(n, v, e) {
      if (n <= st.N) return GRAY;
      return Math.abs(v - st.L) >= e ? RED : BLUE;
    }

    /* ---------- view 1: n against a_n ---------- */
    function drawPlot(f) {
      var L = st.L, e = f.e, half = f.half, nMax = f.nMax;
      var W = 720, H = 360, mL = 74, mR = 14, mT = 16, mB = 36;
      var pw = W - mL - mR, ph = H - mT - mB;
      var X = function (n) { return mL + (n / nMax) * pw; };
      var Y = function (v) { return mT + (1 - (v - (L - half)) / (2 * half)) * ph; };
      var d = decimals(half);
      var p = ['<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="איברי הסדרה מול הרצועה סביב הגבול">'];

      p.push('<rect x="' + mL + '" y="' + Y(L + e) + '" width="' + pw +
             '" height="' + (Y(L - e) - Y(L + e)) + '" fill="' + BAND + '"/>');
      p.push('<line x1="' + mL + '" y1="' + Y(L) + '" x2="' + (mL + pw) + '" y2="' + Y(L) +
             '" stroke="' + BLUE + '" stroke-width="1.4" stroke-dasharray="7 4"/>');
      [L + e, L - e].forEach(function (v) {
        p.push('<line x1="' + mL + '" y1="' + Y(v) + '" x2="' + (mL + pw) + '" y2="' + Y(v) +
               '" stroke="' + BLUE + '" stroke-width="1" stroke-dasharray="2 3"/>');
      });
      /* numeric value on the axis, symbolic name inside the plot */
      [[L + e, "L+ε"], [L, "L"], [L - e, "L−ε"]].forEach(function (a) {
        var y = Y(a[0]);
        p.push('<text x="' + (mL - 8) + '" y="' + (y + 4) + '" text-anchor="end" font-size="11.5" fill="#64748b">' +
               a[0].toFixed(d) + '</text>');
        p.push('<text class="mathlbl" x="' + (mL + pw - 6) + '" y="' + (y - 5) +
               '" text-anchor="end" font-size="12.5" fill="' + BLUE + '">' + a[1] + '</text>');
      });

      if (!divergent && st.N >= 1 && st.N <= nMax) {
        p.push('<line x1="' + X(st.N) + '" y1="' + mT + '" x2="' + X(st.N) + '" y2="' + (mT + ph) +
               '" stroke="' + GRAY + '" stroke-width="1.2" stroke-dasharray="5 4"/>');
        p.push('<text class="mathlbl" x="' + X(st.N) + '" y="' + (mT + 12) +
               '" text-anchor="middle" font-size="13" fill="#64748b">N</text>');
      }

      p.push('<line x1="' + mL + '" y1="' + (mT + ph) + '" x2="' + (mL + pw) + '" y2="' + (mT + ph) +
             '" stroke="' + SOFT + '"/>');
      var raw = nMax / 6;
      var mag = Math.pow(10, Math.floor(Math.log10(raw)));
      var step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; })
                  .filter(function (s) { return s >= raw; })[0] || 10 * mag;
      step = Math.max(1, Math.round(step));
      for (var t = step; t <= nMax; t += step) {
        p.push('<line x1="' + X(t) + '" y1="' + (mT + ph) + '" x2="' + X(t) + '" y2="' + (mT + ph + 4) +
               '" stroke="' + SOFT + '"/>');
        p.push('<text x="' + X(t) + '" y="' + (mT + ph + 18) + '" text-anchor="middle" font-size="11.5" fill="#64748b">' + t + '</text>');
      }
      p.push('<text class="mathlbl" x="' + (mL + pw) + '" y="' + (mT + ph + 32) +
             '" text-anchor="end" font-size="13" fill="#64748b">n</text>');
      p.push('<text class="mathlbl" x="' + (mL - 8) + '" y="' + (mT + 10) +
             '" text-anchor="end" font-size="13" fill="#64748b">a<tspan font-size="10" dy="3">n</tspan></text>');

      f.idx.forEach(function (n) {
        var v = cfg.f(n), x = X(n), y = Y(v), c = colour(n, v, e);
        if (y < mT || y > mT + ph) {
          var yy = y < mT ? mT + 5 : mT + ph - 5, s = y < mT ? -1 : 1;
          p.push('<path d="M ' + (x - 4) + ' ' + (yy + 4 * s) + ' L ' + (x + 4) + ' ' + (yy + 4 * s) +
                 ' L ' + x + ' ' + (yy - 3 * s) + ' Z" fill="' + c + '" fill-opacity=".55"/>');
          return;
        }
        if (c === RED) {
          p.push('<circle cx="' + x + '" cy="' + y + '" r="4.4" fill="none" stroke="' + RED + '" stroke-width="1.8"/>');
        } else {
          p.push('<circle cx="' + x + '" cy="' + y + '" r="3.1" fill="' + c + '"/>');
        }
      });
      p.push("</svg>");
      return p.join("");
    }

    /* ---------- view 2: the same terms as points on a number line ----------
       There is no n-axis here, so N cannot be a position. It splits the dots
       by colour instead, and the term sitting at the gate is ringed and named
       with its actual index, so the cut point stays locatable. */
    function drawLine(f) {
      var L = st.L, e = f.e, half = f.half;
      var W = 720, H = 150, mL = 22, mR = 22, y0 = 66;
      var pw = W - mL - mR;
      var X = function (v) { return mL + ((v - (L - half)) / (2 * half)) * pw; };
      var d = decimals(half);
      var p = ['<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="איברי הסדרה כנקודות על ציר המספרים">'];

      p.push('<rect x="' + X(L - e) + '" y="' + (y0 - 22) + '" width="' + (X(L + e) - X(L - e)) +
             '" height="44" fill="' + BAND + '"/>');
      p.push('<line x1="' + mL + '" y1="' + y0 + '" x2="' + (mL + pw) + '" y2="' + y0 +
             '" stroke="#334155" stroke-width="1.1"/>');
      [[L - e, "L−ε"], [L, "L"], [L + e, "L+ε"]].forEach(function (a) {
        var x = X(a[0]), big = a[1] === "L";
        p.push('<line x1="' + x + '" y1="' + (y0 - (big ? 13 : 9)) + '" x2="' + x + '" y2="' + (y0 + (big ? 13 : 9)) +
               '" stroke="' + BLUE + '" stroke-width="' + (big ? 1.6 : 1.1) + '"/>');
        p.push('<text class="mathlbl" x="' + x + '" y="' + (y0 + 30) + '" text-anchor="middle" font-size="13" fill="' + BLUE + '">' + a[1] + '</text>');
        p.push('<text x="' + x + '" y="' + (y0 + 44) + '" text-anchor="middle" font-size="10.5" fill="#94a3b8">' + a[0].toFixed(d) + '</text>');
      });

      /* grey first, so the surviving tail sits on top of it */
      [0, 1].forEach(function (pass) {
        f.idx.forEach(function (n) {
          var after = n > st.N;
          if ((pass === 1) !== after) return;
          var v = cfg.f(n), x = X(v), c = colour(n, v, e);
          if (x < mL - 6 || x > mL + pw + 6) {
            var ex = x < mL ? mL + 4 : mL + pw - 4, s = x < mL ? -1 : 1;
            p.push('<path d="M ' + (ex + 4 * s) + ' ' + (y0 - 4) + ' L ' + (ex + 4 * s) + ' ' + (y0 + 4) +
                   ' L ' + (ex - 3 * s) + ' ' + y0 + ' Z" fill="' + c + '" fill-opacity=".55"/>');
            return;
          }
          if (c === RED) {
            p.push('<circle cx="' + x + '" cy="' + y0 + '" r="4.4" fill="none" stroke="' + RED + '" stroke-width="1.8"/>');
          } else {
            p.push('<circle cx="' + x + '" cy="' + y0 + '" r="3.4" fill="' + c + '" fill-opacity=".85"/>');
          }
        });
      });

      if (!divergent && st.N >= 1) {
        var xN = X(cfg.f(st.N));
        if (xN >= mL - 2 && xN <= mL + pw + 2) {
          p.push('<circle cx="' + xN + '" cy="' + y0 + '" r="7" fill="none" stroke="#334155" stroke-width="1.4"/>');
          p.push('<line x1="' + xN + '" y1="' + (y0 - 8) + '" x2="' + xN + '" y2="' + (y0 - 24) + '" stroke="#334155" stroke-width="1"/>');
          p.push('<text class="mathlbl" x="' + xN + '" y="' + (y0 - 28) + '" text-anchor="middle" font-size="13" fill="#334155">a<tspan font-size="10" dy="3">' + st.N + '</tspan></text>');
        }
      }
      p.push("</svg>");
      return p.join("");
    }

    /* ---------- render ---------- */
    function draw() {
      var f = frame();
      $("plot").innerHTML = st.view === "plot" ? drawPlot(f) : drawLine(f);

      var out = '<div><span class="key">איברים מחוץ לרצועה:</span> <span class="val">' +
                (f.s.endless ? "∞" : f.s.count) + '</span></div>';
      if (!divergent) {
        out = '<div><span class="key mathlbl">N</span><span class="key"> המינימלי:</span> <span class="val">' +
              f.s.Nmin + '</span></div>' + out;
      }
      $("readout").innerHTML = out;

      $("eBadge").textContent = f.e;
      if (!divergent) $("nBadge").textContent = st.N;

      requestAnimationFrame(function () {
        if (global.parent && global.parent !== global) {
          global.parent.postMessage({
            type: "widget-height",
            height: Math.ceil(document.documentElement.scrollHeight)
          }, "*");
        }
      });
    }

    /* N is free from 1 upward; only its ceiling follows ε */
    function syncN() {
      if (divergent) return;
      var s = scan(eps(), st.L);
      var top = Math.max(40, Math.ceil((s.endless ? st.N : s.Nmin) * 1.6));
      var sl = $("nSl");
      sl.max = top;
      if (st.N > top) st.N = top;
      if (st.N < 1) st.N = 1;
      sl.value = st.N;
    }
    function refresh() { syncN(); draw(); }

    /* ---------- wiring ---------- */
    var eSl = $("eSl");
    eSl.max = EPS.length - 1;
    eSl.value = st.ei;
    eSl.addEventListener("input", function (ev) {
      st.ei = +ev.target.value;
      refresh();
    });

    if (!divergent) {
      $("nSl").addEventListener("input", function (ev) { st.N = +ev.target.value; draw(); });
      $("nMinBtn").addEventListener("click", function () {
        var s = scan(eps(), st.L);
        st.N = Math.max(1, s.Nmin);
        refresh();
      });
    }

    function segment(id, onPick) {
      var box = $(id);
      if (!box) return;
      box.addEventListener("click", function (ev) {
        var b = ev.target.closest("button");
        if (!b) return;
        Array.prototype.forEach.call(box.querySelectorAll("button"), function (o) {
          o.setAttribute("aria-pressed", String(o === b));
        });
        onPick(b.dataset.v);
      });
    }
    segment("views", function (v) { st.view = v; draw(); });
    segment("cands", function (v) { st.L = +v; refresh(); });

    global.addEventListener("resize", draw);

    /* open on the minimal N for the default ε */
    if (!divergent) st.N = Math.max(1, scan(eps(), st.L).Nmin);
    refresh();
  }

  global.SeqLimit = { mount: mount };

})(window);
