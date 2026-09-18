/* ebx_postsbox — THE DISCUSSION BOX.
 *
 * Moved here from cause.html on 2026-09-17 (INSTRUCTIONS build-seq, the feed
 * pass). cause.html is becoming the NEWSFEED — "designed to capture attention.
 * NOT sorted by mission" — and this box is the opposite of that: it is one
 * mission's own conversation, a matrix of four dated stages against three post
 * categories. structure.md §6 box **i** is where it belongs, so mission.html
 * mounts it now and the feed takes the cause page's spine.
 *
 * NOTHING BELOW IS REWRITTEN. The code is the code that ran on cause.html,
 * lifted whole so the move can be judged on its own: same `#pb-*` element ids,
 * same `window.pb*` handlers, same `renderPostsBox(cause, ctx)` entry point,
 * same CSS (now in ebx_frontend.css so both pages can reach it). What changed
 * is only where it is mounted and who builds the `ctx`.
 *
 *     EBX.PostsBox.render(cause, ctx)   ctx: { mission, leader, decisionDate,
 *                                              orgVoteDate, releaseDate,
 *                                              p2Active, p2Recap }
 *     EBX.PostsBox.bind()               wire the search + sort inputs
 *     EBX.PostsBox.invalidate()         drop the cached posts after a write
 *
 * Load it after ebx_shared.js; it needs EBX.Auth, EBX.config and EBX.Cycle.
 */
