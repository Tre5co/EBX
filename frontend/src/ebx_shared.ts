/* =============================================
   EARTHBUCKS — Shared TypeScript Utilities
   src/ebx_shared.ts  v0.3.0

   Built into resources/js/ebx_shared.js as an IIFE
   that exposes a global `EBX` symbol for use by inline
   <script> blocks on every HTML page.
   ============================================= */

import type {
  Cause,
  CreditHolding,
  CycleState,
  FeedPost,
  Initiative,
  Opinion,
  TokenChip,
} from './types.js';

declare global {
  interface Window {
    EBX: typeof EBX;
  }
}

/* ─────────────────────────────────────────
   API CONFIG
   Swap dataRoot to '/api/' once the FastAPI
   backend is reachable and seeded.
   ───────────────────────────────────────── */

interface EBXConfig {
  dataRoot: string;
  apiBase: string;
  version: string;
  cycleStart: Date;
  causeLengthDays: number;
  cycleLengthDays: number;
  useApi: boolean;
  causes: Cause[];
  initiatives: Initiative[];
  feed: FeedPost[];
}

const config: EBXConfig = {
  dataRoot: '/data/',
  apiBase: 'http://localhost:8000',
  version: '0.3.0',
  cycleStart: new Date('2026-01-01T00:00:00'),
  causeLengthDays: 14,
  cycleLengthDays: 98,
  useApi: true,
  causes: [],
  initiatives: [],
  feed: [],
};


/* ─────────────────────────────────────────
   DATA FETCHING
   ───────────────────────────────────────── */

async function fetchJSON<T = unknown>(path: string): Promise<T | null> {
  const url = config.dataRoot + path;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
    return (await res.json()) as T;
  } catch (err) {
    console.error('[EBX] fetchJSON failed:', err);
    return null;
  }
}

async function fetchAPI<T = unknown>(path: string): Promise<T | null> {
  const url = config.apiBase + path;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
    return (await res.json()) as T;
  } catch (err) {
    console.error('[EBX] fetchAPI failed:', err);
    return null;
  }
}

async function loadCauses(): Promise<Cause[]> {
  const data = config.useApi
    ? await fetchAPI<Cause[]>('/causes')
    : await fetchJSON<Cause[]>('causes/causes.json');
  if (data) config.causes = data;
  return config.causes;
}

async function loadInitiatives(): Promise<Initiative[]> {
  const data = config.useApi
    ? await fetchAPI<Initiative[]>('/initiatives')
    : await fetchJSON<Initiative[]>('causes/initiatives.json');
  if (data) {
    // The API returns ebx_committed; the JSON file uses committed_ebx.
    // Normalize so downstream code keeps working with `committed_ebx`.
    config.initiatives = data.map((i: any) => ({
      ...i,
      committed_ebx: i.committed_ebx ?? i.ebx_committed ?? 0,
    })) as Initiative[];
  }
  return config.initiatives;
}

async function loadFeed(): Promise<FeedPost[]> {
  const data = config.useApi
    ? await fetchAPI<FeedPost[]>('/posts?limit=50')
    : await fetchJSON<FeedPost[]>('causes/feed.json');
  if (data) config.feed = data;
  return config.feed;
}

async function loadAll(): Promise<void> {
  await Promise.all([loadCauses(), loadInitiatives(), loadFeed()]);
}


/* ─────────────────────────────────────────
   CYCLE ENGINE
   ───────────────────────────────────────── */

const MS_PER_DAY = 86_400_000;

