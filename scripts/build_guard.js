#!/usr/bin/env node
/* RETIRED 2026-09-16 (INSTRUCTIONS build-seq §1).
 *
 * This guard stood in front of `npm run build`, which compiled
 * `frontend/src/ebx_shared.ts` over `resources/js/ebx_shared.js` and would have
 * deleted the ~24 KB the .js had grown past its source. The TypeScript source
 * is retired instead: `resources/js/ebx_shared.js` is edited directly and there
 * is no build. This file and `frontend/` are in the REMOVAL REGISTER.
 */
console.error('build_guard: retired 2026-09-16 — edit resources/js/ebx_shared.js directly; there is no build.');
process.exit(1);
