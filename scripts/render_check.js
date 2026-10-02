// Loads each page in jsdom against the live test API and reports (a) any
// uncaught script error and (b) whether the new areas actually painted.
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';

const PAGES = [
  // index.html — the five sections of structure.md §1a–§1e, 2026-08-18. The
  // old selectors (.ld-sys__row, .ld-fine__item, #cause-change, #ld-causes)
  // named blocks §1f moved off the page and into the doc's backlog.
  // 2026-09-16: the landing as rebuilt 2026-09-15 plus build-seq §2.
  // P2 · Home (2026-09-25): Home is the phase rows, the wheel, the Network
  // and the feed; the explainer (bands, dimes, runway) moved to about.html.
  // P2 · Home mods (2026-09-30): the hero with the five steps to its right,
  // the mission hub, the Network (links, not toggles) and the feed.
  ['index.html', '', ['#ld-flow .ld-flow__i', '#hk .hk__card', '#mh-week .mw', '.hx #ebx-steps .sx__scene.on', '#ebx-steps .sx__msg',
                      '#mh-toggle',
                      '#hf-list .ep--card']],
  ['about.html', '', ['.ld-band', '.ld-trio__cell', '#ld-dime-viz svg', '.ld-runway__bars', '#ld-active-users b', '#ab-phases li']],
  // build-seq P1 (2026-09-24) — THE MERGE. main.html is a redirect; the mission
  // page carries the elections. Its default (/m) is the newest initiative
  // election (D2). Every state: the annulus in its mission variant between the
  // toggler and the overview, the 5-phase toggle, the 7 cause toggles with
  // their dates, the five ballots, the table, the allocations, and below them
  // the mission's own story.
  ['mission.html', '', ['#mx-wheel .lw--mission, #mx-wheel.lw--mission', '#lw-ringlayer .lw-sector', '#lw-pielayer', '#lw-globe .lw-land',
                        '#mx-cards .mx-card', '#mx-cards .mx-card--on', '#mx-toggler #mx-search',
                        '#mx-overview .mx-ov__row', '#mx-title', '#mx-copy',
                        '#mx-stage #mx-phases .mx-phase.on[data-step="tiv"]', '#mx-phases .mx-phase__d', '#mx-sub',
                        '.hero__causetabs .cause-tab', '.hero__causetabs .cause-tab.selected', '.cause-tab__date',
                        '#el3-me.on', '#votebar-mount .votebar', '#el3-top-me .el3__top-title', '#el3-blurb-me',
                        '#ce-panel-mount .ce-panel', '.ce-bars .ce-bars__row',
                        '.ce-panel .ce-row--votes .ce-vote', '.ce-panel .ce-dist__bar', '.ce-panel .bb .vb-btn',
                        '#fr-ballot-mount .votebar', '#ex-ballot-mount .votebar', '#fx-view',
                        '#init-search',
                        '#votebar-notice-mount .votebar--notice', '#votebar-notice-mount .vb-notice__body',
                        '#mx-phases .mx-phase--row', '#mh-candidates', '.el3__col.on .bb .bb__post', '#mb-report .mb-report__sec', '#mxt-bg', '#mxc-bg',
                        '#mx-stage .mx-logcol__how', '#mx-stage #mx-table #init-table-body', '#mx-head #mx-title', '#mx-sub .mx-now']],
  // An organization election, by its old link. The discussion box (structure.md
  // §6 box i, 2026-09-17) and the final standings of the initiative election
  // this mission came out of.
  ['mission.html', '?mission=oce1', ['#el3-oe.on', '#mx-phases .mx-phase.on[data-step="org"]',
                                     '#mx-phases .mx-phase--past', '#mx-phases .mx-phase--future',
                                     '#init-table-body .oet-cap__tiv', '#init-table-body .init-table__row--nom .rf-btn',
                                     '.init-table__myvote, #init-table-body .init-table__empty',
                                     '#votebar-notice-mount .votebar--notice',
                                     '#ml-board .ml-row', '.ml-row__bar i', '#ml-note',
                                     '#mb-report .mb-report__sec', '#mx-sub .mx-got']],
  // review 2026-09-24: a phase that is not the mission's live one is a recap
  ['mission.html', '?mission=oce1&phase=me', ['#mx-recap .mx-recap__p', '#mx-phases .mx-phase.on[data-step="tiv"]']],
  // 2026-09-17: the feed took the page's spine; the box's selectors went to
  // mission.html above. feed_check.js drives the feed's behaviour — these are
  // only "it painted".
  ['cause.html', '?id=atmosphere', ['#fd-panel', '#fd-search', '#fd-sort', '#fd-compose',
                                    '#fd-filters .fd-chip', '#fd-filters .fd-chip--on',
                                    'article.ep--card', 'article.ep--card [data-ep-vote]', 'article.ep--card [data-ep-reply]',
                                    '#leading-initiatives-panel',
                                    '#mission-header #mission-overview', '#lhs-vote',
                                    // §2 (2026-08-26) — THE ANNULUS SWAP. This page has the
                                    // seven-sector WHEEL now (EBX.Annulus), with the centre
                                    // stack as an HTML panel over its dark core, and it has
                                    // no cause tabs in the top bar: the sectors are the
                                    // toggle.
                                    '#cause-annulus-mount svg', '#ebx-rotating-group',
                                    '#cause-annulus-center .cause-center__today',
                                    '#cause-annulus-center .cause-center__title',
                                    '#ebx-pagetag']],
  // …the old Elect links still land, through the redirect, in the right phase.
  // for0 (Forests) is in framing until Oct 20, 2026; after that this view shows
  // the empty state, so the mission selectors accept it.
  ['mission.html', '?state=fr&cause=forests', ['#el3-fr.on', '#mx-phases .mx-phase.on[data-step="frame"]',
                              '#fr-ballot-mount .votebar', '#fx-view .fx-mission, #fx-view .fx-empty']],
  ['mission.html', '?state=ex&cause=forests', ['#el3-ex.on', '#mx-phases .mx-phase.on[data-step="ex"]',
                              '#ex-ballot-mount .votebar', '#fx-view .fx-mission, #fx-view .fx-empty',
                              '#mb-live, #mb-none']],
  ['mission.html', '?state=ce', ['#el3-ce.on', '#mx-phases .mx-phase.on[data-step="cause"]',
                              '#votebar-mount .votebar', '#ce-panel-mount .ce-panel',
                              '.ce-vote__pct', '.ce-row--votes .ce-vote',
                              '.ce-row--sugg .ce-sugg',
                              '.init-table__row[data-kind="cause-window"]',
                              '.cw-tag--set', '.cw-tag--open',
                              '#mb-none']],
];