const Cycle = {
  MS_PER_DAY,

  now(): CycleState {
    const elapsed = Date.now() - config.cycleStart.getTime();
    const cycleLengthMs = config.cycleLengthDays * MS_PER_DAY;
    const causeLengthMs = config.causeLengthDays * MS_PER_DAY;

    const cycleMs = ((elapsed % cycleLengthMs) + cycleLengthMs) % cycleLengthMs;
    const cycleDay = Math.floor(cycleMs / MS_PER_DAY) + 1;

    const causeIndex = Math.floor(cycleMs / causeLengthMs) % 7;
    const msInCause = cycleMs % causeLengthMs;
    const dayInCause = Math.floor(msInCause / MS_PER_DAY) + 1;
    const causePhase: CycleState['causePhase'] = dayInCause <= 12 ? 'debate' : 'vote';

    const msRemaining = causeLengthMs - msInCause;
    const daysRemaining = Math.floor(msRemaining / MS_PER_DAY);
    const hoursRemaining = Math.floor((msRemaining % MS_PER_DAY) / 3_600_000);

    const anglePerSeg = 360 / 7;
    const baseRotation = -(causeIndex * anglePerSeg);
    const subProgress = msInCause / causeLengthMs;
    const rotationDeg = baseRotation - subProgress * anglePerSeg;

    return {
      causeIndex, causePhase, dayInCause,
      daysRemaining, hoursRemaining,
      rotationDeg, isRecap: false, cycleDay,
    };
  },

  currentCycleNum(): number {
    return Math.floor(
      (Date.now() - config.cycleStart.getTime()) /
        (config.cycleLengthDays * MS_PER_DAY)
    );
  },

  windowStart(causeIndex: number, cycleNum: number): Date {
    return new Date(
      config.cycleStart.getTime() +
        cycleNum * config.cycleLengthDays * MS_PER_DAY +
        causeIndex * config.causeLengthDays * MS_PER_DAY
    );
  },

  voteCloseDate(causeIndex: number, cycleNum: number): Date {
    return new Date(
      Cycle.windowStart(causeIndex, cycleNum).getTime() +
        config.causeLengthDays * MS_PER_DAY
    );
  },

  phaseForCause(causeIndex: number): CycleState['causePhase'] | 'recap' {
    const state = Cycle.now();
    if (state.isRecap) return 'recap';
    if (causeIndex === state.causeIndex) return state.causePhase;
    const offset = ((causeIndex - state.causeIndex) + 7) % 7;
    return offset === 0 ? state.causePhase : 'debate';
  },

  initiativeForCause(causeIndex: number): Initiative | null {
    return config.initiatives.find(i => i.cause_index === causeIndex) ?? null;
  },
};


/* ─────────────────────────────────────────
   THE ANNULUS
   ───────────────────────────────────────── */

interface LabelEntry {
  el: SVGGElement;
  lx: number;
  ly: number;
}

