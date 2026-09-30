"use strict";
/* ebx_steps.js — HOME'S FIVE STEPS (P2 · Home mods, 2026-09-30).
 *
 * Jax, INSTRUCTIONS › P2 › Home mods: "To the right of the hero, put 5 pages
 * that automatically page every 10 seconds or so from cause-initiative-
 * organization-network-reporting … images and diagrams that are visually
 * aesthetic and represent the 5 steps. Each section will contain little arrows
 * pointing to the left or right to make clear that it's just one step in the
 * process. The transitions should have a fade effect. Each section will have a
 * short message about the step. This will be the only text in this section."
 *
 *   EBX.Steps.mount('#ebx-steps')            // this week's cause
 *   EBX.Steps.mount(el, { cause: 'oceans' }) // any cause
 *
 * One page = one scene = one SVG, driven by a 10-second timeline (`update(t)`),
 * so a manual page restarts its scene from 0. The five scenes hand one object
 * along — THE SECTOR (the cause's segment of the annulus):
 *
 *   1 Cause         the week's segment leaves the rotating annulus, grows,
 *                   shows its cause's vista and beams down on the globe.
 *   2 Initiative    the segment opens to fill the frame; the camera pans the
 *                   vista past three problems, a cursor votes one, it glows.
 *   3 Organization  the voted sector shrinks and is handed to a team — people,
 *                   a building, a van — who pour money, people and supplies
 *                   into it until the problem heals.
 *   4 Network       people all around send ideas, messages, photos and votes
 *                   into the sector; the whole map closes into one coin.
 *   5 Reporting     a news crew takes the coin in and sends articles, photos
 *                   and video out to people, who trade missions (coins).
 *
 * The vistas and problems are drawn here, one panorama per cause (PANOS), as
 * placeholders: "As we report on real missions, we will get real images to
 * replace this." Swapping one in is a change to that cause's PANOS entry only.
 *
 * Self-contained: no network of its own (causes come from EBX.config when
 * loaded, else a built-in list), d3-geo + EBX_LAND for the globe when present
 * (a plain sphere otherwise), and its CSS is injected once. Honors
 * prefers-reduced-motion (no autoplay; each page is a still of its scene) and
 * pauses off-screen and in a hidden tab.
 */