(async () => {
  let bad = 0;
  for (const [page, qs, sels] of PAGES) {
    const errors = [];
    const vc = new VirtualConsole();
    vc.on('jsdomError', e => errors.push(String(e.message || e).slice(0, 220)));
    vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ').slice(0, 200)));
    let dom;
    try {
      dom = await JSDOM.fromURL(BASE + '/' + page + qs, {
        runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
        virtualConsole: vc,
        // jsdom ships no fetch; hand the page node's, with relative URLs
        // resolved against the test API so every XHR is real.
        beforeParse(win) {
          win.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
          win.matchMedia = win.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
        },
      });
    } catch (e) {
      console.log('FAIL  ' + page + ' — could not load: ' + e.message);
      bad++; continue;
    }
    await new Promise(r => setTimeout(r, 4500));
    const d = dom.window.document;
    console.log('\n=== ' + page + qs);
    // jsdom cannot do SVG layout or CSS vars; only script errors matter.
    // The sandbox has no outbound network, so the Google-Fonts <link> always
    // fails here. That is the environment, not the page — oe_check has always
    // filtered it and this one counted it as a defect on every page.
    const real = errors.filter(e => !/Not implemented|getContext|SVGElement/i.test(e))
                       .filter(e => !/fonts\.googleapis|fonts\.gstatic/i.test(e));
    if (real.length) { console.log('  script errors:'); real.slice(0, 6).forEach(e => console.log('    ! ' + e)); bad += real.length; }
    else console.log('  script errors: none');
    if (page === 'mission.html' && d.querySelectorAll('#init-table-body tr.votebar-row').length) {
      console.log('  FAIL  a votebar-row is still inside the tbody'); bad++;
    }
    for (const s of sels) {
      const n = d.querySelectorAll(s).length;
      console.log('  ' + (n ? 'ok  ' : 'MISS') + '  ' + s + '  x' + n);
      if (!n) bad++;
    }
    dom.window.close();
  }
  console.log('\n' + (bad ? 'PROBLEMS: ' + bad : 'RENDER CHECK CLEAN'));
  process.exit(bad ? 1 : 0);
})();
