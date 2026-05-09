/* =============================================
   EARTHBUCKS — Shared TypeScript Utilities
   src/ebx_shared.ts  v0.4.0

   Built into resources/js/ebx_shared.js as an IIFE that exposes a global
   `EBX` symbol for use by inline <script> blocks on every HTML page.

   v0.4 redesign
   -------------
   • Cycle: 49-day cause windows, staggered by 7 days. Every week one cause
     has its decision day. Annulus rotates 1/7 per week.
   • Annulus: two-tier. Inner ring carries the cause name + decision date
     (clickable to cause page). Outer ring is the org race for that cause —
     stacked sub-arcs sized by vote share, colored by rank.
   • Active-mission state has been removed from the homepage; missions live
     in the feed only.
   ============================================= */

import type {
  Cause,
  CreditHolding,
  CycleState,
  FeedPost,
  Initiative
  Organization,
  TokenChip,
  VoteShare,
} from './types.js';

declare global {
  interface Window {
    EBX: typeof EBX;
  }
}


/* ─────────────────────────────────────────
   API CONFIG
   ───────────────────────────────────────── */

interface EBXConfig {
  dataRoot: string;
  apiBase: string;
  version: string;
  cycleStart: Date;
  /** Length of one cause's debate+election window. */
  causeLengthDays: number;
  /** Spacing between consecutive cause decisions (also the rotation step). */
  decisionIntervalDays: number;
  useApi: boolean;
  causes: Cause[];
  initiatives: Initiative[];
  organizations: Organization[];
  feed: FeedPost[];
}

const config: EBXConfig = {
  dataRoot: '/data/',
  apiBase: '',  // empty means same origin — works when FastAPI hosts the static files
  version: '0.4.0',
  cycleStart: new Date('2026-01-01T00:00:00'),
  causeLengthDays: 49,         // 7 weeks per cause
  decisionIntervalDays: 7,     // one decision per week
  useApi: true,
  causes: [],
  initiatives: [],
  organizations: [],
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
    // API returns ebx_committed; legacy JSON uses committed_ebx. Normalize.
    config.initiatives = data.map((i: any) => {
      const causeIndex = i.cause_index ??
        (config.causes.find(c => c.id === i.cause_id)?.index ?? 0);
      return {
        ...i,
        cause_index: causeIndex,
        committed_ebx: i.committed_ebx ?? i.ebx_committed ?? 0,
      } as Initiative;
    });
  }
  return config.initiatives;
}

async function loadOrganizations(): Promise<Organization[]> {
  const data = config.useApi
    ? await fetchAPI<any[]>('/organizations')
    : await fetchJSON<Organization[]>('causes/orgs.json');
  if (data) {
    config.organizations = data.map((o: any) => ({
      id: o.id,
      name: o.name,
      causes: o.causes ?? [],
      verified: o.verified ?? false,
      description: o.description,
      founded: o.founded ?? o.founded_year,
    }));
  }
  return config.organizations;
}

async function loadFeed(): Promise<FeedPost[]> {
  const data = config.useApi
    ? await fetchAPI<FeedPost[]>('/posts?limit=50')
    : await fetchJSON<FeedPost[]>('causes/feed.json');
  if (data) config.feed = data;
  return config.feed;
}

async function loadAll(): Promise<void> {
  // Causes must come first so the initiatives loader can fill cause_index.
  await loadCauses();
  await Promise.all([loadInitiatives(), loadOrganizations(), loadFeed()]);
}


/* ─────────────────────────────────────────
   CYCLE ENGINE
   Each cause: 49-day debate+election, staggered by 7 days.
   ───────────────────────────────────────── */

const MS_PER_DAY = 86_400_000;

