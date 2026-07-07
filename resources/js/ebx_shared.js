"use strict";
(() => {
  // src/ebx_shared.ts
  var config = {
    dataRoot: "/data/",
    apiBase: "",
    // empty means same origin — works when FastAPI hosts the static files
    version: "0.4.0",
    cycleStart: /* @__PURE__ */ new Date("2026-04-28T12:00:00"),
    // mission GENESIS (atm0 open / program week 0) — matches backend bootstrap.GENESIS + seeded started_at
    causeLengthDays: 49,
    // 7 weeks per cause
    decisionIntervalDays: 7,
    // one decision per week
    useApi: true,
    causes: [],
    initiatives: [],
    organizations: [],
    feed: [],
    missions: []
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
      const _normStatus = (s) => s === "won" || s === "org_vote" ? "active" : (s === "lost" || s === "in_election" || s === "debate" ? "suggested" : (s || "suggested"));
      config.initiatives = data.map((i) => ({
        ...i,
        status: _normStatus(i.status),
        cause_index: config.causes.find((c) => c.id === i.cause_id)?.index ?? 0,
        // Mirror the backend's committed-EBX aggregate (ebx_committed) onto the
        // committed_ebx field the homepage cards read. Was hardcoded 0, which
        // zeroed every leaderboard. 10 EBX = 1 vote.
        committed_ebx: i.ebx_committed ?? i.committed_ebx ?? 0,
        ebx_committed: i.ebx_committed ?? i.committed_ebx ?? 0
      }));
    }
    return config.initiatives;
  }
  async function loadOrganizations() {
    const data = config.useApi ? await fetchAPI("/organizations") : await fetchJSON("causes/orgs.json");
    if (data) {
      config.organizations = data.map((o) => ({
        id: o.id,
        name: o.name,
        causes: [],
        verified: o.verified ?? false,
        description: o.description,
        founded: o.founded_year
      }));
    }
    return config.organizations;
  }
  async function loadFeed() {
    const data = config.useApi ? await fetchAPI("/posts?limit=50") : await fetchJSON("causes/feed.json");
    if (data) {
      config.feed = data.map((p) => ({
        ...p,
        type: p.type ?? p.category ?? "editorial",
        author: p.author ?? p.author_type ?? "Earthbux",
        likes: p.likes ?? p.helpful_count ?? 0,
        cause_index: p.cause_index ?? (config.causes.find((c) => c.id === p.cause_id)?.index ?? 0)
      }));
    }
    return config.feed;
  }
  async function loadMissions() {
    if (!config.useApi) return config.missions;
    const data = await fetchAPI("/missions");
    if (data) {
      config.missions = data.map((m) => ({
        ...m,
        cause_index: config.causes.find((c) => c.id === m.cause_id)?.index ?? 0
      }));
    }
    return config.missions;
  }
  async function loadAll() {
    await loadCauses();
    await Promise.all([loadInitiatives(), loadOrganizations(), loadFeed(), loadMissions()]);
    try {
      const me = await Auth.fetchMe();
      Accounts.activate(me ? me.handle : null);
    } catch (_e) {
      Accounts.activate(null);
    }
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
        config.cycleStart.getTime() + targetWeek * config.decisionIntervalDays * MS_PER_DAY
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
    },
    /**
     * Anchor-date model (README §4). Given a mission's election date (= mission
     * start date = the day its initiative was elected), derive every later phase
     * boundary by fixed week offsets. One anchor in, all downstream dates out.
     *
     * Offsets follow STRUCTURE §SYSTEM "Weekly missions — 5 phases":
     *   New-Initiative wks 1-8  -> Phase 1 (anchor)
     *   Budget         wks 9-16 -> Phase 2 begins +8w
     *   Credit-Release wks 17-32-> Phase 3 begins +16w
     *   Resolution     wks 33+  -> Phase 4 begins +32w
     * (README §7 sketched +7/+14/+32; STRUCTURE week boundaries give +8/+16/+32,
     *  which is canonical — logged as a pass-32 decision in README.)
     */
    missionPhaseDates(electionDate) {
      const anchor = electionDate instanceof Date ? electionDate : new Date(electionDate);
      const wk = config.decisionIntervalDays * MS_PER_DAY;
      const base = anchor.getTime();
      return {
        phase1_start: new Date(base),
        phase2_start: new Date(base + 8 * wk),
        phase3_start: new Date(base + 16 * wk),
        phase4_start: new Date(base + 32 * wk),
        phase4_resolved: new Date(base + 48 * wk)
      };
    }
  };
  var LocalElections = {
    // DECONSTRUCTED (v2): phase transitions are server-side (scheduler.py +
    // the /missions/{id}/p1|p2 tallies). Kept as no-op stubs so any lingering
    // call sites don't throw while the pages are rebuilt.
    records() {
      return {};
    },
    recordFor(_causeId) {
      return null;
    },
    touchEpoch(_causeId, _causeIndex) {
    },
    runRollover() {
    },
    applyOverrides() {
    }
  };
  var ACCOUNT_SCOPED_KEYS = [
    "ebx_org_regs",
    "ebx_org_tasks",
    "ebx_post_votes",
    "ebx_local_posts",
    "ebx_profile",
    "ebx_watchlist"
  ];
  var Accounts = {
    CUR_KEY: "ebx_active_account",
    _stashKey(account, key) {
      return "ebx_acct:" + account + ":" + key;
    },
    /** Switch the localStorage working set to `handle` (null = guest). */
    activate(handle) {
      const next = handle || "__guest__";
      const prev = localStorage.getItem(Accounts.CUR_KEY);
      if (prev === null) {
        localStorage.setItem(Accounts.CUR_KEY, next);
        return;
      }
      if (prev === next) return;
      ACCOUNT_SCOPED_KEYS.forEach((k) => {
        const cur = localStorage.getItem(k);
        const stash = Accounts._stashKey(prev, k);
        if (cur !== null) localStorage.setItem(stash, cur);
        else localStorage.removeItem(stash);
        const restored = localStorage.getItem(Accounts._stashKey(next, k));
        if (restored !== null) localStorage.setItem(k, restored);
        else localStorage.removeItem(k);
      });
      localStorage.setItem(Accounts.CUR_KEY, next);
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
  var Votes = {
    RANK_COLORS,
    OTHER_COLOR,
    rankColor,
    // DECONSTRUCTED (v2): org standings + initiative ranking come from the
    // backend tallies (/missions/{id}/p2/tally and /p1/tally), not a synthetic
    // distribution. These return empty / passthrough until the pages are wired.
    forCause(_causeIndex, _cycleNum, _orgs) {
      return [];
    },
    orgsForCause(_causeIndex) {
      return [];
    },
    initiativesForCause(_causeIndex, _cycleNum, inits) {
      return [...inits];
    }
  };
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
        innerPath.setAttribute("d", chevronSectorPath(cx, cy, midR, innerR, startAngle, endAngle));
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
      const nextIndex = (state.causeIndex + 1) % n;
      Annulus._segments.forEach((seg, i) => {
        seg.labelGroup.setAttribute(
          "transform",
          `rotate(${-state.rotationDeg}, ${seg.midX}, ${seg.midY})`
        );
        if (i === state.causeIndex) {
          seg.innerPath.setAttribute("stroke", "#ffffff");
          seg.innerPath.setAttribute("stroke-width", "3");
          seg.innerPath.setAttribute("filter", "drop-shadow(0 0 8px rgba(255,255,200,0.55))");
        } else if (i === nextIndex) {
          // Upcoming cause — glow in its own color (layered colored halo).
          const col = config.causes[i] ? config.causes[i].color : "#ffffff";
          seg.innerPath.setAttribute("stroke", col);
          seg.innerPath.setAttribute("stroke-width", "2");
          seg.innerPath.setAttribute("filter", `drop-shadow(0 0 4px ${col}) drop-shadow(0 0 11px ${col})`);
        } else {
          seg.innerPath.setAttribute("stroke", "#0f1a14");
          seg.innerPath.setAttribute("stroke-width", "1.5");
          seg.innerPath.removeAttribute("filter");
        }
      });
      // Raise the active + upcoming sectors above their neighbors so the glow
      // halos aren't painted over by adjacent chevrons. Only reorder when the
      // active cause changes (not every animation frame).
      if (Annulus._lastHiCause !== state.causeIndex) {
        Annulus._lastHiCause = state.causeIndex;
        [nextIndex, state.causeIndex].forEach(hi => {
          const seg = Annulus._segments[hi];
          if (seg && group) { group.appendChild(seg.innerPath); group.appendChild(seg.labelGroup); }
        });
      }
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
  // Curved-chevron sector (build-seq: arrow wheel). Each sector is two
  // parallelograms mirrored across the mid-radius spine, giving a 90° tip at
  // the a1 (clockwise) end and a 90° notch at the a0 end. The 45° edges come
  // from offsetting the inner/outer arcs by `al` = ringThickness/2 ÷ midRadius,
  // so the slanted edges rise one radial half-thickness over an equal tangential
  // run (≈45°). Tips point clockwise — opposite the wheel's rotation.
  function chevronSectorPath(cx, cy, rOuter, rInner, a0, a1) {
    const rMid = (rOuter + rInner) / 2;
    const al = (rOuter - rInner) / (rOuter + rInner); // angular offset ≈ 45° edges
    const P = (r, a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    const A = P(rMid, a1);        // tip (points toward a1)
    const B = P(rOuter, a1 - al); // outer front
    const C = P(rOuter, a0);      // outer back
    const D = P(rMid, a0 + al);   // back notch (on the spine)
    const E = P(rInner, a0);      // inner back
    const F = P(rInner, a1 - al); // inner front
    return [
      `M ${A[0]} ${A[1]}`,
      `L ${B[0]} ${B[1]}`,
      `A ${rOuter} ${rOuter} 0 0 0 ${C[0]} ${C[1]}`,
      `L ${D[0]} ${D[1]}`,
      `L ${E[0]} ${E[1]}`,
      `A ${rInner} ${rInner} 0 0 1 ${F[0]} ${F[1]}`,
      "Z"
    ].join(" ");
  }
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
            <a href="main.html" class="ebx-footer__logo" style="text-decoration:none;color:inherit;">Earthbux</a>
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
  var EBX_PER_VOTE = 10;   // 10 EBX = 1 vote (≈ $1), matching the backend p1 tally
  function voteWeight(baseVotes, committedEbx) {
    return Math.max(baseVotes || 0, (committedEbx || 0) / EBX_PER_VOTE);
  }
  // Votes are fractional now (10 EBX = 1 vote, 1 EBX = 0.1 vote). Show a fixed
  // 1-decimal precision so leaderboards line up and never look like raw ints.
  var formatVotes = (n) => {
    const v = Number(n) || 0;
    return `${v.toFixed(1)} vote${v === 1 ? "" : "s"}`;
  };
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
      headline: "Headline",
      case: "Case",
      context: "Context",
      analysis: "Analysis",
      evaluation: "Feedback"
    };
    // Show the post's actual type, plus its stance where one applies:
    // case -> for|against ; evaluation(feedback) -> positive|negative.
    const baseLabel = typeLabel[post.type] ?? post.type;
    const label = baseLabel + (post.stance ? " \xB7 " + post.stance : "");
    // build-seq 11: discussion posts open in their cause's p1 viewer (with the
    // voting dialog); editorial/headline news stays on en.html.
    var _isDiscussion = ["case", "context", "analysis", "evaluation"].indexOf(post.type) >= 0;
    var _href = (cause && _isDiscussion)
      ? ("cause.html?id=" + cause.id + "&post=" + post.id)
      : ("en.html?id=" + post.id);
    return `
    <a href="${_href}" class="ebx-feed-card"
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
      if (!Auth.getToken()) return null;
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
  // Card action footer (build-seq: two-button cards). Vote → the cause-page
  // p1/p2 voting area (caller supplies d.voteHref). Research → opens the
  // matching entity's expanded table row via the page's idxResearch() hook.
  function _electionCardFooter(d) {
    const voteHref = d.voteHref || d.href || "#";
    const cid = String(d.causeId || "").replace(/'/g, "");
    const base = "flex:1;display:block;text-align:center;font-family:var(--font-mono);font-size:0.7rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:8px 6px;border-radius:6px;cursor:pointer;text-decoration:none;box-sizing:border-box;transition:filter 0.15s,background 0.15s;";
    const vote = '<a href="' + voteHref + '" class="rc-vote" style="' + base + "background:" + d.color + ";color:#0f1a14;border:1px solid " + d.color + ';">Vote</a>';
    const research = '<button type="button" class="rc-research" onclick="if(window.idxResearch)idxResearch(\'' + cid + "');return false;\" style=\"" + base + "background:transparent;color:" + d.color + ";border:1px solid " + d.color + ';">Discuss</button>';
    return '<div style="display:flex;gap:7px;padding:9px 12px 11px;border-top:1px solid rgba(255,255,255,0.07);">' + vote + research + "</div>";
  }
  // Vote window shown in a card's corner: the full election phase ending on the
  // decision/close date — "<open> - <close>". Phase 1 (initiative vote) runs 7
  // weeks; phase 2 (org vote) runs 8 weeks.
  function formatVoteWindow(closeDate, weeks) {
    const close = new Date(closeDate);
    const open = new Date(close.getTime() - (weeks || 7) * 7 * MS_PER_DAY);
    return formatShortDate(open) + " - " + formatShortDate(close);
  }
  function electionCardFace(d) {
    // build-seq (readability pass): dark card, leader-only row spilling to 2
    // lines, larger type, high-contrast light text, dates emphasized. The card
    // body is no longer clickable — only the header link and the footer
    // Vote / Discuss buttons carry actions.
    const CARD_BG = "rgba(15,26,20,0.85)";       // dark card background
    const INK = "rgba(245,240,232,0.95)";        // light primary text (high contrast)
    const INK_MUTED = "rgba(245,240,232,0.62)";  // light secondary text
    const leader = d.rows && d.rows.length ? d.rows[0] : null;
    const _num = (n) => Number(n || 0).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    // My choice's rank + vote count within the field, so it reads like the
    // leader row ("<rank>. <name> - <votes>"). Matched by name in d.rows.
    const _myIdx = (d.myChoice && d.rows) ? d.rows.findIndex(r => r.name === d.myChoice) : -1;
    const _myRank = _myIdx >= 0 ? _myIdx + 1 : null;
    const _myVotes = _myIdx >= 0 ? Number(d.rows[_myIdx].votes || 0) : 0;
    // Leader row: "1. <leader> - <votes>" (name spills to 2 lines; votes pinned).
    const body = leader
      ? '<div style="display:flex;align-items:flex-start;gap:6px;padding:9px 14px;font-family:var(--font-mono);font-size:0.82rem;color:' + INK + ';"><span style="flex:1;min-width:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-weight:600;line-height:1.3;word-break:break-word;">1. ' + leader.name + '</span><span style="color:' + d.color + ';font-weight:700;flex-shrink:0;">' + (leader.votes > 0 ? _num(leader.votes) : "--") + "</span></div>"
      : '<div style="padding:12px 14px;font-size:0.82rem;color:rgba(245,240,232,0.4);font-style:italic;">No votes yet.</div>';
    const glow = d.glowColor
      ? "box-shadow:0 0 16px " + d.glowColor + ",0 0 5px " + d.glowColor + ";"
      : (d.glow ? "box-shadow:0 0 14px rgba(255,255,255,0.28),0 0 4px rgba(255,255,255,0.5);" : "");
    return '<div class="race-card" data-cause-id="' + d.causeId + '" style="--rc-color:' + d.color + ";display:block;text-decoration:none;width:100%;box-sizing:border-box;background:" + CARD_BG + ";border:1.5px solid var(--rc-color);border-radius:10px;overflow:hidden;color:" + INK + ";" + glow + '"><div style="padding:10px 14px;background:rgba(0,0,0,0.22);border-bottom:1.5px solid var(--rc-color);display:flex;justify-content:space-between;align-items:flex-start;gap:8px;"><a href="' + d.href + '" style="font-family:var(--font-mono);font-size:0.74rem;letter-spacing:0.04em;text-transform:uppercase;color:var(--rc-color);font-weight:700;text-decoration:none;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.35;word-break:break-word;">' + d.headerLeft + '</a><span style="font-family:var(--font-mono);font-size:0.72rem;color:' + INK + ';font-weight:700;white-space:nowrap;flex-shrink:0;background:rgba(255,255,255,0.08);padding:3px 8px;border-radius:5px;">' + d.headerRight + "</span></div>" + body + '<div style="border-top:1px solid rgba(255,255,255,0.07);padding:8px 14px 9px;display:flex;flex-direction:column;gap:4px;"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-family:var(--font-mono);font-size:0.74rem;color:' + INK + ';"><span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + (d.myChoice ? (_myRank ? _myRank + '. ' : '') + d.myChoice : '<span style="opacity:0.5;font-style:italic;">no vote yet</span>') + '</span><span style="color:' + d.color + ';font-weight:700;flex-shrink:0;">' + (d.myChoice ? _num(_myVotes) : "--") + '</span></div><div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-family:var(--font-mono);font-size:0.74rem;color:' + INK + ';"><span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"><span style="color:' + INK_MUTED + ';font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;">My commitment</span> ' + (d.myCommit > 0 ? formatEBX(d.myCommit) : "--") + '</span><span style="color:' + d.color + ';font-weight:700;flex-shrink:0;"><span style="color:' + INK_MUTED + ';font-weight:400;font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;">pool</span> ' + (d.pool > 0 ? formatEBX(d.pool) : "--") + "</span></div></div>" + _electionCardFooter(d) + "</div>";
  }
  function sideCard(causeIndex, opts) {
    const cause = config.causes.find((c) => c.index === causeIndex);
    if (!cause) return "";
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(causeIndex);
    const orgShares = Votes.forCause(causeIndex, cycleNum, orgs);
    const all = config.initiatives.filter((i) => i.cause_index === causeIndex);
    const mission = all.filter((i) => ["org_vote", "active"].includes(i.status)).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0] || null;
    const phase1Pool = mission ? mission.committed_ebx || 0 : 0;
    let myChoice = null;
    let myCommit = 0;
    try {
      const _ovRaw = JSON.parse(localStorage.getItem("ebx_org_votes") || "{}")[cause.id] || null;
      const votedOrgId = _ovRaw && typeof _ovRaw === "object" ? _ovRaw.org_id : _ovRaw;
      if (votedOrgId) {
        const o = orgs.find((x) => x.id === votedOrgId);
        myChoice = o ? o.name : null;
      }
      const committed = JSON.parse(localStorage.getItem("ebx_org_committed") || "{}")[cause.id];
      if (committed) myCommit = committed.ebx || 0;
    } catch (_e) {
    }
    const pool = phase1Pool + myCommit;
    const SYNTH_TURNOUT = 200;
    const rows = orgShares.filter((sh) => !sh.isOther).map((sh) => ({ name: sh.org_name, votes: Math.round(sh.pct / 100 * SYNTH_TURNOUT), ebx: Math.round(sh.pct / 100 * pool) }));
    const myRow = myChoice ? rows.find((r) => r.name === myChoice) : null;
    // Org vote day = 8 weeks after the tiv vote day (phase 2 runs the 8 weeks
    // following the initiative vote), so the org window opens where tiv closes.
    const orgVoteDay = new Date(
      Cycle.nextDecisionDate(causeIndex).getTime() + 8 * config.decisionIntervalDays * MS_PER_DAY
    );
    return electionCardFace({
      causeId: cause.id,
      color: cause.color,
      headerLeft: mission ? mission.title : cause.name,
      headerRight: formatVoteWindow(orgVoteDay, 8),
      rows,
      myChoice,
      myChoiceEbx: myRow ? myRow.ebx : 0,
      myCommit,
      pool,
      href: "cause.html?id=" + cause.id,
      voteHref: "cause.html?id=" + cause.id + "&vote=2#phase-recap-2",
      glowColor: opts && opts.glowColor ? opts.glowColor : null
    });
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
    const btn = `<span style="font-family:var(--font-mono);font-size:0.56rem;font-weight:700;padding:3px 9px;border-radius:4px;background:${cause.color};color:#0f1a14;white-space:nowrap;flex-shrink:0;">${formatShortDate(decision)} \xB7 ${daysUntil}d</span>`
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
  function topCard(activeIndex, face = "front") {
    const cause = config.causes.find((c) => c.index === activeIndex);
    if (!cause) return "";
    const cycleNum = Cycle.currentCycleNum();
    const orgs = Votes.orgsForCause(activeIndex);
    const all = config.initiatives.filter((i) => i.cause_index === activeIndex);
    const winStart = Cycle.nextDecisionDate(activeIndex);
    const wk = config.decisionIntervalDays * MS_PER_DAY;
    let missionTiv;
    let orgVoteDay;
    let shares;
    if (face === "front") {
      // Tiv mode (initiatives): the UPCOMING organization (p2) election — the
      // next org vote to close, shown with the upcoming/near date so the
      // initiative-mode card points forward to the vote that's coming up.
      missionTiv = all.filter((i) => ["org_vote", "active"].includes(i.status)).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0] || null;
      orgVoteDay = new Date(winStart.getTime() + wk);
      shares = Votes.forCause(activeIndex, cycleNum, orgs);
    } else {
      // Org mode (active missions): the JUST-ELECTED initiative now heading to
      // its organization vote — shown with the farther-out date (its org
      // election is ~7-8 weeks out, the cause's next active window).
      missionTiv = all.filter((i) => ["org_vote", "active"].includes(i.status)).sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0))[0] || null;
      orgVoteDay = new Date(winStart.getTime() + config.causeLengthDays * MS_PER_DAY + wk);
      shares = Votes.forCause(activeIndex, cycleNum, orgs);
    }
    const phase1Pool = missionTiv ? missionTiv.committed_ebx || 0 : 0;
    let myChoice = null;
    let myCommit = 0;
    try {
      const _ovRaw = JSON.parse(localStorage.getItem("ebx_org_votes") || "{}")[cause.id] || null;
      const votedOrgId = _ovRaw && typeof _ovRaw === "object" ? _ovRaw.org_id : _ovRaw;
      if (votedOrgId) {
        const o = orgs.find((x) => x.id === votedOrgId);
        myChoice = o ? o.name : null;
      }
      const committed = JSON.parse(localStorage.getItem("ebx_org_committed") || "{}")[cause.id];
      if (committed) myCommit = committed.ebx || 0;
    } catch (_e) {
    }
    const pool = phase1Pool + myCommit;
    const SYNTH_TURNOUT = 200;
    const rows = shares.filter((sh) => !sh.isOther).map((sh) => ({ name: sh.org_name, votes: Math.round(sh.pct / 100 * SYNTH_TURNOUT), ebx: Math.round(sh.pct / 100 * pool) }));
    const myRow = myChoice ? rows.find((r) => r.name === myChoice) : null;
    return electionCardFace({
      causeId: cause.id,
      color: cause.color,
      headerLeft: missionTiv ? missionTiv.title : cause.name,
      headerRight: formatShortDate(orgVoteDay),
      rows,
      myChoice,
      myChoiceEbx: myRow ? myRow.ebx : 0,
      myCommit,
      pool,
      href: "cause.html?id=" + cause.id,
      glow: true
    });
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
    loadMissions,
    loadAll,
    Cycle,
    Annulus,
    Votes,
    LocalElections,
    Accounts,
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
    formatVotes,
    voteWeight,
    formatPercent,
    formatDate,
    formatShortDate,
    formatVoteWindow,
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
    electionCardFace,
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
