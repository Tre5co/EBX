"use strict";
/* ebx_wheel.js — THE PHASE WHEEL. The mission page's annulus, and the data layer
 * Home's mission hub reads (2026-09-30: no longer drawn on Home).
 *
 * build-seq §2–§4 (2026-09-18):
 *   §2  "Replace how it works section with: 1. Confirm Cause 2. Elect
 *        Initiative 3. Elect Philanthropy 4. Frame Mission 5. Exchange
 *        Resources — they will operate as toggles. No dates or descriptions."
 *   §3  "A new Top Card that functions as a detailed description of what is
 *        being elected and why. It toggles with the how it works elements."
 *   §4  "Move the annulus and the 6 side cards to below the new top card from
 *        Election. The centre of the annulus should be the globe: inner to
 *        outer, globe -> pie chart -> sectors with rotating now indicator."
 *        Card : pie, per phase —
 *          Cause      incumbent, or the bars for a replacement : this week's votes
 *          Initiative (as the election page)                   : token share
 *          Org        (as the election page)                   : vote share
 *          Framing    7-week checklist                          : (not specified — the 32nds)
 *          Exchange   leading coins from the cause              : (backlog — pool share for now)
 *
 * Self-contained: it reads the public API (no sign-in needed) and paints into
 * ONE mount. It depends on `EBX` (ebx_shared.js) for causes, missions and the
 * mission clock, and on d3-geo + the vendored Natural Earth land for the globe;
 * if d3 is missing the globe falls back to graticule-only and nothing else
 * changes. Nothing here writes — every card links to the Elect page, where the
 * decision is executed.
 *
 *   EBX.Wheel.mount('#ebx-wheel', { step: 'tiv' })
 *
 * build-seq P1 (2026-09-24) — ONE COMPONENT, TWO VARIANTS. The landing page
 * mounts the default variant (five step toggles, the top card, six side
 * cards). The mission page mounts `{ variant: 'mission' }`: the ring, the pie
 * and the globe only. The page owns the two side columns (the mission toggler
 * on the left, the overview on the right) and drives the wheel with
 * `EBX.Wheel.show({ step, cause, mission })`; a click on a sector is handed to
 * `opts.onFocus(causeId)` instead of refocusing in place, because on the
 * mission page choosing a cause is choosing a mission (D4). `mission` PINS the
 * race the pie reads, so the pie is the selected mission's election rather
 * than whichever race of that cause the clock would pick.
 */
