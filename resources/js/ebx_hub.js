/* ebx_hub.js — THE MISSIONS HUB (moved off Home in the 10/9 Reshuffle, 2026-10-09).
 *
 * "Home: Missions hub -> Missions." · "Profile will have a missions hub, but
 * instead of showing the leaders, it will show the selections of the user."
 *
 * One hub, two readings:
 *   EBX.Hub.mount(el, { mode: 'leaders' })   mission.html — who is leading each race
 *   EBX.Hub.mount(el, { mode: 'mine' })      profile.html — the choices hub: what YOU chose
 *
 * Rows: the seven causes, in wheel order (the cause whose newest organization
 * election is in week 6 at the top, week 0 at the bottom). Column 0: the
 * cause's open cause election (its first votable window on /causes/slate).
 * Then its missions, newest first. A mission's stage is read from its dates
 * (T = started_at + 7 weeks; T+8 organization elected; T+15 budget day):
 *   before T                 initiative election
 *   T … T+8, initiative won  organization election
 *   T+8 … T+15, org elected  prep
 *   after T+15               exchange
 *   a date passed with no winner → "no initiative / organization elected"
 * A card glows when its decision falls in this week. Collapsed (the default),
 * the hub shows this week's two elections — the initiative election and the
 * organization election that decide this week — each with its top three
 * (leaders) or with your vote beside the leader (mine).
 *
 * Needs ebx_shared.js and ebx_wheel.js (the data layer: missions, initiatives,
 * organizations, the slate, the organization tallies). Styles: ebx_frontend.css
 * § THE MISSIONS HUB. History: Home's own copy (P2 · Home mods 2026-09-30, the
 * Home pass 2026-10-01, P2 · Home 2026-10-05) — INSTRUCTIONS › ARCHIVE.
 */
