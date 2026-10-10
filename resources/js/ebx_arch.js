/* ebx_arch.js — THE ARCH: the top 3/7 of the mission annulus, with the globe
 * at the circle's centre (built for the profile on 2026-10-07; moved to the top
 * of News in the 10/9 Reshuffle, 2026-10-09: "The globe and 3/7 annulus display
 * from profile is now at the top" — and News is "either all-encompassing, or
 * toggled by a specific mission").
 *
 *   EBX.Arch.mount(el, {
 *     onSelect(missionId, section),   // a sector was clicked (null = cleared)
 *     selected: missionId,            // the sector to light up as chosen
 *     left(api), right(api),          // HTML for the cards beside the globe
 *     onWeek(api),                    // the week changed (swipe / arrows / keys)
 *   })  →  api { state, step(dir), select(id), repaint(), sections(), weekLabel() }
 *
 * A sector is a MISSION; its three layers are that mission's initiative
 * election (inner) · organization election (middle) · budget day (outer). For
 * cycle week w (the middle sector is w's cause):
 *   left  (+1)  the initiative election that closes at the end of w (inner lit)
 *   middle (0)  the organization election that closes at the end of w (middle lit)
 *   right (−1)  the budget day of the organization election that closed as w began (outer lit)
 * A mission opened in week s is cause s mod 7; its initiative election closes
 * s+7, its organization election s+15, budget day s+22. Swipe (drag), the
 * buttons or the arrow keys move one week; the ring turns one sector.
 *
 * Needs ebx_shared.js (EBX.config, EBX.Cycle) and, for land on the globe, the
 * vendored d3-array, d3-geo and ebx_land110m.js. Styles: ebx_frontend.css
 * § THE ARCH. Everything it says is public: the leaders come from the
 * initiatives' totals and each organization race's tally.
 */
