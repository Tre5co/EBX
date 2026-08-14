// Loads each page in jsdom against the live test API and reports (a) any
// uncaught script error and (b) whether the new areas actually painted.
const { JSDOM, VirtualConsole } = require('jsdom');

const BASE = process.argv[2] || 'http://127.0.0.1:8000';

const PAGES = [
  ['index.html', '', ['.ld-lede', '#ld-cta .ld-cta__btn', '.ld-step', '.ld-runway__bars',
                       '#ld-dime-viz svg', '.ld-sys__row', '.ld-fine__item', '.ld-term--org',
                       '#cause-change', '#ld-causes .ld-cause']],
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
                                    '#mission-header #mission-overview', '#lhs-vote']],
  ['main.html', '', ['#hero-statetoggle .st-side', '#st-rail', '.hero__togglerow',
                     '#hero-topgrid', '#ebx-top-card-mount .tc-half', '#ebx-top-card-mount-b .tc-half--tall',
                     '.tc-half__head--sentence',
                     '.ce-row--propose .ce-input', '.ce-case', '.ce-vote__pct',
                     '.ce-tabs--abbr .ce-tab__abbr', '.ce-foot__more', '.cs-bars .cs-col',
                     '#votebar-mount .votebar', '.votebar__chip--lead', '.st-now']],
  ['main.html', '?state=oe', ['#hero-statetoggle .st-side--oe.on', '#hero-topgrid.hero__topgrid--oe',
                              '#ebx-top-card-mount .tc-half', '#ebx-top-card-mount-b .tc-half',
                              '#votebar-mount .votebar', '.init-table__myvote']],
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
    const real = errors.filter(e => !/Not implemented|getContext|SVGElement/i.test(e));
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
