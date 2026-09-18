// Drives the DISCUSSION BOX in a headless DOM (build-seq §1, 2026-08-11,
// extended 2026-08-12). Replaces scripts/timeline_check.js, which drove the
// four-section accordion this box deletes.
//
// 2026-09-17: THE BOX MOVED. It is mounted on mission.html now (structure.md §6
// box i, resources/js/ebx_postsbox.js) and cause.html is the newsfeed, so the
// first half of this file drives the mission page. Nothing else changed: the
// assertions are the same ones, against the same ids and the same window.pb*
// handlers, which is the point — a move that needs the check rewritten is not
// a move. The second half still drives cause.html's hero, which stayed.
//
// What it asserts:
//   · 4 phase tabs (a–d), every one dated; 3 category tabs (e–g)
//   · exactly one phase tab and one category tab selected at all times
//   · the gray rules — budgeting disabled on a and b, enabled on c and d
//   · every enabled cell paints ONE explanation (three for budgeting: s/s/s),
//     one composer and one leading-post area
//   · the composer is shut, with a reason, on types not open at this stage
//   · nothing survives from the deleted accordion / bands / dual panels
const { JSDOM, VirtualConsole } = require('jsdom');
const BASE = process.argv[2] || 'http://127.0.0.1:8000';
// The box needs a mission with an elected initiative and an open organization
// race — the stage where every one of the twelve cells has something to say.
const MISSION = process.argv[3] || 'oce1';   // elected initiative, open org race WITH a candidate

