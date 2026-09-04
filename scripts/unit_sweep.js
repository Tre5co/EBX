// unit_sweep — where does a PAGE say "EBX", and does it mean the minted state?
//
//   node scripts/unit_sweep.js [http://127.0.0.1:8000] [page ...]
//
// §3 (2026-08-28), build-seq item 3: "Ebx / token distinction will need to be
// grepped and implemented throughout. We can do this one page at a time."
//
// A grep of the source cannot do this: `EBX.` is the client namespace and it is
// on every line of every page. What matters is the word a READER sees, so this
// renders each page and walks its visible text nodes.
//
// The rule it is checking (docs/token_model.md, finalized 2026-08-27c):
//   tokens  the unit a vote is cast in — unallocated and committed money
//   EBX     a STATE: minted, mission-tied, no longer movable
// So "commit 3 EBX" is wrong and "3 EBX held against this mission" is right.
// The script cannot read intent, so it prints every hit with its context and
// flags the ones sitting next to vote/commit words, which are the wrong ones.
const { JSDOM, VirtualConsole } = require('jsdom');
const BASE = process.argv[2] || 'http://127.0.0.1:8000';
const PAGES = process.argv.slice(3).length ? process.argv.slice(3)
  : ['index.html', 'main.html', 'main.html?state=oe', 'cause.html?id=atmosphere',
     'mission.html', 'profile.html'];
// Words that mean the money is still a TOKEN. "EBX" beside one of these is the
// bug: it is naming the unit of a vote, which is what tokens are for.
const VOTEY = /\b(vote|votes|voting|commit|committed|commitment|allocate|allocated|allocation|spend|spent|buy|purchase|uncommitted|unallocated)\b/i;

(async () => {
  let flagged = 0, total = 0;
  for (const page of PAGES) {
    const vc = new VirtualConsole();
    let dom;
    try {
      dom = await JSDOM.fromURL(BASE + '/' + page, {
        runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
        virtualConsole: vc,
        beforeParse(w) {
          w.fetch = (u, o) => fetch(String(u).startsWith('http') ? u : BASE + u, o);
          w.matchMedia = w.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
        }
      });
    } catch (e) { console.log('\n=== ' + page + ' — could not load: ' + e.message); continue; }
    await new Promise(r => setTimeout(r, 6000));
    const D = dom.window.document;
    const hits = [];
    const walk = el => {
      if (/^(SCRIPT|STYLE|NOSCRIPT|TITLE)$/.test(el.tagName)) return;
      // The brand is the PRODUCT's name and always stays.
      if (el.closest && el.closest('.ebx-topbar, .ebx-home-mark, footer')) return;
      for (const n of el.childNodes) {
        if (n.nodeType === 3 && /\bEBX\b/.test(n.textContent)) {
          const t = n.textContent.replace(/\s+/g, ' ').trim();
          if (t && t !== 'EBX' || (el.className || '').toString().includes('alloc')) hits.push({ el, t });
          else if (t === 'EBX') hits.push({ el, t });
        }
      }
      for (const c of el.children) walk(c);
    };
    walk(D.body);
    console.log('\n=== ' + page + ' — ' + hits.length + ' visible "EBX"');
    hits.forEach(h => {
      const near = (h.el.parentElement ? h.el.parentElement.textContent : h.t)
        .replace(/\s+/g, ' ').trim().slice(0, 110);
      const bad = VOTEY.test(near);
      total++; if (bad) flagged++;
      console.log('  ' + (bad ? 'CHECK' : 'ok   ') + '  ' + h.t.slice(0, 80) +
        (bad ? '\n           ctx: ' + near : ''));
    });
    dom.window.close();
  }
  console.log('\n' + total + ' visible uses of EBX · ' + flagged + ' sitting beside vote/commit words');
  console.log(flagged ? 'REVIEW THE FLAGGED ONES — EBX beside a vote word is the unit, and the unit is tokens.'
                      : 'UNIT SWEEP CLEAN');
  process.exit(0);
})();
