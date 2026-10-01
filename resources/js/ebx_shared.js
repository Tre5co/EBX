"use strict";
/* ebx_shared.js — THE SOURCE. Edit this file directly; there is no build step.
 *
 * 2026-09-16 (INSTRUCTIONS build-seq §1): the TypeScript source
 * `frontend/src/ebx_shared.ts` is RETIRED. It had fallen ~24 KB behind this
 * file (six EBX.* entry points and twelve diverged functions), so the build
 * that was meant to regenerate this file from it could only delete live code.
 * `frontend/` and `scripts/build_guard.js` are inert and listed in the
 * REMOVAL REGISTER. Bump the `?v=` on the pages' script tags after an edit.
 */
(() => {
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
    },
    /**
     * §7 (2026-08-10) — THE FIVE DATES OF ONE MISSION, FROM ONE ANCHOR.
     * The single source of truth for every date any page prints about a
     * mission. Jax, build-seq §1: "The anchor is 'Mission started' which
     * happens at week 0. Cause open is exactly 7 weeks before 0, cause
     * finalized is 7-14 weeks before 0. Philanthropy Elected is 8 weeks
     * after 0."
     *
     *   T (mission started, UX week 0) = started_at + 7 weeks
     *   cause opened                   = T - 7 weeks  (= started_at exactly)
     *   cause finalized                = a WINDOW, T-14w .. T-7w
     *   philanthropy elected           = T + 8 weeks
     *   credit release                 = T + 16 weeks
     *
     * THE +8 EXCURSION, AND WHY IT IS BACK AT +7. On 2026-08-10 this briefly
     * read `started_at + 8wk`, after "you have T a week early". That was a
     * DOUBLE CORRECTION — the week had already been accounted for — and Jax
     * called it: "everything is right, T is just 1 week late."
     * The decisive check is that +7 reproduces the two philanthropy dates Jax
     * gave directly in §5, and +8 reproduces neither:
     *     atm0 Carbon Capture Expansion  -> Aug 11   (+7 ✓, +8 gives Aug 18)
     *     atm1 Methane Leak Detection    -> Sep 29   (+7 ✓, +8 gives Oct 6)
     * Those two dates are the fixed points; anything that misses them is wrong.
     *
     * A CONSEQUENCE, STATED SO IT ISN'T MISTAKEN FOR A BUG: 8 weeks is not a
     * multiple of the 7-week rotation, so `phlElected` does NOT sit on the same
     * point of the cause's cycle that T does. That is Jax's explicit call:
     * "T + 8 weeks is the philanthropy election, T - 7 weeks is when the cause
     * is opened."
     *
     * DUPLICATED, ON PURPOSE: main.html and cause.html carry a byte-identical
     * fallback copy of this function (see their §7b shim) so a stale cache of
     * THIS file cannot blank those pages. If the formula changes, change all
     * three and bump the `?v=` on both script tags.
     */
    missionDates(mission) {
      const wk = config.decisionIntervalDays * MS_PER_DAY;
      const startMs = (mission && mission.started_at)
        ? new Date(mission.started_at).getTime() : Date.now();
      const T = startMs + 7 * wk;
      return {
        startedAt:          new Date(startMs),
        causeFinalizedFrom: new Date(T - 14 * wk),
        causeFinalizedTo:   new Date(T - 7 * wk),
        causeOpened:        new Date(T - 7 * wk),
        missionStarted:     new Date(T),
        phlElected:         new Date(T + 8 * wk),
        creditRelease:      new Date(T + 16 * wk)
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
    /** Sector that wears the "coming up" glow; null = the next cause. */
    glowIndex: null,
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
        // §2 (2026-08-27) — **the rays are gone from this wheel.** They were
        // added on 2026-08-05 for the home page, which does not mount this
        // annulus any anymore; on the discussion page, where it lives now, the
        // sectors are the cause TOGGLE and short spikes around them read as
        // decoration on a control. The election page's pie carries the rays
        // instead, drawn as chevrons that point the way the wheel turns.
        Annulus._segments.push({
          innerPath,
          outerGroup,
          labelGroup,
          rayGroup: null,
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
      // §2 (2026-08-05, jax notes 2: "main glowy marker pointing") — the now
      // marker is an arrowhead aimed INTO the wheel, not a dot: it points at
      // the cause the clock is currently standing on.
      const nowTip = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
      const _ty = cy - outerR - 4;          // tip sits just above the ring
      nowTip.setAttribute("points",
        `${cx},${_ty + 9} ${cx - 6},${_ty - 4} ${cx + 6},${_ty - 4}`);
      nowTip.setAttribute("fill", "white");
      nowTip.setAttribute("filter", "url(#ebx-now-glow)");
      nowGroup.appendChild(nowTip);
      // (No "NOW" caption: at r=184 the label lands on the viewBox edge and the
      // arrowhead already reads as the marker — the centre panel carries today's
      // date in words.)
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
      // §2 (2026-08-05): which sector wears the "coming up" glow. Defaults to
      // the next cause; main.html points it at the ACTIVE cause while the page
      // is showing active missions (structure.md backlog).
      const nextIndex = (Annulus.glowIndex == null)
        ? (state.causeIndex + 1) % n
        : ((Annulus.glowIndex % n) + n) % n;
      Annulus._segments.forEach((seg, i) => {
        seg.labelGroup.setAttribute(
          "transform",
          `rotate(${-state.rotationDeg}, ${seg.midX}, ${seg.midY})`
        );
        const _rays = (opacity, glowCol) => {
          if (!seg.rayGroup) return;
          Array.from(seg.rayGroup.childNodes).forEach(r => r.setAttribute("opacity", String(opacity)));
          if (glowCol) seg.rayGroup.setAttribute("filter", `drop-shadow(0 0 5px ${glowCol})`);
          else seg.rayGroup.removeAttribute("filter");
        };
        if (i === state.causeIndex) {
          seg.innerPath.setAttribute("stroke", "#ffffff");
          seg.innerPath.setAttribute("stroke-width", "3");
          seg.innerPath.setAttribute("filter", "drop-shadow(0 0 8px rgba(255,255,200,0.55))");
          _rays(1, "rgba(255,255,255,0.8)");
        } else if (i === nextIndex) {
          // Upcoming cause — glow in its own color (layered colored halo).
          const col = config.causes[i] ? config.causes[i].color : "#ffffff";
          seg.innerPath.setAttribute("stroke", col);
          seg.innerPath.setAttribute("stroke-width", "2");
          seg.innerPath.setAttribute("filter", `drop-shadow(0 0 4px ${col}) drop-shadow(0 0 11px ${col})`);
          _rays(0.95, col);
        } else {
          seg.innerPath.setAttribute("stroke", "#0f1a14");
          seg.innerPath.setAttribute("stroke-width", "1.5");
          seg.innerPath.removeAttribute("filter");
          _rays(0.32, null);
        }
      });
      // Raise the active + upcoming sectors above their neighbors so the glow
      // halos aren't painted over by adjacent chevrons. Only reorder when the
      // active cause changes (not every animation frame).
      if (Annulus._lastHiCause !== state.causeIndex) {
        Annulus._lastHiCause = state.causeIndex;
        [nextIndex, state.causeIndex].forEach(hi => {
          const seg = Annulus._segments[hi];
          if (seg && group) {
            group.appendChild(seg.innerPath);
            if (seg.rayGroup) group.appendChild(seg.rayGroup);
            group.appendChild(seg.labelGroup);
          }
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
  // one end and a 90° notch at the other. The 45° edges come from offsetting
  // the inner/outer arcs by `al` = ringThickness/2 ÷ midRadius, so the slanted
  // edges rise one radial half-thickness over an equal tangential run (≈45°).
  //
  // §1 (2026-08-27b) — **the tips point CLOCKWISE**, toward a1: the same way
  // the now-marker travels on the election page's annulus, and the same way
  // every ray on it points. They were flipped to a0 for one day on 2026-08-27
  // ("reverse the direction the svg annulus sections are pointing"), which put
  // them at odds with the only moving thing on either wheel; "discussion
  // sectors still pointing wrong way" is that flip being undone.
  function chevronSectorPath(cx, cy, rOuter, rInner, a0, a1) {
    const rMid = (rOuter + rInner) / 2;
    const al = (rOuter - rInner) / (rOuter + rInner); // angular offset ≈ 45° edges
    const P = (r, a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    const A = P(rMid, a1);        // tip (points toward a1 — clockwise)
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
  // ── THE FOOTER — on every page (2026-09-25) ──────────────────────────────
  // Jax: "Build the footer on every page. It will be changed, but the 'contact
  // us' part is important to do now." Columns follow INSTRUCTIONS › Footer
  // (keep / later / drop): About (the justification, what we do, how it works
  // — about.html's sections), Take part, Causes, Help & legal. Anything whose
  // page does not exist yet is drawn as "soon", not linked (F9). A page with
  // no `#ebx-footer-mount` gets one appended, so every page carries it.
  //
  // CONTACT US opens a dialog (EBX.Dialogs.contact) that POSTs /contact: the
  // message is stored, and emailed to jax@earthbux.net once SMTP is set.
  // Any element with `data-ebx-contact` (optionally ="topic") opens it, and so
  // does a `#contact` hash on any page.
  function initFooter() {
    let mount = document.getElementById("ebx-footer-mount");
    if (!mount) {
      if (document.querySelector("footer.ebx-footer")) return;
      mount = document.createElement("div");
      mount.id = "ebx-footer-mount";
      document.body.appendChild(mount);
    }
    const soon = (label) => '<li><span class="ebx-footer__soon" title="Coming soon">' + label + "</span></li>";
    const link = (href, label, ext) => '<li><a href="' + href + '"' + (ext ? ' rel="noopener" target="_blank"' : "") + ">" + label + "</a></li>";
    const causes = [["atmosphere", "Atmosphere"], ["oceans", "Oceans"], ["land", "Land"], ["forests", "Forests"],
      ["wildlife", "Wildlife"], ["human-rights", "Human Rights"], ["human-progress", "Human Progress"]];
    mount.innerHTML = `
    <footer class="ebx-footer">
      <div class="container">
        <div class="ebx-footer__grid ebx-footer__grid--5">
          <div class="ebx-footer__col ebx-footer__brand">
            <a href="index.html" class="ebx-footer__logo">Earthbux</a>
            <div class="ebx-footer__tagline">Collective action, measured in impact.</div>
            <p>The social network for charities. You donate, we follow.</p>
            <button type="button" class="ebx-footer__contact" data-ebx-contact>Contact us</button>
          </div>
          <div class="ebx-footer__col">
            <h4>About</h4>
            <ul>
              ${link("about.html#why", "Why Earthbux")}
              ${link("about.html#what", "What we do")}
              ${link("about.html#how", "How it works")}
              ${link("about.html#earthbuck", "What an Earthbuck is")}
              ${soon("White paper")}
              ${soon("Rules")}
            </ul>
          </div>
          <div class="ebx-footer__col">
            <h4>Take part</h4>
            <ul>
              ${link("mission.html", "Join a mission")}
              ${link("cause.html", "Read the news")}
              ${link("mission.html?state=oe", "Nominate an organization")}
              ${soon("Register a philanthropy")}
              <li><a href="#contact" data-ebx-contact="join">Join the team</a></li>
            </ul>
          </div>
          <div class="ebx-footer__col">
            <h4>Causes</h4>
            <ul>${causes.map(([id, n]) => link("cause.html?id=" + id, n)).join("")}</ul>
          </div>
          <div class="ebx-footer__col">
            <h4>Help &amp; legal</h4>
            <ul>
              <li><a href="#contact" data-ebx-contact>Contact us</a></li>
              ${soon("Help Center")}
              ${soon("Safety")}
              ${soon("Privacy")}
              ${soon("Terms")}
            </ul>
          </div>
        </div>
        <div class="ebx-footer__bottom">
          <span>\xA9 ${(/* @__PURE__ */ new Date()).getFullYear()} Earthbux &middot; <a href="https://earthbux.net">earthbux.net</a> &middot; <a href="https://earthbuxinc.com" rel="noopener" target="_blank">earthbuxinc.com</a></span>
          <span class="mono">v${config.version}</span>
        </div>
      </div>
    </footer>
  `;
    if (!document.documentElement.dataset.ebxContactBound) {
      document.documentElement.dataset.ebxContactBound = "1";
      document.addEventListener("click", (e) => {
        const t = e.target.closest && e.target.closest("[data-ebx-contact]");
        if (!t) return;
        e.preventDefault();
        Dialogs.contact({ topic: t.getAttribute("data-ebx-contact") || "general" });
      });
      const hash = () => { if (location.hash === "#contact") Dialogs.contact({}); };
      window.addEventListener("hashchange", hash);
      hash();
    }
  }
  // ── SITE NAV — the five tabs, on every page. ─────────────────────────────
  // Build-seq Misc (2026-09-08): "Add 5 navigation tabs across the top on every
  // page: About(index) - Elections(main) - Missions(mission) - News(cause) -
  // Profile(profile)."
  //
  // Written HERE, once, because `initPage` already runs on all five pages and a
  // nav that is copied five times is a nav that drifts — main.html and
  // cause.html each carry a byte-identical fallback of `missionDates` for
  // exactly that reason, and one of those in the codebase is enough.
  //
  // THE LIT TAB IS THE PAGE TAG. main.html's top bar said "ELECTION" and
  // cause.html's said "Discussion · <cause>"; the lit tab says that and also
  // says what the other four are, so the tag comes off where the nav goes in.
  // cause.html keeps the cause name beside the tabs — that half of its tag is
  // not navigation.
  //
  // Two mount modes: `#ebx-nav-mount` when the page has a top bar with a centre
  // cell to put it in, and otherwise a fixed strip at top-centre, between the
  // fixed `.ebx-home-mark` at top-left and the fixed user badge at top-right,
  // so mission.html and profile.html get it with no layout change at all.
  // build-seq §1 (2026-09-18): "Replace page toggles with Home - Elect -
  // Missions - News - Profile." Same five pages, verbs where the page is an act.
  // build-seq P1 (2026-09-24): "Home · Missions · News · Inbox · Profile".
  // Elect merged into Missions (main.html is a redirect now); Inbox is a stub
  // until P4 — drawn, not linked, so nobody lands on a page that is not there.
  var NAV_TABS = [
    { label: "Home", href: "index.html", match: ["index.html", ""] },
    { label: "Missions", href: "mission.html", match: ["mission.html", "mission.html", "m"] },
    { label: "News", href: "cause.html", match: ["cause.html"] },
    { label: "Inbox", href: null, match: [], soon: "Your inbox arrives with the event log (P4)." },
    { label: "Profile", href: "profile.html", match: ["profile.html"] }
  ];
  function currentPageFile() {
    // /m and /m/<slug> are the mission page (D1).
    if (/^\/m(\/|$)/.test(window.location.pathname)) return "m";
    const parts = window.location.pathname.split("/");
    return (parts[parts.length - 1] || "").toLowerCase();
  }
  function navTabs() {
    const here = currentPageFile();
    return '<nav class="ebx-nav" aria-label="Site">' + NAV_TABS.map((t) => {
      if (!t.href) {
        return '<span class="ebx-nav__tab ebx-nav__tab--soon" aria-disabled="true" title="' + t.soon + '">' +
          t.label + "</span>";
      }
      const on = t.match.indexOf(here) !== -1;
      return '<a class="ebx-nav__tab' + (on ? " ebx-nav__tab--on" : "") +
        '" href="' + t.href + '"' + (on ? ' aria-current="page"' : "") + ">" +
        t.label + "</a>";
    }).join("") + "</nav>";
  }
  // build-seq P2 (2026-09-25) — "Mobile: the five tabs pin to the bottom,
  // hiding on scroll-down." The pinning is CSS (≤640px, `.ebx-nav`); this adds
  // `ebx-nav--hide` to <body> while the reader is scrolling down and removes
  // it on any scroll up, or near the top. Also F14: the top bar no longer has
  // to fit the tabs at phone width.
  var _navScrollBound = false;
  function bindNavScroll() {
    if (_navScrollBound || typeof window === "undefined") return;
    _navScrollBound = true;
    var last = window.scrollY || 0;
    window.addEventListener("scroll", function () {
      var y = window.scrollY || 0;
      if (Math.abs(y - last) < 6) return;
      document.body.classList.toggle("ebx-nav--hide", y > last && y > 80);
      last = y;
    }, { passive: true });
  }
  function initNav() {
    bindNavScroll();
    const mount = document.getElementById("ebx-nav-mount");
    if (mount) { mount.innerHTML = navTabs(); return; }
    if (document.querySelector(".ebx-nav")) return;
    const wrap = document.createElement("div");
    wrap.className = "ebx-nav-float";
    wrap.innerHTML = navTabs();
    document.body.insertBefore(wrap, document.body.firstChild);
  }
  async function initPage() {
    initFooter();
    initNav();
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
  // §2 (2026-08-05): EBX reads as a whole count on cards and in dialogs —
  // fractional EBX exists in the ledger (a 0.5 skim is real) but "39.429 EBX"
  // in a card footer is noise, not information.
  var formatEBX = (n) => `${formatNumber(Math.round(Number(n) || 0))} EBX`;
  // §0 (2026-08-21) — **voting is counted in TOKENS.** "Voting no longer happens
  // in EBX. It happens in tokens… it's confusing because votes and ebx appear to
  // be separate." They are the same quantity — 1 EBX = 1 token = 10¢ — so this
  // formats the same number under the name the voting surfaces use. `formatEBX`
  // stays for the surfaces that are not the voting area (the credit badge and
  // the ledger still speak in EBX); main.html uses this one throughout.
  var formatTokens = (n) => {
    const v = Math.round(Number(n) || 0);
    return `${formatNumber(v)} token${v === 1 ? "" : "s"}`;
  };
  // The same amount as money. Voting IS donating, and a benefactor reading a
  // balance is entitled to know what it cost: 1 token = 10¢.
  var USD_PER_TOKEN = 0.1;
  var formatTokenUSD = (n) => `$${((Number(n) || 0) * USD_PER_TOKEN).toFixed(2)}`;
  var EBX_PER_VOTE = 10;   // 10 tokens = 1 vote (≈ $1), matching the backend p1 tally
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
      context: "Background",   // review 2026-09-24
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
          // F18 (2026-09-28): a validation error's `detail` is a LIST of
          // objects ({loc, msg, type}); printing it whole read "[object Object]".
          // Say each rule that was broken, in its own words.
          const d = body.detail;
          Auth.lastSignupError = Array.isArray(d)
            ? d.map(e => (e && e.msg ? String(e.msg).replace(/^Value error, /, '') : String(e))).join(' · ')
            : (typeof d === 'string' ? d : (d ? JSON.stringify(d) : `Server error (HTTP ${res.status})`));
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
  // Card action footer (build-seq: two-button cards).
  // §1 (2026-08-05, structure.md main.html): **View is gone — Vote does both.**
  // Vote filters the Context table to this cause AND points the table's top-row
  // vote dialog at it (window.voteOnCause on main.html); Discuss leaves for the
  // cause page, which is the discussion hub. Pages without a voteOnCause hook
  // (cause.html reuses these cards) fall back to the caller's voteHref.
  // NOTE: this file is the source (the TypeScript copy was retired 2026-09-16).
  function _electionCardFooter(d) {
    const voteHref = d.voteHref || d.href || "#";
    const cid = String(d.causeId || "").replace(/'/g, "");
    const base = "flex:1;display:block;text-align:center;font-family:var(--font-mono);font-size:0.7rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:8px 6px;border-radius:6px;cursor:pointer;text-decoration:none;box-sizing:border-box;transition:filter 0.15s,background 0.15s;";
    const vote = '<button type="button" class="rc-vote" onclick="if(window.voteOnCause){voteOnCause(\'' + cid + "');}else{window.location.href='" + voteHref + "';}return false;\" style=\"" + base + "background:" + d.color + ";color:#0f1a14;border:1px solid " + d.color + ';">Vote</button>';
    const discuss = '<a href="cause.html?id=' + cid + '" class="rc-discuss" style="' + base + "background:transparent;color:" + d.color + ";border:1px solid " + d.color + ';">Discuss</a>';
    return '<div style="display:flex;gap:7px;padding:9px 12px 11px;border-top:1px solid rgba(255,255,255,0.07);">' + vote + discuss + "</div>";
  }
  // Vote window shown in a card's corner: the full election phase ending on the
  // decision/close date — "<open> - <close>". Phase 1 (initiative vote) runs 7
  // weeks; phase 2 (org vote) runs 8 weeks.
  function formatVoteWindow(closeDate, weeks) {
    const close = new Date(closeDate);
    const open = new Date(close.getTime() - (weeks || 7) * 7 * MS_PER_DAY);
    return formatShortDate(open) + " - " + formatShortDate(close);
  }
  // The "uncommitted" counter. Dialing a slate in the Context table's top-row
  // vote dialog parks the change locally (main.html `_pendingEbx`) instead of
  // sending it per-drag; this strip surfaces that pending delta on the cause's
  // election card and offers the single Commit that flushes it.
  // §1 (2026-08-05): counted in EBX, matching the dialog.
  // Rendered only when there is something uncommitted for this cause.
  function _uncommittedStrip(d) {
    var n = 0;
    var draft = false;
    try { n = (typeof window !== "undefined" && window._uncommittedVotes) ? window._uncommittedVotes(d.causeId) : 0; } catch (e) { n = 0; }
    try { draft = (typeof window !== "undefined" && window._meHasDraft) ? window._meHasDraft(d.causeId) : !!n; } catch (e) { draft = !!n; }
    if (!draft) return "";
    var cid = String(d.causeId || "").replace(/'/g, "");
    return '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;font-family:var(--font-mono);font-size:0.72rem;color:' + d.color + ';padding-top:2px;">' +
      '<span><span style="color:rgba(245,240,232,0.62);font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;">Uncommitted</span> ' + n + ' EBX</span>' +
      '<button type="button" onclick="if(window.commitVotes)commitVotes(\'' + cid + '\');return false;" style="font:inherit;font-family:var(--font-mono);font-size:0.66rem;font-weight:700;cursor:pointer;background:' + d.color + ';color:#0f1a14;border:none;border-radius:5px;padding:2px 10px;">Commit</button>' +
      '</div>';
  }
  function electionCardFace(d) {
    // §2 (2026-08-05) — the card anatomy from Jax's drawing (jax notes 2,
    // CONTEXT), which is now the ONE shape every election card on the Context
    // page uses, side cards and top card alike:
    //
    //   ____________________________________
    //   |<header left>                 date|
    //   |1. name                        ebx|
    //   |2. name                        ebx|
    //   |3. name________________________ebx|
    //   |My choice - choice_name     |ebx   |
    //   |My commitment - x ebx_______|pool__|
    //
    // Two changes from the old face: THREE ranked rows instead of the leader
    // alone, and every number is an **EBX count, never a percentage** — "that
    // allows one to estimate the total pool size" (jax notes 2). `d.scale`
    // renders the same anatomy larger for the full-width top card.
    const CARD_BG = "rgba(15,26,20,0.85)";       // dark card background
    const INK = "rgba(245,240,232,0.95)";        // light primary text (high contrast)
    const INK_MUTED = "rgba(245,240,232,0.62)";  // light secondary text
    const big = d.scale === "top";
    const fRow = big ? "0.98rem" : "0.82rem";
    const fHead = big ? "0.86rem" : "0.74rem";
    const fFoot = big ? "0.86rem" : "0.74rem";
    const padX = big ? "20px" : "14px";
    const rows = (d.rows || []).slice(0, 3);
    const _ebx = (n) => Number(n || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
    // My choice's rank + EBX within the field, so it reads like a ranked row.
    const _myIdx = (d.myChoice && d.rows) ? d.rows.findIndex(r => r.name === d.myChoice) : -1;
    const _myRank = _myIdx >= 0 ? _myIdx + 1 : null;
    const _myEbx = _myIdx >= 0 ? Number(d.rows[_myIdx].ebx || 0) : Number(d.myChoiceEbx || 0);
    const body = rows.length
      ? '<div style="padding:' + (big ? "4px 0 5px" : "3px 0 4px") + ';">' + rows.map((r, i) =>
          '<div style="display:flex;align-items:flex-start;gap:8px;padding:' + (big ? "6px " : "4px ") + padX +
            ';font-family:var(--font-mono);font-size:' + fRow + ';color:' + INK + ';">' +
            '<span style="flex:1;min-width:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-weight:' +
              (i === 0 ? "600" : "400") + ';line-height:1.3;word-break:break-word;' +
              (i === 0 ? '' : 'color:' + INK_MUTED + ';') + '">' + (i + 1) + '. ' + r.name + '</span>' +
            '<span style="color:' + (i === 0 ? d.color : INK_MUTED) + ';font-weight:700;flex-shrink:0;">' +
              (Number(r.ebx || 0) > 0 ? _ebx(r.ebx) : "--") + '</span>' +
          '</div>').join('') + '</div>'
      : '<div style="padding:12px ' + padX + ';font-size:' + fRow + ';color:rgba(245,240,232,0.4);font-style:italic;">' +
        (d.emptyText || "No votes yet.") + '</div>';
    const glow = d.glowColor
      ? "box-shadow:0 0 16px " + d.glowColor + ",0 0 5px " + d.glowColor + ";"
      : (d.glow ? "box-shadow:0 0 26px rgba(255,255,255,0.35),0 0 6px rgba(255,255,255,0.6);border-color:rgba(255,255,255,0.85);" : "");
    return '<div class="race-card" data-cause-id="' + d.causeId + '" style="--rc-color:' + d.color + ";display:block;text-decoration:none;width:100%;box-sizing:border-box;background:" + CARD_BG + ";border:1.5px solid var(--rc-color);border-radius:10px;overflow:hidden;color:" + INK + ";" + glow + '">' +
      // header: name (links out) + the card's date
      '<div style="padding:' + (big ? "12px " : "10px ") + padX + ';background:rgba(0,0,0,0.22);border-bottom:1.5px solid var(--rc-color);display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">' +
        '<a href="' + d.href + '" style="font-family:var(--font-mono);font-size:' + fHead + ';letter-spacing:0.04em;text-transform:uppercase;color:var(--rc-color);font-weight:700;text-decoration:none;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.35;word-break:break-word;">' + d.headerLeft + '</a>' +
        '<span style="font-family:var(--font-mono);font-size:' + fHead + ';color:' + INK + ';font-weight:700;white-space:nowrap;flex-shrink:0;background:rgba(255,255,255,0.08);padding:3px 8px;border-radius:5px;">' + d.headerRight + '</span>' +
      '</div>' + body +
      // footer: my choice · my commitment / pool
      '<div style="border-top:1px solid rgba(255,255,255,0.07);padding:8px ' + padX + ' 9px;display:flex;flex-direction:column;gap:4px;">' +
        '<div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-family:var(--font-mono);font-size:' + fFoot + ';color:' + INK + ';">' +
          '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"><span style="color:' + INK_MUTED + ';font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;">My choice</span> ' +
          (d.myChoice ? (_myRank ? _myRank + '. ' : '') + d.myChoice : '<span style="opacity:0.5;font-style:italic;">no vote yet</span>') + '</span>' +
          '<span style="color:' + d.color + ';font-weight:700;flex-shrink:0;">' + (d.myChoice ? _ebx(_myEbx) : "--") + '</span>' +
        '</div>' +
        '<div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-family:var(--font-mono);font-size:' + fFoot + ';color:' + INK + ';">' +
          '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"><span style="color:' + INK_MUTED + ';font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;">My commitment</span> ' + (d.myCommit > 0 ? formatTokens(d.myCommit) : "--") + '</span>' +
          '<span style="color:' + d.color + ';font-weight:700;flex-shrink:0;"><span style="color:' + INK_MUTED + ';font-weight:400;font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;">pool</span> ' + (d.pool > 0 ? formatTokens(d.pool) : "--") + '</span>' +
        '</div>' + _uncommittedStrip(d) +
      '</div>' + (d.noFooter ? "" : _electionCardFooter(d)) + '</div>';
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
  // ════════════════════════════════════════════════════════════════════════
  // Dialogs — §2 (2026-08-05). structure.md, main.html: "Propose / nominate
  // dialogs shared with the cause page."
  //
  // The Context page and the Discussion page each carried their own copy of
  // the propose-an-initiative dialog, and the org dialog had DIVERGED: the
  // cause page had the real one (nominate/register, duplicate detection,
  // per-mission candidacies) while the Context page had a stub that punted to
  // profile.html. Both now mount these. Markup and styles are injected on
  // first open, so a page only needs to call EBX.Dialogs.propose(...) /
  // EBX.Dialogs.orgRegister(...).
  // ════════════════════════════════════════════════════════════════════════
  function openP1Mission(causeId) {
    const ms = (config.missions || []).filter((m) => m.cause_id === causeId);
    return ms.find((m) => m.current_phase === "initiative" && !m.winning_tiv_id)
        || ms.find((m) => m.current_phase === "initiative")
        || ms.slice().sort((a, b) => (b.cycle_num || 0) - (a.cycle_num || 0))[0]
        || null;
  }
  function _slugFor(title) {
    const base = (title || "").toLowerCase()
      .normalize("NFKD").replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48) || "initiative";
    return base + "-" + Math.random().toString(36).slice(2, 7);
  }
  var _dlgStyled = false;
  function _dlgStyles() {
    if (_dlgStyled) return;
    _dlgStyled = true;
    const st = document.createElement("style");
    st.textContent = `
      .ebx-dlg-bg { position: fixed; inset: 0; background: rgba(10,16,12,0.72); backdrop-filter: blur(2px);
        display: flex; align-items: center; justify-content: center; z-index: 400; padding: 20px;
        opacity: 0; pointer-events: none; transition: opacity 0.18s; }
      .ebx-dlg-bg.open { opacity: 1; pointer-events: auto; }
      .ebx-dlg { width: 100%; max-width: 520px; max-height: 88vh; overflow-y: auto; box-sizing: border-box;
        background: #14211a; border: 1.5px solid rgba(245,240,232,0.18); border-radius: 12px;
        padding: 22px 24px 20px; color: var(--clr-parchment, #f5f0e8);
        box-shadow: 0 18px 60px rgba(0,0,0,0.55); }
      .ebx-dlg__title { font-family: var(--font-display, serif); font-size: 1.25rem; font-weight: 800; margin-bottom: 14px; }
      .ebx-dlg label { display: block; font-family: var(--font-mono, monospace); font-size: 0.6rem;
        letter-spacing: 0.12em; text-transform: uppercase; color: rgba(245,240,232,0.5); margin: 12px 0 5px; }
      .ebx-dlg input[type=text], .ebx-dlg input[type=email], .ebx-dlg textarea, .ebx-dlg select {
        width: 100%; box-sizing: border-box; font: inherit; font-size: 0.88rem; padding: 8px 10px;
        color: var(--clr-parchment, #f5f0e8); background: rgba(255,255,255,0.05);
        border: 1px solid rgba(245,240,232,0.18); border-radius: 6px; outline: none; }
      .ebx-dlg textarea { min-height: 92px; resize: vertical; }
      .ebx-dlg input:focus, .ebx-dlg textarea:focus, .ebx-dlg select:focus { border-color: var(--clr-honey, #e8a84c); }
      .ebx-dlg select option { background: #14211a; }
      .ebx-dlg__actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 18px; }
      .ebx-dlg__btn { font: inherit; font-family: var(--font-mono, monospace); font-size: 0.7rem; font-weight: 700;
        letter-spacing: 0.06em; cursor: pointer; padding: 8px 16px; border-radius: 6px;
        background: var(--clr-honey, #e8a84c); color: #0f1a14; border: 1px solid var(--clr-honey, #e8a84c); }
      .ebx-dlg__btn--ghost { background: transparent; color: rgba(245,240,232,0.7); border-color: rgba(245,240,232,0.22); }
      .ebx-dlg__btn--ghost:hover { color: var(--clr-honey, #e8a84c); border-color: var(--clr-honey, #e8a84c); }
      .ebx-dlg__btn--sm { padding: 5px 11px; font-size: 0.64rem; }
      .ebx-dlg__msg { font-size: 0.8rem; line-height: 1.5; margin-top: 12px; min-height: 1em; }
      .ebx-dlg__picker { max-height: 150px; overflow: auto; border: 1px solid rgba(245,240,232,0.14);
        border-radius: 6px; padding: 8px; margin-top: 5px; }
      .ebx-dlg__picker label { display: flex; gap: 8px; align-items: center; font-family: var(--font-body, sans-serif);
        font-size: 0.82rem; letter-spacing: 0; text-transform: none; color: rgba(245,240,232,0.9);
        margin: 0; padding: 3px 0; cursor: pointer; }
      .ebx-dlg__kinds { display: flex; gap: 6px; margin-bottom: 6px; }
      .ebx-dlg__lede { font-size: 0.88rem; line-height: 1.6; color: rgba(245,240,232,0.75); margin: -4px 0 4px; }
      .ebx-dlg__hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
    `;
    document.head.appendChild(st);
  }
  function _dlgShell(id, titleHtml, bodyHtml) {
    _dlgStyles();
    let bg = document.getElementById(id);
    if (!bg) {
      bg = document.createElement("div");
      bg.id = id;
      bg.className = "ebx-dlg-bg";
      bg.addEventListener("click", (e) => { if (e.target === bg) bg.classList.remove("open"); });
      document.body.appendChild(bg);
    }
    bg.innerHTML = '<div class="ebx-dlg"><div class="ebx-dlg__title">' + titleHtml + "</div>" + bodyHtml + "</div>";
    requestAnimationFrame(() => bg.classList.add("open"));
    return bg;
  }
  var Dialogs = {
    close(id) {
      const bg = document.getElementById(id);
      if (bg) bg.classList.remove("open");
    },
    /** Contact us (2026-09-25). opts: { topic } — POST /contact. */
    contact(opts) {
      opts = opts || {};
      const topics = [["general", "General"], ["organization", "Organizations & philanthropies"],
        ["press", "Press & news"], ["problem", "Report a problem"], ["join", "Join the team"]];
      const want = topics.some((t) => t[0] === opts.topic) ? opts.topic : "general";
      const bg = _dlgShell("ebx-dlg-contact", "Contact us",
        '<p class="ebx-dlg__lede">Send a message to the Earthbux team. We reply by email.</p>' +
        '<form id="ebx-contact-form" novalidate>' +
        '<label for="ebx-contact-name">Your name *</label><input type="text" id="ebx-contact-name" maxlength="120" autocomplete="name" required />' +
        '<label for="ebx-contact-email">Your email *</label><input type="email" id="ebx-contact-email" maxlength="200" autocomplete="email" required />' +
        '<label for="ebx-contact-topic">About</label><select id="ebx-contact-topic">' +
          topics.map((t) => '<option value="' + t[0] + '"' + (t[0] === want ? " selected" : "") + ">" + t[1] + "</option>").join("") + "</select>" +
        '<label for="ebx-contact-body">Message *</label><textarea id="ebx-contact-body" maxlength="5000" required></textarea>' +
        '<div class="ebx-dlg__hp" aria-hidden="true"><label for="ebx-contact-website">Website</label><input type="text" id="ebx-contact-website" tabindex="-1" autocomplete="off" /></div>' +
        '<div class="ebx-dlg__actions"><button type="button" class="ebx-dlg__btn ebx-dlg__btn--ghost" data-act="cancel">Cancel</button>' +
        '<button type="submit" class="ebx-dlg__btn" data-act="send">Send message</button></div>' +
        '<p class="ebx-dlg__msg" id="ebx-contact-msg" role="status" aria-live="polite"></p></form>');
      const $ = (id) => bg.querySelector("#" + id);
      const msg = $("ebx-contact-msg");
      const say = (t, good) => { msg.textContent = t; msg.style.color = good ? "#8fce9d" : "#f08a6a"; };
      bg.querySelector("[data-act=cancel]").onclick = () => Dialogs.close("ebx-dlg-contact");
      $("ebx-contact-form").addEventListener("input", () => { if (msg.style.color !== "rgb(143, 206, 157)") msg.textContent = ""; });
      setTimeout(() => { const n = $("ebx-contact-name"); if (n) n.focus(); }, 60);
      $("ebx-contact-form").onsubmit = async (e) => {
        e.preventDefault();
        const name = $("ebx-contact-name").value.trim(), email = $("ebx-contact-email").value.trim();
        const body = $("ebx-contact-body").value.trim();
        if (!name) return say("Please add your name.");
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return say("Please add an email address we can reply to.");
        if (body.length < 5) return say("Please write a message.");
        const btn = bg.querySelector("[data-act=send]");
        btn.disabled = true; say("Sending…", true);
        try {
          const headers = { "Content-Type": "application/json" };
          const tok = Auth.getToken && Auth.getToken();
          if (tok) headers.Authorization = "Bearer " + tok;
          const r = await fetch((config.apiBase || "") + "/contact", {
            method: "POST", headers,
            body: JSON.stringify({ name, email, topic: $("ebx-contact-topic").value, body,
              page: location.pathname + location.search, website: $("ebx-contact-website").value }),
          });
          if (!r.ok) {
            const d = await r.json().catch(() => ({}));
            const detail = Array.isArray(d.detail) ? "Please check your email address." : (d.detail || "HTTP " + r.status);
            btn.disabled = false;
            return say("That didn't send: " + detail);
          }
          bg.querySelector(".ebx-dlg").innerHTML = '<div class="ebx-dlg__title">Thank you</div>' +
            '<p class="ebx-dlg__lede">Your message reached the Earthbux team. We&rsquo;ll reply to <b>' +
            email.replace(/[<>&"]/g, "") + "</b>.</p>" +
            '<div class="ebx-dlg__actions"><button type="button" class="ebx-dlg__btn" data-act="done">Close</button></div>';
          bg.querySelector("[data-act=done]").onclick = () => Dialogs.close("ebx-dlg-contact");
          if (location.hash === "#contact") try { history.replaceState(null, "", location.pathname + location.search); } catch (x) {}
        } catch (err) {
          btn.disabled = false;
          say("Couldn't reach the server. Please try again.");
        }
      };
      return bg;
    },
    /** P3 (2026-09-29) — a nomination may carry a post, defaulting to a
     *  Justification. It is a general post on what was nominated, so it is
     *  voted, replied to and edited like any other post. */
    async _justify(targetKind, targetId, text, tags) {
      text = (text || "").trim();
      if (!text || !targetId) return null;
      try {
        const r = await Auth.fetchAuthed("/posts", { method: "POST", body: JSON.stringify({
          id: "pj-" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
          author_type: "ben", category: "general", type: "general", body: text,
          tags: ["justification"].concat(tags || []), target_kind: targetKind, target_id: targetId }) });
        return r.ok ? await r.json() : null;
      } catch (e) { return null; }
    },
    /** Mission pass (2026-10-01) — a Mission statement: a general post tagged
     *  mission_statement on an initiative, one or two lines (≤280). */
    async _statement(tivId, text) {
      text = (text || "").trim().slice(0, 280);
      if (!text || !tivId) return null;
      try {
        const r = await Auth.fetchAuthed("/posts", { method: "POST", body: JSON.stringify({
          id: "pm-" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
          author_type: "ben", category: "general", type: "general", body: text,
          tags: ["mission_statement"], target_kind: "initiative", target_id: tivId }) });
        return r.ok ? await r.json() : null;
      } catch (e) { return null; }
    },
    _justifyField(id, what) {
      return '<label style="display:flex;gap:8px;align-items:center;"><input type="checkbox" id="' + id + '-on" checked /> ' +
        "Post a Justification with it <span style=\"opacity:0.55;font-weight:400;\">(optional — recommended)</span></label>" +
        '<textarea id="' + id + '" placeholder="Why ' + what + ' should win — what should happen, why it matters, how you would know it worked. ' +
        'It is posted as a Justification you can edit, and people can vote on it and reply."></textarea>';
    },
    /** Propose an initiative. opts: { causeId, onCreated } */
    propose(opts) {
      opts = opts || {};
      const fixed = opts.causeId || null;
      const causeField = fixed
        ? '<input type="hidden" id="ebx-dlg-cause" value="' + fixed + '" />'
        : '<label>Cause *</label><select id="ebx-dlg-cause"><option value="">Select a cause…</option>' +
          (config.causes || []).map((c) => '<option value="' + c.id + '">' + c.name + "</option>").join("") +
          "</select>";
      const cname = fixed ? ((config.causes || []).find((c) => c.id === fixed) || {}).name : null;
      const bg = _dlgShell("ebx-dlg-propose",
        "Propose an Initiative" + (cname ? ' <span style="opacity:0.5;font-size:0.8rem;">· ' + cname + "</span>" : ""),
        causeField +
        // build-seq §3 (2026-09-16): the title and the CASE are separate. "The
        // description is a case" — a short name goes in the title, the argument
        // goes below it, and the two are displayed apart everywhere.
        "<label>Title * <span style=\"opacity:0.5;font-weight:400;\">(a short name — 90 characters)</span></label><input type=\"text\" id=\"ebx-dlg-title\" maxlength=\"90\" placeholder=\"e.g. Restore kelp forests in the Pacific\" />" +
        // Mission pass (2026-10-01): "When suggesting an initiative, the inputs
        // should be a title, and the other box should be an optional 'Suggest a
        // mission statement.'" The statement is a general post tagged
        // mission_statement on the new initiative — a one- or two-liner.
        '<label for="ebx-dlg-desc">Suggest a mission statement <span style="opacity:0.55;font-weight:400;">(optional — one or two lines)</span></label>' +
        '<textarea id="ebx-dlg-desc" maxlength="280" style="min-height:60px;" placeholder="e.g. Pull 40 tonnes of ghost nets from the reefs of the Coral Triangle by next autumn."></textarea>' +
        '<div class="ebx-dlg__actions">' +
          '<button class="ebx-dlg__btn ebx-dlg__btn--ghost" data-act="cancel">Cancel</button>' +
          '<button class="ebx-dlg__btn" data-act="submit">Submit proposal</button>' +
        "</div><p class=\"ebx-dlg__msg\" id=\"ebx-dlg-msg\"></p>");
      const msg = bg.querySelector("#ebx-dlg-msg");
      bg.querySelector('[data-act=cancel]').onclick = () => Dialogs.close("ebx-dlg-propose");
      bg.querySelector('[data-act=submit]').onclick = async (ev) => {
        const causeId = (bg.querySelector("#ebx-dlg-cause").value || "").trim();
        const title = (bg.querySelector("#ebx-dlg-title").value || "").trim();
        const desc = (bg.querySelector("#ebx-dlg-desc").value || "").trim();
        if (!causeId) { msg.style.color = "#e8a84c"; msg.textContent = "Please select a cause."; return; }
        if (!title) { msg.style.color = "#e8a84c"; msg.textContent = "An initiative needs a title."; return; }
        if (!(Auth && Auth.isLoggedIn && Auth.isLoggedIn())) {
          msg.style.color = "#e8a84c";
          msg.textContent = "Please log in to propose an initiative.";
          if (Auth && Auth.openModal) Auth.openModal("login");
          return;
        }
        ev.target.setAttribute("disabled", "true");
        msg.style.color = ""; msg.textContent = "Submitting…";
        try {
          // No mission_id: the backend attaches the cause's open phase-1
          // mission itself (crud.create_tiv, §0a) — one rule, both pages.
          const res = await Auth.fetchAuthed("/initiatives", {
            method: "POST",
            body: JSON.stringify({
              id: _slugFor(title), title, description: null,
              cause_id: causeId, proposed_by: "benefactor", status: "suggested",
            }),
          });
          if (!res.ok) {
            let detail = "";
            try { detail = (await res.json()).detail || ""; } catch (e) {}
            msg.style.color = "#e07b6b";
            msg.textContent = detail ? "Couldn't submit: " + detail : "Couldn't submit (HTTP " + res.status + ").";
            return;
          }
          const created = await res.json();
          const post = await Dialogs._statement(created.id, desc);
          msg.style.color = "#5abd6c";
          msg.innerHTML = 'Proposal submitted! "' + title.replace(/[<>&"]/g, "") + '" is now in the election.' +
            (post ? " Your mission statement is posted." : Post.suggest("initiative", created.id, "it"));
          bg.querySelector("#ebx-dlg-title").value = "";
          bg.querySelector("#ebx-dlg-desc").value = "";
          if (typeof opts.onCreated === "function") { try { opts.onCreated(created); } catch (e) {} }
          if (post) setTimeout(() => Dialogs.close("ebx-dlg-propose"), 1500);
        } catch (e) {
          msg.style.color = "#e07b6b";
          msg.textContent = "Cannot reach the server. Is the API running?";
        } finally {
          ev.target.removeAttribute("disabled");
        }
      };
      return bg;
    },
    /** §1 (2026-08-21) — Nominate a cause. opts: { slot, onCreated }
     *
     * "Proposing a cause should be similar to proposing an initiative." It was
     * a name box and a colour swatch wedged into one row of the cause ballot,
     * which asked for the two things a cause is least defined by and no room
     * for the one it is most: what it is for. Same shell as `propose` above,
     * same fields, same submit-and-report behaviour — a cause is a proposal
     * like any other.
     */
    causePropose(opts) {
      opts = opts || {};
      const bg = _dlgShell("ebx-dlg-cause",
        "Nominate a Cause" +
          (opts.slot ? ' <span style="opacity:0.5;font-size:0.8rem;">· the window ' +
            opts.slot + " week" + (opts.slot === 1 ? "" : "s") + " out</span>" : ""),
        '<p style="font-size:0.82rem;line-height:1.5;color:rgba(245,240,232,0.6);margin:0 0 4px;">' +
          "A cause runs a mission every seven weeks. It should be an experience " +
          "everyone has, resistant to capture, and something a year of funded " +
          "work could actually move." +
        "</p>" +
        '<label>Name *</label><input type="text" id="ebx-dlg-cname" placeholder="e.g. Fresh Water" />' +
        '<label>What it covers *</label><textarea id="ebx-dlg-cdesc" ' +
          'placeholder="What falls under this cause, and what a mission for it would look like…"></textarea>' +
        Dialogs._justifyField("ebx-dlg-cjust", "this cause") +
        '<label>Colour</label><input type="color" id="ebx-dlg-ccolor" value="#39c0c8" ' +
          'style="width:64px;height:34px;padding:2px;cursor:pointer;" />' +
        '<div class="ebx-dlg__actions">' +
          '<button class="ebx-dlg__btn ebx-dlg__btn--ghost" data-act="cancel">Cancel</button>' +
          '<button class="ebx-dlg__btn" data-act="submit">Nominate</button>' +
        '</div><p class="ebx-dlg__msg" id="ebx-dlg-msg"></p>');
      const msg = bg.querySelector("#ebx-dlg-msg");
      bg.querySelector('[data-act=cancel]').onclick = () => Dialogs.close("ebx-dlg-cause");
      bg.querySelector('[data-act=submit]').onclick = async (ev) => {
        const name = (bg.querySelector("#ebx-dlg-cname").value || "").trim();
        const desc = (bg.querySelector("#ebx-dlg-cdesc").value || "").trim();
        const color = bg.querySelector("#ebx-dlg-ccolor").value || "#39c0c8";
        if (!name || !desc) {
          msg.style.color = "#e8a84c";
          msg.textContent = "A name and a description are required.";
          return;
        }
        if (!(Auth && Auth.isLoggedIn && Auth.isLoggedIn())) {
          msg.style.color = "#e8a84c";
          msg.textContent = "Please log in to nominate a cause.";
          if (Auth && Auth.openModal) Auth.openModal("login");
          return;
        }
        ev.target.setAttribute("disabled", "true");
        msg.style.color = ""; msg.textContent = "Submitting…";
        try {
          const res = await Auth.fetchAuthed("/causes/suggest", {
            method: "POST",
            body: JSON.stringify({ name, color, description: desc }),
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok) {
            msg.style.color = "#e07b6b";
            msg.textContent = data.detail ? "Couldn't submit: " + data.detail
                                          : "Couldn't submit (HTTP " + res.status + ").";
            return;
          }
          const cid = data && (data.id || (data.cause && data.cause.id));
          const just = bg.querySelector("#ebx-dlg-cjust-on").checked ? bg.querySelector("#ebx-dlg-cjust").value : "";
          const post = cid ? await Dialogs._justify("cause", cid, just) : null;
          msg.style.color = "#5abd6c";
          msg.innerHTML = '"' + name.replace(/[<>&"]/g, "") + '" is on the ballot.' +
            (post ? " Your Justification is posted." : (cid ? Post.suggest("cause", cid, "it") : ""));
          if (typeof opts.onCreated === "function") { try { opts.onCreated(data); } catch (e) {} }
          if (post || !cid) setTimeout(() => Dialogs.close("ebx-dlg-cause"), 1400);
        } catch (e) {
          msg.style.color = "#e07b6b";
          msg.textContent = "Cannot reach the server. Is the API running?";
        } finally {
          ev.target.removeAttribute("disabled");
        }
      };
      return bg;
    },
    /** Nominate or register an organization.
     *  opts: { causeId, tivId, missionId, onDone }
     *
     *  P3 (2026-09-29): "The organization nomination dialog loses its
     *  initiative checkboxes. The mission comes from where the dialog was
     *  opened (an initiative row's + org, the mission page), or is chosen on
     *  the organization's page." Opened with no mission, it registers the
     *  organization on its own — so one whose initiative has not been
     *  elected yet can still be put on the platform (BACKLOG). The
     *  justification is a post now, and optional. */
    orgRegister(opts) {
      opts = opts || {};
      const causeId = opts.causeId || null;
      const tivId = opts.tivId || null;
      const all = config.initiatives || [];
      const tiv = tivId ? all.find((i) => i.id === tivId) : null;
      // Mission pass (2026-10-01): "Option to attach an org to an initiative in
      // earlier phases." An initiative that has not won has no organization
      // race yet (its mission's race is for whichever initiative wins), so the
      // organization is registered on its own and SUGGESTED for the initiative
      // by a Justification tagged with it; if the initiative wins, its race
      // lists the suggestion for anyone to nominate in one click.
      const tivElected = !!(tiv && (config.missions || []).some((x) => x.winning_tiv_id === tiv.id));
      const suggestOnly = !!(tiv && !tivElected && !opts.missionId);
      const missionId = suggestOnly ? null : (opts.missionId || (tiv && tiv.mission_id) || null);
      const m = missionId ? (config.missions || []).find((x) => x.id === missionId) : null;
      const mtiv = m && m.winning_tiv_id ? all.find((i) => i.id === m.winning_tiv_id) : null;
      const forWhat = tiv ? tiv.title : (mtiv ? mtiv.title : null);
      const cname = causeId ? ((config.causes || []).find((c) => c.id === causeId) || {}).name : null;
      const bg = _dlgShell("ebx-dlg-orgreg",
        "Organization — Nominate or Register" + (cname ? ' <span style="opacity:0.5;font-size:0.8rem;">· ' + cname + "</span>" : ""),
        '<div class="ebx-dlg__kinds">' +
          '<button class="ebx-dlg__btn ebx-dlg__btn--sm" data-kind="nomination">Nominate</button>' +
          '<button class="ebx-dlg__btn ebx-dlg__btn--sm ebx-dlg__btn--ghost" data-kind="registration">Register (I\'m a member) →</button>' +
        "</div>" +
        '<p id="ebx-dlg-org-for" style="font-size:0.82rem;line-height:1.5;margin:4px 0 0;color:rgba(245,240,232,0.75);">' +
          (suggestOnly
            ? "It is suggested for <b>" + String(tiv.title || tiv.id).replace(/[<>&"]/g, "") + "</b>. If that initiative wins its election, " +
              "its organization race lists your suggestion for anyone to nominate."
            : missionId
            ? "It enters the organization race for <b>" + String(forWhat || missionId).replace(/[<>&"]/g, "") + "</b>."
            : "It is registered on Earthbux. Put it forward for a mission from that mission&rsquo;s page, or click an initiative and <b>+ Suggest an organization</b>.") +
        "</p>" +
        "<label>Organization name *</label><input type=\"text\" id=\"ebx-dlg-org-name\" placeholder=\"e.g. River Cleanup Collective\" />" +
        "<label>Website *</label><input type=\"text\" id=\"ebx-dlg-org-site\" placeholder=\"https://…\" />" +
        Dialogs._justifyField("ebx-dlg-org-just", "this organization") +
        '<div class="ebx-dlg__actions">' +
          '<button class="ebx-dlg__btn ebx-dlg__btn--ghost" data-act="cancel">Cancel</button>' +
          '<button class="ebx-dlg__btn" data-act="submit">Submit</button>' +
        "</div><p class=\"ebx-dlg__msg\" id=\"ebx-dlg-org-msg\"></p>");
      const msg = bg.querySelector("#ebx-dlg-org-msg");
      let pickedId = null, force = false;
      bg.querySelector('[data-act=cancel]').onclick = () => Dialogs.close("ebx-dlg-orgreg");
      // Registration is an ORG act and lives behind the admin door
      // (org-experience restructure 2026-07-10); nomination is a community act
      // and happens right here.
      bg.querySelector('[data-kind=registration]').onclick = () => {
        location.href = "admin.html?register=1" + (missionId ? "&mission=" + missionId : "");
      };
      bg.querySelector('[data-kind=nomination]').onclick = () => {};
      const submit = async () => {
        const name = (bg.querySelector("#ebx-dlg-org-name").value || "").trim();
        const site = (bg.querySelector("#ebx-dlg-org-site").value || "").trim();
        const just = bg.querySelector("#ebx-dlg-org-just-on").checked ? (bg.querySelector("#ebx-dlg-org-just").value || "").trim() : "";
        if (!name || !site) { msg.style.color = "#e07b6b"; msg.textContent = "A name and a website are required."; return; }
        msg.style.color = ""; msg.textContent = "Submitting…";
        if (!(Auth && Auth.isLoggedIn && Auth.isLoggedIn())) {
          try {
            const stash = JSON.parse(localStorage.getItem("ebx_org_regs") || "[]");
            stash.push({ kind: "nomination", org_name: name, website: site, justification: just,
                         mission_id: missionId, cause_id: causeId, at: Date.now() });
            localStorage.setItem("ebx_org_regs", JSON.stringify(stash));
            msg.style.color = "#5abd6c";
            msg.textContent = "✓ Saved locally — sign in to submit it for real.";
            setTimeout(() => Dialogs.close("ebx-dlg-orgreg"), 1500);
          } catch (e) { msg.style.color = "#e07b6b"; msg.textContent = "Could not save — try again."; }
          return;
        }
        try {
          const res = await Auth.fetchAuthed("/organizations/register", {
            method: "POST",
            body: JSON.stringify({
              name, website_link: site, kind: "nomination",
              mission_id: missionId, mission_statement: null,
              member_name: null, member_position: null,
              org_id: pickedId || null, force,
            }),
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok) { msg.style.color = "#e07b6b"; msg.textContent = data.detail || ("Could not submit (HTTP " + res.status + ")."); return; }
          if (!data.created && !data.org && (data.matches || []).length) {
            // "Did you mean an existing org?" — an org is never duplicated.
            msg.style.color = "";
            msg.innerHTML = "Similar organizations already exist — an org is never duplicated:<br/>" +
              data.matches.map((mt) =>
                '<button class="ebx-dlg__btn ebx-dlg__btn--ghost ebx-dlg__btn--sm" style="margin:6px 6px 0 0;" data-use="' +
                mt.org_id + '">Use “' + mt.name + "”</button>").join("") +
              '<button class="ebx-dlg__btn ebx-dlg__btn--sm" style="margin:6px 0 0 0;" data-force="1">Mine is different — create it</button>';
            msg.querySelectorAll("[data-use]").forEach((b) => {
              b.onclick = () => { pickedId = b.getAttribute("data-use"); submit(); };
            });
            const f = msg.querySelector("[data-force]");
            if (f) f.onclick = () => { force = true; submit(); };
            return;
          }
          const orgId = data.org ? data.org.id : pickedId;
          pickedId = null; force = false;
          // A suggestion needs its post — it is the link to the initiative.
          const text = just || (suggestOnly ? "Suggested to run " + (tiv.title || tiv.id) + "." : "");
          const post = await Dialogs._justify("organization", orgId, text, tivId ? ["tiv:" + tivId] : []);
          msg.style.color = "#5abd6c";
          msg.innerHTML = (suggestOnly ? "✓ Suggested for " + String(tiv.title || tiv.id).replace(/[<>&"]/g, "") + "."
            : missionId ? "✓ Nominated. It shows in this election (capped until approved)." : "✓ Registered on Earthbux.") +
            (post ? " Your Justification is posted." : Post.suggest("organization", orgId, "it"));
          if (typeof opts.onDone === "function") { try { opts.onDone(data); } catch (e) {} }
          if (post) setTimeout(() => Dialogs.close("ebx-dlg-orgreg"), 1700);
        } catch (e) {
          msg.style.color = "#e07b6b"; msg.textContent = "Could not submit — try again.";
        }
      };
      bg.querySelector('[data-act=submit]').onclick = submit;
      return bg;
    },
  };

  // ── Slug — every mission's readable URL (build-seq P1, 2026-09-24, D1) ──
  // "Use the initiative title. This way the mission page will be identifiable
  // as a link to someone who is not familiar with earthbux."
  //   /m/<initiative-title-slug>   an initiative's mission page — won or not.
  //                                Once it wins it IS the mission's address.
  //   /m/<mission-id>              a mission before any initiative is elected
  //   /m                           the mission page's default
  // Uniqueness: initiatives are ordered by (proposed_at, id); the first to
  // take a slug keeps it, later ones get -2, -3… A slug may never look like a
  // mission id (three letters + digits).
  // D13 (2026-09-24): the slugs are STORED (`initiative_slugs`, written by the
  // server with this same rule) and keep their history — "old titles of the
  // initiative should also link to the new title". `Slug.load()` reads them;
  // until it has, or for an initiative the server has not seen, the rule
  // below derives the same answer.
  var Slug = /* @__PURE__ */ (() => {
    let _t = null, _stored = null;
    async function load() {
      try {
        const r = await fetch("/initiatives/slugs");
        if (r.ok) { _stored = await r.json(); _t = null; }
      } catch (e) {}
      return _stored;
    }
    function slugify(title) {
      const s = String(title || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
        .replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80).replace(/-+$/, "");
      return s || "initiative";
    }
    function table() {
      const list = (config.initiatives || []);
      if (_t && _t.n === list.length) return _t;
      const bySlug = {}, byTiv = {};
      (_stored || []).forEach((r) => { bySlug[r.slug] = r.tiv_id; if (r.current) byTiv[r.tiv_id] = r.slug; });
      list.slice().sort((a, b) => String(a.proposed_at || "").localeCompare(String(b.proposed_at || "")) ||
        String(a.id).localeCompare(String(b.id))).forEach((i) => {
        if (byTiv[i.id]) return;              // stored — the server's answer wins
        const base = slugify(i.title);
        let s = base, k = 2;
        while (bySlug[s] || /^[a-z]{3}\d+$/.test(s)) s = base + "-" + k++;
        bySlug[s] = i.id; byTiv[i.id] = s;
      });
      return _t = { n: list.length, bySlug, byTiv };
    }
    function of(tivId) { return table().byTiv[tivId] || null; }
    function tivFor(slug) { return table().bySlug[String(slug || "").toLowerCase()] || null; }
    // The href for a mission (object or id), optionally for one of its initiatives.
    function href(m, tivId) {
      const mid = m && typeof m === "object" ? m.id : m;
      const mo = m && typeof m === "object" ? m : (config.missions || []).find((x) => x.id === mid);
      const t = tivId || (mo && mo.winning_tiv_id) || null;
      const s = t ? of(t) : null;
      if (s) return "/m/" + s;
      return mid ? "/m/" + mid : "/m";
    }
    return { slugify, of, tivFor, href, load };
  })();

  // ══ P3 · POSTING (2026-09-29) — EBX.Post ════════════════════════════════
  // "One way to make a post, reachable from everywhere … every post
  // displayable by every page on the platform." (INSTRUCTIONS › P3.)
  //
  //   EBX.Post.guide()                 the taxonomy + each type's guide (GET /posts/guide)
  //   EBX.Post.composeUrl(opts)        post.html with the target and type preselected
  //   EBX.Post.collapsed(p, opts)      the collapsed view — who · when · kind, excerpt, ↑ n ↩ n
  //   EBX.Post.full(detail, replies)   the full view — contents, References, votes, replies
  //   EBX.Post.open(id, opts)          the full view in a dialog, with vote + reply
  //   EBX.Post.preview(el, query)      a short preview of a discussion (an initiative's or
  //                                    an organization's row), best justification first
  //   EBX.Post.suggest(kind, id, lab)  "Make a post about it" — after a nomination
  //
  // Both views say what the post targets (P3 › Display). The CSS is injected
  // once, so every page that loads this file can show a post.
  const Post = (() => {
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const TYPE = { general: "Post", context: "Background", investigation: "Investigation", analysis: "Analysis",
      service: "Service", supply: "Supply", support: "Support" };
    const CAT_WORD = { editorial: "News", headline: "News", mission_update: "Mission update",
      org_update: "Organization update", testimonial: "Testimonial", resolution: "Resolved" };
    const TARGET_WORD = { cause: "cause", initiative: "initiative", organization: "organization",
      mission: "mission", post: "post", budget: "budget item" };
    let _guide = null;

    function css() {
      if (document.getElementById("ebx-post-css")) return;
      const s = document.createElement("style");
      s.id = "ebx-post-css";
      s.textContent = `
      .ep { display:block; text-decoration:none; color:var(--clr-parchment,#f5f0e8); border:1px solid rgba(245,240,232,0.12);
        border-radius:12px; padding:12px 14px; background:rgba(245,240,232,0.03); }
      a.ep:hover, .ep--click:hover { border-color:rgba(232,168,76,0.55); cursor:pointer; }
      .ep__meta { display:flex; flex-wrap:wrap; gap:6px; align-items:baseline; font-size:0.74rem; color:rgba(245,240,232,0.6); }
      .ep__who { color:var(--clr-parchment,#f5f0e8); font-weight:600; }
      .ep__kind { font-family:var(--font-mono,monospace); font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase;
        color:var(--clr-honey,#e8a84c); }
      .ep__tag { font-size:0.66rem; padding:1px 7px; border-radius:999px; border:1px solid rgba(245,240,232,0.18); color:rgba(245,240,232,0.7); }
      .ep__target { font-size:0.74rem; color:rgba(245,240,232,0.72); margin-top:4px; }
      .ep__target a { color:var(--clr-honey,#e8a84c); text-decoration:none; }
      .ep__title { font-family:var(--font-display,serif); font-weight:800; font-size:1rem; margin:6px 0 2px; }
      .ep__body { font-size:0.86rem; line-height:1.55; color:rgba(245,240,232,0.82); margin:4px 0 0; white-space:pre-wrap; }
      .ep__img { max-width:100%; border-radius:10px; margin-top:8px; display:block; }
      .ep__foot { display:flex; gap:14px; justify-content:flex-end; font-size:0.78rem; color:rgba(245,240,232,0.7); margin-top:8px; }
      .ep__ver { font-size:0.68rem; color:rgba(245,240,232,0.5); }
      .ep-full__refs { margin-top:14px; border-top:1px solid rgba(245,240,232,0.12); padding-top:10px; }
      .ep-full__h { font-family:var(--font-mono,monospace); font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase;
        color:rgba(245,240,232,0.55); margin:0 0 6px; }
      .ep-full__refs ul { margin:0; padding-left:18px; font-size:0.84rem; line-height:1.6; }
      .ep-full__refs a { color:var(--clr-honey,#e8a84c); }
      .ep-full__votes { display:flex; gap:8px; align-items:center; margin-top:14px; border-top:1px solid rgba(245,240,232,0.12); padding-top:10px; flex-wrap:wrap; }
      .ep-vote { font:inherit; font-size:0.8rem; cursor:pointer; padding:5px 12px; border-radius:999px; background:none;
        color:rgba(245,240,232,0.85); border:1px solid rgba(245,240,232,0.22); }
      .ep-vote:hover { border-color:var(--clr-honey,#e8a84c); }
      .ep-full__replies { margin-top:12px; display:flex; flex-direction:column; gap:8px; }
      .ep-reply { border-left:2px solid rgba(245,240,232,0.14); padding:4px 0 4px 10px; font-size:0.84rem; }
      .ep-reply b { font-size:0.76rem; }
      .ep-dlg { position:fixed; inset:0; z-index:95; background:rgba(5,10,8,0.74); display:flex; align-items:center; justify-content:center; padding:3vh 3vw; }
      .ep-dlg__card { width:min(760px,100%); max-height:100%; overflow-y:auto; background:#13211a; color:var(--clr-parchment,#f5f0e8);
        border:1px solid rgba(245,240,232,0.16); border-radius:16px; padding:18px 22px; box-shadow:0 30px 80px rgba(0,0,0,0.55); }
      .ep-dlg__x { float:right; font:inherit; font-size:1.5rem; line-height:1; background:none; border:0; color:rgba(245,240,232,0.6); cursor:pointer; }
      .ep-dlg__reply { display:flex; gap:8px; margin-top:10px; }
      .ep-dlg__reply textarea { flex:1; font:inherit; color:inherit; background:rgba(0,0,0,0.25); border:1px solid rgba(245,240,232,0.16); border-radius:10px; padding:8px 10px; min-height:54px; }
      .ep-btn { font:inherit; font-weight:700; font-size:0.82rem; cursor:pointer; padding:8px 16px; border-radius:999px; background:var(--clr-honey,#e8a84c); color:#0f1a14; border:0; text-decoration:none; display:inline-block; }
      .ep-btn--ghost { background:none; color:rgba(245,240,232,0.8); border:1px solid rgba(245,240,232,0.22); }
      .ep-msg { font-size:0.8rem; margin-top:6px; }
      .ep-prev { font-size:0.8rem; line-height:1.5; color:rgba(245,240,232,0.78); border-left:2px solid var(--clr-honey,#e8a84c); padding:4px 0 4px 10px; margin:6px 0; }
      .ep-prev a { color:var(--clr-honey,#e8a84c); text-decoration:none; }
      .ep-suggest { margin-top:8px; font-size:0.82rem; }
      .ep-suggest a { color:var(--clr-honey,#e8a84c); font-weight:700; }
      `;
      document.head.appendChild(s);
    }

    async function guide() {
      if (_guide) return _guide;
      try {
        const r = await fetch((config.apiBase || "") + "/posts/guide");
        if (r.ok) _guide = await r.json();
      } catch (e) {}
      return _guide || { types: [], categories: [], general_tags: [], votes: [] };
    }

    // post.html?type=…&cause=…&initiative=…&org=…&mission=…&post=…&budget=…&tag=…&back=…
    function composeUrl(opts) {
      opts = opts || {};
      const q = new URLSearchParams();
      ["type", "cause", "initiative", "org", "mission", "post", "budget", "tag", "edit"].forEach((k) => {
        if (opts[k]) q.set(k, opts[k]);
      });
      const back = opts.back === undefined ? (location.pathname + location.search) : opts.back;
      if (back) q.set("back", back);
      const s = q.toString();
      return "post.html" + (s ? "?" + s : "");
    }

    function kind(p) {
      if (p.type && TYPE[p.type] && p.type !== "general") return TYPE[p.type];
      const tag = (p.tags || []).find((t) => t.indexOf(":") < 0);
      if (tag) return (tag.charAt(0).toUpperCase() + tag.slice(1)).replace(/_/g, " ");
      return CAT_WORD[p.category] || "Post";
    }
    function when(iso) {
      const d = new Date(iso);
      return isNaN(d) ? "" : d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    }
    function missionHref(id) {
      try { if (Slug && Slug.href) return Slug.href(id); } catch (e) {}
      return "/m/" + encodeURIComponent(id);
    }
    function threadHref(id) { return "cause.html?thread=" + encodeURIComponent(id); }
    function targetHref(p) {
      const k = p.target_kind, id = p.target_id;
      if (!id) return null;
      if (k === "mission") return missionHref(id);
      if (k === "initiative") return p.mission_id ? missionHref(p.mission_id) : null;
      if (k === "organization") return "mission.html?org=" + encodeURIComponent(id);
      if (k === "cause") return "cause.html?cause=" + encodeURIComponent(id);
      if (k === "post" || k === "budget") return threadHref(id);
      return null;
    }
    // "Both views must clearly display what mission, org, or initiative the
    // post targets (if any)."
    function targetLine(p) {
      if (!p.target_kind || p.target_kind === "none" || !p.target_id) return "";
      const lab = p.target_label || p.target_id;
      const href = targetHref(p);
      const inResp = (p.tags || []).indexOf("response") >= 0 && p.target_kind === "post";
      const word = p.parent_id ? "Reply to" : inResp ? "In response to" : "On the " + TARGET_WORD[p.target_kind] || "On";
      return '<div class="ep__target">' + word + " " +
        (href ? '<a href="' + esc(href) + '">' + esc(lab) + "</a>" : "<b>" + esc(lab) + "</b>") +
        (p.mission_id && p.target_kind !== "mission" && p.mission_label && p.target_kind !== "initiative"
          ? ' &middot; <a href="' + esc(missionHref(p.mission_id)) + '">' + esc(p.mission_label) + "</a>" : "") +
        "</div>";
    }
    function tagsHTML(p) {
      const words = (p.tags || []).filter((t) => t.indexOf(":") < 0);
      const first = words[0];
      return words.filter((t) => !(p.type === "general" && t === first))
        .map((t) => '<span class="ep__tag">' + esc(t) + "</span>").join("");
    }
    function votes(p) { return (p.helpful_count || 0) - (p.harmful_count || 0); }

    // Collapsed: "Jax · Sep 29 · Opinion", the excerpt, "↑ 37  ↩ 12".
    function collapsed(p, opts) {
      css();
      opts = opts || {};
      const body = String(p.body || "");
      const cut = opts.chars || 280;
      const tagName = opts.href === false ? "div" : "a";
      const href = opts.href === false ? "" : ' href="' + esc(opts.href || threadHref(p.id)) + '"';
      return "<" + tagName + ' class="ep' + (opts.click ? " ep--click" : "") + '"' + href + ' data-post="' + esc(p.id) + '">' +
        '<div class="ep__meta"><span class="ep__who">' + esc(p.author_name || "Benefactor") + "</span>" +
          "<span>&middot; " + when(p.created_at) + '</span><span>&middot;</span><span class="ep__kind">' + esc(kind(p)) + "</span>" +
          tagsHTML(p) + (p.version > 1 ? '<span class="ep__ver">v' + (p.version_shown || p.version) + "</span>" : "") + "</div>" +
        targetLine(p) +
        (p.title ? '<div class="ep__title">' + esc(p.title) + "</div>" : "") +
        '<p class="ep__body">' + esc(body.length > cut ? body.slice(0, cut).trim() + "…" : body) + "</p>" +
        '<div class="ep__foot"><span title="' + esc(p.vote_name || "Votes") + '">&uarr; ' + votes(p) + "</span>" +
          "<span title=\"Replies\">&#8617; " + (p.reply_count || 0) + "</span></div>" +
        "</" + tagName + ">";
    }

    function refItem(r) {
      if (r.kind === "link") return '<li><a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.label || r.url) + "</a></li>";
      if (r.kind === "mission") return '<li>Mission <a href="' + esc(missionHref(r.mission_id)) + '">' + esc(r.mission_id) + "</a></li>";
      const name = TYPE[r.type] || "Post";
      return '<li>' + esc(name) + ' &middot; <a href="' + esc(threadHref(r.post_id)) + '">' + esc(r.title || r.post_id) + "</a>" +
        (r.auto ? ' <span class="ep__tag" title="Attached to every Analysis of this mission">leading</span>' : "") +
        (r.changed ? ' <span class="ep__ver">cited v' + r.cited_version + ' &middot; now v' + r.latest_version + "</span>" : "") + "</li>";
    }

    // Full: the contents, References, the votes, then the replies.
    function full(d, replies, opts) {
      css();
      opts = opts || {};
      const refs = d.references || [];
      const voteBtns = (opts.reactions || [["helpful", "Upvote"]]).map(([v, lab]) =>
        '<button type="button" class="ep-vote" data-vote="' + v + '">' + esc(lab) + "</button>").join("");
      const mission = d.mission_id
        ? '<a class="ep-btn ep-btn--ghost" href="' + esc(missionHref(d.mission_id)) + '">Go to ' + esc(d.mission_label || "the mission") + " &rarr;</a>" : "";
      const edit = opts.mine ? '<a class="ep-btn ep-btn--ghost" href="' + esc(composeUrl({ edit: d.id })) + '">Edit (new version)</a>' : "";
      return '<div class="ep-full" data-post="' + esc(d.id) + '">' +
        '<div class="ep__meta"><span class="ep__who">' + esc(d.author_name || "Benefactor") + "</span>" +
          "<span>&middot; " + when(d.created_at) + '</span><span>&middot;</span><span class="ep__kind">' + esc(kind(d)) + "</span>" +
          tagsHTML(d) + (d.latest_version > 1 ? '<span class="ep__ver">version ' + (d.version_shown || d.version) + " of " + d.latest_version + "</span>" : "") + "</div>" +
        targetLine(d) +
        (d.title ? '<h2 class="ep__title" style="font-size:1.3rem;">' + esc(d.title) + "</h2>" : "") +
        (d.image_url ? '<img class="ep__img" src="' + esc(d.image_url) + '" alt="" />' : "") +
        '<p class="ep__body">' + esc(d.body || "") + "</p>" +
        (refs.length ? '<div class="ep-full__refs"><p class="ep-full__h">References</p><ul>' + refs.map(refItem).join("") + "</ul></div>" : "") +
        '<div class="ep-full__votes"><b title="' + esc(d.vote_name || "") + '">&uarr; ' + votes(d) + " " + esc(d.vote_name || "votes") + (Math.abs(votes(d)) === 1 ? "" : "s") + "</b>" +
          voteBtns + '<span style="flex:1"></span>' + edit + mission + "</div>" +
        '<p class="ep-full__h" style="margin-top:14px;">' + (replies || []).length + " repl" + ((replies || []).length === 1 ? "y" : "ies") + "</p>" +
        '<div class="ep-full__replies">' + (replies || []).map((r) =>
          '<div class="ep-reply"><b>' + esc(r.author_name || "Benefactor") + "</b> <span class=\"ep__ver\">&middot; " + when(r.created_at) + "</span>" +
          '<div class="ep__body">' + esc(r.body || "") + "</div></div>").join("") + "</div>" +
        "</div>";
    }

    async function open(id, opts) {
      css();
      opts = opts || {};
      const ctx = opts.mission ? "?mission_id=" + encodeURIComponent(opts.mission) : "";
      const [dr, rr, g] = await Promise.all([
        fetch((config.apiBase || "") + "/posts/" + encodeURIComponent(id) + ctx),
        fetch((config.apiBase || "") + "/posts/" + encodeURIComponent(id) + "/comments"),
        guide(),
      ]);
      if (!dr.ok) return null;
      const d = await dr.json();
      const replies = rr.ok ? await rr.json() : [];
      const t = (g.types || []).find((x) => x.key === d.type);
      const reactions = t ? t.reactions.map((r) => [r.value, r.label]) : [["helpful", "Upvote"]];
      let me = null;
      try { me = Auth.isLoggedIn() ? await Auth.fetchMe() : null; } catch (e) {}
      document.getElementById("ep-dlg")?.remove();
      const bg = document.createElement("div");
      bg.className = "ep-dlg"; bg.id = "ep-dlg";
      bg.innerHTML = '<div class="ep-dlg__card" role="dialog" aria-modal="true"><button type="button" class="ep-dlg__x" aria-label="Close">&times;</button>' +
        full(d, replies, { reactions, mine: me && me.id === d.ben_author_id }) +
        '<div class="ep-dlg__reply"><textarea id="ep-reply-in" placeholder="Write a reply…"></textarea>' +
        '<button type="button" class="ep-btn" id="ep-reply-send">Reply</button></div><div class="ep-msg" id="ep-msg"></div></div>';
      document.body.appendChild(bg);
      const close = () => bg.remove();
      bg.querySelector(".ep-dlg__x").onclick = close;
      bg.addEventListener("click", (e) => { if (e.target === bg) close(); });
      const msg = bg.querySelector("#ep-msg");
      const say = (s, good) => { msg.textContent = s; msg.style.color = good ? "#8fce9d" : "#f08a6a"; };
      bg.querySelectorAll("[data-vote]").forEach((b) => b.onclick = async () => {
        if (!Auth.isLoggedIn()) return Auth.openModal("login");
        const r = await Auth.fetchAuthed("/posts/" + encodeURIComponent(id) + "/react", { method: "POST",
          body: JSON.stringify({ value: b.dataset.vote, mission_id: opts.mission || null }) });
        const out = await r.json().catch(() => ({}));
        if (!r.ok) return say(out.detail || "Refused.");
        say("Counted.", true);
        if (opts.onChange) try { opts.onChange(out); } catch (e) {}
        setTimeout(() => open(id, opts), 300);
      });
      bg.querySelector("#ep-reply-send").onclick = async () => {
        if (!Auth.isLoggedIn()) return Auth.openModal("login");
        const body = bg.querySelector("#ep-reply-in").value.trim();
        if (!body) return say("Write something first.");
        const r = await Auth.fetchAuthed("/posts", { method: "POST", body: JSON.stringify({
          id: "rp-" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
          body, author_type: "ben", parent_id: id, category: d.category, type: d.type }) });
        const out = await r.json().catch(() => ({}));
        if (!r.ok) return say(out.detail || "Refused.");
        if (opts.onChange) try { opts.onChange(out); } catch (e) {}
        open(id, opts);
      };
      return bg;
    }

    // A short preview of a discussion — for an initiative's or an
    // organization's row. "A highly rated justification if available, or
    // anything relevant. It should not show too much text."
    async function preview(el, q, opts) {
      opts = opts || {};
      css();
      if (!el) return;
      const params = new URLSearchParams(Object.assign({ roots_only: "true", sort: "hot", limit: "20" }, q || {}));
      let rows = [];
      try { const r = await fetch((config.apiBase || "") + "/posts?" + params); rows = r.ok ? await r.json() : []; } catch (e) {}
      const score = (p) => (["justification", "case", "mission_statement"].some((t) => (p.tags || []).indexOf(t) >= 0) ? 1000 : 0) + votes(p);
      const best = rows.slice().sort((a, b) => score(b) - score(a))[0];
      const target = q.tiv_id ? { initiative: q.tiv_id } : q.org_id ? { org: q.org_id } : {};
      // opts.noWrite: the caller draws its own post button (the mission ballot's expansion)
      const write = opts.noWrite ? "" : '<a href="' + esc(composeUrl(Object.assign({ tag: "justification" }, target))) + '">Post about it</a>';
      el.innerHTML = best
        ? '<div class="ep-prev">' + '<span class="ep__kind">' + esc(kind(best)) + "</span> " +
            esc((best.title ? best.title + " — " : "") + String(best.body || "").slice(0, 160)) + (String(best.body || "").length > 160 ? "…" : "") +
            ' <span class="ep__ver">&uarr; ' + votes(best) + "</span>" +
            '<br/><a href="#" data-ep-open="' + esc(best.id) + '">Read</a> &middot; ' + rows.length + " post" + (rows.length === 1 ? "" : "s") + (write ? " &middot; " + write : "") + "</div>"
        : '<div class="ep-prev">No discussion yet' + (write ? " &middot; " + write : "") + "</div>";
      el.querySelectorAll("[data-ep-open]").forEach((a) => a.onclick = (e) => { e.preventDefault(); e.stopPropagation(); open(a.dataset.epOpen); });
    }

    // "New budget items, new initiatives and new organizations strongly
    // suggest posting."
    function suggest(targetKind, id, label) {
      css();
      const key = { initiative: "initiative", organization: "org", cause: "cause", budget: "budget", mission: "mission" }[targetKind] || targetKind;
      return '<div class="ep-suggest">Now make the case: <a href="' +
        esc(composeUrl({ [key]: id, tag: "justification" })) + '">post a Justification for ' + esc(label || "it") + " &rarr;</a></div>";
    }

    return { guide, composeUrl, kind, collapsed, full, open, preview, suggest, targetLine, css, threadHref, missionHref };
  })();

  var EBX = {
    config,
    Slug,
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
    initNav,
    navTabs,
    getParam,
    buildURL,
    $,
    $$,
    render,
    renderSkeleton,
    renderEmpty,
    formatNumber,
    formatEBX,
    formatTokens,
    formatTokenUSD,
    USD_PER_TOKEN,
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
    Dialogs,
    openP1Mission,
    Post,
    Auth
  };
  window.EBX = EBX;
  document.addEventListener("DOMContentLoaded", () => {
    EBX.initPage();
  });
  var ebx_shared_default = EBX;
})();
