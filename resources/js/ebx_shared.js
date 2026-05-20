"use strict";
(() => {
  // src/ebx_shared.ts
  var config = {
    dataRoot: "/data/",
    apiBase: "",
    // empty means same origin — works when FastAPI hosts the static files
    version: "0.4.0",
    cycleStart: /* @__PURE__ */ new Date("2026-01-01T00:00:00"),
    causeLengthDays: 49,
    // 7 weeks per cause
    decisionIntervalDays: 7,
    // one decision per week
    useApi: true,
    causes: [],
    initiatives: [],
    organizations: [],
    feed: []
  };
  async function fetchJSON(path) {
    const url = config.dataRoot + path;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
      return await res.json();
    } catch (err) {
      console.error("[EBX] fetchJSON failed:", err);
      return null;
    }
  }
  async function fetchAPI(path) {
    const url = config.apiBase + path;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
      return await res.json();
    } catch (err) {
      console.error("[EBX] fetchAPI failed:", err);
      return null;
    }
  }
  async function loadCauses() {
    const data = config.useApi ? await fetchAPI("/causes") : await fetchJSON("causes/causes.json");
    if (data) config.causes = data;
    return config.causes;
  }
  async function loadInitiatives() {
    const data = config.useApi ? await fetchAPI("/initiatives") : await fetchJSON("causes/initiatives.json");
    if (data) {
      config.initiatives = data.map((i) => {
        const causeIndex = i.cause_index ?? (config.causes.find((c) => c.id === i.cause_id)?.index ?? 0);
        return {
          ...i,
          cause_index: causeIndex,
          committed_ebx: i.committed_ebx ?? i.ebx_committed ?? 0
        };
      });
    }
    return config.initiatives;
  }
  async function loadOrganizations() {
    const data = config.useApi ? await fetchAPI("/organizations") : await fetchJSON("causes/orgs.json");
    if (data) {
      config.organizations = data.map((o) => ({
        id: o.id,
        name: o.name,
        causes: o.causes ?? [],
        verified: o.verified ?? false,
        description: o.description,
        founded: o.founded ?? o.founded_year
      }));
    }
    return config.organizations;
  }
  async function loadFeed() {
    const data = config.useApi ? await fetchAPI("/posts?limit=50") : await fetchJSON("causes/feed.json");
    if (data) config.feed = data;
    return config.feed;
  }
  async function loadAll() {
    await loadCauses();
    await Promise.all([loadInitiatives(), loadOrganizations(), loadFeed()]);
  }
  var MS_PER_DAY = 864e5;
  var Cycle = {
    MS_PER_DAY,
    /** Current state — which cause has its decision THIS week, etc. */
    now() {
      const elapsedMs = Date.now() - config.cycleStart.getTime();
      const dayMs = MS_PER_DAY;
      const weekMs = config.decisionIntervalDays * dayMs;
      const totalDays = Math.floor(elapsedMs / dayMs);
      const weekNum = Math.floor(elapsedMs / weekMs);
      const causeIndex = (weekNum % 7 + 7) % 7;
      const dayInWeek = totalDays - weekNum * config.decisionIntervalDays;
      const decisionMs = (weekNum + 1) * weekMs - elapsedMs;
      const daysRemaining = Math.max(0, Math.floor(decisionMs / dayMs));
      const hoursRemaining = Math.max(
        0,
        Math.floor(decisionMs % dayMs / 36e5)
      );
      const anglePerSeg = 360 / 7;
      const subProgress = elapsedMs % weekMs / weekMs;
      const rotationDeg = -(causeIndex * anglePerSeg) - subProgress * anglePerSeg;
      return {
        causeIndex,
        daysRemaining,
        hoursRemaining,
        rotationDeg,
        weekNum,
        dayInWeek
      };
    },
    /** Decision date for any cause: the next end-of-week when (weekNum % 7) === causeIndex. */
    nextDecisionDate(causeIndex) {
      const state = Cycle.now();
      const offset = (causeIndex - state.causeIndex + 7) % 7;
      const targetWeek = state.weekNum + offset;
      return new Date(
        config.cycleStart.getTime() + (targetWeek + 1) * config.decisionIntervalDays * MS_PER_DAY
      );
    },
    /** Date when this cause's CURRENT 7-week debate window opened. */
    windowStart(causeIndex) {
      const decision = Cycle.nextDecisionDate(causeIndex);
      return new Date(decision.getTime() - config.causeLengthDays * MS_PER_DAY);
    },
    /** Back-compat alias (older inline scripts called voteCloseDate). */
    voteCloseDate(causeIndex) {
      return Cycle.nextDecisionDate(causeIndex);
    },
    /** 0-based count of completed full rotations since cycleStart. */
    currentCycleNum() {
      const elapsedMs = Date.now() - config.cycleStart.getTime();
      return Math.floor(
        elapsedMs / (7 * config.decisionIntervalDays * MS_PER_DAY)
      );
    },
    initiativeForCause(causeIndex) {
      return config.initiatives.find((i) => i.cause_index === causeIndex) ?? null;
    }
  };
  var RANK_COLORS = [
    "#a78bfa",
    // 1 violet
    "#818cf8",
    // 2 indigo
    "#60a5fa",
    // 3 blue
    "#34d399",
    // 4 green
    "#fbbf24",
    // 5 yellow
    "#fb923c",
    // 6 orange
    "#f87171"
    // 7 red
  ];
  var OTHER_COLOR = "#6b7280";
  function rankColor(rank) {
    if (rank < 0) return OTHER_COLOR;
    return RANK_COLORS[Math.min(rank, RANK_COLORS.length - 1)];
  }
  function pseudoRandom(seed) {
    const x = Math.sin(seed * 12.9898) * 43758.5453;
    return x - Math.floor(x);
  }
  var Votes = {
    RANK_COLORS,
    OTHER_COLOR,
    rankColor,
    /**
     * Synthesize a stable vote distribution for (causeIndex, cycleNum, orgs).
     * Bucket anything < 5% into a single gray "Other" slice.
     */
    forCause(causeIndex, cycleNum, orgs) {
      if (!orgs.length) return [];
      const weights = orgs.map((o, i) => {
        const seed = causeIndex * 1009 + cycleNum * 31 + i * 17 + hashString(o.id);
        return Math.pow(pseudoRandom(seed) + 0.05, 2.4);
      });
      const total = weights.reduce((a, b) => a + b, 0) || 1;
      const shares = orgs.map((o, i) => ({
        org_id: o.id,
        org_name: o.name,
        pct: weights[i] / total * 100
      })).sort((a, b) => b.pct - a.pct);
      const main = shares.filter((s) => s.pct >= 5);
      const tail = shares.filter((s) => s.pct < 5);
      const result = main.map((s, idx) => ({
        ...s,
        rank: idx,
        isOther: false,
        color: idx === 0 ? config.causes[causeIndex]?.color ?? "#888" : fadeToWhite(
          config.causes[causeIndex]?.color ?? "#888",
          Math.min(0.92, idx / Math.max(2, main.length - 1))
        )
      }));
      if (tail.length) {
        result.push({
          org_id: "other",
          org_name: `Other (${tail.length})`,
          pct: tail.reduce((a, b) => a + b.pct, 0),
          rank: -1,
          isOther: true,
          color: OTHER_COLOR
        });
      }
      return result;
    },
    /** Pick the orgs that will appear in a given cause's race. */
    orgsForCause(causeIndex) {
      const all = config.organizations;
      if (!all.length) return [];
      const tagged = all.filter((o) => (o.causes || []).includes(causeIndex));
      return tagged.length ? tagged : all;
    }
  };
  function hashString(s) {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = h * 16777619 >>> 0;
    }
    return h % 1e5;
  }
  var Annulus = {
    _rafId: null,
    _rotatingGroup: null,
    _nowGroup: null,
    _segments: [],
    _svg: null,
    /** Cached refs for legacy inline-script hooks — set once in mount(). */
    _nameEl: null,
    _timerEl: null,
    _cx: 200,
    _cy: 200,
    _outerR: 184,
    _midR: 144,
    // boundary between outer ring and inner ring
    _innerR: 104,
    // inner edge of the inner ring
    mount(container) {
      const el = typeof container === "string" ? document.querySelector(container) : container;
      if (!el) return;
      if (!config.causes.length) {
        console.warn("[EBX.Annulus] No causes loaded \u2014 call EBX.loadCauses() first.");
        return;
      }
      const { _cx: cx, _cy: cy, _outerR: outerR, _midR: midR, _innerR: innerR } = Annulus;
      const n = 7;
      const anglePerSeg = 2 * Math.PI / n;
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 0 400 400");
      svg.style.cssText = "width:100%;height:100%;display:block;overflow:visible;";
      Annulus._svg = svg;
      const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
      group.setAttribute("id", "ebx-rotating-group");
      group.style.transformOrigin = `${cx}px ${cy}px`;
      svg.appendChild(group);
      Annulus._rotatingGroup = group;
      const core = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      core.setAttribute("cx", String(cx));
      core.setAttribute("cy", String(cy));
      core.setAttribute("r", String(innerR - 2));
      core.setAttribute("fill", "#0f1a14");
      core.setAttribute("opacity", "0.95");
      group.appendChild(core);
      Annulus._segments = [];
      for (let i = 0; i < n; i++) {
        const cause = config.causes[i];
        const startAngle = i * anglePerSeg - Math.PI / 2;
        const endAngle = startAngle + anglePerSeg;
        const innerPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
        innerPath.setAttribute("d", annularSectorPath(cx, cy, midR, innerR, startAngle, endAngle));
        innerPath.setAttribute("fill", cause.color);
        innerPath.setAttribute("fill-opacity", "0.92");
        innerPath.setAttribute("stroke", "#0f1a14");
        innerPath.setAttribute("stroke-width", "1.5");
        innerPath.style.cursor = "pointer";
        innerPath.style.transition = "filter 0.2s";
        innerPath.addEventListener("mouseenter", () => {
          innerPath.style.filter = "brightness(1.25)";
        });
        innerPath.addEventListener("mouseleave", () => {
          innerPath.style.filter = "none";
        });
        innerPath.addEventListener("click", () => {
          window.location.href = `cause.html?id=${cause.id}`;
        });
        group.appendChild(innerPath);
        const outerGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        outerGroup.setAttribute("data-segment", String(i));
        group.appendChild(outerGroup);
        const midAngle = startAngle + anglePerSeg / 2;
        const labelR = (midR + innerR) / 2;
        const lx = cx + labelR * Math.cos(midAngle);
        const ly = cy + labelR * Math.sin(midAngle);
        const labelGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        labelGroup.setAttribute("pointer-events", "none");
        const nameLine = document.createElementNS("http://www.w3.org/2000/svg", "text");
        nameLine.setAttribute("x", String(lx));
        nameLine.setAttribute("y", String(ly));
        nameLine.setAttribute("text-anchor", "middle");
        nameLine.setAttribute("dominant-baseline", "middle");
        nameLine.setAttribute("font-size", "11");
        nameLine.setAttribute("font-weight", "700");
        nameLine.setAttribute("fill", "#0f1a14");
        nameLine.textContent = cause.name;
        labelGroup.appendChild(nameLine);
        const dateLine = document.createElementNS("http://www.w3.org/2000/svg", "text");
        dateLine.setAttribute("x", String(lx));
        dateLine.setAttribute("y", String(ly + 7));
        dateLine.setAttribute("text-anchor", "middle");
        dateLine.setAttribute("dominant-baseline", "middle");
        dateLine.setAttribute("font-size", "8");
        dateLine.setAttribute("fill", "#0f1a14");
        dateLine.setAttribute("opacity", "0.7");
        dateLine.setAttribute("data-date-label", String(i));
        dateLine.textContent = "\u2026";
        labelGroup.appendChild(dateLine);
        group.appendChild(labelGroup);
        Annulus._segments.push({
          innerPath,
          outerGroup,
          labelGroup,
          midX: lx,
          midY: ly
        });
      }
      const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
      defs.innerHTML = `
      <filter id="ebx-now-glow" x="-400%" y="-400%" width="900%" height="900%"
              color-interpolation-filters="sRGB">
        <feGaussianBlur in="SourceGraphic" stdDeviation="3.5" result="blur1"/>
        <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur2"/>
        <feMerge>
          <feMergeNode in="blur1"/>
          <feMergeNode in="blur2"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    `;
      svg.appendChild(defs);
      const nowGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
      nowGroup.setAttribute("pointer-events", "none");
      const nowLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
      nowLine.setAttribute("x1", String(cx));
      nowLine.setAttribute("y1", String(cy - outerR - 6));
      nowLine.setAttribute("x2", String(cx));
      nowLine.setAttribute("y2", String(cy - innerR + 6));
      nowLine.setAttribute("stroke", "rgba(255,255,255,0.88)");
      nowLine.setAttribute("stroke-width", "1.5");
      nowLine.setAttribute("stroke-linecap", "round");
      nowLine.setAttribute("filter", "url(#ebx-now-glow)");
      nowGroup.appendChild(nowLine);
      const nowDot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      nowDot.setAttribute("cx", String(cx));
      nowDot.setAttribute("cy", String(cy - outerR - 3));
      nowDot.setAttribute("r", "3");
      nowDot.setAttribute("fill", "white");
      nowDot.setAttribute("filter", "url(#ebx-now-glow)");
      nowGroup.appendChild(nowDot);
      svg.appendChild(nowGroup);
      Annulus._nowGroup = nowGroup;
      el.appendChild(svg);
      Annulus._nameEl = document.getElementById("ebx-cause-name");
      Annulus._timerEl = document.getElementById("ebx-cause-timer");
      Annulus._tick();
    },
    _tick() {
      Annulus._update();
      Annulus._rafId = requestAnimationFrame(Annulus._tick);
    },
    _update() {
      const state = Cycle.now();
      const group = Annulus._rotatingGroup;
      if (!group) return;
      group.style.transform = `rotate(${state.rotationDeg}deg)`;
      const cycleNum = Cycle.currentCycleNum();
      const { _cx: cx, _cy: cy, _outerR: outerR, _midR: midR } = Annulus;
      const n = 7;
      const anglePerSeg = 2 * Math.PI / n;
      Annulus._segments.forEach((seg, i) => {
        seg.labelGroup.setAttribute(
          "transform",
          `rotate(${-state.rotationDeg}, ${seg.midX}, ${seg.midY})`
        );
        if (i === state.causeIndex) {
          seg.innerPath.setAttribute("stroke", "#ffffff");
          seg.innerPath.setAttribute("stroke-width", "3");
          seg.innerPath.setAttribute("filter", "drop-shadow(0 0 8px rgba(255,255,200,0.55))");
        } else {
          seg.innerPath.setAttribute("stroke", "#0f1a14");
          seg.innerPath.setAttribute("stroke-width", "1.5");
          seg.innerPath.removeAttribute("filter");
        }
      });
      if (Annulus._nameEl) {
        const cause = config.causes[state.causeIndex];
        if (cause) Annulus._nameEl.textContent = cause.name;
      }
      if (Annulus._timerEl) {
        Annulus._timerEl.textContent = `${state.daysRemaining}d ${state.hoursRemaining}h`;
      }
    },
    stop() {
      if (Annulus._rafId !== null) cancelAnimationFrame(Annulus._rafId);
    }
  };
  function annularSectorPath(cx, cy, rOuter, rInner, a0, a1) {
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
      "Z"
    ].join(" ");
  }
  function initFooter() {
    const mount = document.getElementById("ebx-footer-mount");
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
              <li><a href="en.html">EN</a></li>
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
          <span>\xA9 ${(/* @__PURE__ */ new Date()).getFullYear()} Earthbux. Open source, open impact.</span>
          <span class="mono">v${config.version}</span>
        </div>
      </div>
    </footer>
  `;
  }
  async function initPage() {
    initFooter();
    if (!document.querySelector(".ebx-home-mark")) {
      const a = document.createElement("a");
      a.href = "index.html";
      a.className = "ebx-home-mark";
      a.textContent = "EBX";
      document.body.insertBefore(a, document.body.firstChild);
    }
    let mount = document.getElementById("ebx-user-badge-mount");
    if (!mount) {
      mount = document.createElement("div");
      mount.id = "ebx-user-badge-mount";
      mount.style.cssText = "position:fixed;top:10px;right:20px;z-index:200;";
      document.body.appendChild(mount);
    }
    const me = await Auth.fetchMe();
    mount.innerHTML = userBadge({ handle: me?.handle });
  }
  function getParam(key) {
    return new URLSearchParams(window.location.search).get(key);
  }
  function buildURL(base, params = {}) {
    const url = new URL(base, window.location.origin);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    return url.toString();
  }
  function $(sel, ctx = document) {
    return ctx.querySelector(sel);
  }
  function $$(sel, ctx = document) {
    return Array.from(ctx.querySelectorAll(sel));
  }
  function render(target, html) {
    const el = typeof target === "string" ? document.querySelector(target) : target;
    if (el) el.innerHTML = html;
  }
  function renderSkeleton(target, rows = 3) {
    render(
      target,
      Array.from(
        { length: rows },
        () => `<div class="skeleton" style="height:80px;margin-bottom:12px;border-radius:8px;"></div>`
      ).join("")
    );
  }
  function renderEmpty(target, message = "Nothing here yet.") {
    render(target, `
    <div style="text-align:center;padding:48px 24px;color:var(--clr-ink-light);">
      <div style="font-size:2rem;margin-bottom:12px;">\u{1F331}</div>
      <p style="font-size:0.9rem;">${message}</p>
    </div>
  `);
  }
  var formatNumber = (n) => Number(n).toLocaleString();
  var formatEBX = (n) => `${formatNumber(n)} EBX`;
  var formatPercent = (v, d = 1) => `${Number(v).toFixed(d)}%`;
  var formatDate = (iso) => new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  var formatShortDate = (d) => new Date(d).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  function timeAgo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 6e4);
    const hours = Math.floor(diff / 36e5);
    const days = Math.floor(diff / 864e5);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 30) return `${days}d ago`;
    return formatDate(iso);
  }
  function tokenChip({ index, title, org, causeColor, amount }) {
    return `
    <div class="ebx-token" style="border-left: 4px solid ${causeColor};">
      <div class="ebx-token__index mono">#${String(index).padStart(3, "0")}</div>
      <div class="ebx-token__title">${title}</div>
      ${org ? `<div class="ebx-token__org text-xs text-muted">${org}</div>` : ""}
      ${amount != null ? `<div class="ebx-token__amount mono text-xs">${formatEBX(amount)}</div>` : ""}
    </div>
  `;
  }
  function creditBadge(holdings, size = 64) {
    const causes = config.causes;
    if (!causes.length) return "";
    const cx = size / 2, cy = size / 2;
    const outerR = size * 0.46, innerR = size * 0.25;
    const n = 7;
    const anglePerSeg = 2 * Math.PI / n;
    const segments = causes.map((cause, i) => {
      const holding = holdings.find((h) => h.causeIndex === i);
      const opacity = holding ? 0.9 : 0.15;
      const startAngle = i * anglePerSeg - Math.PI / 2;
      const endAngle = startAngle + anglePerSeg;
      return `<path d="${annularSectorPath(cx, cy, outerR, innerR, startAngle, endAngle)}"
      fill="${cause.color}" fill-opacity="${opacity}" stroke="#0f1a14" stroke-width="0.8"/>`;
    }).join("");
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
  function tag(label, variant = "neutral") {
    return `<span class="tag tag-${variant}">${label}</span>`;
  }
  function progressBar(percent, variant = "") {
    const cls = variant ? `progress-bar__fill--${variant}` : "";
    return `
    <div class="progress-bar">
      <div class="progress-bar__fill ${cls}" style="width:${Math.min(100, percent)}%"></div>
    </div>
  `;
  }
  function statBlock(value, label, variant = "") {
    return `
    <div class="stat-block">
      <div class="stat-block__value ${variant ? "stat-block__value--" + variant : ""}">${value}</div>
      <div class="stat-block__label">${label}</div>
    </div>
  `;
  }
  function initiativeCard(init) {
    const cause = config.causes.find((c) => c.index === init.cause_index);
    const causeColor = cause ? cause.color : "#888";
    const phaseLabelMap = {
      org_vote: { label: "Org Vote Open", variant: "amber" },
      initiative_debate: { label: "Initiative Debate", variant: "forest" },
      planning: { label: "Financial Planning", variant: "sage" },
      execution: { label: "In Execution", variant: "sage" },
      resolved: { label: "Resolved", variant: "neutral" }
    };
    const phase = phaseLabelMap[init.phase ?? ""] || { label: init.phase ?? init.status, variant: "neutral" };
    const pct = (init.pool_total ?? 0) > 0 ? Math.round(init.committed_ebx / (init.pool_total ?? 1) * 100) : 0;
    return `
    <a href="initiative.html?id=${init.id}" class="card ebx-init-card"
       style="text-decoration:none;display:block;border-left:4px solid ${causeColor};">
      <div class="flex-between mb-sm">
        ${tag(phase.label, phase.variant)}
        <span class="mono text-xs text-muted">#${String(init.index ?? 0).padStart(3, "0")}</span>
      </div>
      <h4 style="margin-bottom:var(--sp-xs);">${init.emoji ?? ""} ${init.title}</h4>
      <p class="text-xs text-muted mb-md">${cause ? cause.name : ""} \xB7 ${init.winning_org || "Org TBD"}</p>
      <p class="text-sm text-muted mb-md">${init.description ?? ""}</p>
      ${progressBar(pct, "amber")}
      <div class="flex-between mt-sm">
        <span class="text-xs text-muted">${formatEBX(init.committed_ebx)} committed</span>
        <span class="text-xs fw-medium" style="color:${causeColor};">${pct}% of pool \u2192</span>
      </div>
    </a>
  `;
  }
  function feedCard(post) {
    const cause = config.causes.find((c) => c.index === post.cause_index);
    const causeColor = cause ? cause.color : "#888";
    const typeLabel = {
      editorial: "Editorial",
      opinion: "Opinion",
      org_update: "Org Update",
      headline: "Headline"
    };
    const label = typeLabel[post.type] ?? post.type;
    return `
    <a href="en.html?id=${post.id}" class="ebx-feed-card"
       style="text-decoration:none;color:inherit;display:flex;flex-direction:column;
              gap:8px;padding:16px;border-radius:10px;
              background:rgba(15,26,20,0.5);border:1px solid rgba(255,255,255,0.07);
              border-left:3px solid ${causeColor};transition:background 0.2s;">
      <div style="display:flex;justify-content:space-between;align-items:baseline;
                  font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.12em;
                  text-transform:uppercase;opacity:0.65;">
        <span style="color:${causeColor};">${label}${cause ? " \xB7 " + cause.name : ""}</span>
        <span style="color:rgba(245,240,232,0.4);">${timeAgo(post.created_at)}</span>
      </div>
      ${post.title ? `<h4 style="font-size:0.95rem;line-height:1.3;color:rgba(245,240,232,0.92);margin:0;">${post.title}</h4>` : ""}
      <p style="font-size:0.78rem;line-height:1.45;color:rgba(245,240,232,0.6);margin:0;
                display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">
        ${post.body}
      </p>
      <div style="display:flex;justify-content:space-between;align-items:center;
                  font-family:var(--font-mono);font-size:0.6rem;color:rgba(245,240,232,0.4);">
        <span>\u2014 ${post.author}</span>
        <span>\u2665 ${post.likes}</span>
      </div>
    </a>
  `;
  }
  function raceCard(causeIndex) {
    const cause = config.causes.find((c) => c.index === causeIndex);
    if (!cause) return "";
    const init = config.initiatives.filter((i) => i.cause_index === causeIndex).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(causeIndex);
    const shares = Votes.forCause(causeIndex, cycleNum, orgs);
    const leader = shares[0];
    const decision = Cycle.nextDecisionDate(causeIndex);
    const voteStart = new Date(decision.getTime() - 6 * MS_PER_DAY);
    const sameMonth = voteStart.getMonth() === decision.getMonth();
    const dateRange = sameMonth ? `${voteStart.toLocaleDateString("en-US", { month: "short" })} ${voteStart.getDate()}\u2013${decision.getDate()}` : `${formatShortDate(voteStart)} \u2013 ${formatShortDate(decision)}`;
    const processRow = (label) => `
    <div style="padding:9px 12px;">
      <div style="font-family:var(--font-mono);font-size:0.5rem;letter-spacing:0.14em;
                  text-transform:uppercase;color:rgba(245,240,232,0.42);margin-bottom:3px;">
        ${label}
      </div>
      <div style="font-size:0.74rem;color:rgba(245,240,232,0.9);font-weight:600;
                  line-height:1.25;
                  display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden;">
        ${init ? init.title : "No initiative yet"}
      </div>
      <div style="font-family:var(--font-mono);font-size:0.6rem;
                  color:rgba(245,240,232,0.6);margin-top:2px;
                  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
        ${leader ? `${leader.org_name} \xB7 ${leader.pct.toFixed(0)}%` : "\u2014"}
      </div>
    </div>
  `;
    return `
    <a class="race-card" href="cause.html?id=${cause.id}"
       style="--rc-color:${cause.color};
              display:block;text-decoration:none;width:248px;
              background:rgba(15,26,20,0.72);
              border:1px solid var(--rc-color);border-radius:10px;
              overflow:hidden;
              transition:background 0.2s;">
      <!-- Header: cause name + Next Vote date range -->
      <div style="padding:8px 12px;background:rgba(0,0,0,0.18);
                  border-bottom:1px solid var(--rc-color);
                  display:flex;justify-content:space-between;align-items:baseline;">
        <span style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;
                     text-transform:uppercase;color:var(--rc-color);font-weight:700;">
          ${cause.name}
        </span>
        <span style="font-family:var(--font-mono);font-size:0.54rem;
                     color:rgba(245,240,232,0.55);white-space:nowrap;">
          Next Vote ${dateRange}
        </span>
      </div>
      <!-- Two equal process sections -->
      <div style="display:grid;grid-template-rows:1fr 1px 1fr;">
        ${processRow("Initiative")}
        <div style="background:rgba(255,255,255,0.06);"></div>
        ${processRow("Org election")}
      </div>
    </a>
  `;
  }
  function filterBySearch(items, query, fields) {
    if (!query) return items;
    const q = query.toLowerCase();
    return items.filter(
      (item) => fields.some((f) => String(item[f] ?? "").toLowerCase().includes(q))
    );
  }
  function filterByField(items, field, value) {
    if (!value || value === "all") return items;
    return items.filter((item) => String(item[field]) === value);
  }
  function sortBy(items, field, dir = "desc") {
    return [...items].sort((a, b) => {
      const av = a[field], bv = b[field];
      if (typeof av === "number" && typeof bv === "number") {
        return dir === "desc" ? bv - av : av - bv;
      }
      return dir === "desc" ? String(bv).localeCompare(String(av)) : String(av).localeCompare(String(bv));
    });
  }
  var Auth = {
    tokenKey: "ebx_auth_token",
    lastSignupError: null,
    getToken() {
      return localStorage.getItem(Auth.tokenKey);
    },
    setToken(t) {
      localStorage.setItem(Auth.tokenKey, t);
    },
    clear() {
      localStorage.removeItem(Auth.tokenKey);
    },
    isLoggedIn() {
      return !!Auth.getToken();
    },
    async login(username, password) {
      try {
        const body = new URLSearchParams({ username, password });
        const res = await fetch(`${config.apiBase}/auth/login`, {
          method: "POST",
          body,
          headers: { "Content-Type": "application/x-www-form-urlencoded" }
        });
        if (!res.ok) return false;
        const data = await res.json();
        Auth.setToken(data.access_token);
        return true;
      } catch {
        return false;
      }
    },
    async signup(email, handle, password) {
      try {
        const res = await fetch(`${config.apiBase}/auth/signup`, {
          method: "POST",
          body: JSON.stringify({ email, handle, password }),
          headers: { "Content-Type": "application/json" }
        });
        if (res.ok) {
          Auth.lastSignupError = null;
          return true;
        }
        try {
          const body = await res.json();
          Auth.lastSignupError = body.detail ?? `Server error (HTTP ${res.status})`;
        } catch {
          Auth.lastSignupError = `Server error (HTTP ${res.status})`;
        }
        return false;
      } catch {
        Auth.lastSignupError = "Cannot reach the server. Is the API running?";
        return false;
      }
    },
    async fetchAuthed(path, init = {}) {
      const headers = new Headers(init.headers || {});
      const token = Auth.getToken();
      if (token) headers.set("Authorization", `Bearer ${token}`);
      if (typeof init.body === "string" && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
      }
      return fetch(config.apiBase + path, { ...init, headers });
    },
    async fetchMe() {
      const res = await Auth.fetchAuthed("/auth/me");
      if (res.status === 401) {
        Auth.clear();
        return null;
      }
      if (!res.ok) return null;
      return res.json();
    },
    /* ── Login/Signup modal ──────────────────────────────────────────
       Renders a floating modal over the current page.
       Usage: EBX.Auth.openModal()  or  EBX.Auth.openModal('signup')
    ─────────────────────────────────────────────────────────────── */
    openModal(initialTab = "login") {
      document.getElementById("ebx-auth-modal")?.remove();
      const MODAL_CSS = `
      #ebx-auth-modal {
        position:fixed;inset:0;z-index:9000;
        display:flex;align-items:center;justify-content:center;
        background:rgba(5,12,8,0.82);backdrop-filter:blur(6px);
        padding:24px;
      }
      #ebx-auth-modal .am-card {
        width:100%;max-width:400px;
        background:rgba(22,34,24,0.98);
        border:1px solid rgba(255,255,255,0.1);
        border-radius:14px;overflow:hidden;
        box-shadow:0 24px 64px rgba(0,0,0,0.6);
      }
      #ebx-auth-modal .am-tabs {
        display:grid;grid-template-columns:1fr 1fr;
        border-bottom:1px solid rgba(255,255,255,0.07);
      }
      #ebx-auth-modal .am-tab {
        padding:14px;text-align:center;cursor:pointer;
        font-family:var(--font-mono,monospace);font-size:.72rem;
        font-weight:600;letter-spacing:.08em;text-transform:uppercase;
        color:rgba(245,240,232,0.4);
        border:none;background:none;
        transition:color .15s,background .15s;
      }
      #ebx-auth-modal .am-tab.active {
        color:var(--clr-honey,#e8a84c);
        background:rgba(232,168,76,0.06);
        border-bottom:2px solid var(--clr-honey,#e8a84c);
      }
      #ebx-auth-modal .am-body { padding:24px; }
      #ebx-auth-modal .am-field { margin-bottom:16px; }
      #ebx-auth-modal .am-label {
        display:block;font-size:.76rem;font-weight:600;
        color:rgba(245,240,232,0.6);margin-bottom:6px;
      }
      #ebx-auth-modal .am-input {
        width:100%;box-sizing:border-box;
        padding:10px 13px;
        background:rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.1);
        border-radius:8px;
        color:var(--clr-parchment,#f5f0e8);
        font-size:.9rem;outline:none;
        transition:border-color .15s;
      }
      #ebx-auth-modal .am-input:focus { border-color:rgba(232,168,76,0.55); }
      #ebx-auth-modal .am-btn {
        width:100%;padding:11px;margin-top:8px;
        background:var(--clr-amber,#c97c2a);
        border:none;border-radius:8px;cursor:pointer;
        font-family:var(--font-mono,monospace);
        font-size:.78rem;font-weight:700;letter-spacing:.06em;
        color:#0f1a14;transition:opacity .15s;
      }
      #ebx-auth-modal .am-btn:hover { opacity:.88; }
      #ebx-auth-modal .am-btn:disabled { opacity:.45;cursor:default; }
      #ebx-auth-modal .am-msg {
        font-size:.76rem;margin-top:10px;text-align:center;min-height:18px;
      }
      #ebx-auth-modal .am-msg.err { color:#f87171; }
      #ebx-auth-modal .am-msg.ok  { color:#34d399; }
      #ebx-auth-modal .am-close {
        position:absolute;top:14px;right:18px;
        background:none;border:none;cursor:pointer;
        font-size:1.3rem;color:rgba(245,240,232,0.35);
        line-height:1;
      }
      #ebx-auth-modal .am-close:hover { color:rgba(245,240,232,0.75); }
    `;
      const styleEl = document.createElement("style");
      styleEl.textContent = MODAL_CSS;
      const wrap = document.createElement("div");
      wrap.id = "ebx-auth-modal";
      wrap.setAttribute("role", "dialog");
      wrap.setAttribute("aria-modal", "true");
      wrap.innerHTML = `
      <div class="am-card" style="position:relative;">
        <button class="am-close" id="am-close-btn" aria-label="Close">\xD7</button>
        <div class="am-tabs">
          <button class="am-tab ${initialTab === "login" ? "active" : ""}" data-tab="login">Log In</button>
          <button class="am-tab ${initialTab === "signup" ? "active" : ""}" data-tab="signup">Sign Up</button>
        </div>

        <!-- LOGIN PANEL -->
        <div class="am-body" id="am-login-panel" style="display:${initialTab === "login" ? "block" : "none"}">
          <div class="am-field">
            <label class="am-label">Email or handle</label>
            <input class="am-input" id="am-login-user" type="text" autocomplete="username" placeholder="you@example.com or @handle" />
          </div>
          <div class="am-field">
            <label class="am-label">Password</label>
            <input class="am-input" id="am-login-pass" type="password" autocomplete="current-password" placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022" />
          </div>
          <button class="am-btn" id="am-login-btn">Log In \u2192</button>
          <div class="am-msg" id="am-login-msg"></div>
        </div>

        <!-- SIGNUP PANEL -->
        <div class="am-body" id="am-signup-panel" style="display:${initialTab === "signup" ? "block" : "none"}">
          <div class="am-field">
            <label class="am-label">Email</label>
            <input class="am-input" id="am-su-email" type="email" autocomplete="email" placeholder="you@example.com" />
          </div>
          <div class="am-field">
            <label class="am-label">Handle <span style="font-weight:400;opacity:.55;">(public \xB7 no spaces)</span></label>
            <input class="am-input" id="am-su-handle" type="text" autocomplete="username" placeholder="terra_watcher" />
          </div>
          <div class="am-field">
            <label class="am-label">Password <span style="font-weight:400;opacity:.55;">(8+ chars)</span></label>
            <input class="am-input" id="am-su-pass" type="password" autocomplete="new-password" placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022" />
          </div>
          <button class="am-btn" id="am-su-btn">Create Account \u2192</button>
          <div class="am-msg" id="am-su-msg"></div>
        </div>
      </div>
    `;
      document.head.appendChild(styleEl);
      document.body.appendChild(wrap);
      wrap.addEventListener("click", (e) => {
        if (e.target === wrap) Auth._closeModal();
      });
      document.getElementById("am-close-btn").addEventListener("click", () => Auth._closeModal());
      wrap.querySelectorAll(".am-tab").forEach((btn) => {
        btn.addEventListener("click", () => {
          wrap.querySelectorAll(".am-tab").forEach((t) => t.classList.remove("active"));
          btn.classList.add("active");
          const tab = btn.dataset.tab;
          document.getElementById("am-login-panel").style.display = tab === "login" ? "block" : "none";
          document.getElementById("am-signup-panel").style.display = tab === "signup" ? "block" : "none";
        });
      });
      const loginBtn = document.getElementById("am-login-btn");
      const loginMsg = document.getElementById("am-login-msg");
      loginBtn.addEventListener("click", async () => {
        const user = document.getElementById("am-login-user").value.trim();
        const pass = document.getElementById("am-login-pass").value;
        if (!user || !pass) {
          loginMsg.className = "am-msg err";
          loginMsg.textContent = "Please fill in all fields.";
          return;
        }
        loginBtn.disabled = true;
        loginMsg.className = "am-msg";
        loginMsg.textContent = "Logging in\u2026";
        const ok = await Auth.login(user, pass);
        if (ok) {
          loginMsg.className = "am-msg ok";
          loginMsg.textContent = "\u2713 Logged in!";
          setTimeout(() => {
            Auth._closeModal();
            Auth._onLoginSuccess();
          }, 700);
        } else {
          loginMsg.className = "am-msg err";
          loginMsg.textContent = "Invalid credentials. Try again.";
          loginBtn.disabled = false;
        }
      });
      ["am-login-user", "am-login-pass"].forEach((id) => {
        document.getElementById(id).addEventListener("keydown", (e) => {
          if (e.key === "Enter") loginBtn.click();
        });
      });
      const suBtn = document.getElementById("am-su-btn");
      const suMsg = document.getElementById("am-su-msg");
      suBtn.addEventListener("click", async () => {
        const email = document.getElementById("am-su-email").value.trim();
        const handle = document.getElementById("am-su-handle").value.trim();
        const pass = document.getElementById("am-su-pass").value;
        if (!email || !handle || !pass) {
          suMsg.className = "am-msg err";
          suMsg.textContent = "Please fill in all fields.";
          return;
        }
        if (pass.length < 8) {
          suMsg.className = "am-msg err";
          suMsg.textContent = "Password must be at least 8 characters.";
          return;
        }
        if (!/^\S+$/.test(handle)) {
          suMsg.className = "am-msg err";
          suMsg.textContent = "Handle cannot contain spaces.";
          return;
        }
        suBtn.disabled = true;
        suMsg.className = "am-msg";
        suMsg.textContent = "Creating account\u2026";
        const created = await Auth.signup(email, handle, pass);
        if (!created) {
          suMsg.className = "am-msg err";
          suMsg.textContent = Auth.lastSignupError || "Signup failed.";
          suBtn.disabled = false;
          return;
        }
        suMsg.textContent = "Signing you in\u2026";
        const loggedIn = await Auth.login(handle, pass);
        if (loggedIn) {
          suMsg.className = "am-msg ok";
          suMsg.textContent = "\u2713 Account created!";
          setTimeout(() => {
            Auth._closeModal();
            Auth._onLoginSuccess();
          }, 700);
        } else {
          suMsg.className = "am-msg ok";
          suMsg.textContent = "\u2713 Account created \u2014 please log in.";
          setTimeout(() => {
            Auth._closeModal();
            Auth.openModal("login");
          }, 1e3);
        }
      });
      setTimeout(() => {
        const firstInput = wrap.querySelector(".am-input");
        if (firstInput) firstInput.focus();
      }, 50);
    },
    _closeModal() {
      document.getElementById("ebx-auth-modal")?.remove();
    },
    /* Called after a successful login — refreshes the user badge and
       optionally navigates to the profile page. */
    async _onLoginSuccess() {
      const me = await Auth.fetchMe();
      const mount = document.getElementById("ebx-user-badge-mount");
      if (mount && me) {
        mount.innerHTML = userBadge({ handle: me.handle });
      }
      if (window.location.pathname.endsWith("profile.html")) {
        window.location.reload();
      }
    }
  };
  function fadeToWhite(hex, t) {
    const m = hex.match(/^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
    if (!m) return hex;
    const r = parseInt(m[1], 16);
    const g = parseInt(m[2], 16);
    const b = parseInt(m[3], 16);
    const lerp = (a) => Math.round(a + (255 - a) * t);
    return `rgb(${lerp(r)}, ${lerp(g)}, ${lerp(b)})`;
  }
  function electionPanel(causeIndex) {
    const cause = config.causes.find((c) => c.index === causeIndex);
    if (!cause) return "";
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(causeIndex);
    const shares = Votes.forCause(causeIndex, cycleNum, orgs);
    const decision = Cycle.nextDecisionDate(causeIndex);
    const state = Cycle.now();
    const init = config.initiatives.filter((i) => i.cause_index === causeIndex).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];
    const leader = shares[0];
    const leaderColor = leader ? leader.color : cause.color;
    const rows = shares.slice(0, 6).map((s) => `
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
  `).join("");
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
        Decision ${formatShortDate(decision)} \xB7 ${state.daysRemaining}d ${state.hoursRemaining}h remaining
      </div>

      <div style="font-family:var(--font-mono);font-size:0.5rem;letter-spacing:0.16em;
                  text-transform:uppercase;color:rgba(245,240,232,0.4);margin-bottom:4px;">
        Leading initiative
      </div>
      <div style="font-size:0.82rem;font-weight:600;color:rgba(245,240,232,0.92);
                  line-height:1.3;margin-bottom:12px;">
        ${init ? `${init.emoji ?? ""} ${init.title}` : "No initiative committed yet"}
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
          Engage \u2192
        </a>
        <a href="en.html?cause=${cause.id}" style="
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
  function userBadge(opts = {}) {
    const loggedIn = Auth.isLoggedIn();
    if (!loggedIn) {
      return `
      <a href="profile.html" class="ebx-user-badge ebx-user-badge--guest"
         style="display:inline-flex;align-items:center;gap:8px;
                font-family:var(--font-mono);font-size:0.72rem;font-weight:600;
                letter-spacing:0.06em;text-transform:uppercase;
                color:var(--clr-honey);text-decoration:none;
                padding:8px 14px;border-radius:999px;
                background:rgba(15,26,20,0.6);
                border:1px solid rgba(232,168,76,0.45);
                transition:background 0.2s;">
        <span style="width:8px;height:8px;border-radius:50%;background:var(--clr-honey);
                     box-shadow:0 0 6px rgba(232,168,76,0.6);"></span>
        Log in or register
      </a>
    `;
    }
    const initials = (opts.handle ?? "EB").slice(0, 2).toUpperCase();
    const size = 44;
    const cx = size / 2, cy = size / 2;
    const outerR = size * 0.46, innerR = size * 0.27;
    const n = 7;
    const anglePerSeg = 2 * Math.PI / n;
    const segs = config.causes.slice(0, n).map((cause, i) => {
      const a0 = i * anglePerSeg - Math.PI / 2;
      const a1 = a0 + anglePerSeg;
      return `<path d="${annularSectorPath(cx, cy, outerR, innerR, a0, a1)}"
      fill="${cause.color}" fill-opacity="0.22" stroke="#0f1a14" stroke-width="0.6"/>`;
    }).join("");
    const logoutScript = `if(confirm('Log out?')){EBX.Auth.clear();localStorage.removeItem('ebx_profile');location.reload();}`;
    return `
    <div style="display:inline-flex;align-items:center;gap:6px;">
      <a href="profile.html" class="ebx-user-badge"
         style="display:inline-flex;align-items:center;gap:10px;
                text-decoration:none;color:rgba(245,240,232,0.85);
                padding:4px 14px 4px 4px;border-radius:999px;
                background:rgba(15,26,20,0.6);
                border:1px solid rgba(255,255,255,0.12);">
        <svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg"
             style="display:block;">
          <circle cx="${cx}" cy="${cy}" r="${outerR + 0.5}" fill="#0f1a14" opacity="0.7"/>
          ${segs}
          <circle cx="${cx}" cy="${cy}" r="${innerR - 1}" fill="#0f1a14" opacity="0.95"/>
          <text x="${cx}" y="${cy + 3}" text-anchor="middle"
                font-size="9" font-weight="700" fill="rgba(245,240,232,0.9)"
                font-family="var(--font-mono)">${initials}</text>
        </svg>
        <span style="font-family:var(--font-mono);font-size:0.7rem;font-weight:600;">${opts.handle ?? ""}</span>
      </a>
      <button onclick="${logoutScript}"
              title="Log out"
              style="background:none;border:1px solid rgba(255,255,255,0.14);border-radius:999px;
                     color:rgba(245,240,232,0.5);cursor:pointer;font-size:0.65rem;
                     font-family:var(--font-mono);letter-spacing:0.04em;
                     padding:4px 9px;transition:color 0.15s,border-color 0.15s;line-height:1;"
              onmouseover="this.style.color='rgba(245,240,232,0.9)';this.style.borderColor='rgba(255,255,255,0.35)';"
              onmouseout="this.style.color='rgba(245,240,232,0.5)';this.style.borderColor='rgba(255,255,255,0.14)';">
        \u21A9 out
      </button>
    </div>
  `;
  }
  function electionBanner(causeIndex) {
    const cause = config.causes.find((c) => c.index === causeIndex);
    if (!cause) return "";
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(causeIndex);
    const shares = Votes.forCause(causeIndex, cycleNum, orgs).slice(0, 5);
    const decision = Cycle.nextDecisionDate(causeIndex);
    const state = Cycle.now();
    const init = config.initiatives.filter((i) => i.cause_index === causeIndex).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];
    const bars = shares.map((s) => `
    <div title="${s.org_name} - ${s.pct.toFixed(1)}%"
         style="height:6px;flex:${Math.max(2, s.pct).toFixed(2)};
                background:${s.color};opacity:0.95;border-radius:1px;"></div>
  `).join("");
    return `
    <a href="cause.html?id=${cause.id}" class="ebx-election-banner"
       style="--ebc:${cause.color};
              display:flex;align-items:center;gap:14px;
              padding:9px 16px;border-radius:999px;
              background:rgba(15,26,20,0.7);
              border:1.5px solid rgba(255,255,255,0.85);
              box-shadow:0 0 16px rgba(255,255,255,0.32),
                         0 0 4px rgba(255,255,255,0.55) inset;
              text-decoration:none;color:rgba(245,240,232,0.95);
              max-width:560px;">
      <span style="font-family:var(--font-mono);font-size:0.55rem;letter-spacing:0.14em;
                   text-transform:uppercase;color:var(--ebc);font-weight:700;
                   white-space:nowrap;">
        ${cause.name} election
      </span>
      <span style="font-size:0.78rem;color:rgba(245,240,232,0.85);font-weight:600;
                   overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
                   min-width:0;flex:1;">
        ${init ? init.title : "No initiative committed yet"}
      </span>
      <span style="display:flex;align-items:stretch;gap:1px;width:90px;height:8px;
                   border-radius:2px;overflow:hidden;background:rgba(255,255,255,0.05);">
        ${bars || ""}
      </span>
      <span style="font-family:var(--font-mono);font-size:0.62rem;
                   color:rgba(245,240,232,0.55);white-space:nowrap;">
        ${state.daysRemaining}d ${state.hoursRemaining}h
      </span>
    </a>
  `;
  }
  function sideCard(causeIndex) {
    const cause = config.causes.find((c) => c.index === causeIndex);
    if (!cause) return "";
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(causeIndex);
    const orgShares = Votes.forCause(causeIndex, cycleNum, orgs);
    const orgLeader = orgShares[0];
    const decision = Cycle.nextDecisionDate(causeIndex);
    const initiatives = config.initiatives.filter((i) => i.cause_index === causeIndex).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0));
    const initLeader = initiatives[0];
    const totalPool = initiatives.reduce((s, i) => s + (i.committed_ebx || 0), 0);
    const voteStart = new Date(decision.getTime() - 6 * MS_PER_DAY);
    const sameMonth = voteStart.getMonth() === decision.getMonth();
    const dateRange = sameMonth ? voteStart.toLocaleDateString("en-US", { month: "short" }) + " " + voteStart.getDate() + "-" + decision.getDate() : formatShortDate(voteStart) + " - " + formatShortDate(decision);
    const section = (label, title, sub, href, pool, empty) => {
      if (empty) {
        return '<div style="padding:10px 12px;"><div style="font-family:var(--font-mono);font-size:0.5rem;letter-spacing:0.14em;text-transform:uppercase;color:rgba(245,240,232,0.42);margin-bottom:4px;">' + label + '</div><div style="font-size:0.7rem;color:rgba(245,240,232,0.35);font-style:italic;">No votes yet</div></div>';
      }
      return '<div style="padding:10px 12px;"><div style="font-family:var(--font-mono);font-size:0.5rem;letter-spacing:0.14em;text-transform:uppercase;color:rgba(245,240,232,0.42);margin-bottom:3px;">' + label + '</div><div style="display:flex;justify-content:space-between;align-items:baseline;gap:6px;flex-wrap:wrap;"><div style="font-size:0.74rem;color:rgba(245,240,232,0.9);font-weight:600;line-height:1.25;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + title + '</div><a href="' + href + '" style="font-family:var(--font-mono);font-size:0.55rem;font-weight:700;white-space:nowrap;color:' + cause.color + ";text-decoration:none;padding:2px 7px;border-radius:4px;border:1px solid " + cause.color + ';opacity:0.85;">Contribute</a></div><div style="font-family:var(--font-mono);font-size:0.6rem;color:rgba(245,240,232,0.55);margin-top:2px;">' + sub + '</div><div style="font-family:var(--font-mono);font-size:0.55rem;color:rgba(245,240,232,0.38);margin-top:3px;">Total pool: ' + (pool > 0 ? "$" + formatNumber(pool) : "--") + "</div></div>";
    };
    const orgLabel = initLeader ? 'Organization for "' + (initLeader.title.length > 20 ? initLeader.title.slice(0, 20) + "..." : initLeader.title) + '"' : "Organization election";
    const initSub = initLeader ? (initLeader.committed_ebx || 0) > 0 ? formatEBX(initLeader.committed_ebx || 0) + " EBX" : "No commitments yet" : "";
    return '<div class="race-card" style="--rc-color:' + cause.color + ';display:block;text-decoration:none;width:100%;box-sizing:border-box;background:rgba(15,26,20,0.72);border:1px solid var(--rc-color);border-radius:10px;overflow:hidden;transition:background 0.2s;"><div style="padding:8px 12px;background:rgba(0,0,0,0.18);border-bottom:1px solid var(--rc-color);display:flex;justify-content:space-between;align-items:baseline;gap:8px;"><a href="cause.html?id=' + cause.id + '" style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--rc-color);font-weight:700;text-decoration:none;">' + cause.name + '</a><span style="font-family:var(--font-mono);font-size:0.54rem;color:rgba(245,240,232,0.55);white-space:nowrap;">Vote ' + dateRange + "</span></div>" + section(
      "Initiative",
      initLeader ? initLeader.title : "",
      initSub,
      "cause.html?id=" + cause.id,
      totalPool,
      !initLeader
    ) + '<div style="height:1px;background:rgba(255,255,255,0.06);margin:0 12px;"></div>' + section(
      orgLabel,
      orgLeader ? orgLeader.org_name : "",
      orgLeader ? orgLeader.pct.toFixed(0) + "% of votes" : "",
      orgLeader ? "mission.html?cause=" + cause.id : "cause.html?id=" + cause.id,
      totalPool,
      !orgLeader
    ) + "</div>";
  }
  function upcomingCauseBanner(activeIndex) {
    const n = 7;
    const nextIndex = (activeIndex + 1) % n;
    const cause = config.causes.find((c) => c.index === nextIndex);
    if (!cause) return "";
    const inits = config.initiatives.filter((i) => i.cause_index === nextIndex).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0));
    const topInit = inits[0] || null;
    const pool = inits.reduce((s, i) => s + (i.committed_ebx || 0), 0);
    const decision = Cycle.nextDecisionDate(nextIndex);
    const daysUntil = Math.ceil((decision.getTime() - Date.now()) / MS_PER_DAY);
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(nextIndex);
    const shares = Votes.forCause(nextIndex, cycleNum, orgs);
    const orgLeader = shares[0];
    const dot = `<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${cause.color};flex-shrink:0;box-shadow:0 0 5px ${cause.color};"></span>`;
    const label = `<span style="font-family:var(--font-mono);font-size:0.52rem;letter-spacing:0.14em;text-transform:uppercase;color:${cause.color};font-weight:700;white-space:nowrap;flex-shrink:0;">Up next: ${cause.name}</span>`;
    const title = `<span style="font-size:0.8rem;color:rgba(245,240,232,0.88);font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0;">${topInit ? (topInit.emoji ? topInit.emoji + " " : "") + topInit.title : "No initiative yet"}</span>`;
    const orgStr = orgLeader ? `<span style="font-family:var(--font-mono);font-size:0.56rem;color:rgba(245,240,232,0.42);white-space:nowrap;flex-shrink:0;">${orgLeader.org_name} ${orgLeader.pct.toFixed(0)}%</span>` : "";
    const poolStr = pool > 0 ? `<span style="font-family:var(--font-mono);font-size:0.56rem;color:rgba(245,240,232,0.38);white-space:nowrap;flex-shrink:0;">$${formatNumber(pool)}</span>` : "";
    const btn = `<span style="font-family:var(--font-mono);font-size:0.56rem;font-weight:700;padding:3px 9px;border-radius:4px;background:${cause.color};color:#0f1a14;white-space:nowrap;flex-shrink:0;">${formatShortDate(decision)} \xB7 ${daysUntil}d</span>`;
    return `<a href="cause.html?id=${cause.id}" style="display:flex;align-items:center;gap:10px;padding:9px 14px;border-radius:8px;background:rgba(15,26,20,0.78);border:1.5px solid ${cause.color};text-decoration:none;color:rgba(245,240,232,0.95);width:100%;box-sizing:border-box;overflow:hidden;">` + dot + label + title + orgStr + poolStr + btn + "</a>";
  }
  function topCardHeader(activeIndex) {
    const cause = config.causes.find((c) => c.index === activeIndex);
    if (!cause) return "";
    return `<div style="display:flex;align-items:center;gap:8px;padding:0 16px;height:100%;border-top:2px solid ${cause.color};border-left:1px solid rgba(255,255,255,0.09);border-right:1px solid rgba(255,255,255,0.09);border-bottom:none;border-radius:8px 8px 0 0;background:rgba(15,26,20,0.82);box-sizing:border-box;position:relative;z-index:2;">
    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;flex-shrink:0;background:${cause.color};box-shadow:0 0 5px ${cause.color};"></span>
    <span style="font-family:var(--font-mono);font-size:0.58rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:${cause.color};">${cause.name}</span>
    <span style="font-family:var(--font-mono);font-size:0.5rem;color:rgba(245,240,232,0.28);margin-left:auto;white-space:nowrap;">Organization Election</span>
  </div>`;
  }
  function topCard(activeIndex) {
    const cause = config.causes.find((c) => c.index === activeIndex);
    if (!cause) return "";
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(activeIndex);
    const thisShares = Votes.forCause(activeIndex, cycleNum, orgs);
    const thisLeader = thisShares[0];
    const thisDecision = Cycle.nextDecisionDate(activeIndex);
    const daysToThis = Math.ceil((thisDecision.getTime() - Date.now()) / MS_PER_DAY);
    const thisInits = config.initiatives.filter((i) => i.cause_index === activeIndex);
    const thisPool = thisInits.reduce((s, i) => s + (i.committed_ebx || 0), 0);
    const thisInit = [...thisInits].sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];
    let myOrgVote = null;
    try {
      const ch = JSON.parse(localStorage.getItem("ebx_choices") || "{}");
      myOrgVote = ch[`org_${activeIndex}`] || null;
    } catch (_e) {
    }
    const thisVoteBars = thisShares.slice(0, 4).map((s) => `
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
      <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${s.color};flex-shrink:0;"></span>
      <span style="font-family:var(--font-mono);font-size:0.58rem;color:rgba(245,240,232,0.72);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${s.org_name}</span>
      <span style="font-family:var(--font-mono);font-size:0.56rem;color:rgba(245,240,232,0.45);flex-shrink:0;">${s.pct.toFixed(0)}%</span>
    </div>`).join("");
    const leftPane = `
    <div style="padding:12px 14px;min-width:0;display:flex;flex-direction:column;gap:0;">
      <div style="font-family:var(--font-mono);font-size:0.48rem;letter-spacing:0.16em;text-transform:uppercase;color:${cause.color};font-weight:700;margin-bottom:5px;">This week \xB7 ${daysToThis}d</div>
      <div style="font-size:0.8rem;font-weight:700;color:rgba(245,240,232,0.95);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:8px;">${thisInit ? (thisInit.emoji ? thisInit.emoji + " " : "") + thisInit.title : '<span style="opacity:0.4;font-style:italic;">No initiative yet</span>'}</div>
      ${thisVoteBars}
      <div style="margin-top:6px;font-family:var(--font-mono);font-size:0.56rem;color:rgba(245,240,232,0.38);">Pool: ${thisPool > 0 ? "$" + formatNumber(thisPool) : "\u2014"} \xB7 ${formatShortDate(thisDecision)}</div>
      ${myOrgVote ? `<div style="margin-top:5px;font-family:var(--font-mono);font-size:0.52rem;color:${cause.color};opacity:0.85;">\u2713 Your vote: ${myOrgVote}</div>` : ""}
      <a href="m_indx.html" style="display:inline-block;margin-top:9px;font-family:var(--font-mono);font-size:0.54rem;font-weight:700;padding:3px 9px;border-radius:4px;background:${cause.color};color:#0f1a14;text-decoration:none;">Vote \u2192</a>
    </div>`;
    const nextCycle = cycleNum + 1;
    const nextShares = Votes.forCause(activeIndex, nextCycle, orgs);
    const nextLeader = nextShares[0];
    const nextDecision = new Date(thisDecision.getTime() + config.causeLengthDays * MS_PER_DAY);
    const daysToNext = Math.ceil((nextDecision.getTime() - Date.now()) / MS_PER_DAY);
    const nextInits = config.initiatives.filter((i) => i.cause_index === activeIndex);
    const nextInit = [...nextInits].sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0];
    const nextVoteBars = nextShares.slice(0, 3).map((s) => `
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">
      <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:${s.color};flex-shrink:0;opacity:0.75;"></span>
      <span style="font-family:var(--font-mono);font-size:0.58rem;color:rgba(245,240,232,0.55);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${s.org_name}</span>
      <span style="font-family:var(--font-mono);font-size:0.56rem;color:rgba(245,240,232,0.35);flex-shrink:0;">${s.pct.toFixed(0)}%</span>
    </div>`).join("");
    const rightPane = `
    <div style="padding:12px 14px;min-width:0;display:flex;flex-direction:column;gap:0;">
      <div style="font-family:var(--font-mono);font-size:0.48rem;letter-spacing:0.16em;text-transform:uppercase;color:rgba(245,240,232,0.35);margin-bottom:5px;">Newest \xB7 ${daysToNext}d</div>
      <div style="font-size:0.8rem;font-weight:700;color:rgba(245,240,232,0.68);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:8px;">${nextInit ? (nextInit.emoji ? nextInit.emoji + " " : "") + nextInit.title : '<span style="opacity:0.4;font-style:italic;">No initiative yet</span>'}</div>
      ${nextVoteBars}
      <div style="margin-top:6px;font-family:var(--font-mono);font-size:0.56rem;color:rgba(245,240,232,0.28);">${formatShortDate(nextDecision)}</div>
      ${nextLeader ? `<div style="margin-top:5px;font-family:var(--font-mono);font-size:0.52rem;color:rgba(245,240,232,0.42);">Leading: ${nextLeader.org_name} ${nextLeader.pct.toFixed(0)}%</div>` : ""}
      <div style="display:flex;gap:6px;margin-top:9px;flex-wrap:wrap;">
        <a href="m_indx.html" style="font-family:var(--font-mono);font-size:0.52rem;padding:2px 8px;border-radius:4px;border:1px solid rgba(245,240,232,0.16);color:rgba(245,240,232,0.45);text-decoration:none;">m_indx \u2192</a>
        <a href="en.html?cause=${cause.id}" style="font-family:var(--font-mono);font-size:0.52rem;padding:2px 8px;border-radius:4px;border:1px solid rgba(245,240,232,0.1);color:rgba(245,240,232,0.32);text-decoration:none;">EN feed</a>
      </div>
    </div>`;
    return `<div style="background:rgba(15,26,20,0.82);border-left:1px solid rgba(255,255,255,0.09);border-right:1px solid rgba(255,255,255,0.09);border-bottom:1px solid rgba(255,255,255,0.09);border-top:1px solid rgba(255,255,255,0.07);overflow:hidden;width:100%;box-sizing:border-box;height:100%;border-radius:0 0 8px 8px;">
    <div style="display:grid;grid-template-columns:1fr 1px 1fr;height:100%;">
      ${leftPane}
      <div style="background:rgba(255,255,255,0.07);"></div>
      ${rightPane}
    </div>
  </div>`;
  }
  function missionStrip() {
    return config.causes.map((cause) => {
      return `
      <a href="mission.html?cause=${cause.id}" class="mission-link"
         title="${cause.name} mission"
         style="--mc:${cause.color};
                display:flex;align-items:center;justify-content:center;
                aspect-ratio:1 / 1;min-width:0;
                text-decoration:none;color:inherit;
                background:rgba(15,26,20,0.65);
                border:1px solid rgba(255,255,255,0.07);
                border-top:3px solid var(--mc);
                border-radius:8px;
                font-size:1.5rem;
                transition:background 0.2s, transform 0.2s;">
        <span style="opacity:0.9;line-height:1;">${cause.emoji ?? "\u25C6"}</span>
      </a>
    `;
    }).join("");
  }
  var EBX = {
    config,
    fetchJSON,
    fetchAPI,
    loadCauses,
    loadInitiatives,
    loadOrganizations,
    loadFeed,
    loadAll,
    Cycle,
    Annulus,
    Votes,
    initFooter,
    initPage,
    getParam,
    buildURL,
    $,
    $$,
    render,
    renderSkeleton,
    renderEmpty,
    formatNumber,
    formatEBX,
    formatPercent,
    formatDate,
    formatShortDate,
    timeAgo,
    tokenChip,
    creditBadge,
    tag,
    progressBar,
    statBlock,
    initiativeCard,
    electionPanel,
    electionBanner,
    missionStrip,
    userBadge,
    feedCard,
    raceCard,
    sideCard,
    topCard,
    topCardHeader,
    upcomingCauseBanner,
    filterBySearch,
    filterByField,
    sortBy,
    Auth
  };
  window.EBX = EBX;
  document.addEventListener("DOMContentLoaded", () => {
    EBX.initPage();
  });
  var ebx_shared_default = EBX;
})();
