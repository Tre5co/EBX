/* =============================================
   EARTHBUCKS — Shared JavaScript Utilities
   ebx_shared.js  v0.2.0
   ============================================= */

'use strict';

const EBX = {

  config: {
    dataRoot: '/data/',
    version: '0.2.0',
    // Cycle anchor: the known start of cycle epoch
    cycleStart: new Date('2026-01-01T00:00:00'),
    causeLengthDays: 14,    // each cause gets 14 days (12 debate + 2 org vote)
    cycleLengthDays: 98,    // 7 causes × 14 days = 98 days, no recap
    causes: [],             // populated by EBX.loadCauses()
    initiatives: [],        // populated by EBX.loadInitiatives()
  },


  /* ─────────────────────────────────────────
     DATA FETCHING
     ───────────────────────────────────────── */

  async fetchJSON(path) {
    const url = EBX.config.dataRoot + path;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
      return await res.json();
    } catch (err) {
      console.error('[EBX] fetchJSON failed:', err);
      return null;
    }
  },

  async fetchAll(paths) {
    return Promise.all(paths.map(p => EBX.fetchJSON(p)));
  },

  async loadCauses() {
    const data = await EBX.fetchJSON('causes/causes.json');
    if (data) EBX.config.causes = data;
    return EBX.config.causes;
  },

  async loadInitiatives() {
    const data = await EBX.fetchJSON('causes/initiatives.json');
    if (data) EBX.config.initiatives = data;
    return EBX.config.initiatives;
  },

  async loadAll() {
    await Promise.all([EBX.loadCauses(), EBX.loadInitiatives()]);
  },


  /* ─────────────────────────────────────────
     CYCLE ENGINE
     The 7-cause rotating cycle. Each cause
     occupies 14 days. 7×14 = 98-day cycle.

     Within each 14-day window:
       Days 1–12 → initiative debate
       Days 13–14 → org vote
     ───────────────────────────────────────── */

  Cycle: {

    MS_PER_DAY: 86400000,

    /**
     * Returns the current cycle state.
     * @returns {{
     *   causeIndex: number,       // 0-6, which cause is in org-vote (top of wheel)
     *   causePhase: 'debate'|'vote'|'recap',
     *   dayInCause: number,       // 1-14
     *   daysRemaining: number,
     *   hoursRemaining: number,
     *   rotationDeg: number,      // how far to rotate the wheel
     *   isRecap: boolean,
     *   cycleDay: number,         // 1-100
     * }}
     */
    now() {
      const cfg = EBX.config;
      const elapsed = Date.now() - cfg.cycleStart.getTime();
      const cycleLengthMs = cfg.cycleLengthDays * EBX.Cycle.MS_PER_DAY;
      const causeLengthMs = cfg.causeLengthDays * EBX.Cycle.MS_PER_DAY;

      const cycleMs = ((elapsed % cycleLengthMs) + cycleLengthMs) % cycleLengthMs;
      const cycleDay = Math.floor(cycleMs / EBX.Cycle.MS_PER_DAY) + 1;

      const causeIndex = Math.floor(cycleMs / causeLengthMs) % 7;
      const msInCause = cycleMs % causeLengthMs;
      const dayInCause = Math.floor(msInCause / EBX.Cycle.MS_PER_DAY) + 1;
      const causePhase = dayInCause <= 12 ? 'debate' : 'vote';

      const msRemaining = causeLengthMs - msInCause;
      const daysRemaining = Math.floor(msRemaining / EBX.Cycle.MS_PER_DAY);
      const hoursRemaining = Math.floor((msRemaining % EBX.Cycle.MS_PER_DAY) / 3600000);

      // Rotation: bring active segment to top (12 o'clock)
      const anglePerSeg = 360 / 7;
      const baseRotation = -(causeIndex * anglePerSeg);
      // Smooth sub-progress within current cause window
      const subProgress = msInCause / causeLengthMs;
      const rotationDeg = baseRotation - (subProgress * anglePerSeg);

      return {
        causeIndex, causePhase, dayInCause,
        daysRemaining, hoursRemaining,
        rotationDeg, isRecap: false, cycleDay,
      };
    },

    /**
     * Get the phase label for a given cause index relative to current cycle.
     * Causes ahead of the active one are in initiative debate.
     * The active one is in org vote or debate depending on day.
     */
    phaseForCause(causeIndex) {
      const state = EBX.Cycle.now();
      if (state.isRecap) return 'recap';
      if (causeIndex === state.causeIndex) return state.causePhase;
      // Causes rotate: find offset from active
      const offset = ((causeIndex - state.causeIndex) + 7) % 7;
      return offset === 0 ? state.causePhase : 'debate';
    },

    /**
     * Given a cause index, get the initiative currently associated with it.
     */
    initiativeForCause(causeIndex) {
      return EBX.config.initiatives.find(i => i.cause_index === causeIndex) || null;
    },
  },


  /* ─────────────────────────────────────────
     THE ANNULUS
     The 7-segment rotating wheel.
     ───────────────────────────────────────── */

  Annulus: {

    _rafId: null,
    _connectorLines: [],
    _segments: [],
    _labelElements: [],
    _rotatingGroup: null,
    _svg: null,
    _vertices: [],

    /**
     * Build and mount the annulus into a container element.
     * @param {string|Element} container  selector or element
     */
    mount(container) {
      const el = typeof container === 'string'
        ? document.querySelector(container)
        : container;
      if (!el) return;

      const causes = EBX.config.causes;
      if (!causes.length) {
        console.warn('[EBX.Annulus] No causes loaded — call EBX.loadCauses() first.');
        return;
      }

      const cx = 200, cy = 200, outerR = 180, innerR = 118;
      const n = 7;
      const anglePerSeg = (2 * Math.PI) / n;

      // Precompute static outer vertices
      EBX.Annulus._vertices = [];
      for (let i = 0; i < n; i++) {
        const angle = i * anglePerSeg - Math.PI / 2;
        EBX.Annulus._vertices.push({
          x: cx + outerR * Math.cos(angle),
          y: cy + outerR * Math.sin(angle),
          angle,
        });
      }

      // Build SVG
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 400 400');
      svg.style.cssText = 'width:100%;height:100%;display:block;overflow:visible;';
      EBX.Annulus._svg = svg;

      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.setAttribute('id', 'ebx-rotating-group');
      group.style.transformOrigin = `${cx}px ${cy}px`;
      svg.appendChild(group);
      EBX.Annulus._rotatingGroup = group;

      // Core circle
      const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      core.setAttribute('cx', cx); core.setAttribute('cy', cy);
      core.setAttribute('r', innerR - 4);
      core.setAttribute('fill', '#0f1a14');
      core.setAttribute('opacity', '0.95');
      group.appendChild(core);

      // Segments
      EBX.Annulus._segments = [];
      EBX.Annulus._labelElements = [];

      for (let i = 0; i < n; i++) {
        const cause = causes[i];
        const startAngle = i * anglePerSeg - Math.PI / 2;
        const endAngle = startAngle + anglePerSeg;

        const x1 = cx + outerR * Math.cos(startAngle);
        const y1 = cy + outerR * Math.sin(startAngle);
        const x2 = cx + outerR * Math.cos(endAngle);
        const y2 = cy + outerR * Math.sin(endAngle);
        const x3 = cx + innerR * Math.cos(endAngle);
        const y3 = cy + innerR * Math.sin(endAngle);
        const x4 = cx + innerR * Math.cos(startAngle);
        const y4 = cy + innerR * Math.sin(startAngle);

        const d = `M ${x1} ${y1} A ${outerR} ${outerR} 0 0 1 ${x2} ${y2} L ${x3} ${y3} A ${innerR} ${innerR} 0 0 0 ${x4} ${y4} Z`;
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        path.setAttribute('fill', cause.color);
        path.setAttribute('fill-opacity', '0.88');
        path.setAttribute('stroke', '#0f1a14');
        path.setAttribute('stroke-width', '2');
        path.style.cursor = 'pointer';
        path.style.transition = 'filter 0.2s';
        path.addEventListener('mouseenter', () => { path.style.filter = 'brightness(1.25)'; });
        path.addEventListener('mouseleave', () => { path.style.filter = 'none'; });
        path.addEventListener('click', () => {
          window.location.href = `cause.html?id=${cause.id}`;
        });
        group.appendChild(path);
        EBX.Annulus._segments.push(path);

        // Two-line label: cause name + decision date
        const midAngle = startAngle + anglePerSeg / 2;
        const labelR = (outerR + innerR) / 2;   // midpoint of the ring band
        const lx = cx + labelR * Math.cos(midAngle);
        const ly = cy + labelR * Math.sin(midAngle);

        // Wrapper group for counter-rotation
        const labelG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        labelG.setAttribute('pointer-events', 'none');

        const nameLine = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        nameLine.setAttribute('x', lx);
        nameLine.setAttribute('y', ly - 7);
        nameLine.setAttribute('text-anchor', 'middle');
        nameLine.setAttribute('dominant-baseline', 'middle');
        nameLine.setAttribute('font-size', '10');
        nameLine.setAttribute('font-weight', '700');
        nameLine.setAttribute('fill', '#e8f5ec');
        nameLine.textContent = cause.name;
        labelG.appendChild(nameLine);

        // Date line — populated by _update each frame
        const dateLine = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        dateLine.setAttribute('x', lx);
        dateLine.setAttribute('y', ly + 7);
        dateLine.setAttribute('text-anchor', 'middle');
        dateLine.setAttribute('dominant-baseline', 'middle');
        dateLine.setAttribute('font-size', '8');
        dateLine.setAttribute('font-weight', '400');
        dateLine.setAttribute('fill', '#e8f5ec');
        dateLine.setAttribute('opacity', '0.65');
        dateLine.setAttribute('data-date-label', i);
        dateLine.textContent = '…';
        labelG.appendChild(dateLine);

        group.appendChild(labelG);
        EBX.Annulus._labelElements.push({ el: labelG, lx, ly });
      }

      el.appendChild(svg);

      // Init connector lines (appended to SVG, outside rotating group)
      EBX.Annulus._initConnectors(svg, n);

      // Start update loop
      EBX.Annulus._tick();
    },

    _initConnectors(svg, n) {
      EBX.Annulus._connectorLines.forEach(l => l.remove());
      EBX.Annulus._connectorLines = [];
      // One connector per side anchor (7 total: top + left3 + right3)
      for (let i = 0; i < n; i++) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('stroke', '#a7d7c5');
        line.setAttribute('stroke-width', '1.5');
        line.setAttribute('stroke-dasharray', '3 2');
        line.setAttribute('opacity', '0.6');
        svg.appendChild(line);
        EBX.Annulus._connectorLines.push(line);
      }
    },

    _tick() {
      EBX.Annulus._update();
      // smooth animation via rAF for rotation, timer update every 60s
      EBX.Annulus._rafId = requestAnimationFrame(EBX.Annulus._tick);
    },

    _update() {
      const state = EBX.Cycle.now();
      const group = EBX.Annulus._rotatingGroup;
      if (!group) return;

      // Apply rotation
      group.style.transform = `rotate(${state.rotationDeg}deg)`;

      // Keep labels upright and populate dates
      const CYCLE_START_A = new Date('2026-01-01T00:00:00');
      const MS_DAY_A = 86400000;
      const cycleNumA = Math.floor((Date.now() - CYCLE_START_A.getTime()) / (98 * MS_DAY_A));
      const innerR_A = 118, outerR_A = 180;

      EBX.Annulus._labelElements.forEach(({ el, lx, ly }, i) => {
        // Counter-rotate entire label group so text stays upright
        el.setAttribute('transform', `rotate(${-state.rotationDeg}, ${lx}, ${ly})`);

        // Populate the date sub-label for this cause index
        const dateLine = el.querySelector('[data-date-label]');
        if (dateLine) {
          const voteCloseMs = CYCLE_START_A.getTime()
            + cycleNumA * 98 * MS_DAY_A
            + i * 14 * MS_DAY_A
            + 14 * MS_DAY_A;
          const voteCloseDate = new Date(voteCloseMs);
          dateLine.textContent = voteCloseDate.toLocaleDateString('en-US', {
            month: 'short', day: 'numeric'
          });
        }
      });

      // Highlight active segment
      EBX.Annulus._segments.forEach((seg, i) => {
        if (i === state.causeIndex) {
          seg.setAttribute('stroke', '#ffffff');
          seg.setAttribute('stroke-width', '3.5');
          seg.setAttribute('filter', 'drop-shadow(0 0 8px rgba(255,255,200,0.55))');
        } else {
          seg.setAttribute('stroke', '#0f1a14');
          seg.setAttribute('stroke-width', '2');
          seg.removeAttribute('filter');
        }
      });

      // Update center text
      const nameEl = document.getElementById('ebx-cause-name');
      const timerEl = document.getElementById('ebx-cause-timer');
      const phaseEl = document.getElementById('ebx-cause-phase');

      if (nameEl && state.causeIndex !== null) {
        const cause = EBX.config.causes[state.causeIndex];
        if (cause) nameEl.textContent = cause.name;
      }

      if (timerEl) {
        timerEl.textContent = `${state.daysRemaining}d ${state.hoursRemaining}h`;
      }

      if (phaseEl) {
        phaseEl.textContent = state.causePhase === 'vote' ? 'Org Vote' : 'Initiative Debate';
      }

      // Update side panels
      EBX.Annulus._updateSidePanels(state);
    },

    _updateSidePanels(state) {
      if (state.causeIndex === null) return;
      const causes = EBX.config.causes;
      const initiatives = EBX.config.initiatives;
      const n = 7;
      const active = state.causeIndex;

      // Layout: top=active, left=[active-1, active-2, active-3], right=[active+1, active+2, active+3]
      const positions = [
        { slot: 'top',    offset: 0  },
        { slot: 'left-0', offset: -1 },
        { slot: 'left-1', offset: -2 },
        { slot: 'left-2', offset: -3 },
        { slot: 'right-0',offset: +1 },
        { slot: 'right-1',offset: +2 },
        { slot: 'right-2',offset: +3 },
      ];

      positions.forEach(({ slot, offset }) => {
        const idx = ((active + offset) % n + n) % n;
        const cause = causes[idx];
        const init = initiatives.find(i => i.cause_index === idx);
        const el = document.querySelector(`[data-ebx-slot="${slot}"]`);
        if (!el || !cause) return;

        el.querySelector('.ebx-slot-cause').textContent = cause.name;
        el.querySelector('.ebx-slot-initiative').textContent =
          init ? `${init.emoji} ${init.title}` : '—';
        el.style.borderColor = cause.color + '88';
      });
    },

    stop() {
      if (EBX.Annulus._rafId) cancelAnimationFrame(EBX.Annulus._rafId);
    },
  },


  /* ─────────────────────────────────────────
     NAV / PAGE SETUP
     ───────────────────────────────────────── */

  initNav() {
    const mount = document.getElementById('ebx-nav-mount');
    if (!mount) return;
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const links = [
      { href: 'feed.html',    label: 'Feed' },
      { href: 'mission.html', label: 'Missions' },
      { href: 'about.html',   label: 'About' },
    ];
    mount.innerHTML = `
      <nav class="ebx-nav">
        <div class="container">
          <a href="index.html" class="ebx-nav__logo">
            EBX
          </a>
          <ul class="ebx-nav__links">
            ${links.map(l => `
              <li><a href="${l.href}" class="${currentPage === l.href ? 'active' : ''}">${l.label}</a></li>
            `).join('')}
          </ul>
          <div class="ebx-nav__actions">
            <a href="profile.html" class="btn btn-outline btn-sm">My Profile</a>
          </div>
        </div>
      </nav>
    `;
  },

  initFooter() {
    const mount = document.getElementById('ebx-footer-mount');
    if (!mount) return;
    mount.innerHTML = `
      <footer class="ebx-footer">
        <div class="container">
          <div class="ebx-footer__grid">
            <div class="ebx-footer__col">
              <div class="ebx-footer__logo">Earthbux</div>
              <div class="ebx-footer__tagline">Collective action, measured in impact.</div>
              <p>A civic news and charity platform. Every earthbuck tells a story.</p>
            </div>
            <div class="ebx-footer__col">
              <h4>Causes</h4>
              <ul>
                <li><a href="cause.html?id=atmosphere">Atmosphere</a></li>
                <li><a href="cause.html?id=oceans">Oceans</a></li>
                <li><a href="cause.html?id=forests">Forests</a></li>
                <li><a href="cause.html?id=wildlife">Wildlife</a></li>
                <li><a href="cause.html?id=land">Land</a></li>
                <li><a href="cause.html?id=human-rights">Human Rights</a></li>
                <li><a href="cause.html?id=human-progress">Human Progress</a></li>
              </ul>
            </div>
            <div class="ebx-footer__col">
              <h4>Platform</h4>
              <ul>
                <li><a href="feed.html">Feed</a></li>
                <li><a href="stats.html">Directory</a></li>
                <li><a href="about.html">About</a></li>
                <li><a href="profile.html">My Profile</a></li>
              </ul>
            </div>
            <div class="ebx-footer__col">
              <h4>Community</h4>
              <ul>
                <li><a href="#">Organizations</a></li>
                <li><a href="#">Propose an Initiative</a></li>
                <li><a href="#">Governance</a></li>
                <li><a href="#">Open Data</a></li>
              </ul>
            </div>
          </div>
          <div class="ebx-footer__bottom">
            <span>© ${new Date().getFullYear()} Earthbux. Open source, open impact.</span>
            <span class="mono">v${EBX.config.version}</span>
          </div>
        </div>
      </footer>
    `;
  },

  initPage() {
    EBX.initNav();
    EBX.initFooter();
  },


  /* ─────────────────────────────────────────
     URL HELPERS
     ───────────────────────────────────────── */

  getParam(key) {
    return new URLSearchParams(window.location.search).get(key);
  },

  buildURL(base, params = {}) {
    const url = new URL(base, window.location.origin);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    return url.toString();
  },


  /* ─────────────────────────────────────────
     DOM HELPERS
     ───────────────────────────────────────── */

  $(sel, ctx = document)  { return ctx.querySelector(sel); },
  $$(sel, ctx = document) { return Array.from(ctx.querySelectorAll(sel)); },

  render(target, html) {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (el) el.innerHTML = html;
  },

  renderSkeleton(target, rows = 3) {
    EBX.render(target, Array.from({ length: rows }, () =>
      `<div class="skeleton" style="height:80px;margin-bottom:12px;border-radius:8px;"></div>`
    ).join(''));
  },

  renderEmpty(target, message = 'Nothing here yet.') {
    EBX.render(target, `
      <div style="text-align:center;padding:48px 24px;color:var(--clr-ink-light);">
        <div style="font-size:2rem;margin-bottom:12px;">🌱</div>
        <p style="font-size:0.9rem;">${message}</p>
      </div>
    `);
  },


  /* ─────────────────────────────────────────
     FORMATTING
     ───────────────────────────────────────── */

  formatNumber(n)               { return Number(n).toLocaleString(); },
  formatEBX(n)                  { return `${EBX.formatNumber(n)} EBX`; },
  formatPercent(v, d = 1)       { return `${Number(v).toFixed(d)}%`; },
  formatDate(iso)               {
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  },
  timeAgo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    if (mins < 1)   return 'just now';
    if (mins < 60)  return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 30)  return `${days}d ago`;
    return EBX.formatDate(iso);
  },


  /* ─────────────────────────────────────────
     TOKEN IDENTITY
     Each EBX token: initiative title + org +
     cause color + chronological index.
     ───────────────────────────────────────── */

  /**
   * Render an EBX token chip.
   * @param {{ index, title, org, causeColor, amount }} token
   */
  tokenChip({ index, title, org, causeColor, amount }) {
    return `
      <div class="ebx-token" style="border-left: 4px solid ${causeColor};">
        <div class="ebx-token__index mono">#${String(index).padStart(3,'0')}</div>
        <div class="ebx-token__title">${title}</div>
        ${org ? `<div class="ebx-token__org text-xs text-muted">${org}</div>` : ''}
        ${amount != null ? `<div class="ebx-token__amount mono text-xs">${EBX.formatEBX(amount)}</div>` : ''}
      </div>
    `;
  },


  /* ─────────────────────────────────────────
     CREDIT BADGE
     Mini 7-sector annulus snapshot shown on
     user profiles, sized to badge scale.
     ───────────────────────────────────────── */

  /**
   * Render a credit badge SVG.
   * @param {Object[]} holdings  Array of { causeIndex, amount }
   * @param {number}   [size=64]
   * @returns {string} SVG HTML string
   */
  creditBadge(holdings, size = 64) {
    const causes = EBX.config.causes;
    if (!causes.length) return '';
    const cx = size / 2, cy = size / 2;
    const outerR = size * 0.46, innerR = size * 0.25;
    const n = 7;
    const anglePerSeg = (2 * Math.PI) / n;

    const segments = causes.map((cause, i) => {
      const holding = holdings.find(h => h.causeIndex === i);
      const opacity = holding ? 0.9 : 0.15;
      const startAngle = i * anglePerSeg - Math.PI / 2;
      const endAngle = startAngle + anglePerSeg;
      const x1 = cx + outerR * Math.cos(startAngle);
      const y1 = cy + outerR * Math.sin(startAngle);
      const x2 = cx + outerR * Math.cos(endAngle);
      const y2 = cy + outerR * Math.sin(endAngle);
      const x3 = cx + innerR * Math.cos(endAngle);
      const y3 = cy + innerR * Math.sin(endAngle);
      const x4 = cx + innerR * Math.cos(startAngle);
      const y4 = cy + innerR * Math.sin(startAngle);
      const d = `M ${x1} ${y1} A ${outerR} ${outerR} 0 0 1 ${x2} ${y2} L ${x3} ${y3} A ${innerR} ${innerR} 0 0 0 ${x4} ${y4} Z`;
      return `<path d="${d}" fill="${cause.color}" fill-opacity="${opacity}" stroke="#0f1a14" stroke-width="0.8"/>`;
    }).join('');

    const totalEBX = holdings.reduce((s, h) => s + h.amount, 0);

    return `
      <div class="ebx-credit-badge" title="${EBX.formatEBX(totalEBX)} across ${holdings.length} cause(s)">
        <svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
          <circle cx="${cx}" cy="${cy}" r="${outerR + 1}" fill="#0f1a14" opacity="0.6"/>
          ${segments}
          <circle cx="${cx}" cy="${cy}" r="${innerR - 2}" fill="#0f1a14" opacity="0.9"/>
        </svg>
      </div>
    `;
  },


  /* ─────────────────────────────────────────
     COMPONENTS
     ───────────────────────────────────────── */

  tag(label, variant = 'neutral') {
    return `<span class="tag tag-${variant}">${label}</span>`;
  },

  progressBar(percent, variant = '') {
    const cls = variant ? `progress-bar__fill--${variant}` : '';
    return `
      <div class="progress-bar">
        <div class="progress-bar__fill ${cls}" style="width:${Math.min(100, percent)}%"></div>
      </div>
    `;
  },

  statBlock(value, label, variant = '') {
    return `
      <div class="stat-block">
        <div class="stat-block__value ${variant ? 'stat-block__value--'+variant : ''}">${value}</div>
        <div class="stat-block__label">${label}</div>
      </div>
    `;
  },

  /**
   * Render an initiative card with correct phase labeling.
   */
  initiativeCard(init) {
    const cause = EBX.config.causes.find(c => c.index === init.cause_index);
    const causeColor = cause ? cause.color : '#888';
    const phaseLabelMap = {
      org_vote:          { label: 'Org Vote Open',      variant: 'amber' },
      initiative_debate: { label: 'Initiative Debate',  variant: 'forest' },
      planning:          { label: 'Financial Planning',  variant: 'sage' },
      execution:         { label: 'In Execution',        variant: 'sage' },
      resolved:          { label: 'Resolved',            variant: 'neutral' },
    };
    const phase = phaseLabelMap[init.phase] || { label: init.phase, variant: 'neutral' };
    const pct = init.pool_total > 0
      ? Math.round((init.committed_ebx / init.pool_total) * 100)
      : 0;

    return `
      <a href="initiative.html?id=${init.id}" class="card ebx-init-card"
         style="text-decoration:none;display:block;border-left:4px solid ${causeColor};">
        <div class="flex-between mb-sm">
          ${EBX.tag(phase.label, phase.variant)}
          <span class="mono text-xs text-muted">#${String(init.index).padStart(3,'0')}</span>
        </div>
        <h4 style="margin-bottom:var(--sp-xs);">${init.emoji} ${init.title}</h4>
        <p class="text-xs text-muted mb-md">${cause ? cause.name : ''} · ${init.winning_org || 'Org TBD'}</p>
        <p class="text-sm text-muted mb-md">${init.description}</p>
        ${EBX.progressBar(pct, 'amber')}
        <div class="flex-between mt-sm">
          <span class="text-xs text-muted">${EBX.formatEBX(init.committed_ebx)} committed</span>
          <span class="text-xs fw-medium" style="color:${causeColor};">${pct}% of pool →</span>
        </div>
      </a>
    `;
  },

  /**
   * Render an opinion card.
   */
  opinionCard(op) {
    const typeVariant = { org: 'forest', initiative: 'amber', other: 'neutral' }[op.type] || 'neutral';
    return `
      <div class="card-flat ebx-opinion">
        <div class="flex-between mb-sm">
          <div class="flex gap-sm" style="align-items:center;">
            ${EBX.tag(op.type, typeVariant)}
            <span class="text-xs text-muted">${EBX.timeAgo(op.created_at)}</span>
          </div>
          <span class="text-xs text-muted">+${op.feedback} feedback</span>
        </div>
        <p class="text-sm" style="margin-bottom:var(--sp-sm);">${op.body}</p>
        <div class="text-xs text-muted">— ${op.author_handle}</div>
      </div>
    `;
  },


  /* ─────────────────────────────────────────
     SEARCH & FILTER HELPERS
     ───────────────────────────────────────── */

  filterBySearch(items, query, fields) {
    if (!query) return items;
    const q = query.toLowerCase();
    return items.filter(item =>
      fields.some(f => String(item[f] || '').toLowerCase().includes(q))
    );
  },

  filterByField(items, field, value) {
    if (!value || value === 'all') return items;
    return items.filter(item => String(item[field]) === value);
  },

  sortBy(items, field, dir = 'desc') {
    return [...items].sort((a, b) => {
      const av = a[field], bv = b[field];
      if (typeof av === 'number') return dir === 'desc' ? bv - av : av - bv;
      return dir === 'desc'
        ? String(bv).localeCompare(String(av))
        : String(av).localeCompare(String(bv));
    });
  },

};

/* ─────────────────────────────────────────────
   AUTO-INIT
   ───────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  EBX.initPage();
});

if (typeof module !== 'undefined') module.exports = EBX;