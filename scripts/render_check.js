// Loads each page in jsdom against the live test API and reports (a) any
// uncaught script error and (b) whether the new areas actually painted.
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';

const PAGES = [
  // index.html — the five sections of structure.md §1a–§1e, 2026-08-18. The
  // old selectors (.ld-sys__row, .ld-fine__item, #cause-change, #ld-causes)
  // named blocks §1f moved off the page and into the doc's backlog.
  ['index.html', '', ['.ld-lede', '#ld-cta .ld-cta__btn', '.ld-couplet span',
                      '.ld-elect__row', '.ld-elect__when', '#ld-dime-viz svg',
                      '.ld-runway__bars', '#ld-active-users b',
                      '#ld-forum .ld-forum__cat', '#ld-forum .ld-tt__btn',
                      '#ld-forum .ld-tt__btn.on', '#ld-forum .ld-tt__what',
                      '.ld-term--org', '.ld-step', '.ld-scale__split']],
  ['mission.html', '?mission=oce1', ['#ps-ring svg', '.ps-leg',
                                     '#ml-board .ml-row', '.ml-row__bar i', '#ml-note']],
  ['cause.html', '?id=atmosphere', ['#pb', '#pb-heading', '#pb-phase .pb-tab', '#pb-cat .pb-tab',
                                    '#pb-phase .pb-tab--on', '#pb-cat .pb-tab--on',
                                    '#pb-phase .pb-tab--now', '#pb-phase .pb-tab--linked',
                                    '#pb-phase .pb-tab__date',
                                    '#pb-results .pb-k__name', '#pb-joint .pb-k__joint > i.on',
                                    '#pb-types .dual-type',
                                    '#pb-explain .pb-ex', '#pb-explain .pb-meta',
                                    '#pb-compose .pb-c__body', '#pb-compose .pb-rail__btn',
                                    '#pb-leading .pb-j__bar', '#pb-leading .pb-pager',
                                    '#ct-startline', '#leading-initiatives-panel',
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
  // §1–§2 (2026-08-27): the rail beside the ME/OE toggle is gone with the move
  // below the annulus, the cause election is a PANEL rather than a tall card,
  // and the two captions became card furniture.
  ['main.html', '', ['#hero-statetoggle .st-side', '.hero__center .hero__togglerow',
                     '#hero-topgrid', '#ebx-top-card-mount .tc-half',
                     '.hero__causetabs .cause-tab', '#ebx-top-card-mount .tc-howto',
                     '#ebx-top-card-mount-b .tc-bar--top', '#ebx-top-card-mount-b .tc-bar--bot',
                     '.alloc-section #alloc-mount', '#show-all-inits',
                     // §1 (2026-08-27) — THE CE PANEL, above the election panel, in
                     // every page state: seven streak lines, the keep-or-replace ballot,
                     // its own Commit/Cancel, and the way into the cause table.
                     '#ce-panel-mount .ce-panel', '.ce-weeks .ce-week',
                     '.ce-panel .ce-row--votes .ce-vote', '.ce-panel__b .rf-btn',
                     '.ce-panel .ce-row--acts .vb-btn',
                     // §2 (2026-08-21): the allocations panel, under the
                     // annulus, in BOTH page states.
                     // signed out (jsdom has no session) the panel shows its sign-in
                     // prompt rather than a bar — the MOUNT is what must exist.
                     '#alloc-mount .oe-actions', '#alloc-mount .unalloc__signedout',
                     '.race-face--click', '.rf-line__k',
                     '#votebar-mount .votebar', '.votebar__chip--lead', '.st-now',
                     // §2 (2026-08-26) — THE ANNULUS SWAP. The PIE is here now, behind the
                     // centre panel, and the seven cause tabs came with it into the top
                     // bar: "the election page toggles itself from these".
                     '.hero__causetabs .cause-tab.selected',
                     '#ebx-pie-mount svg', '#ebx-pie-mount .pie-slice',
                     '#ebx-annulus-mount .ebx-center']],
  ['main.html', '?state=oe', ['#hero-statetoggle .st-side--oe.on', '#hero-topgrid.hero__topgrid--oe',
                              '#ebx-top-card-mount .tc-half', '#ebx-top-card-mount-b .tc-half',
                              '#alloc-mount .oe-actions',
                              '#votebar-mount .votebar', '.init-table__myvote',
                              '.hero__causetabs .cause-tab.selected', '#ebx-pie-mount svg',
                              // §2 (2026-08-27): the OE side of the row says the same
                              // thing the ME side does — winner bars on the right card,
                              // the how-to line on the left one.
                              '#ebx-top-card-mount .tc-howto',
                              '#ebx-top-card-mount-b .tc-bar--top',
                              '#ebx-top-card-mount-b .tc-bar--bot',
                              '#ce-panel-mount .ce-panel']],
  // …and the ballot is here instead, with the thirteen windows under it.
  ['main.html', '?state=ce', ['#votebar-mount .votebar', '#ce-panel-mount .ce-panel',
                              '.ce-case', '.ce-vote__pct', '.ce-row--votes .ce-vote',
                              '.ce-row--sugg .ce-sugg',
                              '.init-table__row[data-kind="cause-window"]',
                              '.cw-tag--set', '.cw-tag--open',
                              '#alloc-mount .oe-actions']],
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
    if (page === 'main.html' && d.querySelectorAll('#init-table-body tr.votebar-row').length) {
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