const Cycle = {
  MS_PER_DAY,

  /** Current state — which cause has its decision THIS week, etc. */
  now(): CycleState {
    const elapsedMs = Date.now() - config.cycleStart.getTime();
    const dayMs = MS_PER_DAY;
    const weekMs = config.decisionIntervalDays * dayMs;

    const totalDays = Math.floor(elapsedMs / dayMs);
    const weekNum = Math.floor(elapsedMs / weekMs);
    const causeIndex = ((weekNum % 7) + 7) % 7;
    const dayInWeek = totalDays - weekNum * config.decisionIntervalDays;

    // Decision date for the current cause = end of the current week.
    const decisionMs = (weekNum + 1) * weekMs - elapsedMs;
    const daysRemaining = Math.max(0, Math.floor(decisionMs / dayMs));
    const hoursRemaining = Math.max(
      0, Math.floor((decisionMs % dayMs) / 3_600_000)
    );

    // Annulus rotation: bring the active cause to 12 o'clock, then nudge
    // smoothly within the week so it animates.
    const anglePerSeg = 360 / 7;
    const subProgress = (elapsedMs % weekMs) / weekMs;
    const rotationDeg = -(causeIndex * anglePerSeg) - subProgress * anglePerSeg;

    return {
      causeIndex,
      daysRemaining,
      hoursRemaining,
      rotationDeg,
      weekNum,
      dayInWeek,
    };
  },

  /** Decision date for any cause: the next end-of-week when (weekNum % 7) === causeIndex. */
  nextDecisionDate(causeIndex: number): Date {
    const state = Cycle.now();
    const offset = ((causeIndex - state.causeIndex) + 7) % 7;
    const targetWeek = state.weekNum + offset;
    return new Date(
      config.cycleStart.getTime() +
        (targetWeek + 1) * config.decisionIntervalDays * MS_PER_DAY
    );
  },

  /** Date when this cause's CURRENT 7-week debate window opened. */
  windowStart(causeIndex: number): Date {
    const decision = Cycle.nextDecisionDate(causeIndex);
    return new Date(decision.getTime() - config.causeLengthDays * MS_PER_DAY);
  },

  /** Back-compat alias (older inline scripts called voteCloseDate). */
  voteCloseDate(causeIndex: number): Date {
    return Cycle.nextDecisionDate(causeIndex);
  },

  /** 0-based count of completed full rotations since cycleStart. */
  currentCycleNum(): number {
    const elapsedMs = Date.now() - config.cycleStart.getTime();
    return Math.floor(
      elapsedMs / (7 * config.decisionIntervalDays * MS_PER_DAY)
    );
  },

  initiativeForCause(causeIndex: number): Initiative | null {
    return config.initiatives.find(i => i.cause_index === causeIndex) ?? null;
  },
};


/* ─────────────────────────────────────────
   VOTES — deterministic mock distribution
   Replace with /causes/{id}/votes once the backend has a tally.
   ───────────────────────────────────────── */

/** Reverse-rainbow palette: leader → laggard. */
const RANK_COLORS = [
  '#a78bfa', // 1 violet
  '#818cf8', // 2 indigo
  '#60a5fa', // 3 blue
  '#34d399', // 4 green
  '#fbbf24', // 5 yellow
  '#fb923c', // 6 orange
  '#f87171', // 7 red
];
const OTHER_COLOR = '#6b7280'; // gray for sub-5%

function rankColor(rank: number): string {
  if (rank < 0) return OTHER_COLOR;
  return RANK_COLORS[Math.min(rank, RANK_COLORS.length - 1)];
}