(function () {
  if (!window.EBX) return;
  const E = window.EBX;
  const WK = 7 * 864e5;
  const TAU = Math.PI * 2;

  // ── the five steps ─────────────────────────────────────────────────────
  // `half` puts each step under the heading the landing page already owned:
  // the three elections are donor control, the two after are public impact.
  const STEPS = [
    { key: 'cause', n: 1, label: 'Confirm Cause', half: 'you', elect: 'ce' },
    { key: 'tiv', n: 2, label: 'Elect Initiative', half: 'you', elect: 'me' },
    { key: 'org', n: 3, label: 'Elect Philanthropy', half: 'you', elect: 'oe' },
    { key: 'frame', n: 4, label: 'Mission Prep', half: 'us', elect: 'fr' },   // 10/9 Reshuffle: Framing → Prep
    { key: 'ex', n: 5, label: 'Exchange Resources', half: 'us', elect: 'ex' },
  ];

  // 2026-09-30 (P2 · Home mods): Home no longer mounts this component — its
  // phase rows became the five steps (ebx_steps.js) and the mission hub. Each
  // PHASE blurb below is now the line under its ballot's header on the mission
  // page (mission.html `renderBallotHeads`, #el3-blurb-*). The landing variant
  // (`shell`, the top card, the side cards, the span) is mounted by nothing but
  // scripts/wheel_check.js — REMOVAL REGISTER › Added 2026-09-30.
  // build-seq P2 (2026-09-25) — HOME'S TWO ROWS. The landing variant no longer
  // prints the five toggles and a Process/Reason card: those two paragraphs
  // moved to the mission page's phase panels (review 2). Home draws the five
  // phases as two rows of cards — deciding the mission, then planning it — each
  // with its title, one line from the live earthbux.net step cards (the cause
  // line is new: the live site has no cause step), and two actions: show it
  // here, or go and vote. `label` above stays as the mission page reads it.
  const PHASE = {
    cause: { title: 'Cause Election', blurb: 'Keep this week&rsquo;s cause, or back a challenger. It takes a majority six weeks in a row to replace one.', go: 'Vote' },
    tiv: { title: 'Initiative Election', blurb: 'Donate to this week&rsquo;s cause by funding what you want the mission to be.', go: 'Vote' },
    org: { title: 'Organization Election', blurb: 'After the mission is decided, your tokens can be put towards its philanthropy.', go: 'Vote' },
    // 10/9 Reshuffle (2026-10-09): "Framing needs to be switched to 'Prep'."
    frame: { title: 'Mission Prep', blurb: 'Earthbux orients the organization and its benefactors <b>(you)</b>, and the community builds the budget.', go: 'Prep' },
    ex: { title: 'Exchange', blurb: 'Hold on, or exchange for a different mission. Our newsroom keeps you updated.', go: 'Trade' },
  };
  const ROWS = [
    { key: 'decide', title: 'Deciding the mission', steps: ['cause', 'tiv', 'org'] },
    { key: 'plan', title: 'Planning, feedback and accountability', steps: ['frame', 'ex'] },
  ];

  // The top card's copy — WHAT is being decided and WHY — one per step. Taken
  // from README §3–§5 and docs/mission_model.md; the live line under it is
  // computed.
  // The top card's copy. build-seq §1 Landing (2026-09-20) fixes the four
  // fields and their order:
  //   a DATES  — the kicker. It does not say "step" and does not repeat b.
  //   b TITLE  — the five descriptions the Elect page used to carry as its
  //              step toggles (removed there this pass, §2).
  //   c PROCESS — what actually happens.
  //   d REASON  — why it is done that way.
  // Text is Jax's, verbatim from the instruction.
  const COPY = {
    cause: {
      kicker: '7–14 weeks before week 0',
      title: 'First, the cause is determined',
      what: 'If more than 50% of the vote is for the same cause <b>6 weeks in a row</b>, it becomes the cause for the next round of initiatives.',
      why: 'Causes must be simple and should be resistant to change. A good cause is <em>ubiquitously essential to the wellbeing of earth</em> &mdash; something that every human would hope to improve.',
    },
    tiv: {
      kicker: 'Week 0',
      title: 'Next, a mission is elected within it',
      what: 'Initiatives within the cause are nominated and elected by the community. <b>The pool goes to the winner.</b>',
      why: 'A broad cause needs specific, achievable initiatives that are solvable with limited resources. The initiative <em>is</em> the mission.',
    },
    org: {
      kicker: 'Week 8',
      title: 'After, an organization is elected to run it',
      what: 'Philanthropies are nominated and elected by the community to accomplish the initiative. <b>The pool goes to the winner.</b>',
      why: 'When a concrete objective has already been articulated, donors can be more equipped to determine which group they fund.',
    },
    frame: {
      kicker: 'Week 15',
      title: 'All parties verify their intent',
      what: 'Earthbux newsroom ensures that the philanthropy is equipped to accomplish the initiative, working with the community to construct a budget.',
      why: 'Everyone must be absolutely certain that Earthbux and the winning organization can be trusted before sending them any money.',
    },
    ex: {
      kicker: 'Until the money runs out',
      title: 'Earthbux Exchange',
      what: 'If the budget is approved, the mission&rsquo;s EBX becomes tradeable on our exchange. Our journalists, scientists, and community keep you updated.',
      why: 'Donors need a real-time report of their impact, and the ability to redirect it when circumstances change.',
    },
  };

  // Stable points on the sphere, one per cause — the same anchors as
  // profile.html's globe. Missions carry no coordinates yet (INSTRUCTIONS Open
  // Questions); when they do, only `anchorFor` changes.
  const CAUSE_ANCHOR = {
    'atmosphere': [38, -20], 'oceans': [-10, -150], 'land': [10, 25],
    'forests': [-5, -60], 'wildlife': [-20, 30], 'human-rights': [45, 10],
    'human-progress': [20, 80],
  };

  // ── helpers ───────────────────────────────────────────────────────────
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = d => d ? d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—';
  const daysTo = d => d ? Math.max(0, Math.ceil((d.getTime() - Date.now()) / 864e5)) : 0;
  const pct = (a, b) => b > 0 ? Math.round(a / b * 100) : 0;
  const tk = n => {
    const v = Number(n) || 0;
    return (Math.abs(v - Math.round(v)) < 0.05 ? Math.round(v) : v.toFixed(1)) + ' tk';
  };
  const causes = () => (E.config.causes || []).slice().sort((a, b) => a.index - b.index);
  const causeAt = i => causes().find(c => c.index === ((i % 7) + 7) % 7) || null;
  const causeById = id => causes().find(c => c.id === id) || null;
  const tivById = id => (E.config.initiatives || []).find(i => i.id === id) || null;
  const orgName = id => {
    const o = (E.config.organizations || []).find(x => x.id === id);
    return o ? o.name : (id || '—');
  };
  const tivName = id => {
    const t = tivById(id);
    return t ? ((t.emoji ? t.emoji + ' ' : '') + t.title) : (id || '—');
  };
  const dates = m => E.Cycle.missionDates(m);
  // T+15: budget day (money_model §0). missionDates carries T and T+8 only.
  const budgetDay = m => new Date(dates(m).missionStarted.getTime() + 15 * WK);
  const missionsOf = cid => (E.config.missions || []).filter(m => m.cause_id === cid);
  const byCycle = (a, b) => (a.cycle_num || 0) - (b.cycle_num || 0);

  // The five questions a cause can be asked, answered from the missions alone.
  // These are the same definitions main.html uses (`_p1MissionForCause`,
  // `_finalizingMission`), restated so this file stands alone.
  function meMission(cid) {
    return missionsOf(cid).filter(m => !m.winning_tiv_id && ['pre', 'initiative'].includes(m.current_phase))
      .sort(byCycle)[0] || null;
  }
  function oeMission(cid) {
    return missionsOf(cid).filter(m => m.winning_tiv_id && !m.winning_org_id).sort(byCycle)[0] || null;
  }
  function framingMissions(cid) {
    const now = Date.now();
    return missionsOf(cid).filter(m => m.winning_org_id && now < budgetDay(m).getTime()).sort(byCycle);
  }
  function exchangeMissions(cid) {
    const now = Date.now();
    return missionsOf(cid).filter(m => m.winning_org_id && now >= budgetDay(m).getTime()).sort(byCycle);
  }
  function meCandidates(cid) {
    const m = meMission(cid);
    return (E.config.initiatives || []).filter(i => i.cause_id === cid &&
      ['suggested', 'debate'].includes(i.status || 'suggested') &&
      (!m || !i.mission_id || i.mission_id === m.id))
      .sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0));
  }

  // ── state ─────────────────────────────────────────────────────────────
  const S = {
    step: 'tiv', focus: null, root: null,
    slate: null, ballots: {}, p2: {}, cands: {}, claims: {},
    // build-seq §1 Landing (2026-09-20) — what I voted for, so the side cards
    // can highlight it. Empty for a signed-out reader, and the cards paint the
    // same either way.
    mine: { tivs: {}, orgs: {}, cause: null },
    globe: { lon: 0, target: 0, lat: -18, raf: 0, last: 0, visible: true },
    // build-seq P1 (2026-09-24): 'landing' | 'mission', the pinned mission and
    // the page's sector handler (mission variant only).
    variant: 'landing', pin: null, onFocus: null,
  };
  // The pinned mission, when it is the race this step asks about for this cause.
  function pinFor(step, c) {
    const m = S.pin;
    if (!m || !c || m.cause_id !== c.id) return null;
    if (step === 'tiv') return !m.winning_tiv_id ? m : null;
    if (step === 'org') return (m.winning_tiv_id && !m.winning_org_id) ? m : null;
    if (step === 'frame') return (m.winning_org_id && Date.now() < budgetDay(m).getTime()) ? m : null;
    return null;
  }

  async function j(url) {
    try { const r = await fetch(url); return r.ok ? await r.json() : null; } catch (e) { return null; }
  }

  // One load per page, shared by the landing wheel and the Elect page's
  // framing / exchange views (main.html build-seq §6).
  let _loading = null;
  function data() { return _loading || (_loading = load()); }
  async function load() {
    if (!(E.config.causes || []).length) await E.loadCauses();
    await Promise.all([
      (E.config.missions || []).length ? null : E.loadMissions(),
      (E.config.initiatives || []).length ? null : E.loadInitiatives(),
      (E.config.organizations || []).length ? null : E.loadOrganizations(),
    ]);
    const [slate, cands] = await Promise.all([j('/causes/slate'), j('/candidacies')]);
    S.slate = slate;
    (cands || []).forEach(c => { (S.cands[c.mission_id] = S.cands[c.mission_id] || []).push(c); });
    const decided = (E.config.missions || []).filter(m => m.winning_tiv_id);
    const open = slate ? slate.slots.filter(s => s.votable).slice(0, 7) : [];
    const framing = decided.filter(m => m.winning_org_id && Date.now() < budgetDay(m).getTime());
    await Promise.all([
      ...decided.map(async m => { const t = await j('/missions/' + m.id + '/p2/tally'); if (t) S.p2[m.id] = t; }),
      ...open.map(async s => { const b = await j('/causes/ballot/' + s.slot); if (b) S.ballots[s.slot] = b; }),
      ...framing.map(async m => { S.claims[m.id] = (await j('/missions/' + m.id + '/claims')) || []; }),
      loadMine(),
    ]);
  }

  // My own votes. Three sources, all of them optional:
  //   · initiatives — `/benefactors/me/p1-votes`, the same rows main.html reads
  //   · organizations — the local record main.html and cause.html both keep
  //   · the cause — `/causes/vote/mine`
  // Any failure leaves `S.mine` empty and nothing highlights.
  async function loadMine() {
    const authed = !!(E.Auth && E.Auth.isLoggedIn && E.Auth.isLoggedIn() && E.Auth.fetchAuthed);
    if (authed) {
      try {
        const r = await E.Auth.fetchAuthed('/benefactors/me/p1-votes');
        if (r && r.ok) (await r.json()).forEach(v => { if (v.tiv_id) S.mine.tivs[v.tiv_id] = true; });
      } catch (e) {}
      try {
        const r = await E.Auth.fetchAuthed('/causes/vote/mine');
        if (r && r.ok) { const v = await r.json(); S.mine.cause = (v && (v.cause_id || v.choice_id)) || null; }
      } catch (e) {}
    }
    try {
      const raw = JSON.parse(localStorage.getItem('ebx_org_votes') || '{}');
      Object.keys(raw).forEach(cid => {
        const v = raw[cid];
        S.mine.orgs[cid] = (v && typeof v === 'object') ? v.org_id : v;
      });
    } catch (e) {}
  }

  // ── which cause each step starts on ───────────────────────────────────
  // The same defaults the election page used for its two modes: the ME centre
  // is the UPCOMING cause, the OE centre the ACTIVE one. Framing and exchange
  // start wherever there is something to show.
  function defaultFocus(step) {
    const active = E.Cycle.now().causeIndex;
    if (step === 'tiv') return causeAt(active + 1);
    if (step === 'frame' || step === 'ex') {
      const pick = step === 'frame' ? framingMissions : exchangeMissions;
      const hit = causes().map(c => ({ c, m: pick(c.id)[0] })).filter(x => x.m)
        .sort((a, b) => budgetDay(a.m) - budgetDay(b.m))[0];
      if (hit) return hit.c;
      // Nothing exchanging yet: start on the cause whose first exchange opens soonest.
      if (step === 'ex') {
        const soon = causes().map(c => ({ c, m: framingMissions(c.id)[0] })).filter(x => x.m)
          .sort((a, b) => budgetDay(a.m) - budgetDay(b.m))[0];
        if (soon) return soon.c;
      }
    }
    return causeAt(active);
  }

  // The window a cause is up for in the cause election: its first OPEN slot.
  function slotFor(cid) {
    if (!S.slate) return null;
    return S.slate.slots.find(s => s.votable && s.incumbent_id === cid) || null;
  }

  // ── per-step data: what the card and the pie say about one cause ──────
  function raceFor(step, c) {
    if (step === 'cause') {
      const s = slotFor(c.id);
      const b = s ? S.ballots[s.slot] : null;
      const thisWeek = b && b.columns ? (b.columns.find(x => x.index === 1) || {}) : {};
      const counts = thisWeek.counts || {};
      const total = Object.values(counts).reduce((a, v) => a + v, 0);
      return { slot: s, ballot: b, counts, total };
    }
    if (step === 'tiv') {
      const m = pinFor(step, c) || meMission(c.id);
      const inits = meCandidates(c.id).filter(i => !m || !i.mission_id || i.mission_id === m.id);
      const pool = inits.reduce((a, i) => a + (i.committed_ebx || 0), 0);
      return { mission: m, date: m ? dates(m).missionStarted : null, inits, pool };
    }
    if (step === 'org') {
      const m = pinFor(step, c) || oeMission(c.id);
      const t = m ? S.p2[m.id] : null;
      const entries = ((t && t.entries) || []).slice()
        .sort((a, b) => (Number(b.net_votes) || 0) - (Number(a.net_votes) || 0));
      const total = entries.reduce((a, e) => a + Math.max(0, Number(e.net_votes) || 0), 0);
      const cands = m ? (S.cands[m.id] || []) : [];
      return { mission: m, date: m ? dates(m).phlElected : null, entries, total, cands, tally: t };
    }
    if (step === 'frame') {
      const ms = framingMissions(c.id);
      const m = pinFor(step, c) || ms[0] || null;
      const next = oeMission(c.id);
      return { mission: m, more: ms.length - 1, date: m ? budgetDay(m) : null, next };
    }
    const ms = exchangeMissions(c.id).slice()
      .sort((a, b) => (Number(b.credit_value) || 0) - (Number(a.credit_value) || 0));
    const firstFraming = framingMissions(c.id)[0] || null;
    return { missions: ms, opens: firstFraming ? budgetDay(firstFraming) : null, firstFraming };
  }

  // ── the framing checklist ─────────────────────────────────────────────
  // Seven weeks, T+8 → T+15, one item due at the end of each. The set and the
  // schedule are docs/mission_model.md §3a — marked PROPOSED there, so the card
  // says "proposed schedule". Only two items are knowable from the API today:
  // the CLAIM (GET /missions/{id}/claims) and budget day itself (the calendar).
  // Everything else is shown as planned, or as not recorded once its date has
  // passed — never as done.
  const FRAME_ITEMS = [
    { w: 1, t: 'Win notice and claim link sent', who: 'Earthbux' },
    { w: 2, t: 'Mission claimed by a named representative', who: 'Organization', key: 'claim' },
    { w: 3, t: 'Mission statement for this mission', who: 'Organization' },
    { w: 4, t: 'Start estimate · executive and representative named', who: 'Organization' },
    { w: 5, t: 'Identity verified by Earthbux News', who: 'Earthbux' },
    { w: 6, t: 'Payee confirmed · top benefactor threads answered', who: 'Organization' },
    { w: 7, t: 'Budget day — 5/16 claimed, every stake final', who: 'Calendar', key: 'budget' },
  ];
  function frameChecklist(m) {
    const start = dates(m).phlElected.getTime();
    const now = Date.now();
    const claimed = (S.claims[m.id] || []).length > 0;
    return FRAME_ITEMS.map(it => {
      const due = new Date(start + it.w * WK);
      const past = now >= due.getTime();
      let st = past ? 'unrecorded' : 'planned';
      if (it.key === 'claim') st = claimed ? 'done' : (past ? 'late' : 'planned');
      if (it.key === 'budget') st = past ? 'done' : 'planned';
      const current = !past && now >= due.getTime() - WK;
      return Object.assign({ due, st, current }, it);
    });
  }

  // ── side / focus card ────────────────────────────────────────────────
  // build-seq §1 Landing (2026-09-20) — the head formatting that was lost in
  // the move from the Elect page is back: the MISSION TITLE is its own line,
  // and the two dates sit under it.
  const cardHead = (days, title, date) =>
    '<div class="lw-card__name">' + title + '</div>' +
    '<div class="lw-card__head"><span class="lw-card__days">' + days + '</span>' +
    '<span class="lw-card__date">' + date + '</span></div>';

  function cardHTML(step, c, opts) {
    opts = opts || {};
    const r = raceFor(step, c);
    const sel = opts.focus ? ' lw-card--on' : '';
    let head = '', body = '';
    // build-seq §1 Landing (2026-09-20) — MY VOTE is highlighted again. `mine`
    // is set by the caller from `S.mine`, which is only populated when someone
    // is signed in; signed out, every row paints plain.
    const rank = (rows) => {
      const pad = Math.max(0, 3 - rows.length);
      return rows.map((x, i) =>
        '<div class="lw-rank' + (x.mine ? ' lw-rank--mine' : '') + '">' +
        '<span class="lw-rank__n">' + (i + 1) + '</span>' +
        '<span class="lw-rank__v">' + esc(x.name) +
        (x.pct != null ? ' <span class="lw-rank__p">' + x.pct + '%</span>' : '') +
        (x.mine ? '<span class="lw-rank__me">my vote</span>' : '') + '</span></div>').join('') +
        new Array(pad).fill('<div class="lw-rank lw-rank--pad">&nbsp;</div>').join('');
    };
    if (step === 'cause') {
      const s = r.slot;
      const until = (E.Cycle && E.Cycle.nextDecisionDate) ? E.Cycle.nextDecisionDate(c.index) : null;
      head = cardHead((s ? 'wk +' + s.weeks_out : '—'),
        esc(c.name) + ' until ' + fmt(until),
        (s ? (s.confirmed ? 'set' : 'open') : ''));
      if (s && s.challenger_id) {
        const ch = causeById(s.challenger_id);
        const chName = ch ? ch.name : s.challenger_id.replace(/-/g, ' ');
        const streak = s.streak || 0, need = s.weeks_required || 6;
        body =
          '<div class="lw-bars">' +
            '<div class="lw-bar"><span>Keep ' + esc(c.name) + '</span><i style="--w:' + (100 - pct(streak, need)) + '%;--c:' + c.color + '"></i></div>' +
            '<div class="lw-bar"><span>Replace &rarr; ' + esc(chName) + '</span><i style="--w:' + pct(streak, need) + '%;--c:' + ((ch && ch.color) || '#e8a84c') + '"></i></div>' +
          '</div>' +
          '<div class="lw-note">' + esc(chName) + ' has won ' + streak + ' of the ' + need + ' weeks in a row it needs.</div>';
      } else {
        body =
          '<div class="lw-incumbent' + (S.mine.cause === c.id ? ' lw-incumbent--mine' : '') + '">' +
            '<i style="background:' + c.color + '"></i>' +
            '<b>' + esc(c.name) + '</b> is the incumbent' +
            (S.mine.cause === c.id ? '<span class="lw-rank__me">my vote</span>' : '') + '</div>' +
          '<div class="lw-note">' + (s ? 'No challenger yet. ' : '') +
            (r.total ? r.total + ' vote' + (r.total === 1 ? '' : 's') + ' this week.' : 'No votes this week.') + '</div>';
      }
    } else if (step === 'tiv') {
      const n = r.mission ? (r.mission.cycle_num || 0) + 1 : '';
      head = cardHead((r.date ? daysTo(r.date) + ' d' : '—'), esc(c.name) + ' ' + n, fmt(r.date));
      body = r.inits.length
        ? rank(r.inits.slice(0, 3).map(i => ({ name: (i.emoji ? i.emoji + ' ' : '') + i.title, pct: pct(i.committed_ebx || 0, r.pool), mine: !!S.mine.tivs[i.id] })))
        : '<div class="lw-empty">No initiatives proposed yet.</div>';
    } else if (step === 'org') {
      head = cardHead((r.date ? daysTo(r.date) + ' d' : '—'),
        (r.mission ? esc(tivName(r.mission.winning_tiv_id)) : esc(c.name)), fmt(r.date));
      if (!r.mission) body = '<div class="lw-empty">' + esc(c.name) + ' has no organization election open.</div>';
      else if (r.entries.length) body = rank(r.entries.slice(0, 3).map(e => ({ name: orgName(e.org_id), pct: pct(Math.max(0, e.net_votes || 0), r.total), mine: S.mine.orgs[c.id] === e.org_id })));
      else if (r.cands.length) body = rank(r.cands.slice(0, 3).map(x => ({ name: orgName(x.org_id), pct: null, mine: S.mine.orgs[c.id] === x.org_id })));
      else body = '<div class="lw-empty">No organization nominated yet.</div>';
    } else if (step === 'frame') {
      const m = r.mission;
      head = cardHead((m ? daysTo(r.date) + ' d' : '—'),
        (m ? esc(tivName(m.winning_tiv_id)) : esc(c.name)), (m ? fmt(r.date) : ''));
      if (m) {
        const items = frameChecklist(m);
        const cur = items.find(x => x.current) || items.find(x => x.st === 'planned') || items[items.length - 1];
        body =
          '<div class="lw-sub">' + esc(tivName(m.winning_tiv_id)) + '</div>' +
          '<div class="lw-track">' + items.map(x =>
            '<span class="lw-wk lw-wk--' + x.st + (x.current ? ' lw-wk--now' : '') + '" title="' +
              esc('Week ' + x.w + ' · ' + x.t + ' · ' + fmt(x.due) + ' · ' + x.st) + '">' + x.w + '</span>').join('') +
          '</div>' +
          '<div class="lw-note"><b>Wk ' + cur.w + '</b> · ' + esc(cur.t) + ' · ' + fmt(cur.due) + '</div>';
      } else {
        body = '<div class="lw-empty">Nothing in prep.' +
          (r.next ? ' Next: ' + esc(tivName(r.next.winning_tiv_id)) + ', once its organization election ' +
            (dates(r.next).phlElected.getTime() > Date.now() ? 'closes on ' : 'is decided (it was due ') +
            fmt(dates(r.next).phlElected) + (dates(r.next).phlElected.getTime() > Date.now() ? '.' : ').') : '') + '</div>';
      }
    } else {
      const ms = r.missions;
      head = cardHead(ms.length + ' coin' + (ms.length === 1 ? '' : 's'),
        esc(c.name), (ms.length ? 'trading' : ''));
      body = ms.length
        ? ms.slice(0, 3).map((m, i) =>
            '<div class="lw-rank"><span class="lw-rank__n">' + (i + 1) + '</span><span class="lw-rank__v">' +
              esc(tivName(m.winning_tiv_id)) + ' <span class="lw-rank__p">' +
              (Number(m.credit_value) || 1).toFixed(2) + '</span></span></div>').join('')
        : '<div class="lw-empty">No ' + esc(c.name) + ' mission is exchanging yet.' +
            (r.opens ? ' The first opens on budget day, ' + fmt(r.opens) + '.' : '') + '</div>';
    }
    return '<button type="button" class="lw-card' + sel + (opts.active ? ' lw-card--active' : '') +
      '" style="--c:' + c.color + '" ' +
      'data-cause="' + esc(c.id) + '" aria-pressed="' + (opts.focus ? 'true' : 'false') + '">' +
      head + body + '</button>';
  }

  // ── the pie, per step ──────────────────────────────────────────────────
  function pieSlices(step, c) {
    const r = raceFor(step, c);
    if (step === 'cause') {
      return {
        label: 'This week’s cause votes',
        empty: 'No cause votes this week',
        slices: Object.entries(r.counts).map(([id, v]) => {
          const x = causeById(id);
          return { label: x ? x.name : id, value: v, color: x ? x.color : '#e8a84c' };
        }),
      };
    }
    if (step === 'tiv') {
      return {
        label: 'Token share', empty: r.inits.length ? 'No tokens committed yet' : 'No proposals yet',
        slices: r.inits.map((i, k) => ({ label: i.title, value: i.committed_ebx || 0, color: c.color, op: Math.max(0.3, 0.85 - k * 0.1) })),
      };
    }
    if (step === 'org') {
      return {
        label: 'Vote share', empty: r.mission ? 'No organization votes yet' : 'No race open',
        slices: r.entries.map((e, k) => ({ label: orgName(e.org_id), value: Math.max(0, e.net_votes || 0), color: c.color, op: Math.max(0.3, 0.85 - k * 0.12) })),
      };
    }
    if (step === 'frame') {
      // The deployment schedule, in 32nds (README §5). It is the same for
      // every mission — what framing decides is who receives it, and when.
      return {
        label: 'The pool, in 32nds', empty: '',
        slices: [
          { label: 'Research rewards · 3/32', value: 3, color: '#8fce9d' },
          { label: 'Advances · 4/32', value: 4, color: '#e8a84c' },
          { label: 'Prep release · 8/32', value: 8, color: c.color },
          { label: 'Flexible · 17/32', value: 17, color: 'rgba(245,240,232,0.55)' },
        ],
      };
    }
    // Exchange — the market metric is a backlog item (build-seq §4). Until it
    // exists the pie is each exchanging mission's share of the cause's pool.
    return {
      label: 'Pool share (market metric: backlog)', empty: 'No mission exchanging',
      slices: r.missions.map((m, k) => {
        const t = S.p2[m.id];
        return { label: tivName(m.winning_tiv_id), value: t ? (t.pool_ebx || t.total_ebx || 0) : 0, color: c.color, op: Math.max(0.3, 0.85 - k * 0.12) };
      }),
    };
  }

  // ── the wheel SVG: ring (sectors + now marker) and pie. The globe is a
  //    separate SVG layered in the middle so it can redraw on its own. ──────
  const SZ = 420, CX = SZ / 2, CY = SZ / 2;
  const PIE_OUT = 158, PIE_IN = 104;          // the pie is an annulus around the globe
  const RING_IN = 172, RING_OUT = 184;        // the seven sectors
  const GLOBE_R = 96;

  // build-seq §1 Landing (2026-09-20) — THE OUTER ANNULUS, rewritten.
  //   · the now marker is gone, and so are the arrow tips: a sector points
  //     nowhere now, it is just a sector.
  //   · the ring ROTATES with the focus instead of sitting on a fixed
  //     compass. The focused cause is always at 12 o'clock, its neighbours
  //     run out to the sides in the order the side cards are stacked
  //     (+1 +2 +3 down the left, -1 -2 -3 down the right), so every sector
  //     sits on the same line as its own card.
  //   · each sector carries ITS cause's colour at the same strength as that
  //     cause's card border, and the focused one glows the way the focused
  //     card does. The top sector is therefore always the lit one.
  //   · the cause names came off the ring — the card they point at is the
  //     label now.
  //   · a RAY runs from each sector out past the edge of the SVG, under its
  //     card, in the cause's colour.
  const RAY_OUT = 560;                        // past the viewBox: `overflow:visible`
  // -3..+3 from the focus. +1..+3 are the left column top-to-bottom, -1..-3
  // the right column top-to-bottom — `sideOrder()` builds the cards the same way.
  function relIndex(i, f) {
    let r = ((i - f) % 7 + 7) % 7;
    return r > 3 ? r - 7 : r;
  }
  function ringSVG(step, focus) {
    const secA = TAU / 7, gap = 0.028;
    const f = focus ? focus.index : 0;
    const P = (a, r) => (CX + r * Math.cos(a)).toFixed(2) + ',' + (CY + r * Math.sin(a)).toFixed(2);
    let rays = '', ring = '';
    causes().forEach(c => {
      const rel = relIndex(c.index, f);
      const am = -Math.PI / 2 - rel * secA;         // the focus rides at the top
      const a0 = am - secA / 2 + gap / 2, a1 = am + secA / 2 - gap / 2;
      const on = focus && c.id === focus.id;
      // the ray, drawn first so the ring sits on top of it
      rays += '<path d="M' + P(a0, RING_OUT) + ' L' + P(a0, RAY_OUT) +
        ' A' + RAY_OUT + ',' + RAY_OUT + ' 0 0,1 ' + P(a1, RAY_OUT) + ' L' + P(a1, RING_OUT) +
        ' A' + RING_OUT + ',' + RING_OUT + ' 0 0,0 ' + P(a0, RING_OUT) + ' Z" fill="' + c.color +
        '" fill-opacity="' + (on ? 0.14 : 0.05) + '" pointer-events="none"/>';
      // the sector itself — plain annulus segment, no tip
      const d = 'M' + P(a0, RING_OUT) + ' A' + RING_OUT + ',' + RING_OUT + ' 0 0,1 ' + P(a1, RING_OUT) +
        ' L' + P(a1, RING_IN) + ' A' + RING_IN + ',' + RING_IN + ' 0 0,0 ' + P(a0, RING_IN) + ' Z';
      ring += '<path class="lw-sector' + (on ? ' lw-sector--on' : '') + '" data-cause="' + esc(c.id) +
        '" d="' + d + '" fill="' + c.color + '" fill-opacity="' + (on ? 0.95 : 0.45) +
        '" stroke="rgba(15,26,20,0.6)" stroke-width="0.6"' + (on ? ' filter="url(#lw-glow)"' : '') +
        '><title>' + esc(c.name) + '</title></path>';
    });
    return rays + ring;
  }

  function pieSVG(step, focus) {
    const { slices, empty } = pieSlices(step, focus);
    const total = slices.reduce((a, s) => a + Math.max(0, Number(s.value) || 0), 0);
    const color = focus.color;
    if (!slices.length || total <= 0) {
      return '<circle cx="' + CX + '" cy="' + CY + '" r="' + ((PIE_OUT + PIE_IN) / 2) + '" fill="none" stroke="' + color +
        '" stroke-opacity="0.22" stroke-width="' + (PIE_OUT - PIE_IN) + '"/>' +
        (empty ? '<text x="' + CX + '" y="' + (CY + PIE_OUT - 18) + '" text-anchor="middle" class="lw-pie-empty">' + esc(empty) + '</text>' : '');
    }
    let a0 = -Math.PI / 2, out = '';
    slices.forEach((s, k) => {
      const v = Math.max(0, Number(s.value) || 0);
      if (!v) return;
      const share = v / total, ang = share * TAU;
      const title = '<title>' + esc(s.label + ' — ' + Math.round(share * 100) + '%') + '</title>';
      const fill = s.color || color, op = s.op != null ? s.op : 0.8;
      if (share >= 0.999) {
        out += '<circle cx="' + CX + '" cy="' + CY + '" r="' + ((PIE_OUT + PIE_IN) / 2) + '" fill="none" stroke="' + fill +
          '" stroke-opacity="' + op + '" stroke-width="' + (PIE_OUT - PIE_IN) + '" class="lw-slice">' + title + '</circle>';
        return;
      }
      const a1 = a0 + ang, L = ang > Math.PI ? 1 : 0;
      const p = (a, r) => (CX + r * Math.cos(a)).toFixed(2) + ',' + (CY + r * Math.sin(a)).toFixed(2);
      out += '<path class="lw-slice" d="M' + p(a0, PIE_OUT) + ' A' + PIE_OUT + ',' + PIE_OUT + ' 0 ' + L + ',1 ' + p(a1, PIE_OUT) +
        ' L' + p(a1, PIE_IN) + ' A' + PIE_IN + ',' + PIE_IN + ' 0 ' + L + ',0 ' + p(a0, PIE_IN) + ' Z" fill="' + fill +
        '" fill-opacity="' + op + '" stroke="#0f1a14" stroke-width="1.5">' + title + '</path>';
      a0 = a1;
    });
    return out;
  }

  // ── the globe ─────────────────────────────────────────────────────────
  // Orthographic, drawn with d3-geo when it is present (the vendored copy in
  // resources/js/vendor), so the land clips properly at the horizon. It turns
  // slowly on its own and swings to the focused cause's anchor when the focus
  // changes. Paused off-screen and for reduced motion.
  const hasD3 = () => !!(window.d3 && d3.geoOrthographic && d3.geoPath);
  function globeFrame() {
    const g = S.root && S.root.querySelector('#lw-globe');
    if (!g) return;
    const G = S.globe;
    const land = g.querySelector('.lw-land'), grat = g.querySelector('.lw-grat'), marks = g.querySelector('.lw-marks');
    const focus = S.focus;
    if (hasD3()) {
      const proj = d3.geoOrthographic().scale(GLOBE_R).translate([CX, CY]).clipAngle(90)
        .rotate([-G.lon, G.lat, 0]).precision(0.6);
      const path = d3.geoPath(proj);
      if (window.EBX_LAND) land.setAttribute('d', path(window.EBX_LAND) || '');
      grat.setAttribute('d', path(d3.geoGraticule10()) || '');
      let mk = '';
      causes().forEach(c => {
        const a = CAUSE_ANCHOR[c.id]; if (!a) return;
        const on = focus && focus.id === c.id;
        const vis = d3.geoDistance([a[1], a[0]], [G.lon, -G.lat]) < Math.PI / 2;
        if (!vis) return;
        const q = proj([a[1], a[0]]);
        mk += '<circle cx="' + q[0].toFixed(1) + '" cy="' + q[1].toFixed(1) + '" r="' + (on ? 5.5 : 2.6) + '" fill="' + c.color +
          '" stroke="rgba(255,255,255,' + (on ? 0.95 : 0.4) + ')" stroke-width="' + (on ? 1.6 : 0.8) + '"' +
          (on ? ' class="lw-pin"' : '') + '/>';
      });
      marks.innerHTML = mk;
    } else {
      // No d3: meridians and parallels only, the same projection by hand.
      const pr = (la, lo) => {
        const L = la * Math.PI / 180, O = (lo - G.lon) * Math.PI / 180;
        return { x: CX + GLOBE_R * Math.cos(L) * Math.sin(O), y: CY - GLOBE_R * Math.sin(L), z: Math.cos(L) * Math.cos(O) };
      };
      let d = '';
      for (let lo = -180; lo < 180; lo += 30) {
        let first = true;
        for (let la = -90; la <= 90; la += 5) {
          const q = pr(la, lo);
          if (q.z < 0) { first = true; continue; }
          d += (first ? 'M' : 'L') + q.x.toFixed(1) + ' ' + q.y.toFixed(1) + ' '; first = false;
        }
      }
      grat.setAttribute('d', d);
    }
  }
  function spin(ts) {
    const G = S.globe;
    G.raf = requestAnimationFrame(spin);
    if (!G.visible || ts - G.last < 33) return;      // ~30 fps is plenty
    G.last = ts;
    const d = ((G.target - G.lon + 540) % 360) - 180;
    if (Math.abs(d) > 0.3) G.lon += d * 0.07;
    else { G.lon += 0.08; G.target = G.lon; }         // arrived: drift eastward
    globeFrame();
  }
  function aimGlobe(c) {
    const a = c && CAUSE_ANCHOR[c.id];
    if (a) { S.globe.target = a[1]; S.globe.lat = -Math.max(-30, Math.min(30, a[0] * 0.6)); }
  }

  // ── painting ──────────────────────────────────────────────────────────
  function sideOrder() {
    const f = S.focus ? S.focus.index : 0;
    // Clockwise down the left, counter-clockwise down the right — the election
    // page's orientation (left +1 +2 +3, right −1 −2 −3 from the focus).
    return { left: [1, 2, 3].map(k => causeAt(f + k)), right: [-1, -2, -3].map(k => causeAt(f + k)) };
  }

  function electHref(step, c) {
    const st = { cause: 'ce', tiv: 'me', org: 'oe', frame: 'fr', ex: 'ex' }[step];
    // build-seq P1 (2026-09-24): the Elect page merged into the mission page.
    return 'mission.html?state=' + st + (c ? '&cause=' + encodeURIComponent(c.id) : '');
  }

  function liveLine(step, c) {
    const r = raceFor(step, c);
    const L = (k, v) => '<div class="lw-live__row"><span>' + k + '</span><b>' + v + '</b></div>';
    if (step === 'cause') {
      const s = r.slot;
      if (!s) return L('Window', 'none open');
      const ch = s.challenger_id ? (causeById(s.challenger_id) || { name: s.challenger_id }) : null;
      return L('Window', esc(c.name) + ' · ' + s.weeks_out + ' weeks out') +
        L('Challenger', ch ? esc(ch.name) + ' · ' + (s.streak || 0) + '/' + (s.weeks_required || 6) + ' weeks' : 'none') +
        L('This week', r.total + ' vote' + (r.total === 1 ? '' : 's'));
    }
    if (step === 'tiv') {
      const lead = r.inits[0];
      return L('Election', esc(c.name) + ' ' + (r.mission ? (r.mission.cycle_num || 0) + 1 : '') + ' · closes ' + fmt(r.date)) +
        L('Leading', lead ? esc(lead.title) + ' · ' + pct(lead.committed_ebx || 0, r.pool) + '%' : 'no proposals yet') +
        L('Pool', tk(r.pool) + ' · ' + r.inits.length + ' initiative' + (r.inits.length === 1 ? '' : 's'));
    }
    if (step === 'org') {
      if (!r.mission) return L('Race', esc(c.name) + ' has none open');
      const lead = r.entries[0];
      return L('Race', esc(tivName(r.mission.winning_tiv_id)) + ' · closes ' + fmt(r.date)) +
        L('Leading', lead ? esc(orgName(lead.org_id)) + ' · ' + pct(Math.max(0, lead.net_votes || 0), r.total) + '%' : 'no votes yet') +
        L('Candidates', r.cands.length + ' nominated');
    }
    if (step === 'frame') {
      if (!r.mission) return L('Prep', esc(c.name) + ' has no mission in prep');
      const items = frameChecklist(r.mission);
      const done = items.filter(x => x.st === 'done').length;
      return L('Mission', esc(tivName(r.mission.winning_tiv_id))) +
        L('Organization', esc(orgName(r.mission.winning_org_id))) +
        L('Budget day', fmt(r.date) + ' · ' + daysTo(r.date) + ' d · ' + done + '/7 recorded');
    }
    const top = r.missions[0];
    return L('Exchanging', r.missions.length + ' ' + esc(c.name) + ' mission' + (r.missions.length === 1 ? '' : 's')) +
      L('Leading coin', top ? esc(tivName(top.winning_tiv_id)) + ' · ' + (Number(top.credit_value) || 1).toFixed(2) : '—') +
      L('Next to open', r.opens ? fmt(r.opens) : '—');
  }

  // build-seq §1 Landing (2026-09-20) — e: "the active card display is just
  // going to be the side card (same size and shape and contents) inside the
  // right hand area." So the right half of the top card is the focused
  // cause's own card, and `liveLine` is not painted for now (it is kept — see
  // the removal register).
  // build-seq P2 (2026-09-25) — the top card is WHAT IS GOING ON, not what the
  // phase is: the definition moved to the mission page. Left, the live facts
  // for the focused cause in the selected phase (`liveLine`, unpainted since
  // 2026-09-20 — F5); right, that cause's own card. The phase rows above point
  // down into it (`.lw-pointer`, placed under the selected phase by `aim`).
  function topCardHTML() {
    const ph = PHASE[S.step], c = S.focus;
    return '<div class="lw-top lw-top--live" style="--c:' + c.color + '">' +
      '<div class="lw-top__main">' +
        '<div class="lw-top__kicker">' + esc(ph.title) + ' &middot; now</div>' +
        '<h3 class="lw-top__title"><i class="lw-top__dot" style="background:' + c.color + '"></i>' + esc(c.name) + '</h3>' +
        '<div class="lw-live">' + liveLine(S.step, c) + '</div>' +
        '<a class="lw-top__go" href="' + electHref(S.step, c) + '">' +
          (S.step === 'frame' ? 'Open the prep ballot' : S.step === 'ex' ? 'See the exchange' : 'Vote in this election') +
          ' &rarr;</a>' +
      '</div>' +
      '<div class="lw-top__live">' + cardHTML(S.step, c, { focus: true, active: true }) + '</div>' +
    '</div>';
  }

  // ── the time span under the annulus ───────────────────────────────────
  // The seven cards are seven weeks: this is the window they cover, from the
  // earliest date any card carries to the latest, for the selected phase.
  function cardDate(step, c) {
    const r = raceFor(step, c);
    if (step === 'cause') return (E.Cycle && E.Cycle.nextDecisionDate) ? E.Cycle.nextDecisionDate(c.index) : null;
    if (step === 'ex') return r.opens || null;
    return r.date || null;
  }
  function spanHTML() {
    const ds = causes().map(c => cardDate(S.step, c)).filter(d => d && !isNaN(d.getTime()))
      .sort((a, b) => a - b);
    const ph = PHASE[S.step];
    if (!ds.length) return '<span class="lw-span__range">' + esc(ph.title) + '</span> &middot; no dates yet';
    const a = ds[0], b = ds[ds.length - 1];
    const weeks = Math.max(1, Math.round((b - a) / WK) + 1);
    const lab = { cause: 'cause decisions', tiv: 'initiative elections closing', org: 'organization elections closing',
                  frame: 'budget days', ex: 'exchanges opening' }[S.step];
    return '<span class="lw-span__range">' + fmt(a) + ' &ndash; ' + fmt(b) + '</span>' +
      '<span class="lw-span__what">' + weeks + ' week' + (weeks === 1 ? '' : 's') + ' of ' + lab +
      ', one cause a week</span>';
  }

  // Place the down-pointer on the top card under the selected phase card.
  function aim() {
    const R = S.root; if (!R) return;
    const on = R.querySelector('.lw-phase.on'), tc = R.querySelector('#lw-topcard'), ptr = R.querySelector('.lw-pointer');
    if (!on || !tc || !ptr) return;
    const a = on.getBoundingClientRect(), b = tc.getBoundingClientRect();
    if (!b.width) return;
    ptr.style.left = Math.round(a.left + a.width / 2 - b.left) + 'px';
  }

  function centerCaption() {
    const c = S.focus, step = STEPS.find(s => s.key === S.step);
    const { label } = pieSlices(S.step, c);
    return '<div class="lw-cap__cause" style="color:' + c.color + '">' + esc(c.name) + '</div>' +
      '<div class="lw-cap__step">' + esc(step.label) + ' · ' + esc(label) + '</div>';
  }

  function paint() {
    const R = S.root; if (!R) return;
    const { left, right } = sideOrder();
    R.querySelectorAll('.lw-step').forEach(b => {
      const on = b.dataset.step === S.step;
      b.classList.toggle('on', on); b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    R.querySelectorAll('.lw-phase').forEach(p => {
      p.classList.toggle('on', p.dataset.step === S.step);
      const go = p.querySelector('.lw-phase__vote');
      if (go) go.href = electHref(p.dataset.step, S.focus);
    });
    if (S.variant !== 'mission') {
      R.querySelector('#lw-topcard .lw-top-slot').innerHTML = topCardHTML();
      R.querySelector('#lw-topcard').style.setProperty('--c', S.focus.color);
      R.querySelector('#lw-span').innerHTML = spanHTML();
      R.querySelector('#lw-left').innerHTML = left.map(c => cardHTML(S.step, c)).join('');
      R.querySelector('#lw-right').innerHTML = right.map(c => cardHTML(S.step, c)).join('');
    }
    R.querySelector('#lw-ringlayer').innerHTML = ringSVG(S.step, S.focus);
    R.querySelector('#lw-pielayer').innerHTML = pieSVG(S.step, S.focus);
    R.querySelector('#lw-cap').innerHTML = centerCaption();
    R.querySelector('#lw-globe .lw-sea').setAttribute('stroke', S.focus.color);
    R.querySelector('.lw-wheel').style.setProperty('--c', S.focus.color);
    globeFrame();
    aim();
  }

  function setStep(key, keepFocus) {
    if (!STEPS.some(s => s.key === key)) return;
    S.step = key;
    if (!keepFocus) { S.focus = defaultFocus(key) || causes()[0]; aimGlobe(S.focus); }
    try { history.replaceState(null, '', '?step=' + key + location.hash); } catch (e) {}
    paint();
  }
  function setFocus(cid) {
    const c = causeById(cid); if (!c) return;
    S.focus = c; aimGlobe(c); paint();
  }

  // The mission variant: the wheel alone. Its side columns belong to the page.
  function wheelHTML() {
    return '<div class="lw-wheel">' +
          '<svg class="lw-svg" viewBox="-40 -40 ' + (SZ + 80) + ' ' + (SZ + 80) + '" role="img" aria-label="The seven causes, this week, and the race in focus">' +
            '<defs><filter id="lw-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.2" result="b"/>' +
              '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>' +
              '<radialGradient id="lw-sea" cx="38%" cy="32%"><stop offset="0%" stop-color="#2d5268"/>' +
              '<stop offset="65%" stop-color="#153040"/><stop offset="100%" stop-color="#0a1a22"/></radialGradient>' +
              '<radialGradient id="lw-shade" cx="36%" cy="30%"><stop offset="55%" stop-color="rgba(0,0,0,0)"/>' +
              '<stop offset="100%" stop-color="rgba(0,0,0,0.55)"/></radialGradient></defs>' +
            '<g id="lw-ringlayer"></g>' +
            '<g id="lw-pielayer"></g>' +
            '<g id="lw-globe">' +
              '<circle class="lw-sea" cx="' + CX + '" cy="' + CY + '" r="' + GLOBE_R + '" fill="url(#lw-sea)" stroke-width="1.2" stroke-opacity="0.7"/>' +
              '<path class="lw-grat" fill="none" stroke="rgba(170,215,235,0.16)" stroke-width="0.6"/>' +
              '<path class="lw-land" fill="rgba(143,206,157,0.55)" stroke="rgba(220,240,225,0.35)" stroke-width="0.4"/>' +
              '<g class="lw-marks"></g>' +
              '<circle cx="' + CX + '" cy="' + CY + '" r="' + GLOBE_R + '" fill="url(#lw-shade)" pointer-events="none"/>' +
            '</g>' +
          '</svg>' +
          '<div class="lw-cap" id="lw-cap"></div>' +
        '</div>';
  }

  function shell() {
    if (S.variant === 'mission') return wheelHTML();
    // build-seq P2 (2026-09-25): two rows of phase cards replace the five
    // toggles. The whole card toggles the page (what's new); the link votes.
    const phase = key => {
      const st = STEPS.find(x => x.key === key), ph = PHASE[key];
      return '<div class="lw-phase lw-phase--' + st.half + '" data-step="' + key + '">' +
        '<div class="lw-phase__head"><span class="lw-step__n">' + st.n + '</span>' +
          '<h3 class="lw-phase__t">' + esc(ph.title) + '</h3></div>' +
        '<p class="lw-phase__p">' + ph.blurb + '</p>' +
        '<div class="lw-phase__acts">' +
          '<button type="button" role="tab" class="lw-step lw-phase__see" data-step="' + key + '" aria-selected="false">What&rsquo;s new</button>' +
          '<a class="lw-phase__vote" href="' + electHref(key, null) + '">' + ph.go + ' &rarr;</a>' +
        '</div>' +
      '</div>';
    };
    const arrow = '<span class="lw-arrow" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22">' +
      '<path d="M4 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
    const row = r => '<div class="lw-row lw-row--' + r.key + '">' +
      '<div class="lw-row__t">' + esc(r.title) + '</div>' +
      '<div class="lw-row__cards lw-row__cards--' + r.steps.length + '">' + r.steps.map(phase).join(arrow) + '</div></div>';
    return '' +
      '<div class="lw-rows lw-steps" role="tablist" aria-label="The five phases">' + ROWS.map(row).join('') + '</div>' +
      '<div id="lw-topcard" role="tabpanel"><span class="lw-pointer" aria-hidden="true"></span><div class="lw-top-slot"></div></div>' +
      '<div class="lw-stage">' +
        '<div class="lw-col lw-col--left" id="lw-left"></div>' +
        wheelHTML() +
        '<div class="lw-col lw-col--right" id="lw-right"></div>' +
      '</div>' +
      '<div class="lw-span" id="lw-span"></div>';
  }

  function bind() {
    const R = S.root;
    R.addEventListener('click', e => {
      const st = e.target.closest('.lw-step');
      if (st) { setStep(st.dataset.step); return; }
      if (e.target.closest('.lw-phase__vote')) return;
      const ph = e.target.closest('.lw-phase');
      if (ph) { setStep(ph.dataset.step); return; }
      const card = e.target.closest('.lw-card');
      if (card) { setFocus(card.dataset.cause); return; }
      const sec = e.target.closest('.lw-sector');
      if (sec) {
        const cid = sec.getAttribute('data-cause');
        if (S.onFocus) S.onFocus(cid); else setFocus(cid);
      }
    });
    const stepsEl = R.querySelector('.lw-steps');
    if (stepsEl) stepsEl.addEventListener('keydown', e => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const i = STEPS.findIndex(s => s.key === S.step);
      const n = STEPS[(i + (e.key === 'ArrowRight' ? 1 : 4)) % 5];
      setStep(n.key);
      const b = R.querySelector('.lw-step[data-step="' + n.key + '"]'); if (b) b.focus();
    });
    window.addEventListener('resize', aim);
    const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(es => { S.globe.visible = es[0].isIntersecting; })
        .observe(R.querySelector('.lw-wheel'));
    }
    if (!reduce) S.globe.raf = requestAnimationFrame(spin);
    // build-seq §1 (2026-09-20): the per-minute ring repaint went with the now
    // marker — the ring is a function of the FOCUS now, not of the clock.
  }

  async function mount(sel, opts) {
    const root = typeof sel === 'string' ? document.querySelector(sel) : sel;
    if (!root) return;
    S.root = root;
    root.classList.add('lw');
    root.innerHTML = '<div class="lw-loading">Loading the week&hellip;</div>';
    await data();
    if (!causes().length) { root.innerHTML = '<div class="lw-loading">The live wheel is unavailable right now.</div>'; return; }
    S.variant = (opts && opts.variant === 'mission') ? 'mission' : 'landing';
    S.onFocus = (opts && typeof opts.onFocus === 'function') ? opts.onFocus : null;
    if (S.variant === 'mission') root.classList.add('lw--mission');
    root.innerHTML = shell();
    bind();
    const want = (S.variant !== 'mission' && E.getParam && E.getParam('step')) || (opts && opts.step) || 'tiv';
    S.step = STEPS.some(s => s.key === want) ? want : 'tiv';
    S.focus = defaultFocus(S.step) || causes()[0];
    const a = CAUSE_ANCHOR[S.focus.id];
    if (a) { S.globe.lon = S.globe.target = a[1] - 40; aimGlobe(S.focus); }
    paint();
  }

  // build-seq P1 (2026-09-24) — the mission page's one call: step, cause and
  // the pinned mission together, one paint, and no URL change (the page owns
  // the URL). Any field left out keeps its value.
  function show(o) {
    o = o || {};
    if (o.step && STEPS.some(s => s.key === o.step)) S.step = o.step;
    if ('mission' in o) S.pin = o.mission || null;
    const c = o.cause ? causeById(o.cause) : null;
    if (c && (!S.focus || S.focus.id !== c.id)) { S.focus = c; aimGlobe(c); }
    if (!S.focus) S.focus = defaultFocus(S.step) || causes()[0];
    if (S.root && S.root.querySelector('#lw-ringlayer')) paint();
  }

  E.Wheel = {
    mount, setStep, setFocus, show, STEPS, data, COPY, PHASE, ROWS,
    meMission, raceFor: (step, cid) => { const c = causeById(cid); return c ? raceFor(step, c) : null; },
    // shared with main.html's steps 4 and 5
    framingMissions, exchangeMissions, oeMission, budgetDay, frameChecklist, tivName, orgName,
    p2Tally: id => S.p2[id] || null, candidacies: id => S.cands[id] || [],
    _state: S, _raceFor: raceFor,
  };
})();