(function () {
  const E = window.EBX = window.EBX || {};
  const NS = 'http://www.w3.org/2000/svg';
  const W = 640, H = 440, DUR = 10;

  const STEPS = [
    { key: 'cause', name: 'Cause', msg: 'A fresh focus each week' },
    { key: 'initiative', name: 'Initiative', msg: 'Broad causes → narrow missions' },
    { key: 'organization', name: 'Organization', msg: 'Identify those worthy of the job' },
    { key: 'network', name: 'Network', msg: 'Collaborate and create a plan' },
    { key: 'reporting', name: 'Reporting', msg: 'Regular updates and built in control' },
  ];

  // When EBX.config.causes is empty (no API): the seven, as the API serves them.
  const FALLBACK = [
    { id: 'atmosphere', index: 0, name: 'Atmosphere', color: '#6baed6' },
    { id: 'oceans', index: 1, name: 'Oceans', color: '#3182bd' },
    { id: 'land', index: 2, name: 'Land', color: '#74c476' },
    { id: 'forests', index: 3, name: 'Forests', color: '#31a354' },
    { id: 'wildlife', index: 4, name: 'Wildlife', color: '#e6550d' },
    { id: 'human-rights', index: 5, name: 'Human Rights', color: '#756bb1' },
    { id: 'human-progress', index: 6, name: 'Human Progress', color: '#bdbdbd' },
  ];
  // [lat, lon] — the same anchors as ebx_wheel.js / profile.html.
  const ANCHOR = {
    'atmosphere': [38, -20], 'oceans': [-10, -150], 'land': [10, 25],
    'forests': [-5, -60], 'wildlife': [-20, 30], 'human-rights': [45, 10],
    'human-progress': [20, 80],
  };
  const PEOPLE = ['#e8a84c', '#8ec5e8', '#8fce9d', '#c9a6d8', '#f28f6b', '#efe6d4', '#6baed6', '#e6c35c'];

  // ── helpers ────────────────────────────────────────────────────────────
  function h(tag, a, p) {
    const e = document.createElementNS(NS, tag);
    if (a) for (const k in a) if (a[k] != null) e.setAttribute(k, a[k]);
    if (p) p.appendChild(e);
    return e;
  }
  const G = (p, a) => h('g', a, p);
  const clamp = (v, a, b) => Math.max(a == null ? 0 : a, Math.min(b == null ? 1 : b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ez = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const eo = t => 1 - Math.pow(1 - t, 3);
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const es = (t, a, b) => ez(seg(t, a, b));
  const eos = (t, a, b) => eo(seg(t, a, b));
  const f2 = n => (Math.round(n * 100) / 100);
  function tr(el, x, y, s, r) {
    el.setAttribute('transform', 'translate(' + f2(x) + ' ' + f2(y) + ')' +
      (s != null && s !== 1 ? ' scale(' + (Math.round(s * 1e4) / 1e4) + ')' : '') + (r ? ' rotate(' + f2(r) + ')' : ''));
  }
  const op = (el, v) => el.setAttribute('opacity', Math.round(clamp(v) * 1000) / 1000);
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  const quad = (p0, p1, p2, t) => [
    (1 - t) * (1 - t) * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
    (1 - t) * (1 - t) * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]];
  function pol(cx, cy, r, deg) { const a = (deg - 90) * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
  function sector(cx, cy, r0, r1, a0, a1) {
    const p0 = pol(cx, cy, r1, a0), p1 = pol(cx, cy, r1, a1), p2 = pol(cx, cy, r0, a1), p3 = pol(cx, cy, r0, a0);
    const lg = (a1 - a0) > 180 ? 1 : 0, n = v => f2(v);
    return 'M' + n(p0[0]) + ',' + n(p0[1]) + 'A' + r1 + ',' + r1 + ' 0 ' + lg + ' 1 ' + n(p1[0]) + ',' + n(p1[1]) +
      'L' + n(p2[0]) + ',' + n(p2[1]) + 'A' + r0 + ',' + r0 + ' 0 ' + lg + ' 0 ' + n(p3[0]) + ',' + n(p3[1]) + 'Z';
  }
  const A7 = 360 / 7, HALF = A7 / 2;
  // THE SECTOR, normalized: the top segment of a ring (r 80–120) with its
  // mid-band at the origin. ~104 × 48; every scene scales this one shape.
  const SEG = sector(0, 100, 80, 120, -HALF, HALF);
  // A mountain / wave line: base − amp·(three sines), closed down to `bottom`.
  function ridge(x0, x1, base, amp, seed, o) {
    o = o || {};
    const r = rng(seed), f = o.freq || 1, bottom = o.bottom == null ? 900 : o.bottom, step = o.step || 10;
    const ph = [r() * 6, r() * 6, r() * 6], fr = [0.004 * f, 0.011 * f, 0.027 * f];
    const y = x => {
      let v = 0.55 * Math.sin(x * fr[0] + ph[0]) + 0.3 * Math.sin(x * fr[1] + ph[1]) + 0.15 * Math.sin(x * fr[2] + ph[2]);
      if (o.sharp) v = 1 - Math.abs(v) * 2;
      return base - amp * v;
    };
    let d = 'M' + x0 + ',' + bottom;
    for (let x = x0; x <= x1 + step; x += step) d += 'L' + x + ',' + f2(y(Math.min(x, x1)));
    return { d: d + 'L' + x1 + ',' + bottom + 'Z', y };
  }
  function pine(x, y, hgt, w) {
    w = w || hgt * 0.42;
    return 'M' + f2(x) + ',' + f2(y - hgt) + 'L' + f2(x + w * 0.5) + ',' + f2(y - hgt * 0.45) + 'L' + f2(x + w * 0.3) + ',' + f2(y - hgt * 0.45) +
      'L' + f2(x + w * 0.62) + ',' + f2(y) + 'L' + f2(x - w * 0.62) + ',' + f2(y) + 'L' + f2(x - w * 0.3) + ',' + f2(y - hgt * 0.45) +
      'L' + f2(x - w * 0.5) + ',' + f2(y - hgt * 0.45) + 'Z';
  }
  function grad(defs, id, stops, o) {
    o = o || {};
    const gr = h(o.radial ? 'radialGradient' : 'linearGradient', Object.assign({ id }, o.attrs || {}), defs);
    stops.forEach(s => h('stop', { offset: s[0], 'stop-color': s[1], 'stop-opacity': s[2] == null ? 1 : s[2] }, gr));
    return gr;
  }
  const use = (p, id, a) => h('use', Object.assign({ href: '#' + id }, a || {}), p);

  // ── the CSS (injected once) ────────────────────────────────────────────
  const CSS = `
.sx{--sx-c:#e8a84c;position:relative;display:flex;flex-direction:column;border-radius:18px;overflow:hidden;
  background:#0c1510;border:1px solid rgba(245,240,232,.12);box-shadow:0 30px 80px -40px rgba(0,0,0,.8),0 0 0 1px rgba(0,0,0,.2)}
.sx__stage{position:relative;aspect-ratio:${W}/${H};width:100%}
.sx__scene{position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .8s ease;display:block}
.sx__scene.on{opacity:1}
.sx__defs{position:absolute;width:0;height:0;overflow:hidden}
.sx__bar{display:flex;align-items:center;gap:14px;padding:14px 18px 16px;border-top:1px solid rgba(245,240,232,.08);
  background:linear-gradient(180deg,rgba(245,240,232,.02),transparent)}
.sx__msg{flex:1;min-width:0;margin:0;font-family:var(--font-display,serif);font-weight:700;letter-spacing:-.01em;
  font-size:clamp(1.02rem,1.9vw,1.32rem);line-height:1.25;color:var(--clr-parchment,#f5f0e8);}
.sx__msg.in{animation:sxIn .5s ease}
@keyframes sxIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
.sx__dots{display:flex;gap:6px;flex:0 0 auto}
.sx__dot{position:relative;width:26px;height:6px;padding:0;border:0;border-radius:3px;cursor:pointer;overflow:hidden;
  background:rgba(245,240,232,.16)}
.sx__dot span{position:absolute;inset:0;background:var(--sx-c);transform-origin:left;transform:scaleX(0)}
.sx__dot.done span{transform:scaleX(1);opacity:.45}
.sx__dot:focus-visible{outline:2px solid var(--sx-c);outline-offset:3px}
.sx__arrow{position:absolute;top:50%;z-index:2;width:34px;height:34px;margin-top:-17px;display:grid;place-items:center;padding:0;
  border-radius:50%;cursor:pointer;color:var(--clr-parchment,#f5f0e8);background:rgba(12,21,16,.55);
  border:1px solid rgba(245,240,232,.22);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);transition:background .15s,border-color .15s,transform .15s}
.sx__arrow:hover{background:rgba(12,21,16,.8);border-color:var(--sx-c)}
.sx__arrow:focus-visible{outline:2px solid var(--sx-c);outline-offset:2px}
.sx__arrow--prev{left:10px}.sx__arrow--next{right:10px}
.sx__arrow--prev:hover{transform:translateX(-2px)}.sx__arrow--next:hover{transform:translateX(2px)}
.sx-anim-drift{animation:sxDrift 5s ease-in infinite;transform-box:fill-box;transform-origin:50% 100%}
.sx-anim-drift2{animation:sxDrift 6.5s ease-in infinite 1.8s;transform-box:fill-box;transform-origin:50% 100%}
.sx-anim-flick{animation:sxFlick .9s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:50% 100%}
.sx-anim-bob{animation:sxBob 3.2s ease-in-out infinite alternate}
.sx-anim-tw{animation:sxTw 1.8s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}
@keyframes sxDrift{0%{transform:translate(0,0) scale(.85);opacity:.9}100%{transform:translate(14px,-26px) scale(1.25);opacity:0}}
@keyframes sxFlick{0%{transform:scale(1,1)}100%{transform:scale(.9,1.12)}}
@keyframes sxBob{0%{transform:translateY(0)}100%{transform:translateY(3px)}}
@keyframes sxTw{0%{opacity:.25;transform:scale(.7)}100%{opacity:1;transform:scale(1.1)}}
@media (prefers-reduced-motion:reduce){.sx__scene{transition:none}.sx-anim-drift,.sx-anim-drift2,.sx-anim-flick,.sx-anim-bob,.sx-anim-tw{animation:none}}
`;
  function injectCSS() {
    if (document.getElementById('sx-css')) return;
    const s = document.createElement('style');
    s.id = 'sx-css'; s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  }

  // ══ ICONS ═══════════════════════════════════════════════════════════════
  function icons(d) {
    // a person: fill = currentColor, feet at the origin
    const p = G(d, { id: 'sx-i-person' });
    h('circle', { cx: 0, cy: -27, r: 7.2, fill: 'currentColor' }, p);
    h('path', { d: 'M-12.5,0C-12.5,-13 -9,-17.5 0,-17.5C9,-17.5 12.5,-13 12.5,0Z', fill: 'currentColor' }, p);
    const ph = G(d, { id: 'sx-i-phone' });
    h('rect', { x: -4, y: -7, width: 8, height: 14, rx: 1.8, fill: '#1a232b', stroke: '#c9d6df', 'stroke-width': 0.8 }, ph);
    h('rect', { x: -2.8, y: -5.4, width: 5.6, height: 10, rx: 0.8, fill: '#8ec5e8' }, ph);
    const lp = G(d, { id: 'sx-i-laptop' });
    h('rect', { x: -10, y: -13, width: 20, height: 13, rx: 1.5, fill: '#1a232b', stroke: '#c9d6df', 'stroke-width': 0.8 }, lp);
    h('rect', { x: -8.3, y: -11.4, width: 16.6, height: 9.6, fill: '#8ec5e8' }, lp);
    h('path', { d: 'M-13,0L13,0L11,3L-11,3Z', fill: '#c9d6df' }, lp);
    const bu = G(d, { id: 'sx-i-bulb' });
    h('circle', { cx: 0, cy: 0, r: 13, fill: '#ffe08a', opacity: 0.25 }, bu);
    h('path', { d: 'M0,-9C5.5,-9 8,-5 8,-1.5C8,2.5 4.5,4 4,8L-4,8C-4.5,4 -8,2.5 -8,-1.5C-8,-5 -5.5,-9 0,-9Z', fill: '#ffd966', stroke: '#fff3c4', 'stroke-width': 0.8 }, bu);
    h('rect', { x: -3.6, y: 8.5, width: 7.2, height: 4, rx: 1, fill: '#b7c2c9' }, bu);
    const en = G(d, { id: 'sx-i-env' });
    h('rect', { x: -9, y: -6, width: 18, height: 12, rx: 1.5, fill: '#f5f0e8' }, en);
    h('path', { d: 'M-9,-5.5L0,1.5L9,-5.5', fill: 'none', stroke: '#b9ae99', 'stroke-width': 1.2 }, en);
    const pt = G(d, { id: 'sx-i-photo' });
    h('rect', { x: -10, y: -8, width: 20, height: 16, rx: 1.5, fill: '#f5f0e8' }, pt);
    h('rect', { x: -8, y: -6, width: 16, height: 12, fill: '#7fb6d9' }, pt);
    h('path', { d: 'M-8,6L-3,-1L1,3L4,0L8,6Z', fill: '#4f8a55' }, pt);
    h('circle', { cx: 4, cy: -3, r: 1.6, fill: '#ffe08a' }, pt);
    const dc = G(d, { id: 'sx-i-doc' });
    h('path', { d: 'M-8,-10L4,-10L8,-6L8,10L-8,10Z', fill: '#f5f0e8' }, dc);
    [-5, -2, 1, 4, 7].forEach((y, i) => h('rect', { x: -5.5, y, width: i === 0 ? 8 : 11, height: 1.3, fill: i === 0 ? '#c97c2a' : '#9a927f' }, dc));
    const vd = G(d, { id: 'sx-i-video' });
    h('rect', { x: -11, y: -8, width: 22, height: 16, rx: 2.5, fill: '#16242d', stroke: '#f5f0e8', 'stroke-width': 1 }, vd);
    h('path', { d: 'M-3,-4.5L5,0L-3,4.5Z', fill: '#e8a84c' }, vd);
    const up = G(d, { id: 'sx-i-up' });
    h('circle', { r: 9, fill: '#8fce9d' }, up);
    h('path', { d: 'M-4,2L0,-3L4,2', fill: 'none', stroke: '#0f1a14', 'stroke-width': 2.2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, up);
    const dn = G(d, { id: 'sx-i-down' });
    h('circle', { r: 9, fill: '#e8826b' }, dn);
    h('path', { d: 'M-4,-2L0,3L4,-2', fill: 'none', stroke: '#0f1a14', 'stroke-width': 2.2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, dn);
    const ht = G(d, { id: 'sx-i-heart' });
    h('path', { d: 'M0,7C-9,1 -9,-6 -4.5,-7C-2,-7.5 -0.5,-6 0,-4.5C0.5,-6 2,-7.5 4.5,-7C9,-6 9,1 0,7Z', fill: '#f28f9b' }, ht);
    const cr = G(d, { id: 'sx-i-crate' });
    h('rect', { x: -8, y: -7, width: 16, height: 14, rx: 1, fill: '#b98149', stroke: '#7a5230', 'stroke-width': 1 }, cr);
    h('path', { d: 'M-8,-7L8,7M8,-7L-8,7', stroke: '#7a5230', 'stroke-width': 1 }, cr);
    const cn = G(d, { id: 'sx-i-coin' });
    h('circle', { r: 8, fill: 'url(#sx-coin)', stroke: '#9a6517', 'stroke-width': 1 }, cn);
    h('circle', { r: 5.2, fill: 'none', stroke: '#fff1c4', 'stroke-width': 0.8, opacity: 0.7 }, cn);
    const bub = G(d, { id: 'sx-i-bubble' });
    h('path', { d: 'M-16,-11L16,-11Q20,-11 20,-7L20,5Q20,9 16,9L-2,9L-8,15L-7,9L-16,9Q-20,9 -20,5L-20,-7Q-20,-11 -16,-11Z', fill: '#f5f0e8' }, bub);
    [-8, 0, 8].forEach(x => h('circle', { cx: x, cy: -1, r: 2.2, fill: '#6f6a5c' }, bub));
  }

  // a coin with a cause ring and the sector embossed
  function bigCoin(p, color, r) {
    const c = G(p);
    h('circle', { r: r + 10, fill: color, opacity: 0.18, filter: 'url(#sx-glow)' }, c);
    h('circle', { r, fill: 'url(#sx-coin)', stroke: '#9a6517', 'stroke-width': 2 }, c);
    h('circle', { r: r - 7, fill: 'none', stroke: color, 'stroke-width': 5 }, c);
    h('circle', { r: r - 12, fill: 'none', stroke: '#fff1c4', 'stroke-width': 1, opacity: 0.55 }, c);
    h('path', { d: SEG, transform: 'scale(' + (r / 70) + ')', fill: '#b77a22', stroke: '#fff1c4', 'stroke-width': 70 / r, opacity: 0.9 }, c);
    return c;
  }
  function bg(svg, id) {
    h('rect', { width: W, height: H, fill: 'url(#' + (id || 'sx-bg') + ')' }, svg);
  }
  function stars(p, n, seed) {
    const r = rng(seed), out = [];
    for (let i = 0; i < n; i++) {
      out.push({ el: h('circle', { cx: f2(r() * W), cy: f2(r() * H * 0.8), r: f2(0.4 + r() * 1.1), fill: '#f5f0e8' }, p), ph: r() * 6, sp: 0.8 + r() * 1.6 });
    }
    return t => out.forEach(s => op(s.el, 0.15 + 0.35 * (0.5 + 0.5 * Math.sin(t * s.sp + s.ph))));
  }

  // ══ THE PANORAMAS — one per cause, 1920 × 440, three problems each ══════
  // Spot 1 (the middle one) is the one voted in scene 2 and healed in scene 3.
  const SPOT_X = [560, 960, 1360];

  function smoke(p, x, y, s, color, cls) {
    const g = G(p, { transform: 'translate(' + x + ' ' + y + ') scale(' + s + ')' });
    const a = G(g, { class: cls || 'sx-anim-drift' });
    [[0, 0, 9], [7, -9, 11], [-2, -20, 13], [9, -31, 15], [2, -44, 17]].forEach(c =>
      h('circle', { cx: c[0], cy: c[1], r: c[2], fill: color, opacity: 0.8 }, a));
    return g;
  }
  function flame(p, x, y, s) {
    const g = G(p, { transform: 'translate(' + x + ' ' + y + ') scale(' + s + ')' });
    const a = G(g, { class: 'sx-anim-flick' });
    h('path', { d: 'M0,0C-9,-4 -10,-16 -3,-26C-3,-18 2,-18 1,-30C9,-20 11,-8 0,0Z', fill: '#ff8c32' }, a);
    h('path', { d: 'M0,0C-5,-3 -5,-10 -1,-16C0,-11 3,-11 3,-17C7,-10 6,-3 0,0Z', fill: '#ffe08a' }, a);
    return g;
  }
  function heal(p, color) {
    // the generic healed state: light, sprouts, sparkles
    h('ellipse', { cx: 0, cy: 8, rx: 90, ry: 42, fill: 'url(#sx-healglow)' }, p);
    const r = rng(7);
    for (let i = 0; i < 7; i++) {
      const x = -60 + i * 20 + r() * 8, y = 26 + r() * 10, s = 0.7 + r() * 0.5;
      const g = G(p, { transform: 'translate(' + f2(x) + ' ' + f2(y) + ') scale(' + f2(s) + ')' });
      h('path', { d: 'M0,0Q1,-8 0,-15', stroke: '#6fbf73', 'stroke-width': 1.8, fill: 'none' }, g);
      h('ellipse', { cx: -4, cy: -11, rx: 4.5, ry: 2.2, transform: 'rotate(-30 -4 -11)', fill: '#8fce9d' }, g);
      h('ellipse', { cx: 4, cy: -14, rx: 4.5, ry: 2.2, transform: 'rotate(30 4 -14)', fill: '#a8e0b0' }, g);
    }
    for (let i = 0; i < 6; i++) {
      const x = -70 + r() * 140, y = -30 + r() * 40, s = 0.6 + r() * 0.7;
      const g = G(p, { transform: 'translate(' + f2(x) + ' ' + f2(y) + ') scale(' + f2(s) + ')' });
      h('path', { d: 'M0,-7L1.5,-1.5L7,0L1.5,1.5L0,7L-1.5,1.5L-7,0L-1.5,-1.5Z', fill: '#fff6d8', class: 'sx-anim-tw', style: 'animation-delay:' + f2(r() * 1.8) + 's' }, g);
    }
  }

  function skyRect(p, defs, stops, horizon) {
    grad(defs, 'sx-sky', stops, { attrs: { gradientUnits: 'userSpaceOnUse', x1: 0, y1: -300, x2: 0, y2: horizon } });
    h('rect', { x: -400, y: -600, width: 2720, height: horizon + 620, fill: 'url(#sx-sky)' }, p);
  }
  function sun(p, x, y, r, color, glow) {
    h('circle', { cx: x, cy: y, r: r * (glow || 3), fill: color, opacity: 0.12 }, p);
    h('circle', { cx: x, cy: y, r: r * 1.6, fill: color, opacity: 0.22 }, p);
    h('circle', { cx: x, cy: y, r, fill: color }, p);
  }
  function cloud(p, x, y, s, color, o) {
    const g = G(p, { transform: 'translate(' + x + ' ' + y + ') scale(' + s + ')', opacity: o == null ? 0.8 : o });
    [[0, 0, 26], [26, -8, 30], [56, 2, 24], [-26, 6, 18], [30, 12, 22]].forEach(c => h('circle', { cx: c[0], cy: c[1], r: c[2], fill: color }, g));
    h('rect', { x: -40, y: 6, width: 118, height: 22, rx: 11, fill: color }, g);
  }
  function ground(p, defs, id, top, a, b) {
    grad(defs, id, [[0, a], [1, b]], { attrs: { gradientUnits: 'userSpaceOnUse', x1: 0, y1: top, x2: 0, y2: 440 } });
    return id;
  }
  function birds(p, x, y, n, seed, color) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
      const bx = x + r() * 120, by = y + r() * 40, s = 0.6 + r() * 0.6;
      h('path', { d: 'M' + f2(bx - 6 * s) + ',' + f2(by) + 'Q' + f2(bx - 3 * s) + ',' + f2(by - 4 * s) + ' ' + f2(bx) + ',' + f2(by) +
        'Q' + f2(bx + 3 * s) + ',' + f2(by - 4 * s) + ' ' + f2(bx + 6 * s) + ',' + f2(by), fill: 'none', stroke: color, 'stroke-width': 1.3 }, p);
    }
  }
  const person = (p, x, y, s, color) => use(p, 'sx-i-person', { transform: 'translate(' + f2(x) + ' ' + f2(y) + ') scale(' + s + ')', style: 'color:' + color });

  const PANOS = {
    oceans: {
      y: [300, 318, 302],
      base(p, d) {
        skyRect(p, d, [[0, '#08203d'], [0.55, '#35608f'], [0.85, '#d98b6a'], [1, '#f7c07a']], 252);
        sun(p, 960, 240, 34, '#ffd89b');
        cloud(p, 300, 120, 1.3, '#f0b29a', 0.3); cloud(p, 1500, 90, 1.6, '#f0b29a', 0.28); cloud(p, 1050, 60, 1, '#f8d0b5', 0.2);
        birds(p, 1150, 150, 6, 3, '#1c2a3a');
        h('path', { d: ridge(120, 460, 254, 26, 11, { bottom: 254 }).d, fill: '#243b5c' }, p);
        h('path', { d: ridge(1560, 1840, 254, 18, 12, { bottom: 254 }).d, fill: '#243b5c' }, p);
        const sea = ground(p, d, 'sx-sea', 250, '#2a5d8f', '#07182b');
        h('rect', { x: -400, y: 250, width: 2720, height: 700, fill: 'url(#' + sea + ')' }, p);
        for (let i = 0; i < 14; i++) {
          const y = 256 + i * i * 1.1 + i * 3, w = 30 + i * 9;
          h('rect', { x: 960 - w / 2, y, width: w, height: 1.6 + i * 0.25, rx: 1, fill: '#ffd89b', opacity: f2(0.55 - i * 0.035) }, p);
        }
        const r = rng(21), wv = G(p, { class: 'sx-anim-bob' });
        for (let i = 0; i < 90; i++) {
          const y = 262 + r() * 180, x = -100 + r() * 2120, w = 10 + (y - 250) * 0.25;
          h('path', { d: 'M' + f2(x) + ',' + f2(y) + 'q' + f2(w / 2) + ',-' + f2(w / 8) + ' ' + f2(w) + ',0', fill: 'none', stroke: '#bfe0f2', 'stroke-width': 1, opacity: f2(0.08 + (y - 250) / 900) }, wv);
        }
      },
      pb: [
        function (p) { // the garbage patch
          h('ellipse', { cx: 0, cy: 6, rx: 82, ry: 20, fill: '#6d6250', opacity: 0.5 }, p);
          const r = rng(5), cs = ['#e76f51', '#f4a261', '#e9c46a', '#f1faee', '#2a9d8f', '#d62828', '#8ecae6'];
          for (let i = 0; i < 46; i++) {
            const a = r() * Math.PI * 2, rr = Math.sqrt(r()), x = Math.cos(a) * rr * 74, y = 6 + Math.sin(a) * rr * 16;
            if (r() < 0.5) h('rect', { x: f2(x), y: f2(y), width: f2(4 + r() * 5), height: 2.6, rx: 1.3, transform: 'rotate(' + f2(r() * 180) + ' ' + f2(x) + ' ' + f2(y) + ')', fill: cs[i % cs.length] }, p);
            else h('path', { d: 'M' + f2(x) + ',' + f2(y) + 'q3,-5 7,-1 q-1,4 -7,1Z', fill: cs[(i * 3) % cs.length], opacity: 0.9 }, p);
          }
        },
        function (p) { // the tanker and its slick
          h('ellipse', { cx: 10, cy: 20, rx: 92, ry: 22, fill: '#0b0b0e', opacity: 0.82 }, p);
          ['#6a4c93', '#1982c4', '#8ac926', '#c77dff'].forEach((c, i) =>
            h('ellipse', { cx: 14 - i * 6, cy: 20 + i, rx: 70 - i * 12, ry: 15 - i * 2.5, fill: 'none', stroke: c, 'stroke-width': 1, opacity: 0.45 }, p));
          h('path', { d: 'M-70,-2L50,-2L40,12L-62,12Z', fill: '#5a1f1f' }, p);
          h('rect', { x: -70, y: -6, width: 120, height: 4, fill: '#2b2b2b' }, p);
          h('rect', { x: 18, y: -24, width: 22, height: 18, fill: '#e6e0d2' }, p);
          h('rect', { x: 22, y: -34, width: 6, height: 10, fill: '#2b2b2b' }, p);
          smoke(p, 25, -36, 0.5, '#3a3a3a');
        },
        function (p) { // a ghost net
          const g = G(p, { opacity: 0.9 });
          for (let i = -6; i <= 6; i++) {
            h('path', { d: 'M' + (i * 12 - 30) + ',-18L' + (i * 12 + 30) + ',30', stroke: '#c8b89a', 'stroke-width': 0.9 }, g);
            h('path', { d: 'M' + (i * 12 + 30) + ',-18L' + (i * 12 - 30) + ',30', stroke: '#c8b89a', 'stroke-width': 0.9 }, g);
          }
          [-78, -40, 0, 40, 78].forEach(x => h('circle', { cx: x, cy: -18, r: 4, fill: '#f77f00' }, p));
          [[-26, 6, 1], [18, 14, -1], [44, 0, 1]].forEach(f => h('path', {
            d: 'M0,0q10,-7 20,0q-10,7 -20,0Zm20,0l7,-5l0,10Z', transform: 'translate(' + f[0] + ' ' + f[1] + ') scale(' + f[2] + ' 1)', fill: '#9fb7c4' }, p));
        },
      ],
    },
    atmosphere: {
      y: [298, 305, 296],
      base(p, d) {
        skyRect(p, d, [[0, '#0e2f55'], [0.5, '#3f7fb5'], [0.85, '#a9cde6'], [1, '#f3dcae']], 262);
        sun(p, 1560, 100, 30, '#fff6d0', 4);
        cloud(p, 250, 110, 1.9, '#ffffff', 0.85); cloud(p, 820, 70, 1.4, '#ffffff', 0.75); cloud(p, 1180, 150, 1.1, '#f4f7fb', 0.7);
        cloud(p, 1750, 170, 1.5, '#ffffff', 0.8); cloud(p, 1420, 40, 0.9, '#ffffff', 0.55);
        birds(p, 600, 180, 5, 9, '#20364d');
        h('path', { d: ridge(-400, 2320, 262, 34, 31, { freq: 0.8 }).d, fill: '#7f9fb8' }, p);
        h('path', { d: ridge(-400, 2320, 300, 30, 32).d, fill: '#5c8a63' }, p);
        const city = G(p, { fill: '#6d879b' }), r = rng(33);
        for (let x = 1640; x < 1900; x += 14) { const hh = 20 + r() * 50; h('rect', { x, y: 290 - hh, width: 12, height: hh + 10 }, city); }
        h('path', { d: ridge(-400, 2320, 350, 26, 34).d, fill: '#3f6e44' }, p);
        h('path', { d: ridge(-400, 2320, 405, 20, 35).d, fill: '#2d5733' }, p);
      },
      pb: [
        function (p) { // smokestacks
          h('rect', { x: -60, y: -4, width: 110, height: 36, fill: '#4a4f57' }, p);
          h('path', { d: 'M-60,-4L-40,-18L-20,-4L0,-18L20,-4L40,-18L50,-10L50,-4Z', fill: '#5b6069' }, p);
          [-44, -10, 24].forEach((x, i) => {
            h('rect', { x, y: -64 + i * 6, width: 10, height: 62 - i * 6, fill: '#6b6f78' }, p);
            h('rect', { x, y: -54 + i * 6, width: 10, height: 3, fill: '#c0392b' }, p);
            smoke(p, x + 5, -66 + i * 6, 1.1, '#4b4b4f', i % 2 ? 'sx-anim-drift2' : 'sx-anim-drift');
          });
          [-50, -30, -10, 10, 30].forEach(x => h('rect', { x, y: 8, width: 8, height: 6, fill: '#e8c46a', opacity: 0.8 }, p));
        },
        function (p) { // a gas flare
          h('path', { d: 'M-8,30L-2,-40L2,-40L8,30Z', fill: 'none', stroke: '#555b63', 'stroke-width': 2 }, p);
          for (let i = 0; i < 6; i++) h('path', { d: 'M' + (-7 + i * 0.9) + ',' + (24 - i * 11) + 'L' + (6.5 - i * 0.9) + ',' + (18 - i * 11), stroke: '#555b63', 'stroke-width': 1.2 }, p);
          h('rect', { x: -1.5, y: -52, width: 3, height: 14, fill: '#555b63' }, p);
          flame(p, 0, -52, 1.2);
          smoke(p, 6, -86, 1.5, '#5b4a3f');
          h('rect', { x: 20, y: 12, width: 40, height: 20, rx: 8, fill: '#8a8f96' }, p);
          h('rect', { x: -70, y: 16, width: 44, height: 16, rx: 7, fill: '#8a8f96' }, p);
          h('path', { d: 'M-26,24L20,24', stroke: '#6b6f78', 'stroke-width': 3 }, p);
        },
        function (p) { // coal plant cooling towers
          [[-34, 1], [22, 0.85]].forEach(t => {
            const s = t[1];
            h('path', { d: 'M' + (-24 * s) + ',30C' + (-16 * s) + ',' + (-10 * s) + ' ' + (-12 * s) + ',' + (-30 * s) + ' ' + (-16 * s) + ',' + (-44 * s) +
              'L' + (16 * s) + ',' + (-44 * s) + 'C' + (12 * s) + ',' + (-30 * s) + ' ' + (16 * s) + ',' + (-10 * s) + ' ' + (24 * s) + ',30Z',
              transform: 'translate(' + t[0] + ' 0)', fill: '#b9b6ae' }, p);
            smoke(p, t[0], -44 * s, 1.6 * s, '#e9e7e2');
          });
          h('rect', { x: 50, y: -30, width: 7, height: 60, fill: '#6b6f78' }, p);
          smoke(p, 53, -32, 0.9, '#3d3d40', 'sx-anim-drift2');
        },
      ],
    },
    land: {
      y: [300, 306, 300],
      base(p, d) {
        skyRect(p, d, [[0, '#1f3550'], [0.5, '#8a6a78'], [0.82, '#e3945e'], [1, '#f7d794']], 250);
        sun(p, 1250, 212, 28, '#fff1c1');
        cloud(p, 420, 110, 1.4, '#f6c7a2', 0.35); cloud(p, 1700, 90, 1.2, '#f6c7a2', 0.3);
        h('path', { d: ridge(-400, 2320, 250, 30, 41, { sharp: true, freq: 0.7 }).d, fill: '#6f5f80' }, p);
        const bands = [[285, 30, '#5f8a4a', 42], [318, 24, '#b8a04a', 43], [352, 22, '#6f9a45', 44], [390, 20, '#c9a95a', 45], [425, 16, '#557f36', 46]];
        bands.forEach(b => h('path', { d: ridge(-400, 2320, b[0], b[1], b[3]).d, fill: b[2] }, p));
        const r = rng(47), rows = G(p, { opacity: 0.18 });
        for (let i = 0; i < 60; i++) { const x = -200 + i * 38; h('path', { d: 'M' + x + ',440L' + (x + 60) + ',320', stroke: '#2e3b1c', 'stroke-width': 1 }, rows); }
        h('path', { d: 'M-400,432C200,410 500,440 900,428S1500,412 2320,436', fill: 'none', stroke: '#8fc1e3', 'stroke-width': 7, opacity: 0.8 }, p);
        [[160, 300], [1110, 312], [1760, 305]].forEach((b, i) => {
          h('rect', { x: b[0], y: b[1] - 16, width: 26, height: 16, fill: '#8e3b2e' }, p);
          h('path', { d: 'M' + (b[0] - 3) + ',' + (b[1] - 16) + 'L' + (b[0] + 13) + ',' + (b[1] - 28) + 'L' + (b[0] + 29) + ',' + (b[1] - 16) + 'Z', fill: '#5b2a22' }, p);
          if (i !== 1) h('rect', { x: b[0] + 34, y: b[1] - 26, width: 9, height: 26, rx: 4, fill: '#cfc6b0' }, p);
        });
        void r;
      },
      pb: [
        function (p) { // an open-pit mine
          [[84, 26, '#8a6a4a'], [66, 20, '#7a5b3e'], [48, 14, '#6a4d33'], [30, 9, '#5a3f28'], [14, 4, '#4a331f']].forEach((e, i) =>
            h('ellipse', { cx: 0, cy: 10 + i * 2, rx: e[0], ry: e[1], fill: e[2], stroke: '#a3845f', 'stroke-width': 0.8 }, p));
          h('rect', { x: 34, y: -6, width: 22, height: 10, rx: 2, fill: '#e0a526' }, p);
          h('circle', { cx: 38, cy: 6, r: 3.5, fill: '#222' }, p); h('circle', { cx: 52, cy: 6, r: 3.5, fill: '#222' }, p);
          smoke(p, -30, -8, 1.6, '#b39574'); smoke(p, 20, -12, 1.2, '#a88b69', 'sx-anim-drift2');
        },
        function (p) { // a landfill
          h('path', { d: 'M-88,30C-60,-10 -30,-30 0,-32C30,-30 60,-10 88,30Z', fill: '#6b6552' }, p);
          const r = rng(52), cs = ['#d9d4c7', '#e76f51', '#8ecae6', '#e9c46a', '#b5a88f', '#4d4d4d', '#f1faee'];
          for (let i = 0; i < 70; i++) {
            const x = -70 + r() * 140, top = -32 + Math.pow(Math.abs(x) / 88, 1.6) * 60, y = top + 4 + r() * (30 - top - 4);
            h('rect', { x: f2(x), y: f2(y), width: f2(3 + r() * 5), height: f2(2 + r() * 3), transform: 'rotate(' + f2(r() * 90) + ' ' + f2(x) + ' ' + f2(y) + ')', fill: cs[i % cs.length] }, p);
          }
          birds(p, -50, -64, 7, 53, '#2b2b2b');
          smoke(p, 30, -26, 0.9, '#8d8a7c');
        },
        function (p) { // drought — cracked soil, a dead tree
          h('ellipse', { cx: 0, cy: 14, rx: 92, ry: 26, fill: '#b08a5a' }, p);
          const r = rng(61);
          for (let i = 0; i < 22; i++) {
            const x = -70 + r() * 140, y = 2 + r() * 24;
            h('path', { d: 'M' + f2(x) + ',' + f2(y) + 'l' + f2(-8 + r() * 16) + ',' + f2(-3 + r() * 6) + 'l' + f2(-8 + r() * 16) + ',' + f2(-3 + r() * 6), fill: 'none', stroke: '#6e4e2c', 'stroke-width': 1 }, p);
          }
          h('path', { d: 'M20,14L22,-20L10,-40M22,-20L34,-36M21,-8L6,-18M22,-28L30,-50', fill: 'none', stroke: '#4a3421', 'stroke-width': 3, 'stroke-linecap': 'round' }, p);
          [-40, -22, -4].forEach(x => h('path', { d: 'M' + x + ',16l-2,-10l4,-4l2,6', fill: 'none', stroke: '#8a7040', 'stroke-width': 1.3 }, p));
        },
      ],
    },
    forests: {
      y: [322, 318, 324],
      base(p, d) {
        skyRect(p, d, [[0, '#18323f'], [0.55, '#6c9a93'], [1, '#e2ead9']], 250);
        sun(p, 700, 150, 30, '#fbf6e2', 3);
        const layers = [[215, 26, '#8fb3a6', 71, 34], [255, 30, '#5f8f7a', 72, 44], [300, 28, '#3c6b52', 73, 58], [352, 24, '#23473a', 74, 74]];
        layers.forEach((L, li) => {
          const rd = ridge(-400, 2320, L[0], L[1], L[3]);
          h('path', { d: rd.d, fill: L[2] }, p);
          const r = rng(L[3] + 100); let dd = '';
          for (let x = -400; x < 2320; x += 9 + r() * 12) dd += pine(x, rd.y(x) + 4, L[4] * (0.6 + r() * 0.6));
          h('path', { d: dd, fill: L[2] }, p);
          if (li < 3) h('rect', { x: -400, y: L[0] - 10, width: 2720, height: 40, fill: '#eef3ea', opacity: 0.12 }, p);
        });
        h('rect', { x: -400, y: 380, width: 2720, height: 600, fill: '#1a382c' }, p);
      },
      pb: [
        function (p) { // clear-cut
          h('path', { d: 'M-92,34C-70,-8 70,-8 92,34Z', fill: '#8a6a44' }, p);
          const r = rng(81);
          for (let i = 0; i < 16; i++) {
            const x = -64 + r() * 128, y = 4 + r() * 24;
            h('rect', { x: f2(x - 3), y: f2(y - 6), width: 6, height: 6, fill: '#6b4a2b' }, p);
            h('ellipse', { cx: f2(x), cy: f2(y - 6), rx: 3.2, ry: 1.4, fill: '#d9b27c' }, p);
          }
          [0, 5, 10].forEach(k => h('rect', { x: 30 - k, y: 12 + k * 0.6, width: 50, height: 5, rx: 2.5, fill: '#9c6b3d', stroke: '#6b4a2b', 'stroke-width': 0.6 }, p));
        },
        function (p) { // wildfire
          h('ellipse', { cx: 0, cy: 20, rx: 90, ry: 24, fill: '#ff7b25', opacity: 0.25 }, p);
          const r = rng(91);
          for (let i = 0; i < 9; i++) { const x = -70 + i * 17; h('path', { d: pine(x, 30, 40 + r() * 20), fill: '#1b120c' }, p); }
          for (let i = 0; i < 8; i++) flame(p, -66 + i * 19 + r() * 6, 30, 0.9 + r() * 0.8);
          smoke(p, -30, -40, 2.4, '#3c3533'); smoke(p, 30, -46, 2.2, '#4a403c', 'sx-anim-drift2');
        },
        function (p) { // invasive vines
          const r = rng(101);
          for (let i = 0; i < 6; i++) {
            const x = -60 + i * 24, hh = 50 + r() * 20;
            h('path', { d: pine(x, 30, hh), fill: '#2f5d48' }, p);
            let dd = 'M' + (x - 10) + ',30';
            for (let k = 0; k < 6; k++) dd += 'Q' + (x + (k % 2 ? 14 : -14)) + ',' + f2(30 - k * hh / 6 - 4) + ' ' + (x + (k % 2 ? -8 : 8)) + ',' + f2(30 - (k + 1) * hh / 6);
            h('path', { d: dd, fill: 'none', stroke: '#9b59b6', 'stroke-width': 2.4 }, p);
            for (let k = 0; k < 5; k++) h('circle', { cx: f2(x - 10 + r() * 20), cy: f2(30 - r() * hh), r: 2.4, fill: '#c39bd3' }, p);
          }
        },
      ],
    },
    wildlife: {
      y: [308, 312, 310],
      base(p, d) {
        skyRect(p, d, [[0, '#2a1440'], [0.5, '#8c3a4a'], [0.8, '#d9653b'], [1, '#f6b84b']], 280);
        sun(p, 960, 232, 58, '#ffcf70', 2.6);
        birds(p, 1250, 120, 7, 121, '#2a1420');
        h('path', { d: ridge(-400, 2320, 280, 8, 122, { bottom: 300 }).d, fill: '#5a2f2b' }, p);
        const pl = ground(p, d, 'sx-plain', 278, '#8a5230', '#3a2214');
        h('rect', { x: -400, y: 278, width: 2720, height: 700, fill: 'url(#' + pl + ')' }, p);
        const acacia = (x, y, s) => {
          const g = G(p, { transform: 'translate(' + x + ' ' + y + ') scale(' + s + ')', fill: '#1d100b' });
          h('path', { d: 'M-2,0L-1,-30L-14,-44M-1,-30L12,-46M-1,-22L-8,-30', stroke: '#1d100b', 'stroke-width': 3, fill: 'none' }, g);
          h('ellipse', { cx: 0, cy: -48, rx: 38, ry: 7 }, g); h('ellipse', { cx: -14, cy: -44, rx: 18, ry: 5 }, g); h('ellipse', { cx: 16, cy: -45, rx: 20, ry: 5 }, g);
        };
        acacia(140, 300, 1.6); acacia(760, 292, 1.1); acacia(1180, 296, 1.3); acacia(1620, 302, 1.8); acacia(1880, 290, 1);
        const giraffe = (x, y, s) => h('path', {
          d: 'M0,0L2,-26L-2,-30L0,-34L16,-34L18,-30L16,-26L18,0M4,-30L8,-34M14,-34L24,-66L30,-68L31,-64L27,-63L20,-34',
          transform: 'translate(' + x + ' ' + y + ') scale(' + s + ')', fill: 'none', stroke: '#1d100b', 'stroke-width': 3.2, 'stroke-linejoin': 'round' }, p);
        giraffe(230, 300, 1.2); giraffe(290, 304, 0.9);
        const eleph = (x, y, s) => h('path', {
          d: 'M0,0L0,-14C-2,-24 6,-34 22,-34C36,-34 44,-28 46,-18C50,-16 52,-8 50,0L46,0L46,-8L42,-6L40,0L34,0L33,-8L14,-8L13,0L7,0L6,-8L4,0Z',
          transform: 'translate(' + x + ' ' + y + ') scale(' + s + ')', fill: '#1d100b' }, p);
        eleph(1680, 310, 1.1); eleph(1760, 312, 0.8);
        const r = rng(125), gr = G(p, { stroke: '#b27a45', 'stroke-width': 1, opacity: 0.45 });
        for (let i = 0; i < 160; i++) { const x = -300 + r() * 2500, y = 300 + r() * 140; h('path', { d: 'M' + f2(x) + ',' + f2(y) + 'l-2,-7M' + f2(x) + ',' + f2(y) + 'l2,-8', fill: 'none' }, gr); }
      },
      pb: [
        function (p) { // a highway through the habitat
          h('path', { d: 'M-95,34L-40,-6L40,-6L95,34Z', fill: '#3a3a3a' }, p);
          h('path', { d: 'M0,-4L0,32', stroke: '#e9c46a', 'stroke-width': 2, 'stroke-dasharray': '6 5' }, p);
          for (let i = 0; i < 10; i++) h('rect', { x: -92 + i * 20, y: -16, width: 2, height: 16, fill: '#c9c1ae' }, p);
          h('path', { d: 'M-92,-12L90,-12M-92,-6L90,-6', stroke: '#c9c1ae', 'stroke-width': 0.8 }, p);
          h('path', { d: 'M-66,-18l2,-12l6,0l-2,-8l4,4l3,-6l0,10l8,2l0,10l-2,0l0,-6l-12,0l0,6Z', fill: '#1d100b' }, p);
          h('rect', { x: 22, y: 8, width: 30, height: 12, rx: 3, fill: '#c0392b' }, p);
        },
        function (p) { // a poisoned water hole
          h('ellipse', { cx: 0, cy: 14, rx: 86, ry: 22, fill: '#5d7f2a' }, p);
          h('ellipse', { cx: 0, cy: 14, rx: 70, ry: 15, fill: '#9adf3a', opacity: 0.7 }, p);
          h('ellipse', { cx: -12, cy: 12, rx: 30, ry: 5, fill: '#e0ff8a', opacity: 0.35 }, p);
          h('rect', { x: 50, y: -14, width: 16, height: 24, rx: 2, fill: '#6b4a2b', transform: 'rotate(20 58 -2)' }, p);
          h('path', { d: 'M52,6Q40,14 30,14', stroke: '#9adf3a', 'stroke-width': 3, fill: 'none' }, p);
          h('path', { d: 'M-40,8q8,-6 16,0q-8,4 -16,0Zm16,0l5,-3l0,6Z', fill: '#e7e2d5', opacity: 0.85 }, p);
          h('path', { d: 'M-62,-4q6,-10 16,-4l6,-2l-4,4q2,8 -8,8q-8,0 -10,-6Z', fill: '#2b1a12' }, p);
          smoke(p, 0, 6, 0.8, '#b9e36b');
        },
        function (p) { // a snare line
          h('path', { d: 'M-80,24L80,24', stroke: '#8a5a35', 'stroke-width': 2 }, p);
          [-50, 0, 50].forEach(x => {
            h('path', { d: 'M' + x + ',24L' + x + ',-6', stroke: '#6b4a2b', 'stroke-width': 3 }, p);
            h('ellipse', { cx: x + 9, cy: 4, rx: 9, ry: 12, fill: 'none', stroke: '#b8b8b8', 'stroke-width': 1.6 }, p);
          });
          h('path', { d: 'M-24,24C-24,14 -6,10 6,14L10,8L12,16C18,18 20,24 16,26L-20,28Z', fill: '#2b1a12' }, p);
        },
      ],
    },
    'human-rights': {
      y: [318, 318, 316],
      base(p, d) {
        skyRect(p, d, [[0, '#191c38'], [0.5, '#5b4b73'], [0.85, '#d98a8a'], [1, '#f8c3a0']], 258);
        sun(p, 420, 248, 26, '#ffe2b8', 3);
        cloud(p, 1200, 120, 1.4, '#f3b7a7', 0.3); cloud(p, 1700, 80, 1.1, '#f3b7a7', 0.25);
        h('path', { d: ridge(-400, 2320, 240, 70, 131, { sharp: true, freq: 0.9 }).d, fill: '#4a3d63' }, p);
        h('path', { d: ridge(-400, 2320, 290, 30, 132).d, fill: '#3a3252' }, p);
        const vil = G(p, { fill: '#2b2640' }), r = rng(133);
        for (let x = 1540; x < 1860; x += 26 + r() * 10) {
          const w = 20 + r() * 10, hh = 14 + r() * 10, y = 300;
          h('rect', { x, y: y - hh, width: w, height: hh + 10 }, vil);
          h('path', { d: 'M' + (x - 3) + ',' + (y - hh) + 'L' + (x + w / 2) + ',' + (y - hh - 10) + 'L' + (x + w + 3) + ',' + (y - hh) + 'Z' }, vil);
          if (r() < 0.6) h('rect', { x: x + w / 2 - 2, y: y - hh + 5, width: 4, height: 4, fill: '#f6c26b' }, p);
        }
        const gr = ground(p, d, 'sx-hrg', 300, '#3a3250', '#1a1726');
        h('path', { d: ridge(-400, 2320, 330, 12, 134).d, fill: 'url(#' + gr + ')' }, p);
      },
      pb: [
        function (p) { // a camp of tents
          const r = rng(141);
          for (let i = 0; i < 9; i++) {
            const x = -76 + (i % 5) * 36 + (i > 4 ? 18 : 0), y = i > 4 ? 26 : 8, s = i > 4 ? 1.1 : 0.9;
            h('path', { d: 'M' + (x - 14 * s) + ',' + y + 'L' + x + ',' + (y - 18 * s) + 'L' + (x + 14 * s) + ',' + y + 'Z', fill: r() < 0.3 ? '#8ab6d6' : '#e9e4d8' }, p);
            h('path', { d: 'M' + x + ',' + (y - 18 * s) + 'L' + (x + 3) + ',' + y + 'L' + (x - 3) + ',' + y + 'Z', fill: '#6d6a74' }, p);
          }
          person(p, 70, 34, 0.55, '#c9a6d8'); person(p, -88, 34, 0.5, '#e8a84c');
        },
        function (p) { // behind the wire
          for (let i = 0; i < 7; i++) person(p, -60 + i * 20, 22 - (i % 2) * 2, 0.62, ['#c9a6d8', '#e8a84c', '#8ec5e8', '#f28f6b'][i % 4]);
          for (let i = 0; i < 9; i++) h('rect', { x: -86 + i * 21, y: -34, width: 2.6, height: 68, fill: '#8a8a8a' }, p);
          for (let k = 0; k < 5; k++) h('path', { d: 'M-88,' + (-28 + k * 14) + 'L88,' + (-28 + k * 14), stroke: '#a9a9a9', 'stroke-width': 0.9 }, p);
          let dd = 'M-88,-36';
          for (let x = -88; x < 88; x += 6) dd += 'q3,-6 6,0';
          h('path', { d: dd, fill: 'none', stroke: '#cfcfcf', 'stroke-width': 1.3 }, p);
        },
        function (p) { // the long walk for water
          h('path', { d: 'M-90,34C-40,20 10,28 90,4', fill: 'none', stroke: '#b08a66', 'stroke-width': 10, opacity: 0.6 }, p);
          [[-60, 27, 0.7], [-30, 24, 0.66], [2, 22, 0.62], [34, 16, 0.58], [62, 10, 0.54]].forEach((q, i) => {
            person(p, q[0], q[1], q[2], ['#f28f6b', '#e6c35c', '#c9a6d8', '#8ec5e8', '#e8a84c'][i]);
            h('rect', { x: q[0] - 4, y: q[1] - 30 * q[2] - 14, width: 8, height: 9, rx: 2, fill: '#f4a261' }, p);
          });
        },
      ],
    },
    'human-progress': {
      y: [304, 306, 308],
      base(p, d) {
        skyRect(p, d, [[0, '#0b1a22'], [0.55, '#284f63'], [0.88, '#c98a5e'], [1, '#f0b27a']], 262);
        const r = rng(151);
        for (let i = 0; i < 50; i++) h('circle', { cx: f2(-300 + r() * 2500), cy: f2(-200 + r() * 330), r: f2(0.5 + r()), fill: '#f5f0e8', opacity: f2(0.3 + r() * 0.5) }, p);
        h('circle', { cx: 300, cy: 70, r: 16, fill: '#f5ecd2' }, p); h('circle', { cx: 307, cy: 65, r: 14, fill: '#1c3a4a' }, p);
        h('path', { d: ridge(-400, 2320, 262, 24, 152).d, fill: '#1f3a48' }, p);
        const city = G(p);
        for (let x = 1520; x < 1900; x += 18) {
          const hh = 30 + r() * 80;
          h('rect', { x, y: 290 - hh, width: 15, height: hh + 10, fill: '#17303c' }, city);
          for (let wy = 290 - hh + 5; wy < 285; wy += 8) for (let wx = 0; wx < 2; wx++) if (r() < 0.55) h('rect', { x: x + 3 + wx * 6, y: wy, width: 3, height: 3, fill: '#ffd98a', opacity: 0.85 }, city);
        }
        const gr = ground(p, d, 'sx-hpg', 290, '#243c46', '#0f1c22');
        h('path', { d: ridge(-400, 2320, 300, 10, 153).d, fill: 'url(#' + gr + ')' }, p);
        h('path', { d: 'M-400,300L2320,300', stroke: '#566b73', 'stroke-width': 0 }, p);
        for (let x = -300; x < 2300; x += 130) {
          h('path', { d: 'M' + x + ',300L' + x + ',250M' + (x - 8) + ',256L' + (x + 8) + ',256', stroke: '#3f555e', 'stroke-width': 2 }, p);
          if (x < 1420) h('path', { d: 'M' + x + ',256Q' + (x + 65) + ',266 ' + (x + 130) + ',256', fill: 'none', stroke: '#3f555e', 'stroke-width': 0.8 }, p);
        }
      },
      pb: [
        function (p) { // homes with no power
          [[-60, 0.9], [-20, 1.1], [24, 0.95], [62, 1]].forEach(q => {
            const x = q[0], s = q[1];
            h('rect', { x: x - 14 * s, y: 30 - 22 * s, width: 28 * s, height: 22 * s, fill: '#3b4a52' }, p);
            h('path', { d: 'M' + (x - 17 * s) + ',' + (30 - 22 * s) + 'L' + x + ',' + (30 - 36 * s) + 'L' + (x + 17 * s) + ',' + (30 - 22 * s) + 'Z', fill: '#2a353b' }, p);
            h('rect', { x: x - 4 * s, y: 30 - 14 * s, width: 8 * s, height: 7 * s, fill: '#11181c' }, p);
          });
          h('path', { d: 'M-90,-26L-50,-20', stroke: '#566b73', 'stroke-width': 1 }, p);
          h('path', { d: 'M-50,-20l4,6l-6,-2l4,8', fill: 'none', stroke: '#e8a84c', 'stroke-width': 1.2 }, p);
        },
        function (p) { // a broken school
          h('rect', { x: -56, y: -16, width: 112, height: 46, fill: '#8a6f5a' }, p);
          h('path', { d: 'M-64,-16L-10,-44L-4,-30L6,-40L64,-16Z', fill: '#5a3f33' }, p);
          h('path', { d: 'M-4,-30L6,-40L10,-16L-8,-16Z', fill: '#1d2a30' }, p);
          [-40, -12, 16].forEach(x => h('rect', { x, y: -4, width: 16, height: 12, fill: '#1d2a30' }, p));
          h('rect', { x: 36, y: 4, width: 12, height: 26, fill: '#3b2a22' }, p);
          h('path', { d: 'M-4,-30L-26,-2L-14,4', fill: 'none', stroke: '#1d2a30', 'stroke-width': 1.5 }, p);
          h('rect', { x: 60, y: 20, width: 20, height: 3, fill: '#a08060' }, p);
          h('path', { d: 'M62,23L62,32M78,23L78,32', stroke: '#a08060', 'stroke-width': 2 }, p);
        },
        function (p) { // a dry well
          h('ellipse', { cx: 0, cy: 20, rx: 84, ry: 18, fill: '#6e5a44' }, p);
          h('rect', { x: -20, y: -6, width: 40, height: 26, fill: '#8a7d6a' }, p);
          h('ellipse', { cx: 0, cy: -6, rx: 20, ry: 5, fill: '#2a2520' }, p);
          h('path', { d: 'M-22,-6L-22,-38L22,-38L22,-6M-26,-38L26,-38', stroke: '#5b4a38', 'stroke-width': 3, fill: 'none' }, p);
          h('path', { d: 'M0,-38L0,-18', stroke: '#c9c1ae', 'stroke-width': 1 }, p);
          h('path', { d: 'M-6,-18L6,-18L4,-10L-4,-10Z', fill: '#8a8f96' }, p);
          h('path', { d: 'M40,16l12,-2l4,8l-14,2Z', fill: '#8a8f96' }, p);
        },
      ],
    },
  };

  function buildPano(defs, cause) {
    const P = PANOS[cause.id] || PANOS.oceans;
    const g = G(defs, { id: 'sx-pano' });
    P.base(g, defs);
    const pbs = P.pb.map((fn, i) => {
      const pg = G(g, { id: 'sx-pb-' + i, transform: 'translate(' + SPOT_X[i] + ' ' + P.y[i] + ')' });
      fn(pg);
      return pg;
    });
    const hg = G(g, { id: 'sx-heal', transform: 'translate(' + SPOT_X[1] + ' ' + P.y[1] + ')', opacity: 0 });
    heal(hg, cause.color);
    return { spots: SPOT_X.map((x, i) => [x, P.y[i]]), pbs, heal: hg };
  }

  // THE SECTOR with a window onto the panorama at `spot` (or the whole vista).
  function sectorWindow(p, spot, o) {
    o = o || {};
    const g = G(p);
    const glow = h('path', { d: SEG, fill: o.color, filter: 'url(#sx-glow)', opacity: 0.5 }, g);
    const body = h('path', { d: SEG, fill: o.color }, g);
    const win = G(g, { 'clip-path': 'url(#sx-segclip)' });
    const inner = use(win, 'sx-pano', { transform: o.inner || ('scale(0.62) translate(' + (-spot[0]) + ' ' + (-spot[1] + 6) + ')') });
    const shine = h('path', { d: SEG, fill: 'url(#sx-segshine)' }, g);
    const edge = h('path', { d: SEG, fill: 'none', stroke: '#fff7e6', 'stroke-width': 1.2, 'vector-effect': 'non-scaling-stroke', opacity: 0.75 }, g);
    return { g, glow, body, win, inner, shine, edge };
  }

  // ══ SCENE 1 — CAUSE ═════════════════════════════════════════════════════
  function scene1(svg, C) {
    bg(svg, 'sx-bg1');
    const tw = stars(G(svg), 60, 3);
    const cx = 320, cy = 300;
    const ring = G(svg);
    const ci = C.causes.findIndex(c => c.id === C.cause.id);
    for (let k = 1; k < 7; k++) {
      const c = C.causes[(ci + k) % C.causes.length];
      const a = k * A7;
      h('path', { d: sector(0, 0, 80, 120, a - HALF + 1.4, a + HALF - 1.4), fill: c.color, opacity: 0.92 }, ring);
      h('path', { d: sector(0, 0, 112, 120, a - HALF + 1.4, a + HALF - 1.4), fill: '#ffffff', opacity: 0.12 }, ring);
    }
    h('path', { d: sector(0, 0, 80, 120, -HALF + 1.4, HALF - 1.4), fill: 'none', stroke: C.cause.color, 'stroke-width': 1.2, 'stroke-dasharray': '4 4', opacity: 0.45 }, ring);
    // the globe
    const gl = G(svg, { transform: 'translate(' + cx + ' ' + cy + ')' });
    h('circle', { r: 76, fill: C.cause.color, opacity: 0.1 }, gl);
    h('circle', { r: 66, fill: 'url(#sx-ocean)' }, gl);
    const grat = h('path', { fill: 'none', stroke: 'rgba(170,215,235,0.16)', 'stroke-width': 0.6 }, gl);
    const land = h('path', { fill: 'rgba(143,206,157,0.62)', stroke: 'rgba(220,240,225,0.35)', 'stroke-width': 0.4 }, gl);
    const hot = G(gl);
    const hotRing = h('circle', { r: 6, fill: 'none', stroke: '#fff6d8', 'stroke-width': 1.4 }, hot);
    h('circle', { r: 3, fill: '#fff6d8' }, hot);
    h('circle', { r: 66, fill: 'url(#sx-shade)', 'pointer-events': 'none' }, gl);
    const d3 = window.d3, LAND = window.EBX_LAND;
    const geo = d3 && d3.geoOrthographic && d3.geoPath ? (() => {
      const proj = d3.geoOrthographic().scale(66).translate([0, 0]).clipAngle(90);
      return { proj, path: d3.geoPath(proj), g10: d3.geoGraticule10 ? d3.geoGraticule10() : null };
    })() : null;
    const anc = ANCHOR[C.cause.id] || [0, 0];
    // the beam, then the detached sector over it
    const beam = h('path', { d: 'M' + (cx - 86) + ',176L' + (cx + 86) + ',176L' + (cx + 46) + ',' + (cy + 10) + 'L' + (cx - 46) + ',' + (cy + 10) + 'Z', fill: 'url(#sx-beam)', opacity: 0 }, svg);
    const S = sectorWindow(svg, null, { color: C.cause.color, inner: 'scale(0.17) translate(-960 -250)' });
    op(S.win, 0);
    let lastGeo = -1;
    return function (t) {
      tw(t);
      C.pano.pbs.forEach(pb => op(pb, 0)); op(C.pano.heal, 0);
      ring.setAttribute('transform', 'translate(' + cx + ' ' + cy + ') rotate(' + f2(-(t / DUR) * A7) + ')');
      op(ring, eos(t, 0, 0.9));
      const p = es(t, 0.9, 3.4);
      tr(S.g, cx, lerp(cy - 100, 104, p), lerp(1, 2.7, p));
      op(S.glow, 0.25 + 0.55 * p + 0.12 * Math.sin(t * 2.4) * p);
      op(S.win, es(t, 2.4, 4));
      S.inner.setAttribute('transform', 'scale(0.17) translate(' + f2(-960 + 160 - 320 * seg(t, 2.4, 10)) + ' -250)');
      op(beam, es(t, 3.4, 4.6) * (0.62 + 0.18 * Math.sin(t * 3.1)));
      // the globe turns slowly; the cause's point lights with the beam
      const lon = anc[1] + 30 - t * 3;
      if (geo && LAND && Math.abs(lon - lastGeo) > 0.2) {
        lastGeo = lon;
        geo.proj.rotate([-lon, -anc[0] + 8]);
        land.setAttribute('d', geo.path(LAND) || '');
        if (geo.g10) grat.setAttribute('d', geo.path(geo.g10) || '');
      }
      const pt = geo ? geo.proj([anc[1], anc[0]]) : [0, -10];
      if (pt) tr(hot, pt[0], pt[1]);
      op(hot, es(t, 3.8, 4.6));
      hotRing.setAttribute('r', f2(5 + 7 * ((t * 0.9) % 1)));
      op(hotRing, 1 - ((t * 0.9) % 1));
      op(gl, eos(t, 0, 0.9));
    };
  }

  // ══ SCENE 2 — INITIATIVE ═════════════════════════════════════════════════
  function scene2(svg, C) {
    bg(svg, 'sx-bg1');
    const clipPath = h('path', { d: SEG }, C.s2clip);
    const world = G(svg, { 'clip-path': 'url(#sx-s2clip)' });
    const cam = G(world);
    use(cam, 'sx-pano');
    const CH = 1;
    const marks = C.pano.spots.map((s, i) => {
      const m = G(cam, { transform: 'translate(' + s[0] + ' ' + (s[1] - 4) + ') scale(1.75)' });
      const glow = h('path', { d: SEG, fill: '#e8a84c', opacity: 0, filter: 'url(#sx-glow)' }, m);
      const fill = h('path', { d: SEG, fill: '#e8a84c', opacity: 0 }, m);
      const edge = h('path', { d: SEG, fill: 'none', stroke: '#fff7e6', 'stroke-width': 2, 'stroke-dasharray': '6 5', 'vector-effect': 'non-scaling-stroke' }, m);
      return { m, glow, fill, edge, i };
    });
    const cursor = G(svg, { opacity: 0 });
    const ripple = h('circle', { r: 4, fill: 'none', stroke: '#fff7e6', 'stroke-width': 2, opacity: 0 }, cursor);
    const arrow = h('path', { d: 'M0,0L0,22L6,16.5L10.5,26L14.5,24L10,15L18,15Z', fill: '#f5f0e8', stroke: '#0f1a14', 'stroke-width': 1.4, 'stroke-linejoin': 'round' }, cursor);
    const sp = C.pano.spots;
    const K = [ // t, cx, cy, s
      [0, 960, 250, 1], [1.4, 960, 250, 1], [2.7, sp[0][0], sp[0][1] - 6, 1.35], [3.6, sp[0][0], sp[0][1] - 6, 1.35],
      [4.9, sp[2][0], sp[2][1] - 6, 1.35], [5.8, sp[2][0], sp[2][1] - 6, 1.35], [6.9, 960, 250, 0.62], [10, 960, 250, 0.62],
    ];
    const camAt = t => {
      let i = 0; while (i < K.length - 2 && t > K[i + 1][0]) i++;
      const a = K[i], b = K[i + 1], q = es(t, a[0], b[0]);
      return [lerp(a[1], b[1], q), lerp(a[2], b[2], q), lerp(a[3], b[3], q)];
    };
    return function (t) {
      C.pano.pbs.forEach(pb => op(pb, 1)); op(C.pano.heal, 0);
      const p = es(t, 0, 1.4);
      clipPath.setAttribute('transform', 'translate(320 ' + f2(lerp(104, 220, p)) + ') scale(' + f2(lerp(2.7, 17, p)) + ')');
      const c = camAt(t);
      cam.setAttribute('transform', 'translate(320 220) scale(' + (Math.round(c[2] * 1e4) / 1e4) + ') translate(' + f2(-c[0]) + ' ' + f2(-c[1]) + ')');
      const click = 8.15;
      marks.forEach(k => {
        const vis = es(t, 1.4 + 0.15 * k.i, 2.2 + 0.15 * k.i);
        const chosen = k.i === CH, won = es(t, click, click + 0.5);
        op(k.edge, vis * (chosen ? 1 : 1 - 0.55 * won));
        k.edge.setAttribute('stroke', chosen && won > 0.01 ? '#e8a84c' : '#fff7e6');
        k.edge.setAttribute('stroke-dasharray', chosen && won > 0.5 ? 'none' : '6 5');
        op(k.fill, chosen ? won * (0.16 + 0.06 * Math.sin(t * 5)) : 0);
        op(k.glow, chosen ? won * (0.55 + 0.25 * Math.sin(t * 4)) : 0);
      });
      const tgt = [320 + (sp[CH][0] - 960) * 0.62 + 4, 220 + (sp[CH][1] - 4 - 250) * 0.62 + 2];
      const m = es(t, 6.9, 8.0);
      const cxp = lerp(560, tgt[0], m), cyp = lerp(420, tgt[1], m);
      const press = t > click - 0.08 && t < click + 0.18 ? 0.84 : 1;
      tr(cursor, cxp, cyp);
      arrow.setAttribute('transform', 'scale(' + press + ')');
      op(cursor, seg(t, 6.8, 7.2));
      const rp = seg(t, click, click + 0.9);
      ripple.setAttribute('r', f2(4 + 34 * rp)); op(ripple, rp > 0 ? 1 - rp : 0);
    };
  }

  // ══ SCENE 3 — ORGANIZATION ═══════════════════════════════════════════════
  function scene3(svg, C) {
    bg(svg);
    h('ellipse', { cx: 250, cy: 410, rx: 380, ry: 60, fill: '#1c2e22', opacity: 0.9 }, svg);
    // the building
    const bld = G(svg);
    h('rect', { x: 34, y: 150, width: 120, height: 220, rx: 3, fill: '#22382c', stroke: '#35523f', 'stroke-width': 1 }, bld);
    h('rect', { x: 34, y: 142, width: 120, height: 10, fill: '#2d4a38' }, bld);
    const r = rng(301);
    for (let y = 166; y < 350; y += 22) for (let x = 46; x < 146; x += 22) h('rect', { x, y, width: 12, height: 13, rx: 1.5, fill: r() < 0.6 ? '#e8c46a' : '#2f4a3a', opacity: 0.85 }, bld);
    h('rect', { x: 80, y: 340, width: 28, height: 30, fill: '#15241b' }, bld);
    h('path', { d: 'M94,142L94,104', stroke: '#8a9a8e', 'stroke-width': 2 }, bld);
    const flag = h('path', { d: 'M95,104L121,110L95,118Z', fill: C.cause.color }, bld);
    // the team at the table
    const team = G(svg);
    [[176, 345, 1.55, 0], [236, 338, 1.6, 1], [296, 345, 1.55, 2]].forEach(q => person(team, q[0], q[1], q[2], PEOPLE[q[3]]));
    h('ellipse', { cx: 236, cy: 356, rx: 112, ry: 22, fill: '#4a3a2c' }, team);
    h('ellipse', { cx: 236, cy: 352, rx: 112, ry: 22, fill: '#6b5440' }, team);
    use(team, 'sx-i-laptop', { transform: 'translate(236 350) scale(1.4)' });
    use(team, 'sx-i-doc', { transform: 'translate(190 350) rotate(-70) scale(0.8)' });
    use(team, 'sx-i-doc', { transform: 'translate(282 352) rotate(80) scale(0.8)' });
    [[140, 404, 1.9, 3], [332, 404, 1.9, 4]].forEach(q => person(team, q[0], q[1], q[2], PEOPLE[q[3]]));
    const bubbles = [[176, 270], [236, 262], [296, 270], [140, 318], [332, 318]].map((b, i) =>
      ({ el: use(svg, 'sx-i-bubble', { transform: 'translate(' + b[0] + ' ' + b[1] + ')', opacity: 0 }), b, i }));
    // the van
    const van = G(svg);
    h('rect', { x: -48, y: -30, width: 62, height: 30, rx: 4, fill: '#e9e4d8' }, van);
    h('path', { d: 'M14,-24L30,-24L40,-10L40,0L14,0Z', fill: '#d6d0c2' }, van);
    h('path', { d: 'M18,-21L29,-21L35,-11L18,-11Z', fill: '#8ec5e8' }, van);
    h('rect', { x: -48, y: -14, width: 62, height: 5, fill: C.cause.color }, van);
    [-32, 24].forEach(x => { h('circle', { cx: x, cy: 1, r: 7, fill: '#1a1a1a' }, van); h('circle', { cx: x, cy: 1, r: 3, fill: '#8a8a8a' }, van); });
    // the sector
    const S = sectorWindow(svg, C.pano.spots[1], { color: C.cause.color });
    // donations in, then money · people · supplies out
    const flow = G(svg);
    const R2 = rng(303);
    const coinsIn = Array.from({ length: 10 }, (_, i) => ({ el: use(flow, 'sx-i-coin', { opacity: 0 }), x0: 150 + R2() * 180, t0: 1.6 + i * 0.22 }));
    const types = ['sx-i-coin', 'sx-i-person', 'sx-i-crate', 'sx-i-coin', 'sx-i-crate', 'sx-i-person'];
    const outs = Array.from({ length: 30 }, (_, i) => {
      const ty = types[i % types.length], fromVan = ty === 'sx-i-crate' && i % 2 === 0;
      return { el: use(flow, ty, { opacity: 0, style: 'color:' + PEOPLE[i % PEOPLE.length] }), ty, fromVan, t0: 3.9 + i * 0.18, jit: R2() * 30 - 15 };
    });
    const SEC = [484, 176];
    return function (t) {
      const p = es(t, 0, 1.3);
      tr(S.g, lerp(320, SEC[0], p), lerp(104, SEC[1], p), lerp(2.7, 2.05, p));
      op(S.glow, 0.35 + 0.4 * es(t, 5, 9.4) + 0.1 * Math.sin(t * 3));
      op(S.win, 1);
      const healed = es(t, 5, 9.3);
      op(C.pano.pbs[1], 1 - 0.95 * healed); op(C.pano.heal, healed);
      C.pano.pbs.forEach((pb, i) => { if (i !== 1) op(pb, 1); });
      op(bld, eos(t, 0.8, 1.8)); tr(bld, 0, lerp(16, 0, eos(t, 0.8, 1.8)));
      op(team, eos(t, 1.1, 2.1)); tr(team, 0, lerp(16, 0, eos(t, 1.1, 2.1)));
      flag.setAttribute('d', 'M95,104Q108,' + f2(104 + 3 * Math.sin(t * 4)) + ' 121,' + f2(110 + 2 * Math.sin(t * 4 + 1)) + 'L95,118Z');
      bubbles.forEach(b => {
        const k = (t + b.i * 1.1) % 3.6, v = t > 1.8 ? (k < 0.3 ? k / 0.3 : k < 1.6 ? 1 : k < 1.9 ? (1.9 - k) / 0.3 : 0) : 0;
        op(b.el, v); b.el.setAttribute('transform', 'translate(' + b.b[0] + ' ' + f2(b.b[1] - 4 * v) + ') scale(' + f2(0.7 + 0.3 * v) + ')');
      });
      const vx = lerp(-80, 420, es(t, 2.4, 5.6));
      tr(van, vx, 408 + (t > 2.4 && t < 5.6 ? Math.sin(t * 30) * 0.6 : 0));
      coinsIn.forEach(c => {
        const q = seg(t, c.t0, c.t0 + 1.1);
        op(c.el, q > 0 && q < 1 ? Math.min(1, q * 4, (1 - q) * 5) : 0);
        c.el.setAttribute('transform', 'translate(' + f2(lerp(c.x0, 236, eo(q))) + ' ' + f2(lerp(-20, 330, q * q)) + ') scale(1.2)');
      });
      outs.forEach(o => {
        const q = seg(t, o.t0, o.t0 + 1.25);
        const src = o.fromVan ? [vx + 40, 392] : [236 + o.jit, 330];
        const ctl = [lerp(src[0], SEC[0], 0.45), 110 + o.jit];
        const pt = quad(src, ctl, [SEC[0] + o.jit * 0.6, SEC[1] + 6], ez(q));
        op(o.el, q > 0 && q < 1 ? Math.min(1, q * 5, (1 - q) * 6) : 0);
        const s = o.ty === 'sx-i-person' ? 0.72 : 1.5;
        o.el.setAttribute('transform', 'translate(' + f2(pt[0]) + ' ' + f2(pt[1] + (o.ty === 'sx-i-person' ? 10 : 0)) + ') scale(' + f2(s * (1 - 0.35 * q)) + ')');
      });
    };
  }

  // ══ SCENE 4 — NETWORK ════════════════════════════════════════════════════
  function scene4(svg, C) {
    bg(svg);
    const cx = 320, cy = 214, N = 8;
    const all = G(svg);
    const edges = G(all), parts = G(all), nodesG = G(all);
    const nodes = Array.from({ length: N }, (_, i) => {
      const a = (i + 0.5) / N * Math.PI * 2;
      return { x: cx + Math.cos(a) * 252, y: cy + Math.sin(a) * 160 + 14, i };
    });
    const line = (a, b, w) => h('path', { d: 'M' + f2(a[0]) + ',' + f2(a[1]) + 'L' + f2(b[0]) + ',' + f2(b[1]), stroke: '#f5f0e8', 'stroke-width': w || 1, opacity: 0.2, pathLength: 1, 'stroke-dasharray': 1, 'stroke-dashoffset': 1 }, edges);
    const E1 = [];
    nodes.forEach((n, i) => {
      E1.push({ el: line([n.x, n.y - 16], [cx, cy], 1.2), d: i * 0.08 });
      const m = nodes[(i + 1) % N]; E1.push({ el: line([n.x, n.y - 16], [m.x, m.y - 16]), d: 0.3 + i * 0.08 });
      if (i % 2 === 0) { const o = nodes[(i + 3) % N]; E1.push({ el: line([n.x, n.y - 16], [o.x, o.y - 16], 0.8), d: 0.6 + i * 0.06 }); }
    });
    nodes.forEach(n => {
      const g = G(nodesG, { transform: 'translate(' + f2(n.x) + ' ' + f2(n.y) + ')' });
      h('circle', { cx: 0, cy: -16, r: 26, fill: PEOPLE[n.i], opacity: 0.08 }, g);
      person(g, 0, 8, 1.05, PEOPLE[n.i]);
      use(g, n.i % 2 ? 'sx-i-laptop' : 'sx-i-phone', { transform: n.i % 2 ? 'translate(0 12) scale(0.9)' : 'translate(11 -4)' });
      n.g = g;
    });
    // the center: the sector, the organization's badge, the bank
    const center = G(svg);
    const S = sectorWindow(center, C.pano.spots[1], { color: C.cause.color });
    tr(S.g, cx, cy, 1.35);
    const badge = G(center, { transform: 'translate(' + (cx + 72) + ' ' + (cy + 44) + ')' });
    h('circle', { r: 17, fill: '#f5f0e8', stroke: C.cause.color, 'stroke-width': 3 }, badge);
    h('path', { d: 'M-9,3C-9,-4 -3,-9 0,-9C3,-9 9,-4 9,3C4,1 2,4 0,8C-2,4 -4,1 -9,3Z', fill: C.cause.color }, badge);
    const bank = G(center, { transform: 'translate(' + (cx - 72) + ' ' + (cy + 50) + ')' });
    [0, -5, -10].forEach(y => { h('ellipse', { cx: 0, cy: y, rx: 13, ry: 5, fill: '#b8791f' }, bank); h('ellipse', { cx: 0, cy: y - 1.5, rx: 13, ry: 5, fill: 'url(#sx-coin)' }, bank); });
    const coin = G(svg, { opacity: 0 });
    bigCoin(coin, C.cause.color, 62);
    const shineClip = G(coin, { 'clip-path': 'url(#sx-coinclip)' });
    const shine = h('rect', { x: -12, y: -90, width: 18, height: 180, fill: '#ffffff', opacity: 0.35, transform: 'rotate(25)' }, shineClip);
    // what the network sends
    const KINDS = ['sx-i-bulb', 'sx-i-env', 'sx-i-photo', 'sx-i-up', 'sx-i-heart', 'sx-i-env', 'sx-i-bulb', 'sx-i-down', 'sx-i-photo', 'sx-i-up'];
    const R = rng(404);
    const items = Array.from({ length: 34 }, (_, i) => {
      const from = Math.floor(R() * N), toC = R() < 0.72;
      const to = toC ? null : (from + (R() < 0.5 ? 1 : N - 1)) % N;
      const kind = KINDS[i % KINDS.length];
      return { el: use(parts, kind, { opacity: 0 }), from, to, kind, t0: 1.7 + i * 0.18 + R() * 0.2 };
    });
    return function (t) {
      C.pano.pbs.forEach((pb, i) => op(pb, i === 1 ? 0.05 : 1)); op(C.pano.heal, 1);
      E1.forEach(e => e.el.setAttribute('stroke-dashoffset', f2(1 - es(t, 0.3 + e.d, 1.3 + e.d))));
      nodes.forEach(n => { const v = eos(t, 0.1 + n.i * 0.09, 0.7 + n.i * 0.09); op(n.g, v); n.g.setAttribute('transform', 'translate(' + f2(n.x) + ' ' + f2(n.y + 10 * (1 - v)) + ')'); });
      op(S.glow, 0.45 + 0.2 * Math.sin(t * 2.2));
      items.forEach(it => {
        const a = nodes[it.from], bulb = it.kind === 'sx-i-bulb';
        const pop = bulb ? 0.45 : 0, q = seg(t, it.t0 + pop, it.t0 + pop + 1.35);
        const pp = seg(t, it.t0, it.t0 + pop);
        const src = [a.x, a.y - 44];
        const dst = it.to == null ? [cx, cy] : [nodes[it.to].x, nodes[it.to].y - 44];
        let x = src[0], y = src[1], s = 1, o = 0;
        if (bulb && pp > 0 && q === 0) { o = pp; s = 0.4 + 0.8 * eo(pp); y -= 6 * pp; }
        else if (q > 0 && q < 1) {
          const e = ez(q); x = lerp(src[0], dst[0], e); y = lerp(src[1] - (bulb ? 6 : 0), dst[1], e) - Math.sin(q * Math.PI) * 18;
          o = Math.min(1, (1 - q) * 5); s = 1.2 - 0.4 * q;
        }
        op(it.el, o);
        it.el.setAttribute('transform', 'translate(' + f2(x) + ' ' + f2(y) + ') scale(' + f2(s) + ')');
      });
      // the whole map closes into one coin
      const k = es(t, 8.0, 9.2);
      all.setAttribute('transform', 'translate(' + cx + ' ' + cy + ') scale(' + f2(1 - 0.96 * k) + ') translate(' + (-cx) + ' ' + (-cy) + ')');
      op(all, 1 - k);
      const cc = es(t, 8.6, 9.5);
      op(center, 1 - es(t, 8.7, 9.3));
      center.setAttribute('transform', 'translate(' + cx + ' ' + cy + ') scale(' + f2(1 - 0.3 * es(t, 8.2, 9.2)) + ') translate(' + (-cx) + ' ' + (-cy) + ')');
      op(coin, cc);
      coin.setAttribute('transform', 'translate(' + cx + ' ' + cy + ') scale(' + f2(0.3 + 0.7 * eo(cc)) + ') rotate(' + f2(-20 * (1 - cc)) + ')');
      shine.setAttribute('x', f2(lerp(-110, 110, seg(t, 9.3, 10))));
    };
  }

  // ══ SCENE 5 — REPORTING ══════════════════════════════════════════════════
  function scene5(svg, C) {
    bg(svg);
    h('ellipse', { cx: 320, cy: 430, rx: 420, ry: 50, fill: '#1c2e22' }, svg);
    // the network, as a coin, being taken in
    const net = G(svg, { transform: 'translate(188 118)' });
    const orbit = G(net);
    for (let i = 0; i < 6; i++) {
      const a = i / 6 * Math.PI * 2, x = Math.cos(a) * 58, y = Math.sin(a) * 40;
      h('path', { d: 'M0,0L' + f2(x) + ',' + f2(y), stroke: '#f5f0e8', 'stroke-width': 0.8, opacity: 0.25 }, orbit);
      h('circle', { cx: f2(x), cy: f2(y), r: 4.5, fill: PEOPLE[i] }, orbit);
    }
    bigCoin(net, C.cause.color, 34);
    // the intake cone, from the coin to the lens
    const lens = [262, 262];
    const cone = h('path', { d: 'M160,100L214,94L' + (lens[0] + 4) + ',' + (lens[1] - 4) + 'L' + (lens[0] - 4) + ',' + (lens[1] + 4) + 'Z', fill: 'url(#sx-cone)', opacity: 0 }, svg);
    const motes = Array.from({ length: 8 }, (_, i) => ({ el: h('circle', { r: 2, fill: '#ffe9b0', opacity: 0 }, svg), ph: i / 8 }));
    // the van and its dish
    const van = G(svg, { transform: 'translate(70 392)' });
    h('rect', { x: -64, y: -40, width: 96, height: 40, rx: 5, fill: '#e9e4d8' }, van);
    h('path', { d: 'M32,-32L52,-32L62,-16L62,0L32,0Z', fill: '#d6d0c2' }, van);
    h('path', { d: 'M36,-29L50,-29L57,-17L36,-17Z', fill: '#8ec5e8' }, van);
    h('rect', { x: -64, y: -22, width: 96, height: 6, fill: '#e8a84c' }, van);
    [-44, 44].forEach(x => { h('circle', { cx: x, cy: 1, r: 8, fill: '#1a1a1a' }, van); h('circle', { cx: x, cy: 1, r: 3.4, fill: '#8a8a8a' }, van); });
    h('path', { d: 'M-20,-40L-20,-58', stroke: '#8a8f96', 'stroke-width': 3 }, van);
    h('path', { d: 'M-44,-60Q-20,-40 4,-78Z', fill: '#f5f0e8', stroke: '#b9b3a6', 'stroke-width': 1 }, van);
    h('path', { d: 'M-20,-64L-8,-76', stroke: '#8a8f96', 'stroke-width': 1.5 }, van);
    const waves = [0, 1, 2].map(() => h('path', { d: 'M-2,-6A8,8 0 0 1 6,2', fill: 'none', stroke: '#e8a84c', 'stroke-width': 2 }, G(svg, { transform: 'translate(64 316)' })));
    // the reporter, the camera and its operator
    person(svg, 172, 404, 1.75, '#c9a6d8');
    h('path', { d: 'M182,368L196,356', stroke: '#2b2b2b', 'stroke-width': 2.4 }, svg);
    h('circle', { cx: 198, cy: 354, r: 4.6, fill: '#2b2b2b' }, svg);
    const cam = G(svg, { transform: 'translate(282 272) rotate(-22)' });
    h('rect', { x: -20, y: -13, width: 42, height: 26, rx: 4, fill: '#2c3338' }, cam);
    h('rect', { x: -34, y: -9, width: 16, height: 18, rx: 2, fill: '#3b444a' }, cam);
    h('circle', { cx: -34, cy: 0, r: 8, fill: '#16242d', stroke: '#8ec5e8', 'stroke-width': 2 }, cam);
    h('rect', { x: -6, y: -20, width: 16, height: 7, rx: 2, fill: '#3b444a' }, cam);
    const rec = h('circle', { cx: 16, cy: -8, r: 2.4, fill: '#e74c3c' }, cam);
    h('path', { d: 'M284,284L262,392M286,284L288,396M288,284L312,390', stroke: '#6b7378', 'stroke-width': 3, 'stroke-linecap': 'round' }, svg);
    person(svg, 322, 404, 1.7, '#8ec5e8');
    // the audience
    const aud = [[452, 340, 1.4, 0], [538, 318, 1.3, 2], [612, 356, 1.45, 5], [500, 410, 1.65, 4], [590, 426, 1.6, 6]].map(q => {
      const g = G(svg);
      person(g, q[0], q[1], q[2], PEOPLE[q[3]]);
      const dev = use(g, q[3] % 2 ? 'sx-i-laptop' : 'sx-i-phone', { transform: 'translate(' + (q[0] - 14 * q[2] / 1.4) + ' ' + (q[1] - 16 * q[2]) + ') scale(' + (q[2] * 0.8) + ')' });
      const glow = h('circle', { cx: q[0] - 14 * q[2] / 1.4, cy: q[1] - 20 * q[2], r: 14, fill: '#8ec5e8', opacity: 0 }, g);
      return { x: q[0], y: q[1] - 30 * q[2], glow, dev };
    });
    // what goes out
    const out = G(svg);
    const KIND = ['sx-i-doc', 'sx-i-photo', 'sx-i-video'];
    const R = rng(505);
    const sends = Array.from({ length: 18 }, (_, i) => ({ el: use(out, KIND[i % 3], { opacity: 0 }), to: i % aud.length, t0: 1.3 + i * 0.44 + R() * 0.15, lift: 60 + R() * 70 }));
    const trades = Array.from({ length: 12 }, (_, i) => {
      const a = Math.floor(R() * aud.length); let b = Math.floor(R() * aud.length); if (b === a) b = (a + 1) % aud.length;
      const c = C.causes[i % C.causes.length];
      const g = G(out, { opacity: 0 });
      h('circle', { r: 7.5, fill: 'url(#sx-coin)', stroke: '#9a6517', 'stroke-width': 1 }, g);
      h('circle', { r: 4.2, fill: c.color }, g);
      return { g, a, b, t0: 3.6 + i * 0.52 };
    });
    return function (t) {
      orbit.setAttribute('transform', 'rotate(' + f2(t * 12) + ')');
      op(cone, 0.35 + 0.2 * Math.sin(t * 3));
      motes.forEach(m => {
        const q = (t * 0.55 + m.ph) % 1;
        const pt = quad([188, 118], [230, 170], lens, q);
        m.el.setAttribute('cx', f2(pt[0])); m.el.setAttribute('cy', f2(pt[1])); op(m.el, Math.sin(q * Math.PI) * 0.9);
      });
      op(rec, (t % 1) < 0.5 ? 1 : 0.2);
      waves.forEach((w, i) => {
        const q = (t * 0.6 + i / 3) % 1;
        w.setAttribute('transform', 'rotate(-40) scale(' + f2(1 + q * 4) + ')'); op(w, (1 - q) * 0.8);
      });
      aud.forEach(a => op(a.glow, 0));
      sends.forEach(s => {
        const q = seg(t, s.t0, s.t0 + 1.5), a = aud[s.to];
        const pt = quad([lens[0] + 30, lens[1] - 12], [lerp(lens[0], a.x, 0.5), a.y - s.lift - 60], [a.x - 14, a.y + 2], ez(q));
        op(s.el, q > 0 && q < 1 ? Math.min(1, q * 6, (1 - q) * 8) : 0);
        s.el.setAttribute('transform', 'translate(' + f2(pt[0]) + ' ' + f2(pt[1]) + ') scale(' + f2(1.35 - 0.5 * q) + ') rotate(' + f2(-12 + 24 * q) + ')');
        const flash = seg(t, s.t0 + 1.4, s.t0 + 2.2);
        if (flash > 0 && flash < 1) op(a.glow, Math.max(Number(a.glow.getAttribute('opacity')) || 0, 0.35 * (1 - flash)));
      });
      trades.forEach(x => {
        const q = seg(t, x.t0, x.t0 + 0.8), A = aud[x.a], B = aud[x.b];
        op(x.g, q > 0 && q < 1 ? Math.min(1, q * 6, (1 - q) * 6) : 0);
        const px = lerp(A.x, B.x, q), py = lerp(A.y - 26, B.y - 26, q) - Math.sin(q * Math.PI) * 44;
        x.g.setAttribute('transform', 'translate(' + f2(px) + ' ' + f2(py) + ') scale(' + f2(0.9 + 0.3 * Math.sin(q * Math.PI)) + ')');
      });
    };
  }

  // ══ THE CAROUSEL ═════════════════════════════════════════════════════════
  function buildDefs(root, C) {
    const svg = h('svg', { class: 'sx__defs', width: 0, height: 0, 'aria-hidden': 'true', focusable: 'false' }, root);
    const d = h('defs', null, svg);
    const fg = h('filter', { id: 'sx-glow', x: '-60%', y: '-60%', width: '220%', height: '220%' }, d);
    h('feGaussianBlur', { stdDeviation: 7 }, fg);
    grad(d, 'sx-bg', [[0, '#1d3226'], [0.65, '#0f1c15'], [1, '#0a120d']], { radial: true, attrs: { cx: '50%', cy: '38%', r: '75%' } });
    grad(d, 'sx-bg1', [[0, '#16283a'], [0.6, '#0d1a1f'], [1, '#080f12']], { radial: true, attrs: { cx: '50%', cy: '70%', r: '80%' } });
    grad(d, 'sx-ocean', [[0, '#2d5268'], [0.65, '#153040'], [1, '#0a1a22']], { radial: true, attrs: { cx: '38%', cy: '32%' } });
    grad(d, 'sx-shade', [[0.55, '#000', 0], [1, '#000', 0.55]], { radial: true, attrs: { cx: '36%', cy: '30%' } });
    grad(d, 'sx-beam', [[0, C.cause.color, 0.85], [0.7, C.cause.color, 0.25], [1, C.cause.color, 0]], { attrs: { x1: 0, y1: 0, x2: 0, y2: 1 } });
    grad(d, 'sx-coin', [[0, '#fff1c4'], [0.45, '#f2c262'], [1, '#c98a2a']], { radial: true, attrs: { cx: '35%', cy: '30%', r: '80%' } });
    grad(d, 'sx-healglow', [[0, '#b8f0a8', 0.55], [1, '#b8f0a8', 0]], { radial: true });
    grad(d, 'sx-segshine', [[0, '#ffffff', 0.22], [0.5, '#ffffff', 0], [1, '#000000', 0.18]], { attrs: { x1: 0, y1: 0, x2: 0, y2: 1 } });
    grad(d, 'sx-cone', [[0, '#ffe9b0', 0.45], [1, '#ffe9b0', 0.02]], { attrs: { x1: 0, y1: 0, x2: 1, y2: 1 } });
    h('path', { d: SEG }, h('clipPath', { id: 'sx-segclip' }, d));
    h('circle', { r: 62 }, h('clipPath', { id: 'sx-coinclip' }, d));
    C.s2clip = h('clipPath', { id: 'sx-s2clip' }, d);
    icons(d);
    C.pano = buildPano(d, C.cause);
  }

  const SCENES = [scene1, scene2, scene3, scene4, scene5];
  const chev = dir => '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="' +
    (dir < 0 ? 'M15 5l-7 7 7 7' : 'M9 5l7 7-7 7') + '" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function causesNow() {
    const cs = ((E.config && E.config.causes) || []).slice().sort((a, b) => a.index - b.index);
    return cs.length === 7 ? cs : FALLBACK;
  }
  function weekCause(causes, want) {
    if (want) { const c = causes.find(x => x.id === want); if (c) return c; }
    let i = 0;
    try { i = E.Cycle && E.Cycle.now ? E.Cycle.now().causeIndex : 0; } catch (e) {}
    return causes.find(c => c.index === i) || causes[0];
  }

  const S = { i: 0, t0: 0, raf: 0, paused: false, visible: true, frozen: 0, scenes: [], root: null };

  function mount(sel, opts) {
    const root = typeof sel === 'string' ? document.querySelector(sel) : sel;
    if (!root) return null;
    opts = opts || {};
    injectCSS();
    const causes = causesNow();
    const C = { causes, cause: weekCause(causes, opts.cause) };
    const reduce = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
    root.innerHTML = '';
    root.classList.add('sx');
    root.style.setProperty('--sx-c', '#e8a84c');
    root.setAttribute('role', 'region');
    root.setAttribute('aria-roledescription', 'carousel');
    root.setAttribute('aria-label', 'How a mission is made, in five steps');
    buildDefs(root, C);
    const stage = document.createElement('div');
    stage.className = 'sx__stage';
    root.appendChild(stage);
    S.scenes = SCENES.map((fn, i) => {
      const svg = h('svg', { class: 'sx__scene', viewBox: '0 0 ' + W + ' ' + H, preserveAspectRatio: 'xMidYMid slice', role: 'img',
        'aria-label': 'Step ' + (i + 1) + ' of 5, ' + STEPS[i].name + ': ' + STEPS[i].msg }, stage);
      let upd = null;
      try { upd = fn(svg, C); } catch (e) { console.warn('[EBX.Steps] scene ' + (i + 1), e); }
      return { svg, update: upd || function () {} };
    });
    stage.insertAdjacentHTML('beforeend',
      '<button type="button" class="sx__arrow sx__arrow--prev" data-sx="-1">' + chev(-1) + '</button>' +
      '<button type="button" class="sx__arrow sx__arrow--next" data-sx="1">' + chev(1) + '</button>');
    root.insertAdjacentHTML('beforeend', '<div class="sx__bar"><p class="sx__msg" aria-live="polite"></p>' +
      '<div class="sx__dots" role="tablist" aria-label="The five steps">' + STEPS.map((s, i) =>
        '<button type="button" class="sx__dot" role="tab" data-sx-go="' + i + '" aria-label="' + (i + 1) + '. ' + s.name + '"><span></span></button>').join('') +
      '</div></div>');
    S.root = root; S.reduce = reduce; S.C = C;
    root.addEventListener('click', e => {
      const a = e.target.closest('[data-sx]'), dt = e.target.closest('[data-sx-go]');
      if (a) go(S.i + Number(a.dataset.sx), true);
      else if (dt) go(Number(dt.dataset.sxGo), true);
    });
    root.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight') { go(S.i + 1, true); e.preventDefault(); }
      else if (e.key === 'ArrowLeft') { go(S.i - 1, true); e.preventDefault(); }
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(es => { S.visible = es[0].isIntersecting; resume(); }).observe(root);
    }
    document.addEventListener('visibilitychange', resume);
    go(0, false);
    return E.Steps;
  }

  function label() {
    const s = STEPS[S.i], a = S.root.querySelector('.sx__arrow--prev'), b = S.root.querySelector('.sx__arrow--next');
    a.setAttribute('aria-label', 'Back to step ' + ((S.i + 4) % 5 + 1) + ', ' + STEPS[(S.i + 4) % 5].name);
    b.setAttribute('aria-label', 'On to step ' + ((S.i + 1) % 5 + 1) + ', ' + STEPS[(S.i + 1) % 5].name);
    const msg = S.root.querySelector('.sx__msg');
    if (msg.textContent !== s.msg) {
      const first = !msg.textContent;
      msg.textContent = s.msg;
      if (!first && !S.reduce) { msg.classList.remove('in'); void msg.offsetWidth; msg.classList.add('in'); }
    }
    S.root.querySelectorAll('.sx__dot').forEach((d, i) => {
      d.classList.toggle('done', i < S.i);
      d.setAttribute('aria-selected', i === S.i ? 'true' : 'false');
      d.querySelector('span').style.transform = i < S.i ? 'scaleX(1)' : 'scaleX(0)';
    });
    S.root.style.setProperty('--sx-c', S.i === 0 || S.i === 3 ? S.C.cause.color : '#e8a84c');
  }

  // Go to page i (wraps). A manual page restarts that page's visual.
  function go(i, manual) {
    S.i = ((i % 5) + 5) % 5;
    S.scenes.forEach((s, k) => s.svg.classList.toggle('on', k === S.i));
    S.t0 = now();
    label();
    try { S.scenes[S.i].update(S.reduce ? 6.5 : 0); } catch (e) {}
    if (S.reduce) { if (S.i === 3) S.scenes[3].update(9.9); return; }
    resume();
    void manual;
  }
  const now = () => (window.performance && performance.now) ? performance.now() : Date.now();
  function frame() {
    S.raf = 0;
    if (!S.visible || document.hidden) return;
    const t = (now() - S.t0) / 1000;
    if (t >= DUR) { go(S.i + 1, false); return; }
    try { S.scenes[S.i].update(t); } catch (e) {}
    const bar = S.root.querySelector('.sx__dot[data-sx-go="' + S.i + '"] span');
    if (bar) bar.style.transform = 'scaleX(' + (t / DUR).toFixed(3) + ')';
    S.raf = requestAnimationFrame(frame);
  }
  let hiddenAt = 0;
  function resume() {
    if (!S.root || S.reduce) return;
    if (!S.visible || document.hidden) {
      if (!hiddenAt) hiddenAt = now();
      if (S.raf) { cancelAnimationFrame(S.raf); S.raf = 0; }
      return;
    }
    if (hiddenAt) { S.t0 += now() - hiddenAt; hiddenAt = 0; }
    if (!S.raf) S.raf = requestAnimationFrame(frame);
  }

  E.Steps = {
    mount, go: i => go(i, true), STEPS, PANOS,
    // scripts/home_check.js: draw page i at second t, without the clock
    _at(i, t) { S.i = i; S.scenes.forEach((s, k) => s.svg.classList.toggle('on', k === i)); label(); S.scenes[i].update(t); },
    _state: S,
  };
})();