(async () => {
  const errs = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => {
    const m = String(e.message || e);
    if (!/fonts\.googleapis\.com/.test(m)) errs.push(m.slice(0, 240));
  });
  vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ').slice(0, 200)));
  const dom = await JSDOM.fromURL(BASE + '/mission.html?mission=' + MISSION, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
    },
  });
  await new Promise(r => setTimeout(r, 4000));
  const d = dom.window.document, W = dom.window;
  let bad = 0;
  const say = (label, ok, extra) => {
    console.log((ok ? '  ok    ' : '  FAIL  ') + label + (extra ? '  ' + extra : ''));
    if (!ok) bad++;
  };
  const q = s => [...d.querySelectorAll(s)];
  // the stage the mission is actually standing on (the tab marked now)
  const _pbNowPhase = doc => {
    const tabs = [...doc.querySelectorAll('#pb-phase .pb-tab')];
    const i = tabs.findIndex(t => t.classList.contains('pb-tab--now'));
    return i >= 0 ? i + 1 : 2;
  };
  const txt = s => (d.querySelector(s) || {}).textContent || '';

  // ── the two tab rows ──
  const ph = q('#pb-phase .pb-tab');
  say('phase tabs a–d', ph.length === 4, ph.length + ' found');
  const dates = q('#pb-phase .pb-tab__date').map(e => e.textContent.trim());
  say('every phase tab dated', dates.length === 4 && dates.every(x => x && !/not scheduled/.test(x)),
      dates.join(' | '));
  say('phase keys read a b c d',
      q('#pb-phase .pb-tab__key').map(e => e.textContent.trim()).join('') === 'abcd');
  const cats = q('#pb-cat .pb-tab');
  say('category tabs e–g', cats.length === 3);
  say('category keys read e f g',
      q('#pb-cat .pb-tab__key').map(e => e.textContent.trim()).join('') === 'efg');
  say('exactly one phase tab on', q('#pb-phase .pb-tab--on').length === 1,
      txt('#pb-phase .pb-tab--on .pb-tab__name').trim());
  say('exactly one category tab on', q('#pb-cat .pb-tab--on').length === 1,
      txt('#pb-cat .pb-tab--on .pb-tab__name').trim());
  say('the stage is marked now', q('#pb-phase .pb-tab--now').length === 1);

  // ── the gray rules, phase by phase ──
  const CELLS = [
    [1, 'research', 1], [1, 'reviews', 1], [1, 'budgeting', 'gray'],
    [2, 'research', 1], [2, 'reviews', 1], [2, 'budgeting', 'gray'],
    [3, 'research', 1], [3, 'reviews', 1], [3, 'budgeting', 3],
    [4, 'research', 1], [4, 'reviews', 1], [4, 'budgeting', 3],
  ];
  for (const [n, cat, want] of CELLS) {
    W.pbPhase(n);
    const gray = !!d.querySelector('#pb-cat .pb-tab[data-cat="' + cat + '"].pb-tab--gray');
    if (want === 'gray') {
      say('phase ' + n + ' · ' + cat + ' grayed', gray);
      continue;
    }
    if (gray) { say('phase ' + n + ' · ' + cat + ' enabled', false); continue; }
    W.pbCat(cat);
    const on = txt('#pb-phase .pb-tab--on .pb-tab__name').trim();
    // budgeting's "explanation" is the three one-row table titles (2026-08-12);
    // every other cell is one .pb-ex block.
    const ex = cat === 'budgeting'
      ? q('#pb-explain .pb-sss__row').length : q('#pb-explain .pb-ex').length;
    // one composer per cell: either the real one (.pb-c) or the closed notice.
    const comp = q('#pb-compose > .pb-c, #pb-compose > .pb-shut').length;
    const lead = cat === 'budgeting'
      ? q('#pb-leading .pb-tbl').length : q('#pb-leading .pb-j__bar').length;
    say('phase ' + n + ' · ' + cat + ' → ' + want + ' explanation' + (want === 1 ? '' : 's'),
        ex === want, on + ' · ' + ex + ' explanation(s), ' + comp + ' composer, ' + lead + ' leading');
    say('   composer + leading present', comp === 1 && lead === (cat === 'budgeting' ? 3 : 1));
  }

  // ── b — the type toggle, in k, always showing every type of the category ──
  W.pbPhase(4); W.pbCat('research');
  const rTypes = q('#pb-types .dual-type').map(e => e.textContent.trim());
  say('research toggle = context · investigation · analysis',
      rTypes.length === 3 && /Context/.test(rTypes[0]) && /Investigation/.test(rTypes[1]) &&
      /Analysis/.test(rTypes[2]), rTypes.join(' | '));
  W.pbPhase(2); W.pbCat('research');
  const early = q('#pb-types .dual-type');
  say('at phase b all three still show, and only context is clickable',
      early.length === 3 && early.filter(e => e.disabled).length === 2,
      early.map(e => e.textContent.trim() + (e.disabled ? '(off)' : '')).join(' | '));
  W.pbPhase(3); W.pbCat('reviews');
  say('phase c reviews = case for a philanthropy',
      /philanthropy/i.test(txt('#pb-explain .pb-ex__title')),
      txt('#pb-explain .pb-ex__title').trim());
  W.pbPhase(4); W.pbCat('budgeting');
  const sss = q('#pb-explain .pb-sss__kind').map(e => e.textContent.trim());
  say('budgeting titles service · supply · support in one row each',
      sss.join(' ') === 'service supply support', sss.join(' | '));
  say('budgeting carries no target/open/reward/rating chips',
      q('#pb-explain .pb-meta').length === 0);
  say('budgeting has no link rails', q('#pb-compose .pb-rail__btn').length === 0);

  const tables = q('#pb-leading .pb-tbl');
  say('the area below prints the three budget tables', tables.length === 3,
      q('#pb-leading .pb-sss__kind').map(e => e.textContent.trim()).join(' | '));

  // ── k — the results panel, notched onto the last completed stage ──
  W.pbPhase(2);
  say('k names a result', !!d.querySelector('#pb-results .pb-k__name'),
      txt('#pb-results .pb-k__eyebrow').trim() + ' · ' + txt('#pb-results .pb-k__name').trim());
  const joint = q('#pb-joint .pb-k__joint > i');
  say('the joint has one cell per phase tab', joint.length === 4);
  const openCell = joint.findIndex(e => e.classList.contains('on'));
  const linked = q('#pb-phase .pb-tab').findIndex(e => e.classList.contains('pb-tab--linked'));
  say('the notch sits over the linked tab, and only one tab is linked',
      openCell >= 0 && openCell === linked && q('#pb-phase .pb-tab--linked').length === 1,
      'notch ' + openCell + ' · tab ' + linked);
  W.pbPhase(4);
  say('k does not follow the browsed tab',
      q('#pb-phase .pb-tab')[linked].classList.contains('pb-tab--linked'));

  // ── what you typed survives a repaint (2026-08-12 bug) ──
  W.pbPhase(2); W.pbCat('research');
  const bodyEl = d.getElementById('pb-body');
  const titleEl = d.getElementById('pb-title');
  if (bodyEl && titleEl) {
    titleEl.value = 'Half-written title';
    bodyEl.value = 'Half-written post that must not vanish.';
    W.pbPick('phls');                       // opening a picker repaints the box
    say('opening a link picker keeps what was typed',
        (d.getElementById('pb-body') || {}).value === 'Half-written post that must not vanish.' &&
        (d.getElementById('pb-title') || {}).value === 'Half-written title',
        (d.getElementById('pb-body') || {}).value || 'EMPTY');
    const opt = d.querySelector('#pb-compose .pb-pick__opt');
    if (opt) { opt.onclick ? opt.onclick() : opt.click(); }
    say('attaching a link keeps it too',
        (d.getElementById('pb-body') || {}).value === 'Half-written post that must not vanish.');
    W.pbCat('reviews'); W.pbCat('research');
    say('and it is still there after leaving the cell and coming back',
        (d.getElementById('pb-body') || {}).value === 'Half-written post that must not vanish.');
    // leave the cell clean for the assertions below
    const chipX = d.querySelector('#pb-compose .pb-chip__x');
    if (chipX) { chipX.onclick ? chipX.onclick() : chipX.click(); }
    const b2 = d.getElementById('pb-body'); if (b2) b2.value = '';
    const t2 = d.getElementById('pb-title'); if (t2) t2.value = '';
    W.pbPhase(2);
  }

  // ── research links itself and requires nothing ──
  W.pbCat('research');
  say('research auto-links the mission and asks for no link',
      /Linked automatically/.test(txt('#pb-compose .pb-auto')) &&
      q('#pb-compose .pb-rail__btn.req').length === 0,
      txt('#pb-compose .pb-auto').trim().slice(0, 70));
  say('research offers an edit link to the profile',
      [...d.querySelectorAll('#pb-compose .pb-auto a')].some(a => /profile\.html/.test(a.href)));

  // ── i — the five link rails ──
  W.pbPhase(2); W.pbCat('research');
  const rails = q('#pb-compose .pb-rail__btn');
  say('five link rails', rails.length === 5, rails.map(e => e.textContent.trim()).join(' | '));
  say('budget items and external links are stubbed, the other three live',
      rails.filter(e => e.disabled).length === 2);
  say('the composer has a title and a body',
      !!d.getElementById('pb-title') && !!d.getElementById('pb-body'));
  // 2026-09-17: read the required rail AT THE STAGE THE MISSION IS IN. A case
  // composer is only open on the stage that takes that case — on cause.html the
  // page could be pointed at a mission still in its initiative election, and a
  // mission page is the mission it is. Stage c takes a case for a philanthropy,
  // so `phls` is the rail that must be marked, and the picker lists orgs.
  W.pbPhase(_pbNowPhase(d)); W.pbCat('reviews');
  const req = q('#pb-compose .pb-rail__btn.req');
  say('a case marks its target rail required', req.length === 1,
      req.length ? req[0].textContent.trim() : 'none marked');
  W.pbPick(req.length && /organization/i.test(req[0].textContent) ? 'phls' : 'tivs');
  const opts = q('#pb-compose .pb-pick__opt');
  say('the picker lists something to link', opts.length > 0, opts.length + ' options');
  if (opts.length) {
    opts[0].onclick ? opts[0].onclick() : opts[0].click();
    say('picking one attaches a chip', q('#pb-compose .pb-chip').length === 1,
        txt('#pb-compose .pb-chip').trim());
    const x = d.querySelector('#pb-compose .pb-chip__x');
    if (x) { x.onclick ? x.onclick() : x.click(); }
    say('unlinking removes it', q('#pb-compose .pb-chip').length === 0);
  }

  // ── a shut composer says WHY ──
  W.pbPhase(4); W.pbCat('reviews');   // evaluation, with the mission still electing
  const shut = d.querySelector('#pb-compose .pb-shut');
  say('a type that is not open yet is shut with a reason',
      !!shut && shut.textContent.trim().length > 20,
      shut ? shut.textContent.trim().slice(0, 60) : 'no .pb-shut');

  // ── the leading post area ──
  W.pbPhase(2); W.pbCat('research');
  say('leading post area has a pager', q('#pb-leading .pb-pager button').length === 2);
  say('research carries the search box', !!d.getElementById('pb-search'));
  W.pbCat('reviews');
  say('reviews carries the sort-by-philanthropy select', !!d.getElementById('pb-sortorg'));

  // ── nothing survives of the systems this replaced ──
  for (const sel of ['.ct-sec', '#ct-rail', '.ct-node', '.ct-states', '.p3-bands',
                     '.p3-band', '.p3-tile', '#phase-recap-1', '#p1-dual-panels', '#phase-disc-1']) {
    say('removed ' + sel, q(sel).length === 0, q(sel).length ? q(sel).length + ' left' : '');
  }
  say('the one key date still crosses the page',
      !!d.getElementById('ct-startline') && /Mission start/.test(txt('#ct-startline-label')),
      txt('#ct-startline-label').trim());

  // ── a mission whose philanthropy is already elected reads as stage 4 ──
  // 2026-09-17: on cause.html this was `setSelectedMission` — one page, many
  // missions. A mission page IS one mission, so the way to read another stage
  // is to open another mission, which is the honest version of the same test.
  const electedMission = (W.EBX.config.missions || []).find(m => m.winning_org_id);
  if (electedMission) {
    const dom3 = await JSDOM.fromURL(BASE + '/mission.html?mission=' + electedMission.id, {
      runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
      beforeParse(w) {
        w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
        w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
      },
    });
    await new Promise(r => setTimeout(r, 4000));
    const d3 = dom3.window.document, W3 = dom3.window;
    const q3 = sel => [...d3.querySelectorAll(sel)];
    const t3 = sel => (d3.querySelector(sel) || {}).textContent || '';
    say('an elected mission puts the notch on tab d and names its philanthropy',
        /Philanthropy elected/.test(t3('#pb-results .pb-k__eyebrow')) &&
        q3('#pb-phase .pb-tab')[3].classList.contains('pb-tab--linked'),
        t3('#pb-results .pb-k__eyebrow').trim() + ' · ' + t3('#pb-results .pb-k__name').trim());
    W3.pbPhase(4);
    say('budgeting is no longer grayed on its tab', q3('#pb-cat .pb-tab--gray').length === 0);
    // ── the row that replaces the title. Budgeting only composes once the
    //    initiative is elected, so this is the first page state that has it. ──
    W3.pbCat('budgeting'); W3.pbType('supply');
    const rowFields = q3('#pb-compose .pb-row__in').map(e => e.id);
    say('the s/s/s row takes this kind\'s fields',
        rowFields.join(',') === 'pb-row-item,pb-row-supplier,pb-row-cost', rowFields.join(' | '));
    const fill = (id, v) => { const el = d3.getElementById(id); if (el) el.value = v; };
    fill('pb-row-item', 'Handheld methane sensors');
    fill('pb-row-supplier', 'FieldKit');
    fill('pb-row-cost', '1200');
    W3.pbRowAdd();
    say('adding a row lists it under the composer, with a total',
        q3('#pb-compose .pb-tbl--draft tbody tr').length === 1,
        t3('#pb-compose .pb-tbl__total').trim());
    W3.pbType('service');
    say('switching kind switches the fields, and keeps the supply draft',
        q3('#pb-compose .pb-row__in').map(e => e.id).join(',') ===
          'pb-row-job,pb-row-hourly_rate,pb-row-days_needed');
    W3.pbType('supply');
    say('the supply row is still there', q3('#pb-compose .pb-tbl--draft tbody tr').length === 1);
    W3.pbRowDel(0);
    say('and it can be removed again', q3('#pb-compose .pb-tbl--draft tbody tr').length === 0);
    dom3.window.close();
  } else {
    console.log('  --    no mission with an elected philanthropy in this db; stage-4 check skipped');
  }
  say('no script errors', errs.length === 0, errs.join(' | '));
  dom.window.close();

  // ══ the philanthropy race belongs to its own mission ═════════════════════
  // Regression guard for "Phl consistency across pages": this page used to read
  // the p2 tally off the INITIATIVE-election mission, which never has one, so
  // the philanthropy cards were empty while main.html showed a full race.
  const errs2 = [];
  const vc2 = new VirtualConsole();
  vc2.on('jsdomError', e => {
    const m = String(e.message || e);
    if (!/fonts\.googleapis\.com/.test(m)) errs2.push(m.slice(0, 200));
  });
  const dom2 = await JSDOM.fromURL(BASE + '/cause.html?id=oceans', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc2,
    beforeParse(w) {
      w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
    },
  });
  await new Promise(r => setTimeout(r, 3500));
  const d2 = dom2.window.document, W2 = dom2.window;
  const t2 = s => ((d2.querySelector(s) || {}).textContent || '').trim();
  say('the left header carries a Vote button', /Vote/.test(t2('#lhs-vote')),
      (d2.querySelector('#lhs-vote') || {}).href || '');
  // (the source comment that records the deletion also contains the words, so
  //  this reads the LINKS on the page rather than its markup)
  say('"View initiatives" is gone',
      ![...d2.querySelectorAll('a, button')].some(e => /View initiatives/i.test(e.textContent)));
  // pick the mission that is running a philanthropy race and open it
  const race = (W2.EBX.config.missions || [])
    .filter(m => m.cause_id === 'oceans' && m.winning_tiv_id && !m.winning_org_id)
    .sort((a, b) => (a.cycle_num || 0) - (b.cycle_num || 0))[0];
  if (race) {
    const cands = await (await fetch(BASE + '/candidacies?mission_id=' + race.id)).json();
    const want = (cands || []).length;
    const ref = (W2.EBX.config.initiatives || []).find(i => i.mission_id === race.id && i.status === 'active')
             || (W2.EBX.config.initiatives || []).find(i => i.mission_id === race.id);
    W2.setSelectedMission(ref.id, { scroll: false });
    await new Promise(r => setTimeout(r, 2500));
    const cards = [...d2.querySelectorAll('#leading-initiatives-panel .init-card__title')]
      .map(e => e.textContent.trim());
    say('the left column swaps to Leading Philanthropies', /Philanthropies/.test(t2('#lhs-eyebrow')),
        t2('#lhs-eyebrow'));
    say('it shows ' + race.id + '\'s ' + want + ' philanthropy card(s), not the p1 mission\'s none',
        cards.length === want && want > 0, cards.join(' | ') || 'NONE');
    say('the Vote button points at the philanthropy election',
        /state=oe/.test((d2.querySelector('#lhs-vote') || {}).href || ''));
  }
  say('no script errors on oceans', errs2.length === 0, errs2.join(' | '));

  console.log(bad ? '\nPOSTS BOX: ' + bad + ' PROBLEM(S)' : '\nPOSTS BOX CLEAN');
  process.exit(bad ? 1 : 0);
})();