/** Stable hash → [0,1). */
function pseudoRandom(seed: number): number {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

const Votes = {
  RANK_COLORS,
  OTHER_COLOR,
  rankColor,

  /**
   * Synthesize a stable vote distribution for (causeIndex, cycleNum, orgs).
   * Bucket anything < 5% into a single gray "Other" slice.
   */
  forCause(causeIndex: number, cycleNum: number, orgs: Organization[]): VoteShare[] {
    if (!orgs.length) return [];

    // Generate raw weights, deterministic per (cause, cycle, org).
    const weights = orgs.map((o, i) => {
      const seed = causeIndex * 1009 + cycleNum * 31 + i * 17 + hashString(o.id);
      // Skewed so a few orgs dominate; rest are tail.
      return Math.pow(pseudoRandom(seed) + 0.05, 2.4);
    });
    const total = weights.reduce((a, b) => a + b, 0) || 1;

    const shares = orgs
      .map((o, i) => ({
        org_id: o.id,
        org_name: o.name,
        pct: (weights[i] / total) * 100,
      }))
      .sort((a, b) => b.pct - a.pct);

    const main = shares.filter(s => s.pct >= 5);
    const tail = shares.filter(s => s.pct < 5);
    const result: VoteShare[] = main.map((s, idx) => ({
      ...s,
      rank: idx,
      isOther: false,
      color: rankColor(idx),
    }));
    if (tail.length) {
      result.push({
        org_id: 'other',
        org_name: `Other (${tail.length})`,
        pct: tail.reduce((a, b) => a + b.pct, 0),
        rank: -1,
        isOther: true,
        color: OTHER_COLOR,
      });
    }
    return result;
  },

  /** Pick the orgs that will appear in a given cause's race. */
  orgsForCause(causeIndex: number): Organization[] {
    const all = config.organizations;
    if (!all.length) return [];
    // Prefer orgs explicitly mapped to this cause; fall back to all of them
    // (the data may not yet associate every org with every cause).
    const tagged = all.filter(o => (o.causes || []).includes(causeIndex));
    return tagged.length ? tagged : all;
  },
};

function hashString(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 16777619) >>> 0;
  }
  return h % 100000;
}


/* ─────────────────────────────────────────
   THE ANNULUS — two-tier
   ───────────────────────────────────────── */

interface SegmentEntry {
  innerPath: SVGPathElement;
  outerGroup: SVGGElement;
  labelGroup: SVGGElement;
  midX: number;
  midY: number;
}

