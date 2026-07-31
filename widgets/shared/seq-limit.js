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

   cfg = { f, L, candidates:[...], eps:{min,max,def|list}, scanMax, n0 }

   Per-widget opt-ins. Every default reproduces the behaviour these knobs had
   before they existed, so adding one changes that widget and nothing else:
     range      — pin the value axis to [lo, hi] instead of letting it follow ε
     zoomOn:"N" — derive the value axis from |f(N) - L|, making N the zoom.
                  Only meaningful when the error falls by a constant factor per
                  step, as in a decimal expansion; pointless otherwise.
     nFloor     — smallest index range to draw (default 20 graph / 120 line)
     minBandPx  — below this the ε band is not drawn at all, since a sub-pixel
                  strip composites into something that reads as a line of some
                  width. Set to 0 to draw it regardless.
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
    /* eps.list overrides the generated ladder, for a widget that needs
       particular stops (the divergent one needs an ε above 2). Descending. */
    var EPS = ec.list ? ec.list.slice()
                      : ladder(ec.min != null ? ec.min : 0.01, ec.max != null ? ec.max : 1);
    var SCAN = cfg.scanMax || 3000;
    var n0 = cfg.n0 != null ? cfg.n0 : 1;   /* first index; the decimal example starts at 0 */
    var divergent = !!cfg.candidates;

    var ei = 0;
    if (ec.def != null) {
      EPS.forEach(function (v, i) {
        if (Math.abs(v - ec.def) < Math.abs(EPS[ei] - ec.def)) ei = i;
      });
    }
    /* no gate in divergent mode, so every term is judged purely by the band */
    var st = { ei: ei, N: divergent ? n0 - 1 : n0, L: cfg.L, view: "plot" };

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
        '<input type="range" id="nSl" step="1">' +
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
      var last = n0 - 1, count = 0;
      for (var n = n0; n <= SCAN; n++) {
        if (Math.abs(cfg.f(n) - L) >= e) { last = n; count++; }
      }
      /* The definition reads "for every n >= N", so the smallest gate that works
         is one past the last term that misses the band — not that term itself.
         With nothing outside, last is n0-1 and Nmin correctly comes out n0. */
      return { Nmin: last + 1, count: count, endless: last > SCAN * 0.5 };
    }

    function decimals(half) {
      return Math.min(9, Math.max(2, Math.ceil(-Math.log10(Math.max(half, 1e-12))) + 2));
    }

    /* ---------- geometry shared by both views ---------- */
    function frame() {
      var e = eps();
      var s = scan(e, st.L);
      /* the view has to reach past both the chosen gate and the minimal one,
         otherwise picking a small N would hide the part of the tail that matters */
      var ref = s.endless ? st.N : Math.max(st.N, s.Nmin);
      /* The graph keeps a low floor so that a small N gives a short axis with
         every index tickable and every term individually visible. The number
         line has no index axis and lives on the pile-up near L, so it needs a
         far denser sample to say anything at all. */
      var floorN = cfg.nFloor != null ? cfg.nFloor : (st.view === "plot" ? 20 : 120);
      var nMax = Math.max(floorN, Math.ceil((ref + 1) * 1.7));
      var stride = Math.max(1, Math.ceil(nMax / 320));
      var idx = [];
      for (var n = n0; n <= nMax; n += stride) idx.push(n);
      if (st.N >= n0 && idx.indexOf(st.N) < 0) idx.push(st.N);
      idx.sort(function (a, b) { return a - b; });

      /* cfg.range pins the value axis. Needed when the point of the widget is
         that the band grows past the terms rather than the terms closing in:
         with a moving axis a huge ε just rescales and nothing looks different. */
      var lo, hi;
      if (cfg.range) {
        lo = cfg.range[0];
        hi = cfg.range[1];
      } else if (cfg.zoomOn === "N") {
        /* For a sequence whose distance to L falls by a constant factor each
           step, one linear scale cannot hold two terms that are decades apart.
           So the axis follows the gate instead of the whole sequence: N becomes
           the zoom, and every notch shows the same picture one decade smaller.
           Terms before the gate leave the view as edge markers, which is honest
           — they really are off the scale. */
        var dN = Math.abs(cfg.f(Math.max(st.N, n0)) - st.L);
        var halfN = Math.max(e, dN) * 2.2;
        lo = st.L - halfN;
        hi = st.L + halfN;
      } else {
        /* keep the band a legible fraction of the view at every ε, without
           leaving a huge empty margin when the sequence is already close in */
        var dev = 0;
        idx.forEach(function (n) { dev = Math.max(dev, Math.abs(cfg.f(n) - st.L)); });
        var half = Math.max(e * 1.25, Math.min(e * 2.5, dev * 1.15));
        lo = st.L - half;
        hi = st.L + half;
      }

      /* A band thinner than a few pixels renders as a line, not a strip — the
         fill, its two edges and the limit line all land on top of each other and
         the reader sees one thick line. Below the threshold it is not drawn at
         all: sub-pixel is sub-pixel, and a hairline strip would misrepresent its
         own width. The stray terms past the gate still show up in red.
         PLOT_PH / LINE_PW are the drawable extents of the two viewBoxes. */
      var PLOT_PH = 308, LINE_PW = 676;
      var minBand = cfg.minBandPx != null ? cfg.minBandPx : 3;   /* 0 = always draw it */
      var bandVisible = (2 * e / (hi - lo)) * (st.view === "plot" ? PLOT_PH : LINE_PW) >= minBand;

      return { s: s, e: e, idx: idx, nMax: nMax, lo: lo, hi: hi, bandVisible: bandVisible };
    }

    /* grey = discarded by the gate; red = a term past the gate that still
       misses the band, so pressing "minimal N" visibly clears every red one */
    function colour(n, v, e) {
      if (n < st.N) return GRAY;
      return Math.abs(v - st.L) >= e ? RED : BLUE;
    }

    /* ---------- view 1: n against a_n ---------- */
    function drawPlot(f) {
      var L = st.L, e = f.e, lo = f.lo, hi = f.hi, nMax = f.nMax;
      var W = 720, H = 360, mL = 74, mR = 14, mT = 16, mB = 36;
      var pw = W - mL - mR, ph = H - mT - mB;
      var X = function (n) { return mL + (n / nMax) * pw; };
      var Y = function (v) { return mT + (1 - (v - lo) / (hi - lo)) * ph; };
      var inY = function (v) { return v >= lo && v <= hi; };
      var d = decimals((hi - lo) / 2);
      var p = ['<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="איברי הסדרה מול הרצועה סביב הגבול">'];

      /* the band may run past the top or bottom of a pinned axis */
      var yTop = Math.max(Y(L + e), mT), yBot = Math.min(Y(L - e), mT + ph);
      if (f.bandVisible && yBot > yTop) {
        p.push('<rect x="' + mL + '" y="' + yTop + '" width="' + pw +
               '" height="' + (yBot - yTop) + '" fill="' + BAND + '"/>');
      }
      if (inY(L)) {
        p.push('<line x1="' + mL + '" y1="' + Y(L) + '" x2="' + (mL + pw) + '" y2="' + Y(L) +
               '" stroke="' + BLUE + '" stroke-width="1.4" stroke-dasharray="7 4"/>');
      }
      (f.bandVisible ? [L + e, L - e] : []).forEach(function (v) {
        if (!inY(v)) return;
        p.push('<line x1="' + mL + '" y1="' + Y(v) + '" x2="' + (mL + pw) + '" y2="' + Y(v) +
               '" stroke="' + BLUE + '" stroke-width="1" stroke-dasharray="2 3"/>');
      });
      /* with a pinned axis, keep its own end values labelled so the scale is
         readable even when L±ε has slid off the top */
      if (cfg.range) {
        [lo, (lo + hi) / 2, hi].forEach(function (v) {
          p.push('<text x="' + (mL - 8) + '" y="' + (Y(v) + 4) + '" text-anchor="end" font-size="11" fill="#b0b8c4">' +
                 (+v.toFixed(2)) + '</text>');
        });
      }
      /* numeric value on the axis, symbolic name inside the plot */
      (f.bandVisible ? [[L + e, "L+ε"], [L, "L"], [L - e, "L−ε"]] : [[L, "L"]]).forEach(function (a) {
        if (!inY(a[0])) return;
        var y = Y(a[0]);
        p.push('<text x="' + (mL - 8) + '" y="' + (y + 4) + '" text-anchor="end" font-size="11.5" fill="#64748b">' +
               a[0].toFixed(d) + '</text>');
        p.push('<text class="mathlbl" x="' + (mL + pw - 6) + '" y="' + (y - 5) +
               '" text-anchor="end" font-size="12.5" fill="' + BLUE + '">' + a[1] + '</text>');
      });

      if (!divergent && st.N >= n0 && st.N <= nMax) {
        var gx = X(st.N - 0.5);   /* a_N is kept, so the gate sits just before it */
        p.push('<line x1="' + gx + '" y1="' + mT + '" x2="' + gx + '" y2="' + (mT + ph) +
               '" stroke="' + GRAY + '" stroke-width="1.2" stroke-dasharray="5 4"/>');
        p.push('<text class="mathlbl" x="' + gx + '" y="' + (mT + 12) +
               '" text-anchor="middle" font-size="13" fill="#64748b">N</text>');
      }

      p.push('<line x1="' + mL + '" y1="' + (mT + ph) + '" x2="' + (mL + pw) + '" y2="' + (mT + ph) +
             '" stroke="' + SOFT + '"/>');
      /* a short axis gets every index; only longer ones fall back to round steps */
      var step;
      if (nMax <= 25) {
        step = 1;
      } else if (nMax <= 50) {
        step = 2;
      } else {
        var raw = nMax / 6;
        var mag = Math.pow(10, Math.floor(Math.log10(raw)));
        step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; })
                .filter(function (s) { return s >= raw; })[0] || 10 * mag;
        step = Math.max(1, Math.round(step));
      }
      for (var t = (step === 1 ? n0 : step); t <= nMax; t += step) {
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
       by colour instead, and a_N — the FIRST term of the tail, since the
       definition keeps n >= N — is ringed and named with its actual index, so
       the cut point stays locatable. */
    function drawLine(f) {
      var L = st.L, e = f.e, lo = f.lo, hi = f.hi;
      var W = 720, H = 150, mL = 22, mR = 22, y0 = 66;
      var pw = W - mL - mR;
      var X = function (v) { return mL + ((v - lo) / (hi - lo)) * pw; };
      var d = decimals((hi - lo) / 2);
      var p = ['<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="איברי הסדרה כנקודות על ציר המספרים">'];

      var bl = Math.max(X(L - e), mL), br = Math.min(X(L + e), mL + pw);
      if (f.bandVisible && br > bl) {
        p.push('<rect x="' + bl + '" y="' + (y0 - 22) + '" width="' + (br - bl) +
               '" height="44" fill="' + BAND + '"/>');
      }
      p.push('<line x1="' + mL + '" y1="' + y0 + '" x2="' + (mL + pw) + '" y2="' + y0 +
             '" stroke="#334155" stroke-width="1.1"/>');
      (f.bandVisible ? [[L - e, "L−ε"], [L, "L"], [L + e, "L+ε"]] : [[L, "L"]]).forEach(function (a) {
        if (a[0] < lo || a[0] > hi) return;
        var x = X(a[0]), big = a[1] === "L";
        p.push('<line x1="' + x + '" y1="' + (y0 - (big ? 13 : 9)) + '" x2="' + x + '" y2="' + (y0 + (big ? 13 : 9)) +
               '" stroke="' + BLUE + '" stroke-width="' + (big ? 1.6 : 1.1) + '"/>');
        p.push('<text class="mathlbl" x="' + x + '" y="' + (y0 + 30) + '" text-anchor="middle" font-size="13" fill="' + BLUE + '">' + a[1] + '</text>');
        p.push('<text x="' + x + '" y="' + (y0 + 44) + '" text-anchor="middle" font-size="10.5" fill="#94a3b8">' + a[0].toFixed(d) + '</text>');
      });

      /* grey first, so the surviving tail sits on top of it */
      [0, 1].forEach(function (pass) {
        f.idx.forEach(function (n) {
          var after = n >= st.N;
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

      if (!divergent && st.N >= n0) {
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
      if (!f.bandVisible) {
        out += '<div><span class="key">הרצועה צרה מכדי להיראות בקנה המידה הזה.</span></div>';
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
      sl.min = n0;
      sl.max = top;
      if (st.N > top) st.N = top;
      if (st.N < n0) st.N = n0;
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
        st.N = Math.max(n0, s.Nmin);
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
    if (!divergent) st.N = Math.max(n0, scan(eps(), st.L).Nmin);
    refresh();
  }

  global.SeqLimit = { mount: mount };

})(window);
