/* ebx_report.js — ONE MISSION'S REPORT, and its thread (moved off the mission
 * page in the 10/9 Reshuffle, 2026-10-09).
 *
 * Jax: "Mission: Report -> home *use new report" — Home carries the new weekly
 * report — and (2026-10-09) the mission's own report goes to NEWS: "When News
 * is filtered to a mission, that mission's report sits above its posts."
 *
 * What it is (review 2, 2026-09-25, unchanged): "The mission progress report
 * becomes a self-improving document thanks to widespread community
 * improvements." The member-generated combination of the LEADING post of each
 * category — a mission statement, a plan, and Background · Investigation ·
 * Analysis. Clicking it opens the thread, where every research post (and the
 * budget items) can be read, rated, replied to — and written (post.html).
 *
 *   EBX.MissionReport.mount(el, missionId [, { color }])   paint it into `el`
 *   EBX.MissionReport.openThread(section?)                   'context' | 'investigation' | 'analysis' | 'budget'
 *
 * The thread and the reply composer are injected into <body> the first time
 * they are needed. Styles: ebx_frontend.css § THE MISSION REPORT. Ported from
 * mission.html's MB module (renderReport, budgetHTML, the thread, the reply
 * composer, the rating) — INSTRUCTIONS › REMOVAL REGISTER › Added 2026-10-09.
 */