const Annulus = {
  _rafId: null as number | null,
  _rotatingGroup: null as SVGGElement | null,
  _segments: [] as SegmentEntry[],
  _svg: null as SVGSVGElement | null,
  _cx: 200,
  _cy: 200,
  _outerR: 184,
  _midR: 144,        // boundary between outer ring and inner ring
  _innerR: 104,      // inner edge of the inner ring

  mount(container: string | Element): void {
    const el = typeof container === 'string'
      ? document.querySelector(container)
      : container;
    if (!el) return;

    if (!config.causes.length) {
      console.warn('[EBX.Annulus] No causes loaded — call EBX.loadCauses() first.');
      return;
    }

    const { _cx: cx, _cy: cy, _outerR: outerR, _midR: midR, _innerR: innerR } = Annulus;
    const n = 7;
    const anglePerSeg = (2 * Math.PI) / n;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 400 400');
    svg.style.cssText = 'width:100%;height:100%;display:block;overflow:visible;';
    Annulus._svg = svg;

    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.setAttribute('id', 'ebx-rotating-group');
    group.style.transformOrigin = `${cx}px ${cy}px`;
    svg.appendChild(group);
    Annulus._rotatingGroup = group;

    // Hub fill so the inner ring has a clean background.
    const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    core.setAttribute('cx', String(cx));
    core.setAttribute('cy', String(cy));
    core.setAttribute('r', String(innerR - 2));
    core.setAttribute('fill', '#0f1a14');
    core.setAttribute('opacity', '0.95');
    group.appendChild(core);

    Annulus._segments = [];

    for (let i = 0; i < n; i++) {
      const cause = config.causes[i];
      const startAngle = i * anglePerSeg - Math.PI / 2;
      const endAngle = startAngle + anglePerSeg;

      // ── INNER RING segment (cause band) ──
      const innerPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      innerPath.setAttribute('d', annularSectorPath(cx, cy, midR, innerR, startAngle, endAngle));
      innerPath.setAttribute('fill', cause.color);
      innerPath.setAttribute('fill-opacity', '0.92');
      innerPath.setAttribute('stroke', '#0f1a14');
      innerPath.setAttribute('stroke-width', '1.5');
      innerPath.style.cursor = 'pointer';
      innerPath.style.transition = 'filter 0.2s';
      innerPath.addEventListener('mouseenter', () => { innerPath.style.filter = 'brightness(1.25)'; });
      innerPath.addEventListener('mouseleave', () => { innerPath.style.filter = 'none'; });
      innerPath.addEventListener('click', () => {
        window.location.href = `cause.html?id=${cause.id}`;
      });
      group.appendChild(innerPath);

      // ── OUTER RING container (vote sub-arcs filled in _update) ──
      const outerGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      outerGroup.setAttribute('data-segment', String(i));
      group.appendChild(outerGroup);

      // ── Label centered in the inner band, counter-rotated to stay upright ──
      const midAngle = startAngle + anglePerSeg / 2;
      const labelR = (midR + innerR) / 2;
      const lx = cx + labelR * Math.cos(midAngle);
      const ly = cy + labelR * Math.sin(midAngle);

      const labelGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      labelGroup.setAttribute('pointer-events', 'none');

      const nameLine = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      nameLine.setAttribute('x', String(lx));
      nameLine.setAttribute('y', String(ly - 6));
      nameLine.setAttribute('text-anchor', 'middle');
      nameLine.setAttribute('dominant-baseline', 'middle');
      nameLine.setAttribute('font-size', '10');
      nameLine.setAttribute('font-weight', '700');
      nameLine.setAttribute('fill', '#0f1a14');
      nameLine.textContent = cause.name;
      labelGroup.appendChild(nameLine);

      const dateLine = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      dateLine.setAttribute('x', String(lx));
      dateLine.setAttribute('y', String(ly + 7));
      dateLine.setAttribute('text-anchor', 'middle');
      dateLine.setAttribute('dominant-baseline', 'middle');
      dateLine.setAttribute('font-size', '8');
      dateLine.setAttribute('fill', '#0f1a14');
      dateLine.setAttribute('opacity', '0.7');
      dateLine.setAttribute('data-date-label', String(i));
      dateLine.textContent = '…';
      labelGroup.appendChild(dateLine);

      group.appendChild(labelGroup);

      Annulus._segments.push({
        innerPath, outerGroup, labelGroup,
        midX: lx, midY: ly,
      });
    }

    el.appendChild(svg);
    Annulus._tick();
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
    const { _cx: cx, _cy: cy, _outerR: outerR, _midR: midR } = Annulus;
    const n = 7;
    const anglePerSeg = (2 * Math.PI) / n;

    Annulus._segments.forEach((seg, i) => {
      // Counter-rotate labels so they stay upright.
      seg.labelGroup.setAttribute(
        'transform',
        `rotate(${-state.rotationDeg}, ${seg.midX}, ${seg.midY})`
      );
      const dateLine = seg.labelGroup.querySelector('[data-date-label]');
      if (dateLine) {
        dateLine.textContent = Cycle.nextDecisionDate(i)
          .toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      }

      // Highlight the active cause's inner segment.
      if (i === state.causeIndex) {
        seg.innerPath.setAttribute('stroke', '#ffffff');
        seg.innerPath.setAttribute('stroke-width', '3');
        seg.innerPath.setAttribute('filter', 'drop-shadow(0 0 8px rgba(255,255,200,0.55))');
      } else {
        seg.innerPath.setAttribute('stroke', '#0f1a14');
        seg.innerPath.setAttribute('stroke-width', '1.5');
        seg.innerPath.removeAttribute('filter');
      }

      // ── Outer ring rendering ─────────────────────────────────────
      // Active cause: leave the outer band empty (a "chunk" cut out of the
      // wheel), the right-side election panel picks it up.
      // Non-active causes: stack initiative sub-arcs sized by ebx_committed,
      // leader gets the full cause color, runners-up fade toward white.
      while (seg.outerGroup.firstChild) {
        seg.outerGroup.removeChild(seg.outerGroup.firstChild);
      }
      const startAngle = i * anglePerSeg - Math.PI / 2;
      const endAngle = startAngle + anglePerSeg;

      if (i === state.causeIndex) {
        // Empty outer band, faint dashed outline so the slot is visible.
        const ghost = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        ghost.setAttribute('d', annularSectorPath(cx, cy, outerR, midR, startAngle, endAngle));
        ghost.setAttribute('fill', 'rgba(15,26,20,0.4)');
        ghost.setAttribute('stroke', config.causes[i]?.color ?? '#ffffff');
        ghost.setAttribute('stroke-width', '1');
        ghost.setAttribute('stroke-dasharray', '3 3');
        ghost.setAttribute('opacity', '0.55');
        seg.outerGroup.appendChild(ghost);
      } else {
        const inits = config.initiatives
          .filter(x => x.cause_index === i)
          .sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0));
        const total = inits.reduce((s, x) => s + (x.committed_ebx || 0), 0);
        const causeColor = config.causes[i]?.color ?? '#888';

        // If nothing is committed yet, give every initiative an equal slice
        // so the ring isn't empty.
        const useEqual = total <= 0 && inits.length > 0;
        const denom = useEqual ? inits.length : total;

        let cursor = startAngle;
        const totalAngle = endAngle - startAngle;
        inits.forEach((init, rank) => {
          const weight = useEqual ? 1 : (init.committed_ebx || 0);
          if (weight <= 0) return;
          const arcSize = totalAngle * (weight / denom);
          const a0 = cursor;
          const a1 = Math.min(endAngle, cursor + arcSize);
          // Fade: 0 = full cause color, 1 = white. Curve so first 3 ranks stay vivid.
          const t = inits.length === 1 ? 0 : Math.min(1, rank / Math.max(2, inits.length - 1));
          const sub = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          sub.setAttribute('d', annularSectorPath(cx, cy, outerR, midR, a0, a1));
          sub.setAttribute('fill', fadeToWhite(causeColor, t));
          sub.setAttribute('fill-opacity', '0.85');
          sub.setAttribute('stroke', '#0f1a14');
          sub.setAttribute('stroke-width', '0.6');
          const titleEl = document.createElementNS('http://www.w3.org/2000/svg', 'title');
          titleEl.textContent = `${init.title} — ${init.committed_ebx ?? 0} EBX`;
          sub.appendChild(titleEl);
          seg.outerGroup.appendChild(sub);
          cursor = a1;
        });

        if (inits.length === 0) {
          const empty = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          empty.setAttribute('d', annularSectorPath(cx, cy, outerR, midR, startAngle, endAngle));
          empty.setAttribute('fill', causeColor);
          empty.setAttribute('fill-opacity', '0.18');
          seg.outerGroup.appendChild(empty);
        }
      }
    });;

    // Optional: legacy hooks for any inline scripts that still query these.
    const nameEl = document.getElementById('ebx-cause-name');
    const timerEl = document.getElementById('ebx-cause-timer');
    if (nameEl) {
      const cause = config.causes[state.causeIndex];
      if (cause) nameEl.textContent = cause.name;
    }
    if (timerEl) {
      timerEl.textContent = `${state.daysRemaining}d ${state.hoursRemaining}h`;
    }
  },

  stop(): void {
    if (Annulus._rafId !== null) cancelAnimationFrame(Annulus._rafId);
  },
};