const Annulus = {
  _rafId: null as number | null,
  _connectorLines: [] as SVGLineElement[],
  _segments: [] as SVGPathElement[],
  _labelElements: [] as LabelEntry[],
  _rotatingGroup: null as SVGGElement | null,
  _svg: null as SVGSVGElement | null,
  _vertices: [] as Array<{ x: number; y: number; angle: number }>,

  mount(container: string | Element): void {
    const el = typeof container === 'string'
      ? document.querySelector(container)
      : container;
    if (!el) return;

    if (!config.causes.length) {
      console.warn('[EBX.Annulus] No causes loaded — call EBX.loadCauses() first.');
      return;
    }

    const cx = 200, cy = 200, outerR = 180, innerR = 118;
    const n = 7;
    const anglePerSeg = (2 * Math.PI) / n;

    Annulus._vertices = [];
    for (let i = 0; i < n; i++) {
      const angle = i * anglePerSeg - Math.PI / 2;
      Annulus._vertices.push({
        x: cx + outerR * Math.cos(angle),
        y: cy + outerR * Math.sin(angle),
        angle,
      });
    }

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 400 400');
    svg.style.cssText = 'width:100%;height:100%;display:block;overflow:visible;';
    Annulus._svg = svg;

    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.setAttribute('id', 'ebx-rotating-group');
    group.style.transformOrigin = `${cx}px ${cy}px`;
    svg.appendChild(group);
    Annulus._rotatingGroup = group;

    const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    core.setAttribute('cx', String(cx));
    core.setAttribute('cy', String(cy));
    core.setAttribute('r', String(innerR - 4));
    core.setAttribute('fill', '#0f1a14');
    core.setAttribute('opacity', '0.95');
    group.appendChild(core);

    Annulus._segments = [];
    Annulus._labelElements = [];

    for (let i = 0; i < n; i++) {
      const cause = config.causes[i];
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
      Annulus._segments.push(path);

      const midAngle = startAngle + anglePerSeg / 2;
      const labelR = (outerR + innerR) / 2;
      const lx = cx + labelR * Math.cos(midAngle);
      const ly = cy + labelR * Math.sin(midAngle);

      const labelG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      labelG.setAttribute('pointer-events', 'none');

      const nameLine = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      nameLine.setAttribute('x', String(lx));
      nameLine.setAttribute('y', String(ly - 7));
      nameLine.setAttribute('text-anchor', 'middle');
      nameLine.setAttribute('dominant-baseline', 'middle');
      nameLine.setAttribute('font-size', '10');
      nameLine.setAttribute('font-weight', '700');
      nameLine.setAttribute('fill', '#e8f5ec');
      nameLine.textContent = cause.name;
      labelG.appendChild(nameLine);

      const dateLine = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      dateLine.setAttribute('x', String(lx));
      dateLine.setAttribute('y', String(ly + 7));
      dateLine.setAttribute('text-anchor', 'middle');
      dateLine.setAttribute('dominant-baseline', 'middle');
      dateLine.setAttribute('font-size', '8');
      dateLine.setAttribute('font-weight', '400');
      dateLine.setAttribute('fill', '#e8f5ec');
      dateLine.setAttribute('opacity', '0.65');
      dateLine.setAttribute('data-date-label', String(i));
      dateLine.textContent = '…';
      labelG.appendChild(dateLine);

      group.appendChild(labelG);
      Annulus._labelElements.push({ el: labelG, lx, ly });
    }

    el.appendChild(svg);
    Annulus._initConnectors(svg, n);
    Annulus._tick();
  },

  _initConnectors(svg: SVGSVGElement, n: number): void {
    Annulus._connectorLines.forEach(l => l.remove());
    Annulus._connectorLines = [];
    for (let i = 0; i < n; i++) {
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('stroke', '#a7d7c5');
      line.setAttribute('stroke-width', '1.5');
      line.setAttribute('stroke-dasharray', '3 2');
      line.setAttribute('opacity', '0.6');
      svg.appendChild(line);
      Annulus._connectorLines.push(line);
    }
  },

  _tick(): void {
    Annulus._update();
    Annulus._rafId = requestAnimationFrame(Annulus._tick);
  },

  _update(): void {
    const state = Cycle.now();
    const group = Annulus._rotatingGroup;
    if (!group) return;

    group.style.transform = `rotate(${state.rotationDeg}deg)`;

    const cycleNum = Cycle.currentCycleNum();

    Annulus._labelElements.forEach(({ el, lx, ly }, i) => {
      el.setAttribute('transform', `rotate(${-state.rotationDeg}, ${lx}, ${ly})`);
      const dateLine = el.querySelector('[data-date-label]');
      if (dateLine) {
        dateLine.textContent = Cycle.voteCloseDate(i, cycleNum)
          .toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      }
    });

    Annulus._segments.forEach((seg, i) => {
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

    const nameEl = document.getElementById('ebx-cause-name');
    const timerEl = document.getElementById('ebx-cause-timer');
    const phaseEl = document.getElementById('ebx-cause-phase');

    if (nameEl && state.causeIndex !== null) {
      const cause = config.causes[state.causeIndex];
      if (cause) nameEl.textContent = cause.name;
    }
    if (timerEl) {
      timerEl.textContent = `${state.daysRemaining}d ${state.hoursRemaining}h`;
    }
    if (phaseEl) {
      phaseEl.textContent = state.causePhase === 'vote' ? 'Org Vote' : 'Initiative Debate';
    }
  },

  stop(): void {
    if (Annulus._rafId !== null) cancelAnimationFrame(Annulus._rafId);
  },
};


/* ─────────────────────────────────────────
   FOOTER ONLY (header bar removed)
   ───────────────────────────────────────── */

function initFooter(): void {
  const mount = document.getElementById('ebx-footer-mount');
  if (!mount) return;
  mount.innerHTML = `
    <footer class="ebx-footer">
      <div class="container">
        <div class="ebx-footer__grid">
          <div class="ebx-footer__col">
            <a href="index.html" class="ebx-footer__logo" style="text-decoration:none;color:inherit;">Earthbux</a>
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
              <li><a href="mission.html">Missions</a></li>
              <li><a href="initiative.html">Initiatives</a></li>
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
          <span class="mono">v${config.version}</span>
        </div>
      </div>
    </footer>
  `;
}

function initPage(): void {
  initFooter();
}


/* ─────────────────────────────────────────
   URL + DOM helpers
   ───────────────────────────────────────── */

function getParam(key: string): string | null {
  return new URLSearchParams(window.location.search).get(key);
}

function buildURL(base: string, params: Record<string, string> = {}): string {
  const url = new URL(base, window.location.origin);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  return url.toString();
}

function $<T extends Element = Element>(sel: string, ctx: ParentNode = document): T | null {
  return ctx.querySelector<T>(sel);
}

function $$<T extends Element = Element>(sel: string, ctx: ParentNode = document): T[] {
  return Array.from(ctx.querySelectorAll<T>(sel));
}

function render(target: string | Element, html: string): void {
  const el = typeof target === 'string' ? document.querySelector(target) : target;
  if (el) (el as HTMLElement).innerHTML = html;
}

function renderSkeleton(target: string | Element, rows = 3): void {
  render(
    target,
    Array.from({ length: rows }, () =>
      `<div class="skeleton" style="height:80px;margin-bottom:12px;border-radius:8px;"></div>`
    ).join('')
  );
}

function renderEmpty(target: string | Element, message = 'Nothing here yet.'): void {
  render(target, `
    <div style="text-align:center;padding:48px 24px;color:var(--clr-ink-light);">
      <div style="font-size:2rem;margin-bottom:12px;">🌱</div>
      <p style="font-size:0.9rem;">${message}</p>
    </div>
  `);
}


/* ─────────────────────────────────────────
   FORMATTING
   ───────────────────────────────────────── */

const formatNumber = (n: number | string) => Number(n).toLocaleString();
const formatEBX = (n: number | string) => `${formatNumber(n)} EBX`;
const formatPercent = (v: number, d = 1) => `${Number(v).toFixed(d)}%`;
const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  const hours = Math.floor(diff / 3_600_000);
  const days = Math.floor(diff / 86_400_000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 30) return `${days}d ago`;
  return formatDate(iso);
}


/* ─────────────────────────────────────────
   COMPONENTS
   ───────────────────────────────────────── */

function tokenChip({ index, title, org, causeColor, amount }: TokenChip): string {
  return `
    <div class="ebx-token" style="border-left: 4px solid ${causeColor};">
      <div class="ebx-token__index mono">#${String(index).padStart(3, '0')}</div>
      <div class="ebx-token__title">${title}</div>
      ${org ? `<div class="ebx-token__org text-xs text-muted">${org}</div>` : ''}
      ${amount != null ? `<div class="ebx-token__amount mono text-xs">${formatEBX(amount)}</div>` : ''}
    </div>
  `;
}

function creditBadge(holdings: CreditHolding[], size = 64): string {
  const causes = config.causes;
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
    <div class="ebx-credit-badge" title="${formatEBX(totalEBX)} across ${holdings.length} cause(s)">
      <svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
        <circle cx="${cx}" cy="${cy}" r="${outerR + 1}" fill="#0f1a14" opacity="0.6"/>
        ${segments}
        <circle cx="${cx}" cy="${cy}" r="${innerR - 2}" fill="#0f1a14" opacity="0.9"/>
      </svg>
    </div>
  `;
}

function tag(label: string, variant: string = 'neutral'): string {
  return `<span class="tag tag-${variant}">${label}</span>`;
}

function progressBar(percent: number, variant = ''): string {
  const cls = variant ? `progress-bar__fill--${variant}` : '';
  return `
    <div class="progress-bar">
      <div class="progress-bar__fill ${cls}" style="width:${Math.min(100, percent)}%"></div>
    </div>
  `;
}

function statBlock(value: string | number, label: string, variant = ''): string {
  return `
    <div class="stat-block">
      <div class="stat-block__value ${variant ? 'stat-block__value--' + variant : ''}">${value}</div>
      <div class="stat-block__label">${label}</div>
    </div>
  `;
}

function initiativeCard(init: Initiative & { phase?: string; pool_total?: number; index?: number }): string {
  const cause = config.causes.find(c => c.index === init.cause_index);
  const causeColor = cause ? cause.color : '#888';
  const phaseLabelMap: Record<string, { label: string; variant: string }> = {
    org_vote:          { label: 'Org Vote Open',     variant: 'amber' },
    initiative_debate: { label: 'Initiative Debate', variant: 'forest' },
    planning:          { label: 'Financial Planning', variant: 'sage' },
    execution:         { label: 'In Execution',       variant: 'sage' },
    resolved:          { label: 'Resolved',           variant: 'neutral' },
  };
  const phase = phaseLabelMap[init.phase ?? ''] || { label: init.phase ?? init.status, variant: 'neutral' };
  const pct = (init.pool_total ?? 0) > 0
    ? Math.round((init.committed_ebx / (init.pool_total ?? 1)) * 100)
    : 0;

  return `
    <a href="initiative.html?id=${init.id}" class="card ebx-init-card"
       style="text-decoration:none;display:block;border-left:4px solid ${causeColor};">
      <div class="flex-between mb-sm">
        ${tag(phase.label, phase.variant)}
        <span class="mono text-xs text-muted">#${String(init.index ?? 0).padStart(3, '0')}</span>
      </div>
      <h4 style="margin-bottom:var(--sp-xs);">${init.emoji ?? ''} ${init.title}</h4>
      <p class="text-xs text-muted mb-md">${cause ? cause.name : ''} · ${init.winning_org || 'Org TBD'}</p>
      <p class="text-sm text-muted mb-md">${init.description ?? ''}</p>
      ${progressBar(pct, 'amber')}
      <div class="flex-between mt-sm">
        <span class="text-xs text-muted">${formatEBX(init.committed_ebx)} committed</span>
        <span class="text-xs fw-medium" style="color:${causeColor};">${pct}% of pool →</span>
      </div>
    </a>
  `;
}

function opinionCard(op: Opinion): string {
  const typeVariant = ({ org: 'forest', initiative: 'amber', other: 'neutral' } as Record<string, string>)[op.type] || 'neutral';
  return `
    <div class="card-flat ebx-opinion">
      <div class="flex-between mb-sm">
        <div class="flex gap-sm" style="align-items:center;">
          ${tag(op.type, typeVariant)}
          <span class="text-xs text-muted">${timeAgo(op.created_at)}</span>
        </div>
        <span class="text-xs text-muted">+${op.feedback} feedback</span>
      </div>
      <p class="text-sm" style="margin-bottom:var(--sp-sm);">${op.body}</p>
      <div class="text-xs text-muted">— ${op.author_handle}</div>
    </div>
  `;
}

/**
 * Render a feed post card (used by the homepage feed-strip below the annulus).
 */
function feedCard(post: FeedPost): string {
  const cause = config.causes.find(c => c.index === post.cause_index);
  const causeColor = cause ? cause.color : '#888';
  const typeLabel: Record<string, string> = {
    editorial:  'Editorial',
    opinion:    'Opinion',
    org_update: 'Org Update',
    headline:   'Headline',
  };
  const label = typeLabel[post.type] ?? post.type;
  return `
    <a href="feed.html?id=${post.id}" class="ebx-feed-card"
       style="text-decoration:none;color:inherit;display:flex;flex-direction:column;
              gap:8px;padding:16px;border-radius:10px;
              background:rgba(15,26,20,0.5);border:1px solid rgba(255,255,255,0.07);
              border-left:3px solid ${causeColor};transition:background 0.2s;">
      <div style="display:flex;justify-content:space-between;align-items:baseline;
                  font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.12em;
                  text-transform:uppercase;opacity:0.65;">
        <span style="color:${causeColor};">${label}${cause ? ' · ' + cause.name : ''}</span>
        <span style="color:rgba(245,240,232,0.4);">${timeAgo(post.created_at)}</span>
      </div>
      ${post.title ? `<h4 style="font-size:0.95rem;line-height:1.3;color:rgba(245,240,232,0.92);margin:0;">${post.title}</h4>` : ''}
      <p style="font-size:0.78rem;line-height:1.45;color:rgba(245,240,232,0.6);margin:0;
                display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">
        ${post.body}
      </p>
      <div style="display:flex;justify-content:space-between;align-items:center;
                  font-family:var(--font-mono);font-size:0.6rem;color:rgba(245,240,232,0.4);">
        <span>— ${post.author}</span>
        <span>♥ ${post.likes}</span>
      </div>
    </a>
  `;
}


/* ─────────────────────────────────────────
   SEARCH & FILTER HELPERS
   ───────────────────────────────────────── */

function filterBySearch<T>(items: T[], query: string, fields: (keyof T)[]): T[] {
  if (!query) return items;
  const q = query.toLowerCase();
  return items.filter(item =>
    fields.some(f => String(item[f] ?? '').toLowerCase().includes(q))
  );
}

function filterByField<T>(items: T[], field: keyof T, value: string): T[] {
  if (!value || value === 'all') return items;
  return items.filter(item => String(item[field]) === value);
}

function sortBy<T>(items: T[], field: keyof T, dir: 'asc' | 'desc' = 'desc'): T[] {
  return [...items].sort((a, b) => {
    const av = a[field], bv = b[field];
    if (typeof av === 'number' && typeof bv === 'number') {
      return dir === 'desc' ? bv - av : av - bv;
    }
    return dir === 'desc'
      ? String(bv).localeCompare(String(av))
      : String(av).localeCompare(String(bv));
  });
}


/* ─────────────────────────────────────────
   AUTH (browser-side helpers for the API)
   ───────────────────────────────────────── */

const Auth = {
  tokenKey: 'ebx_auth_token',

  getToken(): string | null {
    return localStorage.getItem(Auth.tokenKey);
  },

  setToken(t: string): void {
    localStorage.setItem(Auth.tokenKey, t);
  },

  clear(): void {
    localStorage.removeItem(Auth.tokenKey);
  },

  isLoggedIn(): boolean {
    return !!Auth.getToken();
  },

  async login(username: string, password: string): Promise<boolean> {
    const body = new URLSearchParams({ username, password });
    const res = await fetch(`${config.apiBase}/auth/login`, {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (!res.ok) return false;
    const data = (await res.json()) as { access_token: string };
    Auth.setToken(data.access_token);
    return true;
  },

  async signup(email: string, handle: string, password: string): Promise<boolean> {
    const res = await fetch(`${config.apiBase}/auth/signup`, {
      method: 'POST',
      body: JSON.stringify({ email, handle, password }),
      headers: { 'Content-Type': 'application/json' },
    });
    return res.ok;
  },

  async fetchAuthed(path: string, init: RequestInit = {}): Promise<Response> {
    const headers = new Headers(init.headers || {});
    const token = Auth.getToken();
    if (token) headers.set('Authorization', `Bearer ${token}`);
    return fetch(config.apiBase + path, { ...init, headers });
  },
};


/* ─────────────────────────────────────────
   PUBLIC NAMESPACE
   ───────────────────────────────────────── */

const EBX = {
  config,
  // data
  fetchJSON, fetchAPI, loadCauses, loadInitiatives, loadFeed, loadAll,
  // engine
  Cycle, Annulus,
  // page setup
  initFooter, initPage,
  // url
  getParam, buildURL,
  // dom
  $, $$, render, renderSkeleton, renderEmpty,
  // formatting
  formatNumber, formatEBX, formatPercent, formatDate, timeAgo,
  // components
  tokenChip, creditBadge, tag, progressBar, statBlock,
  initiativeCard, opinionCard, feedCard,
  // filters
  filterBySearch, filterByField, sortBy,
  // auth
  Auth,
};

(window as any).EBX = EBX;

document.addEventListener('DOMContentLoaded', () => {
  EBX.initPage();
});

export default EBX;