(function () {
  'use strict';
  const E = window.EBX = window.EBX || {};
  const esc = s => String(s === null || s === undefined ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const fmtD = d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  const loggedIn = () => !!(E.Auth && E.Auth.isLoggedIn && E.Auth.isLoggedIn());
  const money = n => '$' + Math.round(Number(n) || 0).toLocaleString();
  async function jget(url) {
    try { const r = await fetch(url); return r.ok ? await r.json() : null; } catch (e) { return null; }
  }
  const TYPE_WORD = { context: 'Background', investigation: 'Investigation', analysis: 'Analysis',
                      service: 'Service', supply: 'Supply', support: 'Support' };
  const SECTIONS = [['context', 'Background', 'the cause, and the news around it'],
                    ['investigation', 'Investigation', 'the organization that would run it — leadership, proposal, credibility'],
                    ['analysis', 'Analysis', 'the initiative and the organization together']];
  const BUDGET_SEC = ['budget', 'Budget', 'what the mission needs, and what it costs'];
  const score = p => (Number(p.helpful_count) || 0) - (Number(p.harmful_count) || 0);
  const byScore = (a, b) => (score(b) - score(a)) || (new Date(b.created_at) - new Date(a.created_at));
  function costLine(p) {
    const bits = [];
    if (p.est_cost_usd != null) bits.push(money(p.est_cost_usd));
    if (p.est_setup_days != null && Number(p.est_setup_days) > 0) bits.push(Math.round(p.est_setup_days * 10) / 10 + ' days');
    return bits.join(' · ');
  }
  function excerpt(p, n) { const b = p.body || ''; return esc(b.slice(0, n)) + (b.length > n ? '…' : ''); }
  function rateHTML(p) {
    return '<span class="mb-rate" data-post="' + esc(p.id) + '">' +
      '<button type="button" data-val="helpful" title="Helpful">&#9650; ' + (p.helpful_count || 0) + '</button>' +
      '<button type="button" data-val="neutral" title="Neutral">&#9679; ' + (p.neutral_count || 0) + '</button>' +
      '<button type="button" data-val="harmful" title="Harmful">&#9660; ' + (p.harmful_count || 0) + '</button></span>';
  }

  // ── state: one mission at a time ────────────────────────────────────────
  const S = { mid: null, el: null, seq: 0, mission: null, cause: null, winningTiv: null, steps: [],
              candidacies: [], tally: {}, orgsById: {}, budget: [], research: [], color: null };
  const mname = () => S.winningTiv ? S.winningTiv.title
    : ((S.cause ? S.cause.name : (S.mission ? S.mission.cause_id : '')) + ' ' + (((S.mission && S.mission.cycle_num) || 0) + 1));

  async function load(seq) {
    S.mission = await jget('/missions/' + encodeURIComponent(S.mid));
    if (seq !== S.seq || !S.mission) return;
    S.cause = (E.config && (E.config.causes || []).find(c => c.id === S.mission.cause_id)) || null;
    S.winningTiv = S.mission.winning_tiv_id ? await jget('/initiatives/' + encodeURIComponent(S.mission.winning_tiv_id)) : null;
    const [st, cands, t, orgs, budget, research] = await Promise.all([
      jget('/missions/' + S.mid + '/steps'),
      jget('/candidacies?mission_id=' + S.mid),
      jget('/missions/' + S.mid + '/p2/tally'),
      ((E.config && E.config.organizations) || []).length ? null : jget('/organizations'),
      jget('/posts?mission_id=' + S.mid + '&category=budgeting&roots_only=true&limit=40'),
      jget('/posts?mission_id=' + S.mid + '&category=mission_support&roots_only=true&limit=60'),
    ]);
    if (seq !== S.seq) return;
    S.steps = st || []; S.candidacies = cands || [];
    S.tally = {}; ((t && t.entries) || []).forEach(e => { S.tally[e.org_id] = e; });
    S.orgsById = {}; (orgs || (E.config && E.config.organizations) || []).forEach(o => { S.orgsById[o.id] = o; });
    S.budget = (budget || []).sort(byScore);
    S.research = (research || []).sort(byScore);
  }
  async function msPost(tivId) {
    const rows = (await jget('/posts?tiv_id=' + encodeURIComponent(tivId) + '&tag=mission_statement&roots_only=true&limit=20&sort=hot')) || [];
    return rows.slice().sort((a, b) => score(b) - score(a))[0] || null;
  }

  // ── the report: the leading post of each category ───────────────────────
  async function paintReport() {
    const m = S.mission, el = S.el;
    if (!el) return;
    if (!m) { el.innerHTML = ''; el.hidden = true; return; }
    el.hidden = false;
    const won = m.winning_org_id ? S.candidacies.find(c => c.org_id === m.winning_org_id) : null;
    const lead = !won && S.candidacies.length ? S.candidacies.slice().sort((a, b) =>
      ((S.tally[b.org_id] || {}).net_votes || 0) - ((S.tally[a.org_id] || {}).net_votes || 0))[0] : null;
    let statement, ms = null;
    if (won && (won.mission_statement || '').trim()) {
      statement = '<p class="mb-report__quote">&ldquo;' + esc(won.mission_statement.trim()) + '&rdquo;</p>' +
        '<p class="mb-report__by">' + esc((S.orgsById[won.org_id] || {}).name || won.org_id) + ', elected to run it</p>';
    } else if (lead && (lead.mission_statement || '').trim()) {
      statement = '<p class="mb-report__quote">&ldquo;' + esc(lead.mission_statement.trim()) + '&rdquo;</p>' +
        '<p class="mb-report__by">' + esc((S.orgsById[lead.org_id] || {}).name || lead.org_id) + ' — leading the organization election</p>';
    } else if (S.winningTiv && (ms = await msPost(S.winningTiv.id))) {
      statement = '<p class="mb-report__quote">&ldquo;' + esc(String(ms.body || '').trim()) + '&rdquo;</p>' +
        '<p class="mb-report__by">' + esc(ms.author_handle || ms.author_name || 'a benefactor') +
        ' &middot; &#9650; ' + (ms.helpful_count || 0) + ' &middot; the leading mission statement, until an organization writes one</p>';
    } else if (S.winningTiv && S.winningTiv.description) {
      statement = '<p>' + esc(S.winningTiv.description) + '</p><p class="mb-report__by">the initiative&rsquo;s own case, until an organization writes one</p>';
    } else {
      statement = '<p class="mb-report__empty">Written by the organization once one is elected. Until then, the initiative election decides what this mission is.</p>';
    }
    let plan;
    const top = S.budget.slice(0, 4);
    if ((S.steps || []).length) {
      plan = '<ol class="mb-report__plan">' + S.steps.slice(0, 6).map(st => '<li>' + esc(st.title || st.name || 'step') +
        (st.status ? ' <small>' + esc(st.status) + '</small>' : '') + '</li>').join('') + '</ol>';
    } else if (top.length) {
      const total = top.reduce((a, p) => a + (Number(p.est_cost_usd) || 0), 0);
      plan = '<ol class="mb-report__plan">' + top.map(p => '<li><b>' + esc(p.title || TYPE_WORD[p.type]) + '</b> <small>' +
        esc(TYPE_WORD[p.type] || '') + (costLine(p) ? ' · ' + esc(costLine(p)) : '') + '</small></li>').join('') + '</ol>' +
        '<p class="mb-report__by">the leading ' + top.length + ' of ' + S.budget.length + ' budget items · ' + money(total) + '</p>';
    } else {
      plan = m.winning_tiv_id
        ? '<p class="mb-report__empty">No budget items yet — the plan is built from the leading ones. Suggest the first:</p>'
        : '<p class="mb-report__empty">Budget items open once the initiative is elected; the plan is built from the leading ones.</p>';
    }
    const sec = ([key, label, hint]) => {
      const ps = S.research.filter(p => p.type === key);
      const p = ps[0];
      return '<section class="mb-report__sec"><h4>' + label + ' <small>' + ps.length + ' post' + (ps.length === 1 ? '' : 's') + '</small></h4>' +
        (p ? (p.title ? '<div class="mb-report__lead">' + esc(p.title) + '</div>' : '') + '<p>' + excerpt(p, 360) + '</p>' +
               '<p class="mb-report__by">leading · &#9650; ' + (p.helpful_count || 0) + ' &#9660; ' + (p.harmful_count || 0) + '</p>'
           : '<p class="mb-report__empty">No ' + label.toLowerCase() + ' post yet — ' + esc(hint) + '. Be the first.</p>') +
      '</section>';
    };
    const budgetAdd = !m.winning_tiv_id ? '' :
      '<div class="mb-budget__add mb-budget__add--plan">' +
        '<span class="mb-budget__lab">Suggest a budget item' +
          (S.budget.length ? ' &middot; <button type="button" class="mp-post__reply" data-open-sec="budget">all ' +
            S.budget.length + ' item' + (S.budget.length === 1 ? '' : 's') + ' &rarr;</button>' : '') + '</span>' +
        '<button type="button" class="mb-budget__btn" data-budget="service"><b>Service</b><small>a job, a rate, the days</small></button>' +
        '<button type="button" class="mb-budget__btn" data-budget="supply"><b>Supply</b><small>an item and its cost</small></button>' +
        '<button type="button" class="mb-budget__btn" data-budget="support"><b>Support</b><small>a connection; no cost</small></button>' +
      '</div>';
    if (S.color) el.style.setProperty('--mx-c', S.color);
    else if (S.cause && S.cause.color) el.style.setProperty('--mx-c', S.cause.color);
    el.innerHTML =
      '<header class="mb-report__head">' +
        '<div><div class="mb-report__kicker">Mission report &middot; written by its members</div>' +
          '<h3 class="mb-report__title">The report on ' + esc(mname()) + '</h3></div>' +
        '<span class="mb-report__open">Read, rate and add to it &rarr;</span>' +
      '</header>' +
      '<div class="mb-report__body">' +
        '<div class="mb-report__top"><section class="mb-report__sec"><h4>Mission statement</h4>' + statement + '</section>' +
        '<section class="mb-report__sec"><h4>Plan</h4>' + plan + budgetAdd + '</section></div>' +
        '<div class="mb-report__three">' + SECTIONS.map(sec).join('') + '</div>' +
      '</div>';
  }

  // P3 · Posting: a NEW post is written on post.html, preselected; a reply
  // stays in the thread's own composer.
  function composeHref(cat, type) {
    const m = S.mission;
    const word = { context: 'background', investigation: 'investigation', analysis: 'analysis',
                   service: 'service', supply: 'supply', support: 'support' }[type] ||
                 (cat === 'budgeting' ? 'service' : 'general');
    const o = { type: word, mission: S.mid, cause: m ? m.cause_id : undefined, back: location.pathname + location.search };
    if (m && m.winning_tiv_id) o.initiative = m.winning_tiv_id;
    if (word === 'investigation' && m && m.winning_org_id) o.org = m.winning_org_id;
    return (E.Post && E.Post.composeUrl) ? E.Post.composeUrl(o) : 'post.html';
  }

  // ── the thread: read, rate, reply, write ────────────────────────────────
  const T = { sec: 'context', open: {} };
  function threadSecs() { return S.mission && S.mission.winning_tiv_id ? SECTIONS.concat([BUDGET_SEC]) : SECTIONS; }
  function ensureModals() {
    if (document.getElementById('mxt-bg')) return;
    const wrap = document.createElement('div');
    wrap.innerHTML =
      '<div class="mxc-bg" id="mxt-bg" hidden>' +
        '<div class="mxc mxt" role="dialog" aria-modal="true" aria-labelledby="mxt-title">' +
          '<header class="mxc__head"><div><div class="mxc__kicker" id="mxt-kicker"></div><h2 class="mxc__title" id="mxt-title">The report, post by post</h2></div>' +
            '<button type="button" class="mxc__x" id="mxt-close" aria-label="Close">&times;</button></header>' +
          '<div class="mxc__types" id="mxt-tabs" role="tablist" aria-label="Section"></div>' +
          '<div class="mxc__body mxt__body" id="mxt-body"></div>' +
          '<footer class="mxc__foot"><span class="mxc__msg" id="mxt-msg"></span><button type="button" class="mxc__btn" id="mxt-write">Write yours</button></footer>' +
        '</div>' +
      '</div>' +
      '<div class="mxc-bg" id="mxc-bg" hidden>' +
        '<div class="mxc" role="dialog" aria-modal="true" aria-labelledby="mxc-title">' +
          '<header class="mxc__head"><div><div class="mxc__kicker" id="mxc-kicker"></div><h2 class="mxc__title" id="mxc-title">Reply</h2></div>' +
            '<button type="button" class="mxc__x" id="mxc-close" aria-label="Close">&times;</button></header>' +
          '<div class="mxc__body"><div class="mxc__reply" id="mxc-reply"></div>' +
            '<textarea class="mxc__in mxc__in--text" id="mxc-in-body" placeholder="What do you want to say?"></textarea></div>' +
          '<footer class="mxc__foot"><span class="mxc__msg" id="mxc-msg"></span>' +
            '<button type="button" class="mxc__btn mxc__btn--ghost" id="mxc-cancel">Cancel</button>' +
            '<button type="button" class="mxc__btn" id="mxc-send">Post</button></footer>' +
        '</div>' +
      '</div>';
    while (wrap.firstChild) document.body.appendChild(wrap.firstChild);
    const $ = id => document.getElementById(id);
    $('mxt-close').onclick = closeThread;
    $('mxt-bg').addEventListener('click', e => {
      if (e.target.id === 'mxt-bg') return closeThread();
      const tab = e.target.closest('[data-sec]');
      if (tab) { T.sec = tab.dataset.sec; return paintThread(); }
      const rep = e.target.closest('[data-treply]');
      if (rep) { const p = S.research.concat(S.budget).find(x => x.id === rep.dataset.treply); if (p) openReply(p); return; }
      const show = e.target.closest('[data-tshow]');
      if (show) { T.open[show.dataset.tshow] = !T.open[show.dataset.tshow]; return paintThread(); }
    });
    $('mxt-write').onclick = () => { location.href = T.sec === 'budget' ? composeHref('budgeting', null) : composeHref('mission_support', T.sec); };
    $('mxc-close').onclick = closeReply;
    $('mxc-cancel').onclick = closeReply;
    $('mxc-bg').addEventListener('click', e => { if (e.target.id === 'mxc-bg') closeReply(); });
    $('mxc-send').onclick = sendReply;
    document.addEventListener('keydown', e => {
      if (e.key !== 'Escape') return;
      if (!$('mxc-bg').hidden) return closeReply();
      if (!$('mxt-bg').hidden) closeThread();
    });
  }
  async function paintThread() {
    const $ = id => document.getElementById(id);
    if (!threadSecs().some(x => x[0] === T.sec)) T.sec = 'context';
    const sec = threadSecs().find(x => x[0] === T.sec);
    const isBudget = T.sec === 'budget';
    const modal = $('mxt-bg');
    const col = S.color || (S.cause && S.cause.color);
    if (col) modal.style.setProperty('--mx-c', col);
    $('mxt-kicker').textContent = mname() + ' · the report';
    $('mxt-tabs').innerHTML = threadSecs().map(([k, l]) =>
      '<button type="button" class="mxc__type' + (k === T.sec ? ' on' : '') + '" data-sec="' + k + '">' + l +
      ' <small>' + (k === 'budget' ? S.budget.length : S.research.filter(p => p.type === k).length) + '</small></button>').join('');
    $('mxt-write').textContent = isBudget ? 'Suggest a budget item' : 'Write your ' + sec[1].toLowerCase() + ' post';
    const ps = isBudget ? S.budget : S.research.filter(p => p.type === T.sec);
    const body = $('mxt-body');
    let outline = '';
    try {
      const g = await E.Post.guide();
      const t = (g.types || []).find(x => x.key === (isBudget ? 'service' : T.sec));
      if (t && t.guide) outline = '<p class="mb-report__empty" style="font-style:normal;opacity:0.8;">' +
        esc(isBudget ? 'Service · Supply · Support — what this mission needs, and what it costs. ' + t.guide.limit.replace(/Service/g, 'item') : t.guide.purpose + ' ' + t.guide.limit) +
        ' <a href="about.html#posting" style="color:inherit;">How to post &rarr;</a></p>';
    } catch (e) {}
    if (!ps.length) { body.innerHTML = outline + '<p class="mb-report__empty">No ' + sec[1].toLowerCase() + ' posts yet — ' + esc(sec[2]) + '.</p>'; return; }
    const replies = {};
    await Promise.all(ps.filter(p => T.open[p.id]).map(async p => { replies[p.id] = (await jget('/posts/' + encodeURIComponent(p.id) + '/comments')) || []; }));
    body.innerHTML = outline + ps.map((p, i) =>
      '<article class="mxt__post' + (i === 0 ? ' mxt__post--lead' : '') + '">' +
        '<div class="mp-post__meta">' + (i === 0 ? 'leading · ' : '') + (isBudget ? esc(TYPE_WORD[p.type] || p.type) +
          (costLine(p) ? ' · ' + esc(costLine(p)) : '') + ' · ' : '') + fmtD(p.created_at) + '</div>' +
        (p.title ? '<h3>' + esc(p.title) + '</h3>' : '') +
        '<div class="mxt__text">' + esc(p.body || '') + '</div>' +
        '<div class="mp-post__foot">' + rateHTML(p) +
          '<button type="button" class="mp-post__reply" data-treply="' + esc(p.id) + '">Reply</button>' +
          '<button type="button" class="mp-post__reply" data-tshow="' + esc(p.id) + '">' + (T.open[p.id] ? 'Hide replies' : 'Replies') + '</button></div>' +
        (T.open[p.id] ? '<div class="mxt__replies">' + ((replies[p.id] || []).map(r =>
          '<div class="mxt__reply"><div class="mp-post__meta">' + fmtD(r.created_at) + '</div>' + esc(r.body || '') +
          '<div class="mp-post__foot">' + rateHTML(r) + '</div></div>').join('') || '<p class="mb-report__empty">No replies yet.</p>') + '</div>' : '') +
      '</article>').join('');
  }
  async function openThread(sec) {
    if (!S.mission) return;
    ensureModals();
    if (sec) T.sec = sec;
    await paintThread();
    document.getElementById('mxt-msg').textContent = '';
    document.getElementById('mxt-bg').hidden = false;
    document.body.classList.add('mxc-open');
  }
  function closeThread() {
    const bg = document.getElementById('mxt-bg'); if (bg) bg.hidden = true;
    document.body.classList.remove('mxc-open');
  }

  // a reply takes its post's lane, so the existing posting rules accept it
  let _parent = null;
  function openReply(p) {
    if (!loggedIn()) { if (E.Auth && E.Auth.openModal) E.Auth.openModal('login'); return; }
    _parent = p;
    const $ = id => document.getElementById(id);
    $('mxc-kicker').textContent = mname() + ' · reply';
    $('mxc-reply').innerHTML = 'Replying to <b>' + esc(p.title || (p.body || '').slice(0, 80)) + '</b>';
    $('mxc-in-body').value = '';
    $('mxc-msg').textContent = '';
    const col = S.color || (S.cause && S.cause.color);
    if (col) $('mxc-bg').style.setProperty('--mx-c', col);
    $('mxc-bg').hidden = false;
    document.body.classList.add('mxc-open');
    setTimeout(() => $('mxc-in-body').focus(), 30);
  }
  function closeReply() {
    const bg = document.getElementById('mxc-bg'); if (bg) bg.hidden = true;
    const t = document.getElementById('mxt-bg');
    if (!t || t.hidden) document.body.classList.remove('mxc-open');
  }
  async function sendReply() {
    const msg = document.getElementById('mxc-msg');
    const say = (t, ok) => { msg.textContent = t; msg.style.color = ok ? '#8fce9d' : '#f08a6a'; };
    if (!loggedIn()) { if (E.Auth && E.Auth.openModal) E.Auth.openModal('login'); return; }
    const body = document.getElementById('mxc-in-body').value.trim();
    if (!body) return say('Write something first.');
    if (!_parent) return say('Pick the post you are replying to.');
    const data = { id: 'mp-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      body, author_type: 'ben', mission_id: S.mid, cause_id: S.mission.cause_id,
      parent_id: _parent.id, category: _parent.category, type: _parent.type };
    const btn = document.getElementById('mxc-send');
    btn.disabled = true;
    try {
      const r = await E.Auth.fetchAuthed('/posts', { method: 'POST', body: JSON.stringify(data) });
      const out = await r.json().catch(() => ({}));
      if (!r.ok) { say(out.detail || ('Refused (' + r.status + ')')); return; }
      say('Posted.', true);
      T.open[_parent.id] = true;
      setTimeout(closeReply, 500);
      refresh();
    } catch (e) { say('Could not reach the server.'); }
    finally { btn.disabled = false; }
  }

  // rating — POST /posts/{id}/react, wherever the report shows its counts
  document.addEventListener('click', async e => {
    const b = e.target.closest && e.target.closest('.mb-rate [data-val]'); if (!b || !S.mid) return;
    e.stopPropagation();
    if (!loggedIn()) { if (E.Auth && E.Auth.openModal) E.Auth.openModal('login'); return; }
    const id = b.closest('.mb-rate').dataset.post;
    try {
      // P3 (D21): a vote counts in the mission it is cast in.
      const r = await E.Auth.fetchAuthed('/posts/' + encodeURIComponent(id) + '/react', { method: 'POST', body: JSON.stringify({ value: b.dataset.val, mission_id: S.mid }) });
      if (!r.ok) { const d = await r.json().catch(() => ({})); const m = document.getElementById('mxt-msg'); if (m) m.textContent = d.detail || 'Refused.'; return; }
    } catch (err) { return; }
    refresh();
  }, true);

  async function refresh() {
    const seq = ++S.seq;
    await load(seq);
    if (seq !== S.seq) return;
    await paintReport();
    const t = document.getElementById('mxt-bg');
    if (t && !t.hidden) await paintThread();
  }

  function bindReport(el) {
    if (el.dataset.mrBound) return;
    el.dataset.mrBound = '1';
    el.classList.add('mb-report');
    el.setAttribute('tabindex', '0');
    el.setAttribute('aria-label', 'The mission report — open its thread');
    el.addEventListener('click', e => {
      const b = e.target.closest('[data-budget]');
      if (b) { location.href = composeHref('budgeting', b.dataset.budget); return; }
      const o = e.target.closest('[data-open-sec]');
      if (o) { openThread(o.dataset.openSec); return; }
      if (e.target.closest('button, a, select, input')) return;
      openThread();
    });
    el.addEventListener('keydown', e => { if (e.target === el && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openThread(); } });
  }

  async function mount(el, missionId, opts) {
    const root = typeof el === 'string' ? document.querySelector(el) : el;
    if (!root) return null;
    S.el = root; S.mid = missionId || null; S.color = (opts && opts.color) || null;
    T.sec = 'context'; T.open = {};
    if (!S.mid) { root.hidden = true; root.innerHTML = ''; return null; }
    bindReport(root);
    root.hidden = false;
    root.innerHTML = '<div class="mb-report__empty" style="padding:6px 0">Loading the report&hellip;</div>';
    await refresh();
    return { reload: refresh, openThread };
  }

  E.MissionReport = { mount, openThread, refresh, state: S };
})();