/** Build an SVG path for an annular sector (donut wedge). */
function annularSectorPath(
  cx: number, cy: number,
  rOuter: number, rInner: number,
  a0: number, a1: number,
): string {
  const x1 = cx + rOuter * Math.cos(a0);
  const y1 = cy + rOuter * Math.sin(a0);
  const x2 = cx + rOuter * Math.cos(a1);
  const y2 = cy + rOuter * Math.sin(a1);
  const x3 = cx + rInner * Math.cos(a1);
  const y3 = cy + rInner * Math.sin(a1);
  const x4 = cx + rInner * Math.cos(a0);
  const y4 = cy + rInner * Math.sin(a0);
  const largeArc = a1 - a0 > Math.PI ? 1 : 0;
  return [
    `M ${x1} ${y1}`,
    `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2} ${y2}`,
    `L ${x3} ${y3}`,
    `A ${rInner} ${rInner} 0 ${largeArc} 0 ${x4} ${y4}`,
    'Z',
  ].join(' ');
}


/* ─────────────────────────────────────────
   FOOTER (no header bar — About lives in the footer)
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
const formatShortDate = (d: Date | string) =>
  new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

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
    return `<path d="${annularSectorPath(cx, cy, outerR, innerR, startAngle, endAngle)}"
      fill="${cause.color}" fill-opacity="${opacity}" stroke="#0f1a14" stroke-width="0.8"/>`;
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

/**
 * Race card — the homepage side card. Cause name, leading initiative,
 * top org standings color-coded by rank.
 */