(function (EBX) {
  'use strict';

  // The three things the box read from the page around it. `fmtDate` and
  // `fmtRange` are cause.html's, copied rather than referenced so the box no
  // longer depends on the page it used to live in; `renderAnnulus` and
  // `causeOrgShares` are optional and stay guarded where they are called.
  function _v2LoggedIn() { return !!(EBX.Auth && EBX.Auth.isLoggedIn && EBX.Auth.isLoggedIn()); }
  function fmtDate(d) { return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }); }
  function fmtRange(a, b) {
    if (!a || !b) return 'not scheduled';
    const sameYear = a.getFullYear() === b.getFullYear();
    const left = a.toLocaleDateString('en-US', sameYear
      ? { month: 'short', day: 'numeric' }
      : { month: 'short', day: 'numeric', year: 'numeric' });
    return left + ' – ' + fmtDate(b);
  }

    // ══ BUILD-SEQ §1 (2026-08-11) — THE POSTS BOX ═══════════════════════════
    // Jax's drawing, and it REPLACES the four-section accordion built one day
    // earlier (2026-08-10):
    //
    //   |__a__|__b__|__c__|__d__|    phase tabs — the four stages, each dated
    //   |___e___|___f___|___g___|    category tabs — Research · Reviews · Budgeting
    //   |           h           |    explanation — ONE per combined toggle
    //   |           i           |    input dialogue
    //   |           j           |    the leading post in that category
    //
    // WHY A MATRIX, NOT AN ACCORDION. The accordion asked one question — which
    // stage are you reading — and answered it with four bespoke bodies, each
    // growing its own thread and composer. The matrix asks that question on one
    // axis and "which kind of post" on the other, so EVERY cell is the same
    // three things: one explanation, one composer, one leading post. Twelve
    // cells, one renderer.
    //
    // MIGRATION IS GONE, AND IT IS NOT MISSED. `_CT_HOME` moved a thread down
    // the timeline as stages closed, so a type lived in exactly one section.
    // Jax's rule for the new box is CUMULATIVE instead — "Context only in a-b,
    // Context&Investigation in c, Context&Investigation&Analysis in d" — a
    // stage OPENS a type and later stages keep it. That is the same statement
    // migration was making (context is readable wherever the mission is now)
    // without the surprise of a thread vanishing from where you last read it.
    //
    // THE GRAY RULES ARE THE SPEC'S, VERBATIM:
    //   e Research   — grayed until the cause is confirmed (so: never, on this
    //                  page; every mission here is past that)
    //   f Reviews    — tiv cases in a-b, phl cases in c, evaluations in d
    //   g Budgeting  — grayed until the initiative is elected (tabs c and d)
    //
    // The three-band P3 box (`renderP3Bands`, a·Budgeting b·Research c·Reviews)
    // is ABSORBED here — its three bands were these three categories, so it was
    // the same surface for one stage only. Budgeting's costed composer and
    // ranked list are tab g; the research tiles are e's type pills and its
    // ranked list is j's pager + search; reviews-by-organization is f, with the
    // sort-by-philanthropy select moved onto j.
    const PB_PHASES = [
      { key: 'a', n: 1, name: 'Cause confirmed' },
      { key: 'b', n: 2, name: 'Mission open' },
      { key: 'c', n: 3, name: 'Initiative elected' },
      { key: 'd', n: 4, name: 'Philanthropy elected' },
    ];
    const PB_CATS = [
      { key: 'e', cat: 'research',  label: 'Research' },
      { key: 'f', cat: 'reviews',   label: 'Reviews' },
      { key: 'g', cat: 'budgeting', label: 'Budgeting' },
    ];
    // Which post types a (category, phase) cell holds. `case:tiv` and `case:phl`
    // are the same backend type — a case carrying a tiv tag or an org tag.
    const PB_TYPES = {
      research:  { 1: ['context'], 2: ['context'], 3: ['context', 'investigation'],
                   4: ['context', 'investigation', 'analysis'] },
      reviews:   { 1: ['case:tiv'], 2: ['case:tiv'], 3: ['case:phl'], 4: ['evaluation'] },
      budgeting: { 1: [], 2: [], 3: ['service', 'supply', 'support'],
                   4: ['service', 'supply', 'support'] },
    };
    // Every type a CATEGORY has, in ladder order — the toggle in k always shows
    // all of them and grays the ones this stage has not opened.
    const PB_CAT_TYPES = {
      research:  ['context', 'investigation', 'analysis'],
      reviews:   ['case:tiv', 'case:phl', 'evaluation'],
      budgeting: ['service', 'supply', 'support'],
    };
    // The type a phase OPENS — the one its explanation is about. Budgeting is
    // the exception the spec names: it explains all three of s/s/s at once.
    const PB_OPENS = {
      research: { 1: null, 2: 'context', 3: 'investigation', 4: 'analysis' },
      reviews:  { 1: null, 2: 'case:tiv', 3: 'case:phl', 4: 'evaluation' },
      budgeting: { 3: 'sss', 4: 'sss' },
    };
    const PB_LABEL = {
      context: 'Context', investigation: 'Investigation', analysis: 'Analysis',
      'case:tiv': 'Case · initiative', 'case:phl': 'Case · philanthropy',
      evaluation: 'Evaluation', service: 'Service', supply: 'Supply', support: 'Support',
    };
    // Post-config's rules, restated for the client (backend/app/post_config.py
    // is the source of truth; these are the labels it declares).
    const PB_REACTIONS = {
      context:       [['helpful', 'Helpful'], ['neutral', 'Neutral'], ['harmful', 'Harmful']],
      investigation: [['helpful', 'Helpful'], ['neutral', 'Neutral'], ['harmful', 'Harmful']],
      analysis:      [['helpful', 'Helpful'], ['neutral', 'Neutral'], ['harmful', 'Harmful']],
      'case:tiv':    [['helpful', 'Fair'], ['harmful', 'Unfair']],
      'case:phl':    [['helpful', 'Fair'], ['harmful', 'Unfair']],
      evaluation:    [['helpful', 'Fair'], ['harmful', 'Unfair']],
      service:       [['helpful', 'Approve']],
      supply:        [['helpful', 'Approve']],
      support:       [['helpful', 'Approve']],
    };

    let _ctCtx = null;            // last context, so a click can re-render
    // The box's whole state. Kept outside the render so a tab click, a search
    // or a pager step never resets the others.
    const _pb = {
      phase: null,      // null = follow the mission's own stage
      cat: 'research',
      type: {},         // "cat/n" → chosen type key
      page: {},         // "cat/n" → which post in the ranked list is showing
      search: '',       // research: filter inside the open type
      sortOrg: 'all',   // reviews: filter to one philanthropy
      msg: '',          // composer feedback
      pick: null,       // which link rail has its picker open
      draft: {},        // "cat/n/type" → the links attached to the post being written
    };

    function _p3esc(s) {
      return String(s === null || s === undefined ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // The stage the SELECTED mission is actually in, which is also the phase
    // tab that opens by default. 2 = electing an initiative, 3 = electing a
    // philanthropy, 4 = underway. (1 is never "now": every mission on the page
    // is past its cause-confirmed stage, per the spec.)
    function _ctStage(ctx) {
      const m = ctx && ctx.mission;
      if (ctx && ctx.p2Recap) return 4;
      if (m && m.winning_org_id) return 4;
      if (m && ['budget', 'credit', 'resolution'].includes(m.current_phase)) return 4;
      if (m && m.winning_tiv_id) return 3;
      if (ctx && ctx.p2Active) return 3;
      return 2;
    }
    // The four dates, straight off the shared helper — one anchor, one owner.
    // §1 carries a RANGE (`from`/`to`); the other three are points.
    function _ctDates(ctx) {
      const m = ctx && ctx.mission;
      if (!m) return { 1: null, 2: null, 3: null, 4: null, range1: null };
      const d = EBX.Cycle.missionDates(m);
      return {
        1: d.causeFinalizedTo,          // the edge the tabs sort/compare on
        2: d.causeOpened,
        3: d.missionStarted,
        4: d.phlElected,
        range1: { from: d.causeFinalizedFrom, to: d.causeFinalizedTo },
      };
    }
    // §1's date. structure.md: "`T−14wk .. T−7wk` (Display T-14 wk until
    // election actually running)" — so it shows the WINDOW OPENING as a single
    // date, and only becomes a range once a cause election is genuinely live in
    // it. There is no live cause-election signal on this page yet, so it prints
    // the point; `range1` is carried so the switch is one condition away.
    function _ctDateText(n, dates) {
      if (n === 1) return dates.range1 ? fmtDate(dates.range1.from) : 'not scheduled';
      return dates[n] ? fmtDate(dates[n]) : 'not scheduled';
    }

    // ── the posts this page reads ────────────────────────────────────────────
    let _ctPosts = { missionId: null, posts: [] };
    async function _ctLoadPosts(mission, force) {
      if (!mission) { _ctPosts = { missionId: null, posts: [] }; return; }
      if (!force && _ctPosts.missionId === mission.id) return;
      let posts = [];
      try {
        const r = await fetch('/posts?mission_id=' + encodeURIComponent(mission.id) +
          '&roots_only=true&limit=200');
        if (r.ok) posts = await r.json();
      } catch (e) {}
      _ctPosts = { missionId: mission.id, posts: posts || [] };
    }
    const _ctTypeOf = p => p.type || p.stance || p.category || '';
    const _ctScore  = p => (p.helpful_count || 0) - (p.harmful_count || 0) + (p.reply_count || 0);
    const _score    = p => (p.helpful_count || 0) - (p.harmful_count || 0);
    // A "case for a philanthropy" is a case post carrying an org tag; a case for
    // the initiative carries a tiv tag (or neither, legacy).
    const _ctIsPhlCase = p => _ctTypeOf(p) === 'case' && !!p.org_id;
    // A budgeting post is category 'budgeting' with type service|supply|support.
    // Pre-2026-08-08 rows were written as category 'context' with the kind in
    // `stance`, so both shapes are read; only the new shape is ever written.
    const _sssKind = p =>
      (p.category === 'budgeting' && ['service', 'supply', 'support'].includes(p.type)) ? p.type
      : (['service', 'supply', 'support'].includes(p.stance) ? p.stance : null);
    const _fmtCost = n => (n === null || n === undefined || n === '') ? '—'
      : '$' + Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 });
    const _fmtSetup = n => (n === null || n === undefined || n === '') ? '—'
      : Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 }) + ' d';
    const _SSS_META = {
      service: ['🛠', 'Service', 'Something we can send people to DO. Carried by philanthropies.'],
      supply:  ['📦', 'Supply', 'WHAT those people need to do it. Carried by benefactors.'],
      support: ['🤝', 'Support', 'Assurance the issue is being resolved honestly. Carried by Earthbux.'],
    };
    // Does a post belong to this type key?
    function _pbIs(p, key) {
      const t = _ctTypeOf(p);
      if (key === 'case:tiv') return t === 'case' && !_ctIsPhlCase(p);
      if (key === 'case:phl') return _ctIsPhlCase(p);
      if (['service', 'supply', 'support'].includes(key)) return _sssKind(p) === key;
      return t === key;
    }
    function _ctTivName(id) {
      const i = (EBX.config.initiatives || []).find(x => x.id === id);
      return i ? ((i.emoji ? i.emoji + ' ' : '') + (i.title || i.id)) : (id || '—');
    }
    function _ctOrgName(id) {
      const o = (EBX.config.organizations || []).find(x => x.id === id);
      return o ? (o.name || o.id) : (id || '—');
    }
    // The initiative a `case` post must reference: the one selected in the
    // cards to the left of the annulus (spec: "toggled by the selected tiv").
    function _ctSelectedTiv(cause) {
      const id = window._p1SelectedId || null;
      if (id) return (EBX.config.initiatives || []).find(i => i.id === id) || null;
      const m = _ctCtx && _ctCtx.ctx && _ctCtx.ctx.mission;
      if (m && m.winning_tiv_id) {
        return (EBX.config.initiatives || []).find(i => i.id === m.winning_tiv_id) || null;
      }
      return (_ctCtx && _ctCtx.ctx && _ctCtx.ctx.leader) || null;
    }
    // The philanthropies an investigation / case / evaluation may name. Before
    // the mission starts an investigation still "requires at least 1 specific
    // philanthropy", so the list is every registered one; once the race is
    // running the spec narrows it to those in the mission.
    let _ctOrgs = { missionId: null, list: [] };
    async function _ctLoadOrgs(mission) {
      if (!mission) { _ctOrgs = { missionId: null, list: [] }; return; }
      if (_ctOrgs.missionId === mission.id) return;
      let list = [];
      try {
        const r = await fetch('/candidacies?mission_id=' + encodeURIComponent(mission.id));
        if (r.ok) {
          const cands = await r.json();
          list = (cands || []).map(c => ({ id: c.org_id, name: _ctOrgName(c.org_id) }));
        }
      } catch (e) {}
      _ctOrgs = { missionId: mission.id, list };
    }
    function _ctOrgOptions(stage) {
      const inMission = _ctOrgs.list || [];
      const all = (EBX.config.organizations || []).map(o => ({ id: o.id, name: o.name || o.id }));
      const list = (stage >= 3 && inMission.length) ? inMission : all;
      const seen = new Set();
      return list.filter(o => o.id && !seen.has(o.id) && seen.add(o.id));
    }

    // ── the rules ────────────────────────────────────────────────────────────
    // g is grayed until the initiative is elected; e until the cause is
    // confirmed, which on this page is always true (§1 is the earliest tab).
    function _pbCatEnabled(cat, n) {
      if (cat === 'budgeting') return n >= 3;
      return true;
    }
    // Can this type be WRITTEN right now? The phase tabs are free to browse —
    // reading a stage you are not in is the whole point of them — but a post
    // lands in the mission's real stage, so the composer follows that and says
    // so when it is shut.
    function _pbOpenNow(type, stage) {
      switch (type) {
        case 'context':       return stage >= 2;
        case 'case:tiv':      return stage === 2;
        case 'investigation': return stage >= 2;   // opens early, per the spec
        case 'case:phl':      return stage === 3;
        case 'analysis':      return stage >= 4;
        case 'evaluation':    return stage >= 4;
        case 'service': case 'supply': case 'support': return stage >= 3;
      }
      return false;
    }
    function _pbWhyShut(type, stage, dates) {
      const on = d => d ? fmtDate(d) : 'a date not yet set';
      if (type === 'case:tiv') return stage > 2
        ? 'The initiative election closed on ' + on(dates[3]) + ' — a case for an initiative can no longer be posted.'
        : 'Opens when the initiative election opens on ' + on(dates[2]) + '.';
      if (type === 'case:phl') return stage < 3
        ? 'Opens when the philanthropy election opens on ' + on(dates[3]) + '.'
        : 'The philanthropy election closed on ' + on(dates[4]) + '.';
      if (type === 'analysis' || type === 'evaluation')
        return 'Opens when a philanthropy is elected on ' + on(dates[4]) + '.';
      if (['service', 'supply', 'support'].includes(type))
        return 'Opens when the initiative is elected on ' + on(dates[3]) + '.';
      return 'Not open at this stage.';
    }
    function _pbCurPhase() {
      const stage = _ctStage(_ctCtx ? _ctCtx.ctx : null);
      let n = _pb.phase || stage;
      // Never leave the box on a category that this phase grays out.
      if (!_pbCatEnabled(_pb.cat, n)) _pb.cat = 'research';
      return n;
    }
    function _pbTypes(cat, n) { return (PB_TYPES[cat] || {})[n] || []; }
    function _pbCurType(cat, n) {
      const key = cat + '/' + n;
      const types = _pbTypes(cat, n);
      if (!types.length) return null;
      if (!types.includes(_pb.type[key])) _pb.type[key] = types[0];
      return _pb.type[key];
    }

    // ══ the render ══════════════════════════════════════════════════════════
    function renderPostsBox(cause, ctx) {
      _ctCtx = { cause: cause, ctx: ctx };
      const stage = _ctStage(ctx);
      // The one key date, drawn all the way across the page.
      const dates = _ctDates(ctx);
      const startDay = dates[3];
      const started = startDay ? startDay.getTime() <= Date.now() : false;
      const line = document.getElementById('ct-startline');
      const label = document.getElementById('ct-startline-label');
      if (line && label) {
        line.classList.toggle('ct-startline--future', !started);
        label.textContent = (started ? 'Mission started · ' : 'Mission starts · ') +
          (startDay ? fmtDate(startDay) : 'date not set');
      }
      _pbPaint();
      // Data arrives after the frame does; repaint when it lands.
      const mission = ctx.mission || null;
      Promise.all([_ctLoadPosts(mission), _ctLoadOrgs(mission)]).then(_pbPaint);
      // The annulus follows the stage: initiative shares while the initiative
      // is being elected, the philanthropy race once it is.
      try { renderAnnulus(stage >= 3 ? 'me-oe' : 'pre-me'); } catch (e) {}
    }
    window.renderPostsBox = renderPostsBox;

    // ── the composer survives its own repaint ────────────────────────────────
    // Everything in the box repaints together, and an innerHTML swap throws
    // away whatever was typed into the composer. So a repaint CAPTURES the
    // fields into the cell's draft first, re-renders them from it, and puts the
    // caret back where it was. (Bug, 2026-08-12: "my dialogue is deleting every
    // time I try to link something from the rhs of the screen".)
    let _pbPainted = null;      // draft key the composer on screen belongs to
    function _pbCapture() {
      if (!_pbPainted) return;
      const d = _pb.draft[_pbPainted];
      if (!d) return;
      const val = id => { const el = document.getElementById(id); return el ? el.value : undefined; };
      const t = val('pb-title'); if (t !== undefined) d.title = t;
      const b = val('pb-body');  if (b !== undefined) d.body = b;
      Object.keys(PB_ROW_FIELDS).forEach(k => (PB_ROW_FIELDS[k] || []).forEach(([f]) => {
        const v = val('pb-row-' + f);
        if (v !== undefined) d.row[f] = v;
      }));
    }
    function _pbFocusState() {
      const el = document.activeElement;
      if (!el || !el.id || !/^pb-/.test(el.id)) return null;
      let pos = null;
      try { pos = el.selectionStart; } catch (e) {}
      return { id: el.id, pos: pos };
    }
    function _pbRestoreFocus(f) {
      if (!f) return;
      const el = document.getElementById(f.id);
      if (!el || typeof el.focus !== 'function') return;
      el.focus();
      if (f.pos !== null && f.pos !== undefined) {
        try { el.selectionStart = el.selectionEnd = f.pos; } catch (e) {}
      }
    }

    function _pbPaint() {
      const box = document.getElementById('pb');
      if (!box || !_ctCtx) return;
      _pbCapture();
      const focus = _pbFocusState();
      const cause = _ctCtx.cause, ctx = _ctCtx.ctx;
      const stage = _ctStage(ctx);
      const dates = _ctDates(ctx);
      const n = _pbCurPhase();
      const cat = _pb.cat;
      const type = _pbCurType(cat, n);
      // k carries the result that opened the stage the mission is in, notched
      // onto that stage's tab.
      const notch = _pbNotchTab(stage);

      // a–d — the phase tabs, each dated. This is the old rail, laid flat.
      const phaseTabs = PB_PHASES.map(p => {
        const st = p.n < stage ? 'past' : p.n === stage ? 'now' : 'future';
        return '<button type="button" role="tab" class="pb-tab pb-tab--' + st +
          (p.n === n ? ' pb-tab--on' : '') + (p.n === notch ? ' pb-tab--linked' : '') +
          '" data-phase="' + p.n + '"' +
          ' aria-selected="' + (p.n === n) + '" onclick="pbPhase(' + p.n + ')">' +
          '<span class="pb-tab__key">' + p.key + '</span>' +
          '<span class="pb-tab__name">' + _p3esc(p.name) + '</span>' +
          '<span class="pb-tab__date">' + _ctDateText(p.n, dates) +
            (st === 'now' ? ' · now' : '') + '</span></button>';
      }).join('');

      // e–g — the category tabs, grayed by the phase.
      const catTabs = PB_CATS.map(c => {
        const on = _pbCatEnabled(c.cat, n);
        const types = _pbTypes(c.cat, n).map(t => PB_LABEL[t]).join(' · ');
        return '<button type="button" role="tab" class="pb-tab pb-tab--cat' +
          (c.cat === cat ? ' pb-tab--on' : '') + (on ? '' : ' pb-tab--gray') + '"' +
          ' data-cat="' + c.cat + '" aria-selected="' + (c.cat === cat) + '"' +
          (on ? '' : ' disabled title="Opens when the initiative is elected"') +
          ' onclick="pbCat(\'' + c.cat + '\')">' +
          '<span class="pb-tab__key">' + c.key + '</span>' +
          '<span class="pb-tab__name">' + c.label + '</span>' +
          '<span class="pb-tab__date">' + (on ? _p3esc(types || '—') : 'grayed until the initiative is elected') +
          '</span></button>';
      }).join('');

      const set = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
      set('pb-results', _pbResults(notch, cause, ctx, dates));
      set('pb-types', _pbTypeRow(cat, n, type));
      set('pb-joint', _pbJoint(notch));
      set('pb-phase', phaseTabs);
      set('pb-compose', _pbCompose(cat, n, type, cause, stage, dates));
      set('pb-explain', _pbAbout(cat, n, type, cause, ctx, stage, dates));
      set('pb-cat', catTabs);
      set('pb-leading', _pbLeading(cat, n, type, cause, stage));
      _pbPainted = _pbDraftKey(cat, n, type);
      _pbBind();
      _pbRestoreFocus(focus);
    }

    window.pbPhase = function (n) { _pbCapture(); _pb.phase = n; _pb.msg = ''; _pb.pick = null; _pbPaint(); };
    window.pbCat = function (c) { _pbCapture(); _pb.cat = c; _pb.msg = ''; _pb.pick = null; _pbPaint(); };
    window.pbType = function (t) {
      _pbCapture();
      const n = _pbCurPhase();
      _pb.type[_pb.cat + '/' + n] = t;
      _pb.page[_pb.cat + '/' + n] = 0;
      _pb.msg = ''; _pb.pick = null;
      _pbPaint();
    };
    window.pbPage = function (d) {
      const n = _pbCurPhase(), key = _pb.cat + '/' + n;
      _pb.page[key] = Math.max(0, (_pb.page[key] || 0) + d);
      _pbPaint();
    };
    // ── k — THE RESULT THAT OPENED THE STAGE WE ARE IN ───────────────────────
    // "Results of previous section ... whichever section has the most recent
    //  date should be connected to this area visually", with the example
    //  "assume we are post initiative election and pre philanthropy election"
    //  and the notch drawn over tab c.
    //
    // The tab with the most recent PAST date is the stage the mission is in
    // right now — its date is the day it opened — so the notch sits there, and
    // the panel carries the election that opened it. At stage 3 that reads
    // "Initiative elected · {tiv}", exactly the drawing. k therefore does NOT
    // follow the tab you are browsing; you can read stage d's rules with the
    // result that is actually on the table still in front of you.
    //
    // §1 (2026-08-12): the POST-TYPE TOGGLE moved in here, beside the result —
    // "always show every post type, making only the available ones clickable".
    function _pbNotchTab(stage) { return stage; }
    function _pbJoint(notch) {
      return '<div class="pb-k__joint">' +
        PB_PHASES.map(p => '<i class="' + (p.n === notch ? 'on' : '') + '"></i>').join('') + '</div>';
    }
    function _pbResults(notch, cause, ctx, dates) {
      const mission = ctx.mission;
      const wrap = (eyebrow, name, sub, extra) =>
        '<div class="pb-k__head">' +
          '<span class="pb-k__eyebrow">' + eyebrow + '</span>' +
          '<span class="pb-k__date">' + _ctDateText(notch, dates) + '</span></div>' +
        '<div class="pb-k__name">' + name + '</div>' +
        (sub ? '<div class="pb-k__sub">' + sub + '</div>' : '') + (extra || '');
      const topOf = (key, label) => {
        const p = _ctPosts.posts.filter(q => _pbIs(q, key))
          .sort((a, b) => _ctScore(b) - _ctScore(a))[0];
        return p ? '<div class="pb-k__case"><b>' + label + ' · +' + _ctScore(p) + '</b>' +
          _p3esc(p.title || p.body || '') + '</div>' : '';
      };
      // stage 4 — the philanthropy election is the result on the table.
      if (notch >= 4) {
        return wrap('Philanthropy elected',
          _p3esc(mission && mission.winning_org_id ? _ctOrgName(mission.winning_org_id) : 'not recorded'),
          'Running <b>' + _p3esc(_ctTivName(mission && mission.winning_tiv_id)) + '</b> for ' +
          _p3esc(cause.name) + '. Budgeting is open.', topOf('case:phl', 'Top case · philanthropy'));
      }
      // stage 3 — the initiative election just decided; the philanthropy race
      // it opened runs until T+8wk.
      if (notch === 3) {
        return wrap('Initiative elected',
          _p3esc(mission && mission.winning_tiv_id ? _ctTivName(mission.winning_tiv_id) : 'not recorded'),
          'The philanthropy election it opened runs until <b>' +
          (dates[4] ? fmtDate(dates[4]) : '—') + '</b>.', topOf('case:tiv', 'Top case'));
      }
      // stage 2 — the cause vote is what opened the initiative election.
      const inits = (EBX.config.initiatives || []).filter(i =>
        i.cause_id === cause.id || i.cause_index === cause.index).length;
      const leader = ctx.leader;
      return wrap('Cause confirmed', _p3esc(cause.name),
        inits + ' initiative' + (inits === 1 ? '' : 's') + ' on the ballot' +
        (leader && leader.title ? ', leading <b>' + _p3esc(leader.title) + '</b>' : '') +
        '. The election closes on <b>' + (dates[3] ? fmtDate(dates[3]) : '—') + '</b>.',
        topOf('case:tiv', 'Top case'));
    }

    // ── b — THE TYPE TOGGLE, now in k ────────────────────────────────────────
    // Every type the CATEGORY has, always drawn; the ones this stage has not
    // opened are visible but not clickable, so the ladder a benefactor is
    // climbing is legible from any stage instead of appearing a tab at a time.
    function _pbTypeRow(cat, n, type) {
      const all = PB_CAT_TYPES[cat] || [];
      const open = _pbTypes(cat, n);
      return '<div class="pb-b__label">Post type</div>' + all.map(t => {
        const on = open.includes(t);
        return '<button type="button" class="dual-type' + (t === type ? ' on' : '') +
          (on ? '' : ' off') + '"' + (on ? '' : ' disabled title="' +
            _p3esc(_pbWhyShut(t, _ctStage(_ctCtx ? _ctCtx.ctx : null), _ctDates(_ctCtx ? _ctCtx.ctx : null))) + '"') +
          ' onclick="pbType(\'' + t + '\')">' + _p3esc(PB_LABEL[t]) + '</button>';
      }).join('');
    }

    // ── i — THE INPUT DIALOGUE ───────────────────────────────────────────────
    // The H+I detail drawing: a title (c) over the body (d), with the link
    // rails (e–i) down the right — "I'm talking about THIS", each chip pointing
    // at the entity it names.
    //   e linked initiatives → posts.tiv_id      f linked organizations → posts.org_id
    //   g budget items       → NO COLUMN — stub  h media → posts.image_url
    //   i external links     → NO COLUMN — stub
    //
    // §1 (2026-08-12), two rules from Jax:
    //   · RESEARCH REQUIRES NOTHING. A context/investigation/analysis post is
    //     about the mission you are reading, so it links itself; analysis also
    //     auto-links the elected initiative and philanthropy. The rails stay
    //     for anything MORE the author wants to point at.
    //   · BUDGETING HAS NO LINKS AT ALL. It is a costed list, not an argument
    //     about an entity.
    const PB_RAILS = [
      { key: 'tivs',     label: 'Linked Initiatives',   icon: '◆' },
      { key: 'phls',     label: 'Linked Organizations', icon: '🏛' },
      { key: 'budget',   label: 'Budget items',         icon: '🧾', stub: true },
      { key: 'media',    label: 'Media',                icon: '🖼' },
      { key: 'external', label: 'External links',       icon: '↗', stub: true },
    ];
    const _PB_DRAFT0 = () => ({ tivs: [], phls: [], budget: [], media: [], external: [],
                                title: '', body: '', rows: [], row: {} });
    function _pbDraftKey(cat, n, type) { return cat + '/' + n + '/' + (type || ''); }
    function _pbDraft() {
      const n = _pbCurPhase(), cat = _pb.cat;
      const k = _pbDraftKey(cat, n, _pbCurType(cat, n));
      return _pb.draft[k] || (_pb.draft[k] = _PB_DRAFT0());
    }
    // Only reviews require a link now.
    function _pbRequiredRail(type) {
      if (type === 'case:tiv') return 'tivs';
      if (['case:phl', 'evaluation'].includes(type)) return 'phls';
      return null;
    }
    // What a post links WITHOUT being asked: the mission it is written under,
    // and for analysis the initiative + philanthropy that mission elected.
    function _pbAutoLinks(type, ctx) {
      const m = ctx && ctx.mission;
      if (!m) return [];
      const out = [{ label: 'this mission', name: _ctTivName(m.winning_tiv_id) || m.id }];
      if (type === 'analysis') {
        if (m.winning_tiv_id) out.push({ label: 'initiative', name: _ctTivName(m.winning_tiv_id) });
        if (m.winning_org_id) out.push({ label: 'philanthropy', name: _ctOrgName(m.winning_org_id) });
      }
      return out;
    }

    function _pbCompose(cat, n, type, cause, stage, dates) {
      if (!type) {
        return '<div class="pb-shut">Budgeting opens when the initiative is elected on <b>' +
          (dates[3] ? fmtDate(dates[3]) : '—') + '</b>.</div>';
      }
      if (!_pbOpenNow(type, stage)) {
        return '<div class="pb-shut"><b>' + _p3esc(PB_LABEL[type]) + '</b> — ' +
          _p3esc(_pbWhyShut(type, stage, dates)) + '</div>';
      }
      const draft = _pbDraft();
      const send = '<div class="pb-c__foot">' +
        '<button class="election-card__commit-btn" style="padding:5px 14px;font-size:0.64rem;"' +
          ' onclick="pbSend()">Post</button>' +
        '<span id="pb-msg" class="p3-msg" style="margin:0;">' + _p3esc(_pb.msg) + '</span></div>';

      // ── budgeting: the row REPLACES the title, and the post is a list of rows
      if (cat === 'budgeting') {
        return '<div class="pb-c pb-c--wide">' +
          '<div class="pb-c__main">' + _pbRowEditor(type, draft) +
            '<textarea id="pb-body" class="pb-c__body" rows="3" placeholder="Why this is needed…">' +
              _p3esc(draft.body) + '</textarea>' + send +
          '</div></div>';
      }

      // ── research / reviews
      const req = _pbRequiredRail(type);
      const rail = PB_RAILS.map(r => {
        const nsel = (draft[r.key] || []).length;
        return '<button type="button" class="pb-rail__btn' + (req === r.key ? ' req' : '') + '"' +
          (r.stub ? ' disabled title="No field for this on a post yet — see the backlog"' : '') +
          ' onclick="pbPick(\'' + r.key + '\')">' +
          '<span>' + r.icon + '</span><span>' + r.label + (req === r.key ? ' *' : '') + '</span>' +
          (nsel ? '<span class="pb-rail__n">' + nsel + '</span>' : '') + '</button>';
      }).join('') + '<div class="pb-rail__note">Budget items and external links have no field on a ' +
        'post yet — they are drawn, not wired.</div>';
      const chips = ['tivs', 'phls', 'media'].map(k => (draft[k] || []).map((v, idx) =>
        '<span class="pb-chip">' + _p3esc(_pbChipLabel(k, v)) +
          '<button class="pb-chip__x" title="Unlink" onclick="pbUnlink(\'' + k + '\',' + idx + ')">✕</button>' +
        '</span>').join('')).join('');
      const auto = (cat === 'research') ? _pbAutoLinks(type, _ctCtx ? _ctCtx.ctx : null) : [];
      const autoLine = auto.length
        ? '<div class="pb-auto">Linked automatically: ' + auto.map(a =>
            '<b>' + _p3esc(a.name) + '</b> <i>(' + a.label + ')</i>').join(' · ') +
          '. Anything else is optional.</div>'
        : '';
      const editLine = (cat === 'research')
        ? '<div class="pb-auto pb-auto--edit">Already posted one? You get <b>one of each research ' +
          'type per mission</b> — <a href="profile.html">edit it on your profile &rarr;</a></div>'
        : '';

      return '<div class="pb-c">' +
        '<div class="pb-c__main">' +
          '<input id="pb-title" class="pb-c__title" type="text" placeholder="Post title" value="' +
            _p3esc(draft.title) + '" />' +
          '<textarea id="pb-body" class="pb-c__body" rows="4" placeholder="Write your ' +
            _p3esc((PB_LABEL[type] || type).toLowerCase()) + '…">' + _p3esc(draft.body) + '</textarea>' +
          autoLine + editLine +
          (chips ? '<div class="pb-chips">' + chips + '</div>' : '') +
          (_pb.pick ? _pbPicker(_pb.pick, cause, stage) : '') +
          send +
        '</div>' +
        '<div class="pb-rail">' + rail + '</div>' +
      '</div>';
    }

    // ── the budgeting row editor ─────────────────────────────────────────────
    // "Users toggle s/s/s and input into this: Service |Job|hourly_rate|
    //  days_needed| · Supply |Item|Supplier|Cost| · Support |Item|", and the
    // post carries the LIST of rows (posts.line_items, migration a1f6b3c92d47).
    const PB_ROW_FIELDS = {
      service: [['job', 'Job', 'text'], ['hourly_rate', 'Hourly rate ($)', 'number'],
                ['days_needed', 'Days needed', 'number']],
      supply:  [['item', 'Item', 'text'], ['supplier', 'Supplier', 'text'],
                ['cost', 'Cost ($)', 'number']],
      support: [['item', 'Item — approval, professional help, legal help…', 'text']],
    };
    function _pbRowEditor(kind, draft) {
      const fields = PB_ROW_FIELDS[kind] || [];
      const inputs = fields.map(([k, label, t]) =>
        '<input id="pb-row-' + k + '" class="p3-in pb-row__in' + (t === 'number' ? ' p3-in--num' : ' p3-in--grow') +
          '" type="' + t + '"' + (t === 'number' ? ' min="0" step="any"' : '') +
          ' placeholder="' + _p3esc(label) + '" value="' + _p3esc(draft.row[k] || '') + '" />').join('');
      const rows = (draft.rows || []).map((r, i) =>
        '<tr><td>' + fields.map(([k]) => _p3esc(r[k])).join('</td><td>') + '</td>' +
        '<td><button class="pb-chip__x" title="Remove" onclick="pbRowDel(' + i + ')">✕</button></td></tr>').join('');
      const total = _pbRowTotals(kind, draft.rows);
      return '<div class="pb-row">' + inputs +
          '<button class="election-card__commit-btn p3-btn" onclick="pbRowAdd()">+ Add</button></div>' +
        (rows
          ? '<table class="pb-tbl pb-tbl--draft"><thead><tr><th>' +
              fields.map(([, l]) => _p3esc(l)).join('</th><th>') + '</th><th></th></tr></thead>' +
              '<tbody>' + rows + '</tbody></table>' +
              (total ? '<div class="pb-tbl__total">' + total + '</div>' : '')
          : '<div class="pb-row__hint">Add at least one row — a suggestion is costed or it is not a ' +
            'suggestion.</div>');
    }
    function _pbRowTotals(kind, rows) {
      if (!rows || !rows.length) return '';
      const n = v => Number(v) || 0;
      if (kind === 'service') {
        const days = rows.reduce((t, r) => t + n(r.days_needed), 0);
        const cost = rows.reduce((t, r) => t + n(r.hourly_rate) * n(r.days_needed) * 8, 0);
        return days + ' day' + (days === 1 ? '' : 's') + ' · ' + _fmtCost(cost) +
               ' <i style="opacity:0.6;">(rate × days × 8h)</i>';
      }
      if (kind === 'supply') return _fmtCost(rows.reduce((t, r) => t + n(r.cost), 0));
      return rows.length + ' connection' + (rows.length === 1 ? '' : 's') + ' — no cost';
    }
    window.pbRowAdd = function () {
      const n = _pbCurPhase(), type = _pbCurType(_pb.cat, n), d = _pbDraft();
      const fields = PB_ROW_FIELDS[type] || [];
      const row = {};
      let missing = null;
      fields.forEach(([k, label]) => {
        const el = document.getElementById('pb-row-' + k);
        const v = el ? String(el.value || '').trim() : '';
        if (!v) missing = missing || label;
        row[k] = v;
      });
      if (missing) { _pb.msg = 'That row needs a value for “' + missing + '”.'; _pbPaint(); return; }
      d.rows.push(row);
      d.row = {};
      _pb.msg = '';
      _pbPaint();
    };
    window.pbRowDel = function (i) { _pbDraft().rows.splice(i, 1); _pbPaint(); };

    function _pbChipLabel(kind, v) {
      if (kind === 'tivs') return _ctTivName(v);
      if (kind === 'phls') return _ctOrgName(v);
      return String(v).slice(0, 40);
    }
    // The picker a rail button opens. Every option is an ENTITY on this page,
    // so a link is always a pointer at something the reader can open.
    function _pbPicker(kind, cause, stage) {
      const head = '<div class="pb-pick__head"><span>' +
        (kind === 'tivs' ? 'Link an initiative' : kind === 'phls' ? 'Link an organization' : 'Link media') +
        '</span><button class="pb-pick__close" onclick="pbPick(null)">✕</button></div>';
      if (kind === 'media') {
        return '<div class="pb-pick">' + head +
          '<div style="display:flex;gap:6px;">' +
            '<input id="pb-media-url" class="p3-in p3-in--grow" placeholder="Image URL…" />' +
            '<button class="election-card__commit-btn p3-btn" onclick="pbLinkMedia()">Attach</button>' +
          '</div></div>';
      }
      const opts = kind === 'tivs'
        ? (EBX.config.initiatives || [])
            .filter(i => i.cause_id === cause.id || i.cause_index === cause.index)
            .map(i => [i.id, _ctTivName(i.id)])
        : _ctOrgOptions(stage).map(o => [o.id, o.name]);
      const body = opts.length
        ? opts.map(([id, name]) => '<button class="pb-pick__opt" onclick="pbLink(\'' + kind +
            '\',\'' + _p3esc(id) + '\')">' + _p3esc(name) + '</button>').join('')
        : '<div class="pb-pick__empty">Nothing to link here yet.</div>';
      return '<div class="pb-pick">' + head + body + '</div>';
    }
    window.pbPick = function (kind) { _pb.pick = kind; _pbPaint(); };
    window.pbLink = function (kind, id) {
      const d = _pbDraft();
      if (!d[kind].includes(id)) d[kind].push(id);
      _pb.pick = null; _pbPaint();
    };
    window.pbLinkMedia = function () {
      const v = ((document.getElementById('pb-media-url') || {}).value || '').trim();
      if (!v) return;
      _pbDraft().media = [v];   // one image per post — posts.image_url is one column
      _pb.pick = null; _pbPaint();
    };
    window.pbUnlink = function (kind, idx) { _pbDraft()[kind].splice(idx, 1); _pbPaint(); };

    const _PB_SEND_CAT = {
      context: 'mission_support', investigation: 'mission_support', analysis: 'mission_support',
      'case:tiv': 'review', 'case:phl': 'review', evaluation: 'review',
      service: 'budgeting', supply: 'budgeting', support: 'budgeting',
    };
    window.pbSend = async function () {
      const n = _pbCurPhase(), cat = _pb.cat, type = _pbCurType(cat, n);
      const say = s => { _pb.msg = s; const el = document.getElementById('pb-msg'); if (el) el.textContent = s; };
      if (!type) return;
      _pbCapture();
      if (!_v2LoggedIn()) { say('Sign in to post.'); return; }
      const ctx = _ctCtx ? _ctCtx.ctx : {};
      const cause = _ctCtx ? _ctCtx.cause : null;
      const mission = ctx.mission || null;
      const draft = _pbDraft();
      const payload = {
        id: 'p-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 6),
        category: _PB_SEND_CAT[type] || 'mission_support',
        type: type.startsWith('case') ? 'case' : type,
        body: draft.body, author_type: 'ben',
        mission_id: mission ? mission.id : null,
        cause_id: cause ? cause.id : null,
      };
      if (!draft.body.trim()) { say('Write the post first.'); return; }
      if (cat === 'budgeting') {
        if (!draft.rows.length) { say('Add at least one row — a budget item is costed or it is not one.'); return; }
        payload.line_items = draft.rows.map(r => Object.assign({ kind: type }, r));
        payload.title = _pbRowTitle(type, draft.rows);
      } else {
        payload.title = draft.title.trim() || null;
        payload.image_url = draft.media[0] || null;
        // Research links itself: the mission is already on the payload, and
        // analysis takes the initiative and philanthropy that mission elected.
        payload.tiv_id = draft.tivs[0] || null;
        payload.org_id = draft.phls[0] || null;
        if (cat === 'research' && mission) {
          if (type === 'analysis') {
            payload.tiv_id = payload.tiv_id || mission.winning_tiv_id || null;
            payload.org_id = payload.org_id || mission.winning_org_id || null;
          }
        }
        const req = _pbRequiredRail(type);
        if (req && !(draft[req] || []).length) {
          say(req === 'tivs' ? 'Link the initiative this case is for — a case must name one.'
                             : 'Link the organization this post is about — this type requires one.');
          return;
        }
      }
      say('Posting…');
      try {
        const r = await EBX.Auth.fetchAuthed('/posts', { method: 'POST', body: JSON.stringify(payload) });
        if (r && !r.ok) {
          const d = await r.json().catch(() => ({}));
          say(d.detail || ('Failed (HTTP ' + r.status + ')')); return;
        }
      } catch (e) { say('Network error — try again.'); return; }
      _pb.msg = '';
      _pb.draft[_pbDraftKey(cat, n, type)] = _PB_DRAFT0();
      await _ctLoadPosts(mission, true);
      _pbPaint();
    };
    // A budgeting post's title is its list, so it is written rather than typed.
    function _pbRowTitle(kind, rows) {
      const first = rows[0] || {};
      const head = kind === 'service' ? first.job : first.item;
      return (rows.length > 1 ? head + ' +' + (rows.length - 1) + ' more' : head) || kind;
    }
    window.pbReact = async function (postId, value) {
      const say = s => { _pb.msg = s; const el = document.getElementById('pb-msg'); if (el) el.textContent = s; };
      if (!_v2LoggedIn()) { say('Sign in to rate posts.'); return; }
      try {
        const r = await EBX.Auth.fetchAuthed('/posts/' + postId + '/react',
          { method: 'POST', body: JSON.stringify({ value: value }) });
        if (r && !r.ok) {
          const d = await r.json().catch(() => ({}));
          say(d.detail || 'Could not rate that post.'); return;
        }
      } catch (e) { say('Network error — try again.'); return; }
      await _ctLoadPosts(_ctCtx && _ctCtx.ctx ? _ctCtx.ctx.mission : null, true);
      _pbPaint();
    };

    // ── h — ABOUT THE POST YOU ARE WRITING ───────────────────────────────────
    // "with the exception of budgeting, there is only 1 explanation per
    //  combined-tab-toggle" — one block per (category, phase), and for
    //  budgeting the three one-line table titles instead (Jax, 2026-08-12:
    //  "remove the target/open/reward/rating displays ... title each table in
    //  1 row, delete examples").
    function _pbExplainBlock(o) {
      return '<div class="pb-ex">' +
        '<div class="pb-ex__head"><span class="pb-ex__kind">' + _p3esc(o.kind) + '</span>' +
          '<h4 class="pb-ex__title">' + _p3esc(o.title) + '</h4></div>' +
        '<p class="pb-ex__body">' + o.body + '</p>' +
        (o.example ? '<div class="pb-ex__eg"><b>e.g.</b> ' + _p3esc(o.example) + '</div>' : '') +
        (o.meta ? '<div class="pb-meta">' + o.meta.map(([k, v]) =>
          '<span class="pb-meta__i"><span class="pb-meta__k">' + k + '</span>' +
          '<span class="pb-meta__v">' + v + '</span></span>').join('') + '</div>' : '') +
      '</div>';
    }
    function _pbAbout(cat, n, type, cause, ctx, stage, dates) {
      const mission = ctx.mission;
      const winTiv = mission && mission.winning_tiv_id ? _ctTivName(mission.winning_tiv_id) : null;
      const winOrg = mission && mission.winning_org_id ? _ctOrgName(mission.winning_org_id) : null;
      const tiv = _ctSelectedTiv(cause);
      const tivName = tiv ? _ctTivName(tiv.id) : 'the selected initiative';
      const on = d => d ? fmtDate(d) : '—';
      let out = '';

      if (n === 1) {
        out += _pbExplainBlock({
          kind: 'Cause confirmed', title: 'How a cause changes',
          body: 'The seven causes are the standing subjects everything else is elected inside, ' +
            'so a week of enthusiasm should not move one. A challenger has to win the same window ' +
            'in <b>6 successive votes</b>; lose one and the streak resets and the swap date moves ' +
            'back a full rotation. <b>' + _p3esc(cause.name) + '</b> was confirmed for the mission ' +
            'starting <b>' + on(dates[3]) + '</b>, somewhere in the 7–14 weeks before it.',
          meta: [['Target', 'the cause itself'],
                 ['Window', dates.range1 ? fmtRange(dates.range1.from, dates.range1.to) : '—'],
                 ['Reward', 'none — this stage is frame'],
                 ['Rating', 'n/a']],
        });
        out += '<div class="ct-frame">' + (cat === 'research'
          ? 'Research at this stage is <b>context</b> only — the background a voter needs before ' +
            'the initiative election opens.'
          : 'Reviews at this stage are the <b>case for an initiative</b>. The case for the CAUSE ' +
            'will live here once that logic is settled.') + '</div>';
        return out;
      }

      // BUDGETING — three tables, one titled row each. No target/open/reward/
      // rating chips: a budget item is not judged, it is bought.
      if (cat === 'budgeting') {
        return '<div class="pb-sss">' + ['service', 'supply', 'support'].map(k => {
          const m = _SSS_META[k];
          return '<div class="pb-sss__row' + (k === type ? ' on' : '') + '">' +
            '<span class="pb-sss__icon">' + m[0] + '</span>' +
            '<b class="pb-sss__kind">' + k + '</b>' +
            '<span class="pb-sss__what">' + m[1] + '</span></div>';
        }).join('') + '</div>' +
        '<div class="ct-secnote">Suggestions are open from the moment the initiative is elected; ' +
          (n === 4
            ? 'now the philanthropy is elected they are filtered to this mission and <b>' +
              _p3esc(winOrg || 'its philanthropy') + '</b>, and they can be voted on.'
            : 'they cannot be <b>voted on</b> until budgeting opens on <b>' + on(dates[4]) + '</b>.') +
          ' Budget threads are shared between benefactors and the philanthropy running the mission.' +
        '</div>';
      }

      const T = {
        context: {
          title: 'Context', kind: 'Research · opens at Mission open',
          body: 'Background that teaches voters about the initiatives and the news around them. ' +
            'It links itself to this mission — anything else you point at is optional — and it ' +
            'stays readable for the whole mission.',
          example: 'What the 2025 satellite survey actually measured, and what it left out.',
          meta: [['Target', 'this mission — linked automatically'],
                 ['Open', 'from ' + on(dates[2]) + ', onward'],
                 ['Reward', '1/32 of the pool — released with the advances'],
                 ['Rating', 'helpful · neutral · harmful']],
        },
        investigation: {
          title: 'Investigation', kind: 'Research · opens at Initiative elected',
          body: 'Digging into the philanthropies that would run the mission — leadership, ' +
            'proposal quality, credibility. Link the one you are investigating if it is about a ' +
            'single organization; the mission itself is linked for you.',
          example: 'Three years of this philanthropy’s filings, and where the overhead went.',
          meta: [['Target', 'this mission · an organization is optional'],
                 ['Open', 'from ' + on(dates[2]) + ' (early), through the race'],
                 ['Reward', '1/32 — winner decided at the end of phase 3'],
                 ['Rating', 'helpful · neutral · harmful']],
        },
        analysis: {
          title: 'Analysis', kind: 'Research · opens at Philanthropy elected',
          body: 'Combined research: an independent assessment of financials, track record or ' +
            'method, backing what context and investigation have gathered. It is linked to the ' +
            'elected initiative and philanthropy automatically. Never cost-based — costing ' +
            'belongs in budgeting.',
          example: 'Comparing the funded plan against two comparable programmes and their outcomes.',
          meta: [['Target', (winTiv || 'the initiative') + ' + ' + (winOrg || 'the philanthropy') +
                            ' — linked automatically'],
                 ['Open', 'from ' + on(dates[4]) + ', onward'],
                 ['Reward', '1/32 — winner decided after phase 3'],
                 ['Rating', 'helpful · neutral · harmful']],
        },
        'case:tiv': {
          title: 'Case for an initiative', kind: 'Reviews · opens at Mission open',
          body: 'Argues for one initiative in this cause — for or against. It must link the ' +
            'initiative it argues for (the cards beside the wheel start you on <b>' +
            _p3esc(tivName) + '</b>), because a case that names nothing cannot be counted for ' +
            'anything.',
          example: 'Why leak detection buys more tonnes per dollar than capture at this stage.',
          meta: [['Target', 'one initiative — required'],
                 ['Open', on(dates[2]) + ' → ' + on(dates[3])],
                 ['Reward', 'the most-fair case earns a direct line to Earthbux and the philanthropy'],
                 ['Rating', 'fair · unfair']],
        },
        'case:phl': {
          title: 'Case for a philanthropy', kind: 'Reviews · opens at Initiative elected',
          body: 'Argues for the organization that should run <b>' + _p3esc(winTiv || tivName) +
            '</b>. It is shown beside your case for the initiative and <b>the two are scored as ' +
            'one</b> — the post vote is the aggregate of the pair.',
          example: 'Why this philanthropy’s field presence beats the better-funded bid.',
          meta: [['Target', 'an organization — required'],
                 ['Open', on(dates[3]) + ' → ' + on(dates[4])],
                 ['Reward', 'aggregate score with your case for the initiative'],
                 ['Rating', 'fair · unfair']],
        },
        evaluation: {
          title: 'Evaluation', kind: 'Reviews · opens at Philanthropy elected',
          body: 'Reviews the elected organization’s effort on the mission once it is actually ' +
            'running it. Grayed out through the whole election — there is nothing to evaluate ' +
            'until someone is doing the work.',
          example: 'Six weeks in: what was promised in the plan, and what has been delivered.',
          meta: [['Target', winOrg ? _p3esc(winOrg) : 'the elected organization'],
                 ['Open', 'from ' + on(dates[4]) + ', onward'],
                 ['Reward', 'the most-fair evaluation earns a direct line to Earthbux and the philanthropy'],
                 ['Rating', 'fair · unfair']],
        },
      };
      // The explanation belongs to the CELL (the spec's "combined-tab-toggle"),
      // so it follows the type that stage opens — unless you have toggled to
      // another type in k, which is a direct request to read about that one.
      const opens = PB_OPENS[cat][n];
      const spec = T[type] || T[opens];
      if (spec) out += _pbExplainBlock(spec);
      if (cat === 'reviews' && n === 3) out += _pbAggregateCase(cause, ctx);
      return out;
    }

    // The benefactor's case for the initiative and their case for a
    // philanthropy, side by side with the aggregate the spec asks for:
    // "the post vote is the aggregate of the 2".
    function _pbAggregateCase(cause, ctx) {
      const tivCase = _ctPosts.posts.filter(p => _pbIs(p, 'case:tiv'))
        .sort((a, b) => _ctScore(b) - _ctScore(a))[0] || null;
      const phlCase = _ctPosts.posts.filter(p => _pbIs(p, 'case:phl'))
        .sort((a, b) => _ctScore(b) - _ctScore(a))[0] || null;
      if (!tivCase && !phlCase) return '';
      const agg = (tivCase ? _ctScore(tivCase) : 0) + (phlCase ? _ctScore(phlCase) : 0);
      const cell = (label, p) =>
        '<div class="ct-topcase" style="flex:1;min-width:0;margin-bottom:0;">' +
          '<div class="ct-topcase__label">' + label + (p ? ' · +' + _ctScore(p) : '') + '</div>' +
          '<div class="ct-topcase__body">' + (p ? _p3esc(p.body || '')
            : '<i style="opacity:0.6;">not written yet</i>') + '</div></div>';
      return '<div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 0;">' +
          cell('Case · initiative', tivCase) + cell('Case · philanthropy', phlCase) + '</div>' +
        '<div class="ct-moved">Aggregate score for the pair: ' +
          '<b style="color:var(--cause-color);">+' + agg + '</b></div>';
    }
    // ── j — THE LEADING POST, or the three budget tables ─────────────────────
    // "Leading post in that category for that mission" — the highest-rated one,
    // with a pager through the ranked rest, the reactions post_config declares
    // for the type, and the two filters the deleted P3 bands owned: a search
    // inside research, sort-by-organization inside reviews.
    // Budgeting is the exception Jax drew: "the 3 tables are displayed in the
    // area below" — service, supply and support, each titled in one row.
    function _pbRanked(cat, n) {
      const types = _pbTypes(cat, n);
      let list = _ctPosts.posts.filter(p => types.some(t => _pbIs(p, t)));
      if (cat === 'research' && _pb.search) {
        const q = _pb.search.toLowerCase();
        list = list.filter(p => ((p.title || '') + ' ' + (p.body || '')).toLowerCase().includes(q));
      }
      if (cat === 'reviews' && _pb.sortOrg !== 'all') {
        list = list.filter(p => _pb.sortOrg === '__tiv__' ? !p.org_id : String(p.org_id) === _pb.sortOrg);
      }
      return list.sort((a, b) => _ctScore(b) - _ctScore(a));
    }
    function _pbLeading(cat, n, type, cause, stage) {
      if (cat === 'budgeting') return _pbBudgetTables();
      const key = cat + '/' + n;
      const list = _pbRanked(cat, n);
      let i = Math.min(_pb.page[key] || 0, Math.max(0, list.length - 1));
      _pb.page[key] = i;
      const p = list[i] || null;
      const label = (cat === 'research' ? 'Research' : 'Reviews');

      let filter = '';
      if (cat === 'research') {
        filter = '<input id="pb-search" class="p3-in p3-in--search" placeholder="Search ' +
          label.toLowerCase() + '…" value="' + _p3esc(_pb.search) + '" />';
      } else {
        const groups = _pbReviewGroups();
        filter = '<select id="pb-sortorg" class="p3-in p3-in--sort">' +
          ['<option value="all">all organizations</option>']
            .concat(groups.map(g => '<option value="' + _p3esc(g.id) + '"' +
              (_pb.sortOrg === String(g.id) ? ' selected' : '') + '>' + _p3esc(g.name) + '</option>'))
            .join('') + '</select>';
      }
      const pager = '<span class="pb-pager">' +
        '<button ' + (i <= 0 ? 'disabled' : '') + ' onclick="pbPage(-1)">&lsaquo;</button>' +
        (list.length ? (i + 1) + ' of ' + list.length : '0') +
        '<button ' + (i >= list.length - 1 ? 'disabled' : '') + ' onclick="pbPage(1)">&rsaquo;</button></span>';

      let body;
      if (!p) {
        body = '<div class="phase-disc__empty">Nothing posted in ' + label.toLowerCase() +
          ' for this mission yet' + (_pb.search ? ' matching that search' : '') + '.</div>';
      } else {
        const t = _pbIs(p, 'case:phl') ? 'case:phl'
                : _pbIs(p, 'case:tiv') ? 'case:tiv' : _ctTypeOf(p);
        const re = p.tiv_id ? _ctTivName(p.tiv_id) : (p.org_id ? _ctOrgName(p.org_id) : '');
        const reacts = (PB_REACTIONS[t] || []).map(([v, lab]) =>
          '<button class="dual-react" onclick="pbReact(\'' + _p3esc(p.id) + '\',\'' + v + '\')">' +
            lab + ' · ' + (v === 'helpful' ? (p.helpful_count || 0)
              : v === 'harmful' ? (p.harmful_count || 0) : (p.neutral_count || 0)) + '</button>').join('');
        body = '<div class="pb-post">' +
          '<div class="phase-disc__meta"><b>' + _p3esc(PB_LABEL[t] || t) + '</b> · ' +
            new Date(p.created_at || Date.now()).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
            (re ? ' · re: ' + _p3esc(re) : '') + ' · ' + (_ctScore(p) >= 0 ? '+' : '') + _ctScore(p) +
            (i === 0 ? ' · leading' : '') + '</div>' +
          (p.title ? '<div class="pb-post__title">' + _p3esc(p.title) + '</div>' : '') +
          '<div class="pb-post__body">' + _p3esc(p.body || '') + '</div>' +
          '<div class="dual-post__actions">' + reacts +
            (cat === 'research'
              ? '<a class="dual-react" style="text-decoration:none;" href="profile.html">Edit yours &rarr;</a>'
              : '') +
          '</div></div>';
      }
      return '<div class="pb-j__bar"><span class="dual-panel__label">Leading ' + label.toLowerCase() +
          '</span>' + filter + pager + '</div>' + body;
    }

    // The three budget tables. Rows come from `posts.line_items` (migration
    // a1f6b3c92d47); pre-2026-08-12 budgeting posts have no rows, so they are
    // shown as a single row built from the post's own title and estimates
    // rather than dropped.
    function _pbBudgetTables() {
      return ['service', 'supply', 'support'].map(kind => {
        const fields = PB_ROW_FIELDS[kind];
        const meta = _SSS_META[kind];
        const rows = [];
        _ctPosts.posts.filter(p => _sssKind(p) === kind).forEach(p => {
          const items = (Array.isArray(p.line_items) && p.line_items.length)
            ? p.line_items : [_pbLegacyRow(kind, p)];
          items.forEach(it => rows.push({ p: p, it: it }));
        });
        rows.sort((a, b) => _score(b.p) - _score(a.p));
        const head = '<tr><th>' + fields.map(([, l]) => _p3esc(l)).join('</th><th>') +
          '</th><th>approval</th></tr>';
        const body = rows.length
          ? rows.map(({ p, it }) =>
              '<tr><td>' + fields.map(([k]) => _p3esc(_pbRowCell(k, it))).join('</td><td>') + '</td>' +
              '<td class="pb-tbl__act">' +
                '<button class="dual-react" onclick="pbReact(\'' + _p3esc(p.id) + '\',\'helpful\')">' +
                  'approve · ' + (p.helpful_count || 0) + '</button></td></tr>').join('')
          : '<tr><td colspan="' + (fields.length + 1) + '" class="pb-tbl__empty">' +
            'Nothing suggested yet.</td></tr>';
        return '<table class="pb-tbl">' +
          '<caption class="pb-sss__row"><span class="pb-sss__icon">' + meta[0] + '</span>' +
            '<b class="pb-sss__kind">' + kind + '</b>' +
            '<span class="pb-sss__what">' + meta[1] + '</span></caption>' +
          '<thead>' + head + '</thead><tbody>' + body + '</tbody></table>';
      }).join('');
    }
    function _pbRowCell(field, it) {
      const v = it ? it[field] : '';
      if (field === 'cost' || field === 'hourly_rate') return _fmtCost(v);
      if (field === 'days_needed') return _fmtSetup(v);
      return v === undefined || v === null || v === '' ? '—' : v;
    }
    function _pbLegacyRow(kind, p) {
      const text = p.title || (p.body || '').slice(0, 60);
      if (kind === 'service') {
        return { job: text, hourly_rate: null, days_needed: p.est_setup_days };
      }
      if (kind === 'supply') return { item: text, supplier: '—', cost: p.est_cost_usd };
      return { item: text };
    }

    // Reviews are grouped by the organizations running / registered for this
    // mission, with the INITIATIVE as its own group — a case can argue for the
    // initiative without naming one.
    function _pbReviewGroups() {
      const shares = (typeof causeOrgShares === 'function' ? causeOrgShares() : [])
        .filter(sh => !sh.isOther);
      const groups = shares.map(sh => ({ id: sh.org_id, name: sh.org_name }));
      _ctPosts.posts.forEach(p => {
        if (!p.org_id || groups.some(g => String(g.id) === String(p.org_id))) return;
        groups.push({ id: p.org_id, name: _ctOrgName(p.org_id) });
      });
      const leader = _ctCtx && _ctCtx.ctx ? _ctCtx.ctx.leader : null;
      groups.push({ id: '__tiv__', name: '◆ ' + ((leader && leader.title) || 'the initiative') });
      return groups;
    }
    function _pbBind() {
      const s = document.getElementById('pb-search');
      if (s) {
        s.oninput = () => {
          _pb.search = s.value;
          _pb.page[_pb.cat + '/' + _pbCurPhase()] = 0;
          _pbPaint();
        };
      }
      const so = document.getElementById('pb-sortorg');
      if (so) so.onchange = () => {
        _pb.sortOrg = so.value;
        _pb.page[_pb.cat + '/' + _pbCurPhase()] = 0;
        _pbPaint();
      };
    }

  EBX.PostsBox = {
    render: renderPostsBox,
    bind: _pbBind,
    repaint: _pbPaint,
    stage: _ctStage,
    dates: _ctDates,
    invalidate: function () { _ctPosts = { missionId: null, posts: [] }; },
    context: function () { return _ctCtx; },
  };
})(window.EBX = window.EBX || {});