(function () {
  'use strict';
  const E = window.EBX = window.EBX || {};
  const WK = 7 * 864e5;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const cfg = () => E.config || {};
  const Wh = () => E.Wheel || null;
  const fmt = d => d ? d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—';
  const tk = ct => { const t = (Number(ct) || 0) / 100; return Math.abs(t - Math.round(t)) < 0.05 ? String(Math.round(t)) : t.toFixed(1); };

  function weekEnd() {
    try {
      const n = E.Cycle.now();
      return new Date(E.config.cycleStart.getTime() + (n.weekNum + 1) * WK);
    } catch (e) { return new Date(Date.now() + WK); }
  }
  const thisWeek = d => { if (!d) return false; const e = weekEnd().getTime(), t = d.getTime(); return t > e - WK + 36e5 && t <= e + 36e5; };
  const tivTitle = id => { const t = (cfg().initiatives || []).find(i => i.id === id); return t ? t.title : (id || ''); };
  const orgName = id => { const o = (cfg().organizations || []).find(x => x.id === id); return o ? o.name : (id || ''); };
  const causeById = id => (cfg().causes || []).find(x => x.id === id) || null;
  function hrefOf(m) {
    try { if (E.Slug && E.Slug.href) return E.Slug.href(m); } catch (e) {}
    return 'mission.html?mission=' + encodeURIComponent(m.id);
  }

  function stageOf(m) {
    const d = E.Cycle.missionDates(m), T = d.missionStarted;
    const o8 = new Date(T.getTime() + 8 * WK), b15 = new Date(T.getTime() + 15 * WK);
    const now = Date.now(), wk = Math.max(0, Math.floor((now - T.getTime()) / WK));
    if (now < T.getTime()) return { key: m.winning_tiv_id ? 'oe' : 'me', T, o8, b15, wk: null, when: m.winning_tiv_id ? o8 : T };
    if (!m.winning_tiv_id) return { key: 'no-tiv', T, o8, b15, wk };
    if (now < o8.getTime()) return { key: 'oe', T, o8, b15, wk, when: o8 };
    if (!m.winning_org_id) return { key: 'no-org', T, o8, b15, wk };
    if (now < b15.getTime()) return { key: 'fr', T, o8, b15, wk, when: b15 };
    return { key: 'ex', T, o8, b15, wk };
  }
  // 10/9 Reshuffle: Framing reads "Prep" everywhere a reader sees it.
  const PHASE = { me: 'Initiative election', oe: 'Organization election', fr: 'Prep', ex: 'Exchange',
                  'no-tiv': 'Initiative election · closed', 'no-org': 'Organization election · closed' };

  function meLeaders(m) {
    const ins = (cfg().initiatives || []).filter(i => i.mission_id === m.id)
      .sort((a, b) => (b.committed_ebx || 0) - (a.committed_ebx || 0));
    const pool = ins.reduce((a, i) => a + (i.committed_ebx || 0), 0);
    return { ins, pool };
  }
  function oeEntries(m) {
    const t = Wh() && Wh().p2Tally ? Wh().p2Tally(m.id) : null;
    return ((t && t.entries) || []).slice().sort((a, b) => (b.net_votes || 0) - (a.net_votes || 0) || (b.ebx || 0) - (a.ebx || 0));
  }

  // ── what a card says about YOU (mode 'mine') ─────────────────────────
  // `p` is your position in the mission (GET /wallet/positions), or null.
  function mineLine(m, s, p) {
    if (s.key === 'me') {
      const sh = p && p.me && p.me.shares ? Object.entries(p.me.shares).sort((a, b) => b[1] - a[1]) : [];
      if (!sh.length) return { you: false, text: 'No vote yet · 10 granted tokens waiting' };
      return { you: true, text: 'You: ' + tivTitle(sh[0][0]) + ' ' + Math.round(sh[0][1] * 100) + '%' +
        (sh.length > 1 ? ' +' + (sh.length - 1) : '') + ' · ' + tk(p.me.ct) + ' tk' };
    }
    if (s.key === 'no-tiv') return { you: !!(p && p.me && p.me.ct), text: 'No initiative was elected' };
    if (s.key === 'oe') {
      if (p && p.oe && p.oe.org_id) return { you: true, text: 'You: ' + orgName(p.oe.org_id) + (p.stake_ct ? ' · ' + tk(p.stake_ct) + ' tk' : ' · 1 vote') };
      if (p && p.coin !== 'none') return { you: true, text: 'Member · pick an organization' + (p.stake_ct ? ' · ' + tk(p.stake_ct) + ' tk' : '') };
      return { you: false, text: 'Your one vote is not cast' };
    }
    if (s.key === 'no-org') return { you: !!(p && p.stake_ct), text: 'No organization was elected' };
    if (p && p.stake_ct > 0) return { you: true, text: 'You hold ' + tk(p.stake_ct) + ' EBX' + (p.oe && p.oe.org_id ? ' · voted ' + orgName(p.oe.org_id) : '') };
    return { you: false, text: 'Not a member' };
  }

  function makeHub(root, opts) {
    const mode = opts.mode === 'mine' ? 'mine' : 'leaders';
    const KEY = opts.key || (mode === 'mine' ? 'ebx_hub_mine_open' : 'ebx_hub_open3');
    const st = { off: 0, open: !!opts.open, slate: null, rows: [], cols: 1, vis: 1, pos: {}, causeVotes: {}, authed: false };
    try { const v = localStorage.getItem(KEY); if (v != null) st.open = v === '1'; } catch (e) {}
    const TITLE_WEEK = mode === 'mine' ? 'Your choices this week' : 'This Week’s Decisions';
    const TITLE_ALL = mode === 'mine' ? 'Your choices, every mission' : 'All missions';
    root.classList.add('mh');
    if (mode === 'mine') root.classList.add('mh--mine');
    root.innerHTML =
      '<div class="mh__head">' +
        '<h2 class="mh__title" data-hub="title">' + TITLE_WEEK + '</h2>' +
        '<div class="mh__nav" data-hub="nav">' +
          '<button type="button" class="mh__btn mh__btn--page" data-mh="-page" aria-label="Back one page">&laquo;</button>' +
          '<button type="button" class="mh__btn" data-mh="-1" aria-label="Back one column">&lsaquo;</button>' +
          '<button type="button" class="mh__btn" data-mh="1" aria-label="On one column">&rsaquo;</button>' +
          '<button type="button" class="mh__btn mh__btn--page" data-mh="page" aria-label="On one page">&raquo;</button>' +
          '<button type="button" class="mh__btn mh__toggle" data-hub="toggle" aria-expanded="false">Show all missions</button>' +
        '</div>' +
      '</div>' +
      '<div class="mh__week" data-hub="week"></div>' +
      '<div class="mh__body" data-hub="body" hidden><div class="mh__loading">Loading the missions&hellip;</div></div>';
    const $ = k => root.querySelector('[data-hub="' + k + '"]');

    function missionCard(m, c) {
      const s = stageOf(m), n = c.name + ' ' + ((m.cycle_num || 0) + 1);
      const K = PHASE[s.key];
      let title, line, when = '';
      if (s.key === 'me') {
        const { ins, pool } = meLeaders(m);
        const lead = ins[0];
        title = n;
        line = lead ? 'Leading: ' + lead.title + (pool ? ' · ' + Math.round((lead.committed_ebx || 0) / pool * 100) + '%' : '') +
          ' · ' + ins.length + ' initiative' + (ins.length === 1 ? '' : 's') : 'No initiatives yet';
        when = 'closes ' + fmt(s.T);
      } else if (s.key === 'no-tiv') {
        title = n; line = 'No initiative was elected'; when = 'closed ' + fmt(s.T);
      } else {
        title = tivTitle(m.winning_tiv_id);
        if (s.key === 'oe') {
          const es = oeEntries(m);
          const cands = Wh() && Wh().candidacies ? Wh().candidacies(m.id).length : 0;
          line = es.length ? 'Leading: ' + orgName(es[0].org_id) : (cands ? cands + ' nominated' : 'No organizations yet');
          when = 'closes ' + fmt(s.o8);
        } else if (s.key === 'no-org') {
          line = 'No organization was elected'; when = 'closed ' + fmt(s.o8);
        } else if (s.key === 'fr') {
          line = orgName(m.winning_org_id); when = 'budget day ' + fmt(s.b15);
        } else {
          line = orgName(m.winning_org_id); when = 'coin ' + (Number(m.credit_value) || 1).toFixed(2);
        }
      }
      let you = null;
      if (mode === 'mine') { you = mineLine(m, s, st.pos[m.id] || null); line = you.text; }
      const now = !!(s.when && thisWeek(s.when));
      if (now) when = (s.key === 'fr' ? 'budget day ' : 'decides ') + fmt(s.when);
      const started = E.Cycle.missionDates(m).startedAt;
      return { now, html: '<a class="mc mc--' + s.key + (now ? ' mc--now' : '') + (/^no-/.test(s.key) ? ' mc--stalled' : '') +
        (you ? (you.you ? ' mc--you' : ' mc--notyou') : '') +
        '" style="--c:' + esc(c.color) + '" href="' + esc(hrefOf(m)) + '" data-mission="' + esc(m.id) + '" title="' + esc(n + (now ? ' — decided this week' : '')) + '">' +
        '<span class="mc__k">' + esc(K + (when ? ' · ' + when : '')) + '</span>' +
        '<span class="mc__t">' + esc(title) + '</span>' +
        '<span class="mc__l">' + esc(line) + '</span>' +
        '<span class="mc__f"><span><b>' + esc(c.name) + '</b> · started ' + esc(fmt(started)) + '</span></span></a>' };
    }

    // A window becomes the mission of the cause that holds it. 10/9 Reshuffle:
    // its number is read from the window itself (the week its initiative
    // election opens), so the window whose election opened this week reads
    // "Land 4", not one past it.
    function windowName(c, slot) {
      const holderId = slot && slot.holder_id ? slot.holder_id : c.id;
      const holder = causeById(holderId) || { id: holderId, name: (slot && slot.holder_name) || holderId };
      if (holder.id !== ((slot && slot.incumbent_id) || c.id)) return holder.name;
      let w = 0; try { w = E.Cycle.now().weekNum; } catch (e) {}
      const opens = w + Number(slot && slot.weeks_out || 7) - 7;
      return holder.name + ' ' + (Math.floor(Math.max(0, opens) / 7) + 1);
    }
    function ceCard(c) {
      const sl = st.slate, slot = sl ? (sl.slots || []).find(s => s.votable && s.incumbent_id === c.id) : null;
      if (!slot) return { now: false, html: '<a class="mc mc--ce" style="--c:' + esc(c.color) + '" href="mission.html?state=ce&amp;cause=' + encodeURIComponent(c.id) + '">' +
        '<span class="mc__k">Cause election</span><span class="mc__t">' + esc(c.name) + '</span><span class="mc__l">no window open</span><span class="mc__f"><span><b>' + esc(c.name) + '</b></span></span></a>' };
      const ch = slot.challenger_id ? causeById(slot.challenger_id) : null;
      const wait = slot.weeks_out - (sl.first_open_slot || slot.weeks_out);
      const now = wait === 0;
      let line = ch ? esc(ch.name) + ' challenging · ' + (slot.streak || 0) + '/' + (slot.weeks_required || 6) : 'no challenger';
      let youCls = '';
      if (mode === 'mine') {
        const v = st.causeVotes[String(slot.slot)];
        const vc = v ? causeById(v) : null;
        line = v ? 'You: ' + esc(vc ? (vc.id === c.id ? 'keep ' + vc.name : vc.name) : v) : 'No vote this week';
        youCls = v ? ' mc--you' : ' mc--notyou';
      }
      return { now, html: '<a class="mc mc--ce' + (now ? ' mc--now' : '') + youCls + '" style="--c:' + esc(c.color) + '" href="mission.html?slot=' + slot.slot + '" data-slot="' + slot.slot + '"' +
        (now ? ' title="Decided this week"' : '') + '>' +
        '<span class="mc__k">Cause election · ' + (now ? 'confirmed this week' : 'confirms in ' + wait + ' wk' + (wait === 1 ? '' : 's')) + '</span>' +
        '<span class="mc__t">' + esc(windowName(c, slot)) + '</span>' +
        '<span class="mc__l">' + line + '</span>' +
        '<span class="mc__f"><span><b>' + esc(c.name) + '</b> · ' + slot.weeks_out + ' wks out</span></span></a>' };
    }

    // "The current cause with a mission in week 0 should be the bottom row of
    // the hub, and week 6 should be the top row." (Home pass, 2026-10-01)
    function weekOf(c) {
      let a = 0; try { a = E.Cycle.now().causeIndex; } catch (e) {}
      return ((a - c.index) % 7 + 7) % 7;
    }
    function build() {
      const cs = (cfg().causes || []).slice().sort((a, b) => weekOf(b) - weekOf(a));
      st.rows = cs.map(c => {
        const ms = (cfg().missions || []).filter(m => m.cause_id === c.id)
          .sort((a, b) => new Date(b.started_at) - new Date(a.started_at) || (b.cycle_num || 0) - (a.cycle_num || 0));
        return { c, cells: [ceCard(c)].concat(ms.map(m => missionCard(m, c))) };
      });
      st.cols = Math.max(1, ...st.rows.map(r => r.cells.length));
    }

    // Collapsed: this week's initiative election and organization election.
    function weekPair() {
      const all = (cfg().missions || []).map(m => ({ m, s: stageOf(m), c: causeById(m.cause_id) }))
        .filter(x => x.c && x.s.when);
      const pick = key => {
        const xs = all.filter(x => x.s.key === key && x.s.when.getTime() > Date.now() - 36e5)
          .sort((a, b) => a.s.when - b.s.when);
        return xs.find(x => thisWeek(x.s.when)) || xs[0] || null;
      };
      return [pick('me'), pick('oe')];
    }
    function leaders(x) {
      if (x.s.key === 'me') {
        const { ins, pool } = meLeaders(x.m);
        return ins.slice(0, 3).map(i => ({ name: i.title, val: Math.round(i.committed_ebx || 0) + ' tokens' + (pool ? ' · ' + Math.round((i.committed_ebx || 0) / pool * 100) + '%' : '') }));
      }
      const es = oeEntries(x.m);
      if (es.length) return es.slice(0, 3).map(e => ({ name: orgName(e.org_id), val: (e.net_votes || 0) + ' vote' + ((e.net_votes || 0) === 1 ? '' : 's') }));
      const cands = Wh() && Wh().candidacies ? Wh().candidacies(x.m.id) : [];
      return cands.slice(0, 3).map(c => ({ name: orgName(c.org_id), val: '0 votes' }));
    }
    function paintWeek() {
      const el = $('week');
      el.hidden = st.open;
      if (st.open) return;
      const HEAD = { me: 'Initiative Election', oe: 'Organization Election' };
      const LEAD = { me: 'Leading initiative', oe: 'Leading organization' };
      const pair = weekPair();
      el.innerHTML = ['me', 'oe'].map((key, i) => {
        const x = pair[i];
        let card;
        if (!x) card = '<div class="mh__loading">No ' + HEAD[key].toLowerCase() + ' is open.</div>';
        else {
          const ls = leaders(x), now = thisWeek(x.s.when), top = ls[0], rest = ls.slice(1);
          const what = x.c.name + ' ' + ((x.m.cycle_num || 0) + 1) + (key === 'oe' ? ' · ' + tivTitle(x.m.winning_tiv_id) : '');
          let youRow = '';
          if (mode === 'mine') {
            const y = mineLine(x.m, x.s, st.pos[x.m.id] || null);
            youRow = '<span class="mw__you' + (y.you ? '' : ' mw__you--none') + '"><em>Your vote</em>' + esc(y.text.replace(/^You: /, '')) + '</span>';
          }
          card = '<a class="mw mw--' + key + (now ? ' mc--now' : '') + '" style="--c:' + esc(x.c.color) + '" href="' + esc(hrefOf(x.m)) + '" data-mission="' + esc(x.m.id) + '">' +
            '<span class="mw__top"><span class="mw__k">' + esc(what) + '</span><span class="mw__d">' + (now ? 'decides ' : 'closes ') + fmt(x.s.when) + '</span></span>' +
            youRow +
            (top ? '<span class="mw__t"><em>' + LEAD[key] + '</em>' + esc(top.name) + '<small>' + esc(top.val) + '</small></span>' +
                   (rest.length && mode !== 'mine' ? '<span class="mw__lab">Runners-up</span><ol class="mw__lead" start="2">' + rest.map((l, k) => '<li><i>' + (k + 2) + '</i><span>' + esc(l.name) + '</span><b>' + esc(l.val) + '</b></li>').join('') + '</ol>' : '')
                 : '<span class="mw__t"><em>' + LEAD[key] + '</em>&mdash;</span><span class="mw__none">' + (key === 'me' ? 'No initiatives yet' : 'No organizations nominated yet') + '</span>') +
          '</a>';
        }
        return '<div class="mh__wcol"><div class="mh__wh">' + HEAD[key] + '</div>' + card + '</div>';
      }).join('');
    }

    function paint() {
      const body = $('body');
      body.hidden = !st.open;
      paintWeek();
      $('toggle').textContent = st.open ? 'Collapse missions' : 'Show all missions';
      $('toggle').setAttribute('aria-expanded', String(st.open));
      $('title').textContent = st.open ? TITLE_ALL : TITLE_WEEK;
      const w = body.clientWidth || root.clientWidth || 1000;
      st.vis = Math.max(1, Math.min(st.cols, Math.floor((w + 10) / 196)));
      st.off = Math.max(0, Math.min(st.off, st.cols - st.vis));
      root.querySelectorAll('[data-hub="nav"] [data-mh]').forEach(b => {
        const d = b.dataset.mh, back = d.charAt(0) === '-';
        b.disabled = !st.open || (back ? st.off <= 0 : st.off >= st.cols - st.vis);
        b.hidden = !st.open;
      });
      if (!st.open) return;
      const cols = Array.from({ length: st.vis }, (_, k) => st.off + k);
      let html = '<div class="mh__grid" style="grid-template-columns:repeat(' + st.vis + ', minmax(0, 1fr))">';
      st.rows.forEach(r => {
        html += cols.map(k => r.cells[k] ? r.cells[k].html : '<span class="mc--empty" aria-hidden="true"></span>').join('');
      });
      body.innerHTML = html + '</div>';
    }

    $('nav').addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b || b.disabled) return;
      if (b.dataset.hub === 'toggle') {
        st.open = !st.open;
        try { localStorage.setItem(KEY, st.open ? '1' : '0'); } catch (e2) {}
      } else {
        const d = b.dataset.mh, sgn = d.charAt(0) === '-' ? -1 : 1;
        st.off += sgn * (/page/.test(d) ? st.vis : 1);
      }
      paint();
    });
    let rt = 0;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { if (st.rows.length) paint(); }, 120); });

    async function loadMine() {
      st.authed = !!(E.Auth && E.Auth.isLoggedIn && E.Auth.isLoggedIn());
      if (!st.authed) return;
      try {
        const r = await E.Auth.fetchAuthed('/wallet/positions');
        if (r && r.ok) (await r.json()).forEach(p => { st.pos[p.mission_id] = p; });
      } catch (e) {}
      try {
        const r = await E.Auth.fetchAuthed('/causes/vote/mine');
        if (r && r.ok) { const v = await r.json(); st.causeVotes = (v && typeof v === 'object') ? (v.votes || v) : {}; }
      } catch (e) {}
    }
    async function load() {
      const body = $('body');
      if (!Wh()) { body.innerHTML = '<div class="mh__loading">The missions are unavailable right now.</div>'; return; }
      await Promise.all([Wh().data(), mode === 'mine' ? loadMine() : null]);
      st.slate = (Wh()._state && Wh()._state.slate) || null;
      try { if (E.Slug && E.Slug.load) await E.Slug.load(); } catch (e) {}
      if (!(cfg().causes || []).length) { body.innerHTML = '<div class="mh__loading">The missions are unavailable right now.</div>'; return; }
      build(); paint();
    }
    const api = { state: st, reload: load, stageOf, thisWeek, weekOf, weekPair, windowName, mode, root };
    load();
    return api;
  }

  E.Hub = { mount: (el, opts) => {
    const root = typeof el === 'string' ? document.querySelector(el) : el;
    return root ? makeHub(root, opts || {}) : null;
  }, PHASE };
})();