function raceCard(causeIndex: number): string {
  const cause = config.causes.find(c => c.index === causeIndex);
  if (!cause) return '';

  const init = config.initiatives
    .filter(i => i.cause_index === causeIndex)
    .sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];

  const cycleNum = Cycle.currentCycleNum();
  const orgs = Votes.orgsForCause(causeIndex);
  const shares = Votes.forCause(causeIndex, cycleNum, orgs);
  const decision = Cycle.nextDecisionDate(causeIndex);

  return `
    <a class="race-card" href="cause.html?id=${cause.id}"
       style="--rc-color:${cause.color};
              display:block;text-decoration:none;width:228px;
              background:rgba(15,26,20,0.72);
              border:1px solid var(--rc-color);border-radius:10px;
              padding:11px 13px;transition:background 0.2s;">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px;">
        <span style="font-family:var(--font-mono);font-size:0.54rem;letter-spacing:0.12em;
                     text-transform:uppercase;color:var(--rc-color);opacity:0.85;">${cause.name}</span>
        <span style="font-family:var(--font-mono);font-size:0.54rem;color:rgba(245,240,232,0.4);">
          ${formatShortDate(decision)}
        </span>
      </div>
      <div style="font-size:0.78rem;font-weight:600;color:rgba(245,240,232,0.9);
                  line-height:1.3;margin-bottom:8px;
                  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
        ${init ? `${init.emoji ?? ''} ${init.title}` : 'No initiative yet'}
      </div>
      <div style="display:flex;flex-direction:column;gap:3px;">
        ${shares.slice(0, 4).map(s => `
          <div style="display:flex;justify-content:space-between;align-items:center;
                      font-family:var(--font-mono);font-size:0.6rem;
                      color:${s.color};">
            <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
                         max-width:140px;">${s.org_name}</span>
            <span style="opacity:0.75;">${s.pct.toFixed(0)}%</span>
          </div>
        `).join('')}
      </div>
    </a>
  `;
}


/* SEARCH AND FILTER HELPERS */

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


/* AUTH (browser-side helpers for the API) */