(function () {
  'use strict';
  const E = window.EBX = window.EBX || {};
  const WK = 7 * 864e5;
  const A7 = 360 / 7;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = d => d ? d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—';
  const causes = () => ((E.config && E.config.causes) || []).slice().sort((a, b) => a.index - b.index);
  const causeAt = i => causes().find(c => c.index === ((i % 7) + 7) % 7) || null;
  const tivOf = id => ((E.config && E.config.initiatives) || []).find(t => t.id === id) || null;
  const tivTitle = id => { const t = tivOf(id); return t ? t.title : (id || ''); };
  const orgName = id => { const o = ((E.config && E.config.organizations) || []).find(x => x.id === id); return o ? o.name : (id || ''); };
  const G0 = () => E.config.cycleStart.getTime();
  const weekDate = w => new Date(G0() + w * WK);
  const weekOf = d => Math.round((new Date(d).getTime() - G0()) / WK);
  // Same anchors as ebx_wheel.js / ebx_steps.js.
  const ANCHOR = { 'atmosphere': [38, -20], 'oceans': [-10, -150], 'land': [10, 25], 'forests': [-5, -60],
    'wildlife': [-20, 30], 'human-rights': [45, 10], 'human-progress': [20, 80] };
  const LAYER = ['Initiative election', 'Organization election', 'Budget day'];
  const SHORT = ['Initiative', 'Organization', 'Budget day'];
  const ROLE_WORD = { me: 'Initiative election', oe: 'Organization election', prep: 'Budget day' };

  let _uid = 0;
  function make(root, opts) {
    const uid = 'ar' + (++_uid);
    const S = { offset: 0, geo: null, busy: false, sel: opts.selected || null, p2: {}, asked: {},
                globe: { lon: 25, target: 25, lat: -10, raf: 0, last: 0 } };
    const weekNow = () => E.Cycle.now().weekNum;

    function section(rel, w) {
      const role = rel > 0 ? 'me' : (rel === 0 ? 'oe' : 'prep');
      const s = role === 'me' ? w - 7 + rel : w - 14 + rel;
      const cause = causeAt(s);
      const m = ((E.config && E.config.missions) || []).find(x => x.cause_id === (cause && cause.id) && weekOf(x.started_at) === s) || null;
      return { rel, role, s, cause, mission: m, id: m ? m.id : null,
        focus: role === 'me' ? 0 : (role === 'oe' ? 1 : 2),
        dates: [weekDate(s + 7), weekDate(s + 15), weekDate(s + 22)] };
    }
    const visible = w => [1, 0, -1].map(r => section(r, w));

    // ── who leads (public) ─────────────────────────────────────────────
    function leadTiv(m) {
      const ins = ((E.config && E.config.initiatives) || []).filter(i => i.mission_id === m.id)
        .sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0));
      return ins[0] && (ins[0].committed_ebx || 0) > 0 ? ins[0] : null;
    }
    function leadOrg(m) {
      const t = S.p2[m.id];
      const es = ((t && t.entries) || []).slice().sort((a, b) => (b.net_votes || 0) - (a.net_votes || 0) || (b.ebx || 0) - (a.ebx || 0));
      return es[0] ? es[0].org_id : null;
    }
    async function loadTallies(secs) {
      const want = secs.filter(x => x.mission && x.mission.winning_tiv_id && !x.mission.winning_org_id && !S.asked[x.id]);
      if (!want.length) return false;
      want.forEach(x => { S.asked[x.id] = true; });
      await Promise.all(want.map(async x => {
        try { const r = await fetch('/missions/' + encodeURIComponent(x.id) + '/p2/tally'); if (r.ok) S.p2[x.id] = await r.json(); } catch (e) {}
      }));
      return true;
    }
    function focalLine(sec) {
      const m = sec.mission;
      if (!m) return 'Opens ' + fmt(weekDate(sec.s));
      if (sec.role === 'me') {
        if (m.winning_tiv_id) return tivTitle(m.winning_tiv_id) + ' won';
        const l = leadTiv(m);
        return l ? l.title + ' leading' : 'No votes yet — be the first';
      }
      if (sec.role === 'oe') {
        const t = m.winning_tiv_id ? tivTitle(m.winning_tiv_id) : 'No initiative elected';
        if (m.winning_org_id) return t + ' — ' + orgName(m.winning_org_id);
        const o = leadOrg(m);
        return t + (o ? ' — ' + orgName(o) + ' leading' : '');
      }
      const t = m.winning_tiv_id ? tivTitle(m.winning_tiv_id) : 'No initiative elected';
      return m.winning_org_id ? t + ' — run by ' + orgName(m.winning_org_id) : t + ' — no organization yet';
    }

    // ── geometry ─────────────────────────────────────────────────────────
    function geom() {
      const W = Math.max(320, root.clientWidth || document.documentElement.clientWidth);
      const desk = W >= 900;
      const Ro = desk ? Math.min(W / 2 - 10, opts.maxRadius || 700) : Math.max(W * 0.95, 320);
      const band = desk ? Math.max(42, Math.min(58, Ro * 0.085)) : 36;
      const Ri = Ro - 3 * band;
      const top = desk ? 36 : 54;
      const cy = top + Ro, cx = W / 2;
      const Rg = desk ? Ri * 0.44 : Math.min(Ri * 0.52, W / 2 - 40);
      const H = Math.round(cy + Rg + 18);
      const endY = cy - Ri * Math.sin((90 - 1.5 * A7) * Math.PI / 180);
      return { W, desk, Ro, band, Ri, cx, cy, Rg, H, endY };
    }
    const rad = a => a * Math.PI / 180;
    const P = (g, a, r) => [g.cx + r * Math.cos(rad(a)), g.cy + r * Math.sin(rad(a))];
    const f1 = n => Math.round(n * 10) / 10;
    function bandPath(g, a0, a1, r0, r1) {
      const p0 = P(g, a0, r1), p1 = P(g, a1, r1), p2 = P(g, a1, r0), p3 = P(g, a0, r0);
      return 'M' + f1(p0[0]) + ',' + f1(p0[1]) + ' A' + r1 + ',' + r1 + ' 0 0 1 ' + f1(p1[0]) + ',' + f1(p1[1]) +
        ' L' + f1(p2[0]) + ',' + f1(p2[1]) + ' A' + r0 + ',' + r0 + ' 0 0 0 ' + f1(p3[0]) + ',' + f1(p3[1]) + ' Z';
    }
    function arcPath(g, a0, a1, r) {
      const p0 = P(g, a0, r), p1 = P(g, a1, r);
      return 'M' + f1(p0[0]) + ',' + f1(p0[1]) + ' A' + r + ',' + r + ' 0 0 1 ' + f1(p1[0]) + ',' + f1(p1[1]);
    }
    function fit(text, arcLen, px) {
      const max = Math.max(4, Math.floor(arcLen / (px * 0.62)));
      text = String(text || '');
      return text.length > max ? text.slice(0, max - 1).replace(/\s+\S*$/, '') + '…' : text;
    }

    function sectorSVG(g, sec) {
      const c = sec.cause; if (!c) return '';
      const mid = -90 - sec.rel * A7, gap = 0.5;
      const a0 = mid - A7 / 2 + gap, a1 = mid + A7 / 2 - gap;
      const now = Date.now();
      const chosen = !!(S.sel && sec.id && S.sel === sec.id);
      // a mission is named by its cause and number everywhere ("Land 2" — the
      // hub, the weekly report, the cards); the id stays in the data attribute
      const name = (c.name || '') + (sec.mission ? ' ' + ((sec.mission.cycle_num || 0) + 1) : '');
      let out = '<g class="ar-sec' + (chosen ? ' ar-sec--on' : '') + '" data-rel="' + sec.rel + '"' + (sec.id ? ' data-m="' + esc(sec.id) + '" tabindex="0" role="button" aria-pressed="' + chosen + '" aria-label="' + esc(name + ' — ' + ROLE_WORD[sec.role]) + '"' : '') + '>';
      for (let j = 0; j < 3; j++) {
        const r0 = g.Ri + j * g.band + 1.2, r1 = g.Ri + (j + 1) * g.band - 1.2;
        const focal = j === sec.focus;
        const op = focal ? 0.9 : 0.16 + j * 0.05;
        out += '<path class="ar-band" d="' + bandPath(g, a0, a1, r0, r1) + '" fill="' + c.color + '" fill-opacity="' + op +
          '" style="--hov:' + (focal ? 1 : op + 0.12) + '" stroke="rgba(255,255,255,' + (chosen ? 0.9 : (focal ? 0.35 : 0.08)) + ')" stroke-width="' + (chosen ? 1.6 : 0.8) + '"/>';
        const d = sec.dates[j], past = d.getTime() <= now;
        const rm = (r0 + r1) / 2;
        if (focal) {
          const ra = rm + (g.desk ? 4 : 3), rb = rm - (g.desk ? 11 : 9);
          const la = rad(a1 - a0) * ra - 14, lb = rad(a1 - a0) * rb - 14;
          const l1 = LAYER[j].toUpperCase() + ' · ' + (j === 2 ? (past ? 'WAS ' : '') : (past ? 'CLOSED ' : 'CLOSES ')) + fmt(d).toUpperCase();
          const id = uid + 'a' + sec.rel + 'j' + j;
          out += '<path id="' + id + 'a" d="' + arcPath(g, a0, a1, ra) + '" fill="none"/>' +
            '<path id="' + id + 'b" d="' + arcPath(g, a0, a1, rb) + '" fill="none"/>' +
            '<text class="ar-t1"><textPath href="#' + id + 'a" startOffset="50%" text-anchor="middle">' + esc(fit(l1, la, 10.5)) + '</textPath></text>' +
            '<text class="ar-t2"><textPath href="#' + id + 'b" startOffset="50%" text-anchor="middle">' + esc(fit(focalLine(sec), lb, 12.5)) + '</textPath></text>';
        } else {
          const r = rm - 3, len = rad(a1 - a0) * r - 12, id = uid + 'a' + sec.rel + 'j' + j;
          const done = past && ((j === 0 && sec.mission && sec.mission.winning_tiv_id) || (j === 1 && sec.mission && sec.mission.winning_org_id) || j === 2);
          const l = SHORT[j] + ' · ' + fmt(d) + (done ? ' ✓' : '');
          out += '<path id="' + id + '" d="' + arcPath(g, a0, a1, r) + '" fill="none"/>' +
            '<text class="ar-t0"><textPath href="#' + id + '" startOffset="50%" text-anchor="middle">' + esc(fit(l, len, 9.5)) + '</textPath></text>';
        }
      }
      const rl = g.Ro + 10, ll = rad(a1 - a0) * rl - 10, idl = uid + 'l' + sec.rel;
      const mine = opts.mine ? opts.mine(sec) : null;
      out += '<path id="' + idl + '" d="' + arcPath(g, a0, a1, rl) + '" fill="none"/>' +
        '<text class="ar-tl"><textPath href="#' + idl + '" startOffset="50%" text-anchor="middle">' +
        esc(fit(name.toUpperCase(), ll - (mine ? 70 : 0), 10)) +
        (mine ? '<tspan class="you"> · ● ' + esc(mine) + '</tspan>' : '') +
        (chosen ? '<tspan class="you"> · SHOWING</tspan>' : '') +
        '</textPath></text>';
      return out + '</g>';
    }

    function archSVG(g) {
      const w = weekNow() + S.offset;
      const secs = [2, 1, 0, -1, -2].map(r => section(r, w));
      const half = 1.5 * A7;
      const R = g.Ro + 40;
      const c0 = P(g, -90 - half, R), c1 = P(g, -90 + half, R);
      const clip = 'M' + g.cx + ',' + g.cy + ' L' + f1(c0[0]) + ',' + f1(c0[1]) + ' A' + R + ',' + R + ' 0 0 1 ' + f1(c1[0]) + ',' + f1(c1[1]) + ' Z';
      return '<svg class="ar-arch" data-ar="arch" width="' + g.W + '" height="' + g.H + '" viewBox="0 0 ' + g.W + ' ' + g.H + '" role="group" aria-label="This week’s three missions, on the mission annulus — pick one to read its news">' +
        '<defs><clipPath id="' + uid + '-wedge"><path d="' + clip + '"/></clipPath>' +
        '<radialGradient id="' + uid + '-sea" cx="38%" cy="32%"><stop offset="0" stop-color="#2c5168"/><stop offset="1" stop-color="#0d2230"/></radialGradient>' +
        '<radialGradient id="' + uid + '-halo" cx="50%" cy="50%"><stop offset=".7" stop-color="rgba(143,206,157,0.10)"/><stop offset="1" stop-color="rgba(143,206,157,0)"/></radialGradient></defs>' +
        '<g clip-path="url(#' + uid + '-wedge)"><g class="ar-ring" data-ar="ring" style="transform-origin:' + g.cx + 'px ' + g.cy + 'px">' +
        secs.map(sec => sectorSVG(g, sec)).join('') + '</g></g>' +
        '<g data-ar="globe"><circle cx="' + g.cx + '" cy="' + g.cy + '" r="' + (g.Rg * 1.18) + '" fill="url(#' + uid + '-halo)"/>' +
        '<circle cx="' + g.cx + '" cy="' + g.cy + '" r="' + g.Rg + '" fill="url(#' + uid + '-sea)"/>' +
        '<path class="ar-grat"/><path class="ar-land"/><g class="ar-marks"></g>' +
        '<circle cx="' + g.cx + '" cy="' + g.cy + '" r="' + g.Rg + '" fill="none" stroke="rgba(255,255,255,0.18)"/></g>' +
        '</svg>';
    }

    // ── the globe ────────────────────────────────────────────────────────
    function globeFrame() {
      const g = S.geo, gr = root.querySelector('[data-ar="globe"]');
      if (!g || !gr) return;
      const Gs = S.globe;
      const land = gr.querySelector('.ar-land'), grat = gr.querySelector('.ar-grat'), marks = gr.querySelector('.ar-marks');
      if (window.d3 && d3.geoOrthographic) {
        const proj = d3.geoOrthographic().scale(g.Rg).translate([g.cx, g.cy]).clipAngle(90).rotate([-Gs.lon, Gs.lat, 0]).precision(0.7);
        const path = d3.geoPath(proj);
        if (window.EBX_LAND) land.setAttribute('d', path(window.EBX_LAND) || '');
        grat.setAttribute('d', path(d3.geoGraticule10()) || '');
        const mid = section(0, weekNow() + S.offset).cause;
        let mk = '';
        causes().forEach(c => {
          const a = ANCHOR[c.id]; if (!a) return;
          if (d3.geoDistance([a[1], a[0]], [Gs.lon, -Gs.lat]) >= Math.PI / 2) return;
          const q = proj([a[1], a[0]]), on = mid && mid.id === c.id;
          mk += '<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="' + (on ? 6 : 3) + '" fill="' + c.color +
            '" stroke="rgba(255,255,255,' + (on ? 0.95 : 0.4) + ')" stroke-width="' + (on ? 1.6 : 0.8) + '"/>';
        });
        marks.innerHTML = mk;
      }
    }
    function spin(ts) {
      const Gs = S.globe;
      Gs.raf = requestAnimationFrame(spin);
      if (document.hidden || ts - Gs.last < 40) return;
      Gs.last = ts;
      const d = ((Gs.target - Gs.lon + 540) % 360) - 180;
      if (Math.abs(d) > 0.3) Gs.lon += d * 0.06; else { Gs.lon += 0.06; Gs.target = Gs.lon; }
      globeFrame();
    }
    function aimGlobe() {
      const c = section(0, weekNow() + S.offset).cause, a = c && ANCHOR[c.id];
      if (a) { S.globe.target = a[1]; S.globe.lat = -Math.max(-30, Math.min(30, a[0] * 0.6)); }
    }

    // ── the week navigator ───────────────────────────────────────────────
    function weekLabel() {
      return S.offset === 0 ? 'This week' : (S.offset === 1 ? 'Next week' : (S.offset === -1 ? 'Last week'
        : (S.offset > 0 ? S.offset + ' weeks ahead' : -S.offset + ' weeks ago')));
    }
    function weekNavHTML(g) {
      const w = weekNow() + S.offset;
      const [L, M, R] = visible(w);
      const end = weekDate(w + 1);
      // possessive: "Land's", "Oceans'", "Human Progress'"
      const cn = sec => { const n = sec.cause ? sec.cause.name : ''; return esc(n) + (/s$/i.test(n) ? '&rsquo;' : '&rsquo;s'); };
      return '<div class="ar-weeknav" data-ar="weeknav"' + (g.desk ? ' style="top:' + Math.round(g.cy - g.Ri + Math.min(40, g.band)) + 'px"' : '') + '>' +
        '<div class="ar-weeknav__k">' + esc(weekLabel()) + '</div>' +
        '<div class="ar-weeknav__t">' + fmt(weekDate(w)) + ' – ' + fmt(end) + '</div>' +
        '<div class="ar-weeknav__s">' + cn(L) + ' initiative election and ' + cn(M) + ' organization election close ' + fmt(end) +
        '. ' + cn(R) + ' budget day is ' + fmt(R.dates[2]) + '.</div>' +
        '<div class="ar-weeknav__btns">' +
          '<button type="button" class="ar-btn" data-ar-step="-1" aria-label="Previous week">&larr; Last week</button>' +
          (S.offset ? '<button type="button" class="ar-btn" data-ar-step="0">This week</button>' : '') +
          '<button type="button" class="ar-btn" data-ar-step="1" aria-label="Next week">Next week &rarr;</button>' +
        '</div>' +
        '<div class="ar-legend"><span><i></i>Inner · initiative</span><span><i class="l2"></i>Middle · organization</span><span><i class="l3"></i>Outer · budget day</span></div>' +
      '</div>';
    }

    // ── painting ─────────────────────────────────────────────────────────
    // Desktop: the row sits INSIDE the stage, its padding bringing the cards down
    // to where the arch's ends leave room — either side of the globe. Phones:
    // after the stage and the week navigator, stacked.
    function rowHTML(g) {
      const left = opts.left ? opts.left(api) : '', right = opts.right ? opts.right(api) : '';
      if (!left && !right) return '';
      return '<div class="ar-row" data-ar="row" style="padding-top:' + Math.round(g.desk ? g.endY + 18 : 8) + 'px;grid-template-columns:minmax(0,1fr) ' + Math.round(2 * g.Rg + 36) + 'px minmax(0,1fr)">' +
        '<div class="ar-side ar-side--l" data-ar="left">' + left + '</div><div class="ar-row__gap"></div><div class="ar-side ar-side--r" data-ar="right">' + right + '</div></div>';
    }
    function paint() {
      const g = S.geo = geom();
      root.classList.add('ar');
      root.innerHTML = '<div class="ar-stage" data-ar="stage" style="min-height:' + g.H + 'px">' + archSVG(g) +
          (g.desk ? weekNavHTML(g) + rowHTML(g) : '') +
        '</div>' + (g.desk ? '' : weekNavHTML(g) + rowHTML(g));
      bind();
      globeFrame();
    }
    function repaintSides() {
      const l = root.querySelector('[data-ar="left"]'), r = root.querySelector('[data-ar="right"]');
      if (l && opts.left) l.innerHTML = opts.left(api);
      if (r && opts.right) r.innerHTML = opts.right(api);
    }
    function repaintArch() {
      const g = S.geo; if (!g) return paint();
      const old = root.querySelector('[data-ar="arch"]');
      if (!old) return paint();
      const tmp = document.createElement('div'); tmp.innerHTML = archSVG(g);
      old.replaceWith(tmp.firstChild);
      const nav = root.querySelector('[data-ar="weeknav"]');
      if (nav) { const t2 = document.createElement('div'); t2.innerHTML = weekNavHTML(g); nav.replaceWith(t2.firstChild); }
      repaintSides();
      bind();
      aimGlobe(); globeFrame();
    }

    async function step(dir) {
      if (S.busy) return;
      const ring = root.querySelector('[data-ar="ring"]');
      const target = dir === 0 ? 0 : S.offset + dir;
      if (target === S.offset) return;
      S.busy = true;
      const turn = target - S.offset;
      if (ring && Math.abs(turn) === 1 && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
        ring.classList.remove('instant');
        ring.style.transform = 'rotate(' + (turn * A7) + 'deg)';
        await new Promise(r => setTimeout(r, 460));
      }
      S.offset = target;
      repaintArch();
      S.busy = false;
      if (await loadTallies(visible(weekNow() + S.offset))) repaintArch();
      if (opts.onWeek) opts.onWeek(api);
    }
    function select(id, quiet) {
      S.sel = id || null;
      repaintArch();
      if (!quiet && opts.onSelect) {
        const sec = id ? [2, 1, 0, -1, -2].map(r => section(r, weekNow() + S.offset)).find(x => x.id === id) || null : null;
        opts.onSelect(S.sel, sec);
      }
    }

    function bind() {
      root.querySelectorAll('[data-ar-step]').forEach(b => b.onclick = () => step(+b.dataset.arStep));
      const svg = root.querySelector('[data-ar="arch"]'), ring = root.querySelector('[data-ar="ring"]');
      if (!svg || !ring) return;
      svg.querySelectorAll('.ar-sec[data-m]').forEach(el => {
        el.addEventListener('click', () => { if (svg._dragged) return; select(S.sel === el.dataset.m ? null : el.dataset.m); });
        el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(S.sel === el.dataset.m ? null : el.dataset.m); } });
      });
      let x0 = null, dx = 0, pid = null;
      svg.onpointerdown = e => { if (S.busy) return; x0 = e.clientX; dx = 0; pid = e.pointerId; svg._dragged = false; };
      svg.onpointermove = e => {
        if (x0 == null || e.pointerId !== pid) return;
        dx = e.clientX - x0;
        if (!svg._dragged && Math.abs(dx) > 6) {
          svg._dragged = true; svg.classList.add('dragging'); ring.classList.add('instant');
          try { svg.setPointerCapture(pid); } catch (err) {}
        }
        if (svg._dragged) {
          const deg = Math.max(-A7, Math.min(A7, dx / S.geo.Ro * 180 / Math.PI));
          ring.style.transform = 'rotate(' + deg + 'deg)';
        }
      };
      const end = () => {
        if (x0 == null) return;
        const dragged = svg._dragged;
        x0 = null; svg.classList.remove('dragging');
        if (!dragged) return;
        ring.classList.remove('instant');
        const deg = dx / S.geo.Ro * 180 / Math.PI;
        if (Math.abs(deg) > A7 * 0.28) step(deg > 0 ? 1 : -1);
        else ring.style.transform = 'rotate(0deg)';
        setTimeout(() => { svg._dragged = false; }, 50);
      };
      svg.onpointerup = end; svg.onpointercancel = end;
    }
    document.addEventListener('keydown', e => {
      if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
      if (document.querySelector('.ebw-bg, .pf-modal-bg, .mxc-bg:not([hidden])')) return;
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft') step(-1);
    });
    let rz = 0;
    window.addEventListener('resize', () => {
      clearTimeout(rz);
      rz = setTimeout(() => { const g = geom(); if (!S.geo || Math.abs(g.W - S.geo.W) > 4) paint(); }, 150);
    });

    const api = {
      state: S, step, select, repaint: () => paint(), repaintSides,
      sections: () => visible(weekNow() + S.offset), weekLabel, focalLine, section,
      weekStart: () => weekDate(weekNow() + S.offset), weekEnd: () => weekDate(weekNow() + S.offset + 1),
    };
    aimGlobe(); S.globe.lon = S.globe.target;
    paint();
    loadTallies(visible(weekNow())).then(changed => { if (changed) repaintArch(); });
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) S.globe.raf = requestAnimationFrame(spin);
    return api;
  }

  E.Arch = { mount: (el, opts) => {
    const root = typeof el === 'string' ? document.querySelector(el) : el;
    return root ? make(root, opts || {}) : null;
  } };
})();