const Auth = {
  tokenKey: 'ebx_auth_token',
  getToken(): string | null { return localStorage.getItem(Auth.tokenKey); },
  setToken(t: string): void { localStorage.setItem(Auth.tokenKey, t); },
  clear(): void { localStorage.removeItem(Auth.tokenKey); },
  isLoggedIn(): boolean { return !!Auth.getToken(); },

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


/* PUBLIC NAMESPACE */



/* ─────────────────────────────────────────
   Color helper: fade hex toward white
   ───────────────────────────────────────── */
function fadeToWhite(hex: string, t: number): string {
  const m = hex.match(/^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
  if (!m) return hex;
  const r = parseInt(m[1], 16);
  const g = parseInt(m[2], 16);
  const b = parseInt(m[3], 16);
  const lerp = (a: number) => Math.round(a + (255 - a) * t);
  return `rgb(${lerp(r)}, ${lerp(g)}, ${lerp(b)})`;
}


/* ─────────────────────────────────────────
   Election panel
   Renders this week's cause + leading initiative + org race.
   Designed to sit visually next to the active (empty) annulus segment.
   ───────────────────────────────────────── */
function electionPanel(causeIndex: number): string {
  const cause = config.causes.find(c => c.index === causeIndex);
  if (!cause) return '';

  const cycleNum = Cycle.currentCycleNum();
  const orgs = Votes.orgsForCause(causeIndex);
  const shares = Votes.forCause(causeIndex, cycleNum, orgs);
  const decision = Cycle.nextDecisionDate(causeIndex);
  const state = Cycle.now();

  const init = config.initiatives
    .filter(i => i.cause_index === causeIndex)
    .sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];

  const leader = shares[0];
  const leaderColor = leader ? leader.color : cause.color;

  const rows = shares.slice(0, 6).map(s => `
    <div style="display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:center;
                font-family:var(--font-mono);font-size:0.66rem;">
      <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${s.color};"></span>
      <span style="color:rgba(245,240,232,0.85);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
        ${s.org_name}
      </span>
      <span style="color:rgba(245,240,232,0.5);">${s.pct.toFixed(0)}%</span>
    </div>
    <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:2px;margin:1px 0 4px;overflow:hidden;">
      <div style="height:100%;width:${Math.max(2, s.pct).toFixed(1)}%;background:${s.color};opacity:0.85;border-radius:2px;"></div>
    </div>
  `).join('');

  return `
    <div class="election-panel" style="
      --epc:${cause.color};
      position:relative;
      background:rgba(15,26,20,0.78);
      border:1px solid var(--epc);
      border-radius:12px;
      padding:14px 16px;
      min-width:260px; max-width:320px;
      backdrop-filter:blur(6px);
    ">
      <!-- Chevron pointing back at the wheel (the "chunk taken out" lives there) -->
      <div style="position:absolute;left:-9px;top:22px;width:0;height:0;
                  border-top:9px solid transparent;border-bottom:9px solid transparent;
                  border-right:9px solid var(--epc);opacity:0.85;"></div>

      <div style="font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.16em;
                  text-transform:uppercase;color:var(--epc);opacity:0.85;">
        Election in progress
      </div>
      <div style="font-family:var(--font-display);font-size:1.05rem;font-weight:700;
                  color:rgba(245,240,232,0.95);margin:2px 0 2px;">
        ${cause.name}
      </div>
      <div style="font-family:var(--font-mono);font-size:0.65rem;color:rgba(245,240,232,0.55);
                  margin-bottom:10px;">
        Decision ${formatShortDate(decision)} · ${state.daysRemaining}d ${state.hoursRemaining}h remaining
      </div>

      <div style="font-family:var(--font-mono);font-size:0.5rem;letter-spacing:0.16em;
                  text-transform:uppercase;color:rgba(245,240,232,0.4);margin-bottom:4px;">
        Leading initiative
      </div>
      <div style="font-size:0.82rem;font-weight:600;color:rgba(245,240,232,0.92);
                  line-height:1.3;margin-bottom:12px;">
        ${init ? `${init.emoji ?? ''} ${init.title}` : 'No initiative committed yet'}
      </div>

      <div style="font-family:var(--font-mono);font-size:0.5rem;letter-spacing:0.16em;
                  text-transform:uppercase;color:rgba(245,240,232,0.4);margin-bottom:6px;">
        Organization race
      </div>
      ${rows || '<div style="font-size:0.72rem;color:rgba(245,240,232,0.4);">No orgs in this race yet.</div>'}

      <div style="display:flex;gap:8px;margin-top:14px;">
        <a href="cause.html?id=${cause.id}" style="
          flex:1;text-align:center;text-decoration:none;
          font-family:var(--font-mono);font-size:0.68rem;font-weight:600;
          padding:7px 10px;border-radius:6px;
          background:var(--epc);color:#0f1a14;">
          Engage →
        </a>
        <a href="feed.html?cause=${cause.id}" style="
          flex:1;text-align:center;text-decoration:none;
          font-family:var(--font-mono);font-size:0.68rem;
          padding:7px 10px;border-radius:6px;
          border:1px solid rgba(255,255,255,0.15);color:rgba(245,240,232,0.7);">
          Discussion
        </a>
      </div>
    </div>
  `;
}

const EBX = {
  config,
  fetchJSON, fetchAPI,
  loadCauses, loadInitiatives, loadOrganizations, loadFeed, loadAll,
  Cycle, Annulus, Votes,
  initFooter, initPage,
  getParam, buildURL,
  $: $, $$: $$, render, renderSkeleton, renderEmpty,
  formatNumber, formatEBX, formatPercent, formatDate, formatShortDate, timeAgo,
  tokenChip, creditBadge, tag, progressBar, statBlock,
  initiativeCard, electionPanel, feedCard, raceCard,
  filterBySearch, filterByField, sortBy,
  Auth,
};

(window as any).EBX = EBX;

document.addEventListener('DOMContentLoaded', () => {
  EBX.initPage();
});

export default EBX;
