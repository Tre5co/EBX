# Earthbucks — Backlog

Deferred items captured during planning. Roughly ordered by priority.
---
── JAX'S ISSUES ──
<!-- Mission EBX link to home on profile page. -->

── ANSWERS TO JAX'S QUESTIONS ──
---
<!-- ══ AUTOMATED PASS — 2026-05-13 (pass 7) ════════════════════════════════════

  ── FIXES APPLIED ──

  ✅ A. Left-panel cards were in reverse order (Jax's comment)
     The left column showed causes [active−3, active−2, active−1] top-to-bottom,
     which put the furthest-away cause nearest the wheel. Fixed by changing the
     offset array from [-3, -2, -1] to [-1, -2, -3], so the card immediately
     before the active cause (e.g. 6) sits at the top, then 5, then 4 — matching
     the clockwise sector layout Jax described.
     File: index.html (render() function)

  ✅ B. Profile badge + EBX home link now on every page
     initPage() in ebx_shared.ts was upgraded from a sync stub to an async
     function that does three things:
       1. Injects <a class="ebx-home-mark">EBX</a> at the top of <body> if not
          already present (profile.html was the only page missing it; also added
          it explicitly in the HTML so it's visible before JS runs).
       2. Locates or creates a #ebx-user-badge-mount div (fixed top-right if not
          in the DOM already).
       3. Calls Auth.fetchMe() and renders userBadge() into that mount.
     A DOMContentLoaded listener in ebx_shared.ts already called initPage() on
     every page, so the badge now appears on cause, mission, initiative, feed,
     about, and profile pages without any manual fetch. The explicit initPage()
     calls added to each page's IIFE (and the await in index.html) make the
     order predictable in case DOMContentLoaded races with loadAll().
     Files: frontend/src/ebx_shared.ts, index.html, cause.html, mission.html,
            initiative.html, feed.html, about.html, profile.html

  ✅ C. Supabase block removed from cause.html
     The ~190-line Supabase integration block (client init, magic-link auth,
     submitPost/castVote/commitEbx via Supabase SDK) was replaced with thin
     wrappers around the existing FastAPI backend:
       • submitPost()  → POST /posts via EBX.Auth.fetchAuthed()
       • commitEbx()   → POST /initiatives/{id}/commit via fetchAuthed()
       • castVote()    → stub (shows "coming soon" alert; Vote model not yet
                          migrated — see backlog item "Vote model migration")
       • showAuthPrompt() replaced by EBX.Auth.openModal()
     The Supabase CDN script tag was already in a comment; confirmed no live
     Supabase scripts remain on the page.
     File: cause.html

  ✅ D. ebx_shared.ts truncation repaired (same corruption as pass 5)
     The file was again truncated mid-character inside missionStrip(). Root
     cause is still unknown — the build script's EBX_TAIL_SENTINEL guard caught
     it immediately. Tail restored from git HEAD. The DOMContentLoaded handler
     and export block were preserved intact.
     File: frontend/src/ebx_shared.ts
     Build: npm run build → ../resources/js/ebx_shared.js  51.6 kb ⚡ Done in 50ms

  ── NEW INEFFICIENCIES SPOTTED ──

  E. ebx_shared.ts keeps silently truncating (passes 5 and 7 both required repair)
     Two passes in a row have required restoring the tail of ebx_shared.ts. The
     truncation always happens inside a template literal near the end of the file.
     Likely culprit: an editor or tool is writing the file with a fixed buffer size
     and cutting it short. The EBX_TAIL_SENTINEL guard catches it at build time,
     but the repair is manual. Consider moving the export/sentinel block to a
     separate tiny file (e.g. ebx_exports.ts) so the main file can be safely
     truncated without losing the sentinel — or just add the sentinel check to a
     git pre-commit hook so it fails loudly before commit.

  F. initPage() now makes an Auth.fetchMe() call on every page load
     The new initPage() always calls Auth.fetchMe() to populate the badge, even
     on pages that already fetch the user for their own logic (profile.html now
     fetches twice). This is harmless in dev but adds ~1 extra API call per page
     load. Optimize later by accepting an optional `handle` param:
       EBX.initPage({ handle: apiUser.handle })
     so pages that already have the user can pass it in and skip the second fetch.

  G. castVote() on cause.html is now a stub (alert "coming soon")
     The old Supabase implementation at least executed a DB write. The new stub
     does nothing except show an alert. This is correct since the Vote model
     doesn't exist yet — but it's a regression in UX until the Vote migration
     lands. Fix: add `class Vote(Base)` to models.py + alembic autogenerate +
     POST /initiatives/{id}/vote endpoint, then wire castVote() to it.

  ── SUGGESTED NEXT ──

  1. Add the Vote model (backlog: "Vote model migration"). It unblocks real
     vote tallies everywhere — cause page, race cards, and the mock in
     EBX.Votes.forCause. Two steps: add the model + alembic revision, then add
     a POST /initiatives/{id}/vote endpoint and wire castVote() on cause.html.

  2. Add PATCH /auth/me to persist display_name, donation_amount, and cause
     prefs server-side (has been the #1 open item since pass 2). One model
     column + one endpoint + small profile.html form change.

  3. Investigate and fix the ebx_shared.ts truncation bug (inefficiency E).
     Two manual repairs in two passes is unsustainable. Check if any tool,
     editor, or save operation is capping file writes.

  ── LEARN THIS ──

  Topic: Git pre-commit hooks & automated file-integrity checks

  Two passes in a row have required repairing ebx_shared.ts after it was
  silently truncated. The EBX_TAIL_SENTINEL guard in package.json catches the
  problem at build time, but only when you remember to build. A git pre-commit
  hook can make this automatic — it runs before every commit and blocks the
  commit if the check fails.

  Key concepts:
    • .git/hooks/pre-commit — a shell script that runs before git commit.
      Make it executable (chmod +x) and add your checks:
        #!/bin/sh
        grep -q EBX_TAIL_SENTINEL frontend/src/ebx_shared.ts || {
          echo "ERROR: ebx_shared.ts is truncated. Restore the tail before committing."
          exit 1
        }
    • Husky — a Node package that manages git hooks via package.json, so they
      survive npm install and work across machines:
        npm install --save-dev husky
        npx husky init
        echo "grep -q EBX_TAIL_SENTINEL frontend/src/ebx_shared.ts" > .husky/pre-commit
    • lint-staged — runs hooks only on staged files (faster for large repos).
    • The pre-commit hook can also run tsc --noEmit (see pass 5 note D) so
      TypeScript errors block commits too.

  This would have prevented both truncation incidents from ever being committed.
  Start here: https://typicode.github.io/husky/

════════════════════════════════════════════════════════════════════════════ -->
<!-- ══ AUTOMATED PASS — 2026-05-12 (pass 6) ════════════════════════════════════
  ── FIXES APPLIED ──

  ✅ A. bcrypt 72-byte limit crashing signup with HTTP 500 (the bug you reported)
     bcrypt has always had a 72-byte password cap. Older passlib silently
     truncated; newer passlib raises ValueError, which FastAPI converts to 500.
     Fix: added _fit_bcrypt() in backend/app/auth.py that encodes the password
     to UTF-8 bytes, slices to 72, and decodes leniently. Both hash_password()
     and verify_password() now route through it, so signup and login are
     consistent. Passwords ≤ 72 bytes pass through unchanged.
     File: backend/app/auth.py

  ✅ B. Token expiry bumped from 60 min → 7 days (dev convenience)
     Pass 3 flagged that 1-hour tokens silently log users out during dev.
     access_token_expire_minutes is now 10080 (7 × 24 × 60 = 10080).
     Set ACCESS_TOKEN_EXPIRE_MINUTES=60 in your .env for a tighter prod window.
     File: backend/app/config.py

  ✅ C. Date subtraction returns NaN in strict JS / misleads TypeScript
     index.html and feed.html both had:
       .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
     Subtracting two Date objects is a numeric coercion that TypeScript flags
     as an error in strict mode (and is a common footgun). Fixed to:
       .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
     Files: index.html (line ~352), feed.html (line ~452)

  ── NEW INEFFICIENCIES SPOTTED ──

  D. No PATCH /auth/me endpoint — profile prefs still localStorage-only
     display_name, donation_amount, and cause preferences are stored in
     localStorage on profile.html. They don't survive clearing the browser,
     don't sync across devices, and are invisible to the API. This has been
     noted since pass 2. It's the highest-impact backend feature still open.
     Fix: add `display_name: Optional[str]` to BenefactorAccount model, create
     a BenefactorUpdate schema, add PATCH /auth/me to auth.py router, and wire
     the profile form to call it. ~1 hour of work.

  E. list_posts() has no offset/cursor — feed will silently truncate at 50
     crud.list_posts() caps at limit=50 with no way to page further. For now
     that's fine, but once real users are posting, the feed will appear to
     stop at 50 entries. A simple fix: add an `offset: int = 0` parameter and
     change the SQLAlchemy stmt to `.offset(offset).limit(limit)`. The frontend
     would then need to pass ?offset=N to fetch the next page.

  F. Unauthenticated write endpoints still open (noted pass 3 — still unfixed)
     POST /posts, /causes, /initiatives, /organizations all accept anonymous
     writes. Any HTTP client can push garbage to your feed. Minimum fix for
     posts: add `user: BenefactorAccount = Depends(get_current_benefactor)` to
     POST /posts in routers/posts.py. Causes/orgs/initiatives can be admin-only
     or simply JWT-gated for now.

  ── SUGGESTED NEXT ──

  In order of impact:

  1. Add PATCH /auth/me (inefficiency D). This closes the last open profile
     item and means settings actually persist. All the plumbing (auth, DB,
     schema) is already in place — it's just a new endpoint + one model column.

  2. Gate POST /posts behind JWT auth (inefficiency F). Prevents anonymous
     feed spam. Two-line change in routers/posts.py.

  3. Add the Vote model (noted pass 5, still open). `class Vote(Base)` in
     models.py + alembic revision --autogenerate replaces the mock in
     EBX.Votes.forCause with real tallies.

  ── LEARN THIS ──

  Topic: HTTP status codes and FastAPI's exception model

  You hit a 500 this week from a ValueError inside an endpoint. Understanding
  how FastAPI maps Python exceptions to HTTP responses will help you debug
  these faster and write better error handling.

  • 4xx vs 5xx: 4xx is the client's fault (bad input, not authenticated).
    5xx is the server's fault (unhandled exception, database down, etc.).
    A ValueError escaping a route handler always becomes a 500 — it means
    something you didn't expect happened inside your code.

  • HTTPException is the FastAPI way to produce clean 4xx/5xx with a JSON body:
      raise HTTPException(status_code=422, detail="Password too long (max 72 bytes)")
    The client gets {"detail": "..."} instead of a stack trace.

  • RequestValidationError: Pydantic catches malformed request bodies before
    your route code even runs and returns a 422 with field-level detail. You
    can customize this with @app.exception_handler(RequestValidationError).

  • The uvicorn traceback in your terminal is always the most useful artifact
    when you see a 500. The browser only shows "Server Error" but the terminal
    shows the exact line, exception type, and value. Make it a habit to check
    there first.

  • For production: never expose raw tracebacks to clients. Set
    `app = FastAPI(debug=False)` and log exceptions server-side only.

  Start here: https://fastapi.tiangolo.com/tutorial/handling-errors/

════════════════════════════════════════════════════════════════════════════ -->


<!-- ══ AUTOMATED PASS — 2026-05-12 (pass 5) ════════════════════════════════════

  Jax's comments answered above (login bug + Pydantic vs Alembic).
  One bug fixed; one pre-existing truncation healed; new notes below.

  ── FIXES APPLIED ──

  ✅ A. Signup error message was hardcoded and useless (root of the login bug UX)
     Both the profile.html signup form and the floating modal showed a static
     "Email or handle already taken." for EVERY failed signup — including
     network errors, HTTP 500s, or any other API rejection.

     Fix: Auth.signup() now reads the API error detail from the JSON response
     body and stores it in Auth.lastSignupError. The UIs now display that real
     string instead of the hardcoded message.

     Files: frontend/src/ebx_shared.ts (Auth.signup + modal handler)
            profile.html (agDoSignup)
     Result: when you try to sign up with handle "jax" again, the UI will now
             say "Handle already taken" (the exact string FastAPI returns)
             instead of the generic message.

  ✅ B. Pre-existing file truncation in ebx_shared.ts (silent corruption)
     The source file was truncated at `formatNumber, formatEBX, formatPercent, format`
     — the last ~6 lines of the EBX export block were missing. This means the
     file has been in a broken state and esbuild was failing silently since
     sometime after pass 4. The missing tail was restored:
         formatDate, formatShortDate, timeAgo,
         tokenChip, creditBadge, tag, progressBar, statBlock,
         initiativeCard, ... filterBySearch, filterByField, sortBy, Auth,
     };
     (window as any).EBX = EBX;

     File: frontend/src/ebx_shared.ts
     Build: npm run build → ../resources/js/ebx_shared.js  50.6 kb ⚡ Done in 109ms

  ── ROOT CAUSE OF THE LOGIN BUG ──

  The actual functional bug was not in the code — the API and DB logic are
  correct. The real issue is that the database ALREADY HAS one account:
    id=1  email=jax@test.com  handle=jax
  Every attempt to sign up with handle "jax" legitimately fails with a 409.
  Because the UI swallowed the error, Jax had no way to know why.
  Options: (a) log in with jax@test.com, (b) use a different handle,
           (c) delete the test row: `sqlite3 earthbucks.db "DELETE FROM
               benefactor_accounts WHERE id=1;"`

  ── NEW INEFFICIENCIES SPOTTED ──

  C. Auth.signup() was not catching network-level exceptions
     The previous implementation did `return res.ok` with no try/catch. If the
     API server is not running (common in dev), fetch() throws a TypeError and
     the whole agDoSignup/modal handler would crash with an unhandled rejection
     rather than showing a friendly message. The new version still lacks a
     try/catch around the fetch() itself. Should add:
       try { const res = await fetch(...); ... }
       catch { Auth.lastSignupError = 'Cannot reach the server. Is it running?'; return false; }
     This is important during dev when uvicorn isn't running.

  D. ebx_shared.ts file integrity is not verified at build time
     The truncation in Fix B went undetected because there's no integrity check
     (e.g. a line-count assertion, a lint step, or a TypeScript strict compile).
     The esbuild command doesn't typecheck — it just transpiles. Running
     `tsc --noEmit` as a pre-build step would have caught this immediately.
     Consider adding to package.json scripts:
       "typecheck": "tsc --noEmit",
       "build": "tsc --noEmit && esbuild src/ebx_shared.ts ..."
     tsc is already installed (it's in node_modules from the tsconfig).

  E. No tsconfig.json found in frontend/
     The project has TypeScript installed but no tsconfig.json. Without it,
     tsc uses permissive defaults and the `--noEmit` typecheck won't enforce
     strict mode. Add a minimal tsconfig:
       { "compilerOptions": { "strict": true, "target": "ES2020",
         "module": "ESNext", "lib": ["ES2020","DOM"], "noEmit": true } }
     This would have caught the truncation AND several implicit-any issues.

  ── SUGGESTED NEXT ──

  Pick one of these in order of impact:

  1. FIX Auth.signup() network error handling (inefficiency C above).
     Two-minute fix: wrap the fetch() in a try/catch and set
     `Auth.lastSignupError = 'Cannot reach the server. Is the API running?'`.
     This will prevent cryptic console crashes during dev when uvicorn is off.
     File: frontend/src/ebx_shared.ts

  2. Add tsconfig.json + tsc --noEmit to the build (inefficiency D/E above).
     Prevents future silent truncations and adds type safety to the whole file.

  3. Add the Vote model and generate the Alembic migration.
     The schema is fully understood. Add `class Vote(Base)` to models.py, then:
       cd backend && alembic revision --autogenerate -m "add vote model"
       alembic upgrade head
     This closes the "Vote model migration" backlog item and unblocks real vote
     tallies (replacing the deterministic mock in EBX.Votes.forCause).

  ── LEARN THIS ──

  Topic: TypeScript strict mode & `tsc --noEmit` as a linter

  The file truncation this pass was invisible because esbuild doesn't typecheck
  — it just strips types and bundles. TypeScript's own compiler (tsc) is the
  right tool for catching errors at development time. Key concepts:

    • "strict": true in tsconfig enables: strictNullChecks, noImplicitAny,
      strictFunctionTypes, and several others. These catch the class of bugs
      where you assume a value can't be null (it can) or where you accidentally
      pass the wrong type to a function.

    • tsc --noEmit runs the full type-checker without producing any output
      files. It's pure validation — use it in CI or as a pre-build gate.

    • esbuild vs tsc: esbuild is 100x faster because it SKIPS type checking.
      That's a feature for speed, but a risk for correctness. The right workflow
      is: tsc --noEmit (validate) → esbuild (bundle fast).

    • Why this matters for Earthbucks: ebx_shared.ts is 1500+ lines and growing.
      As you add the Vote model, the auth PATCH endpoint, and more UI components,
      strict types will prevent the "wrong shape of data from the API" bugs that
      are hard to debug in the browser.

  Start here: https://www.typescriptlang.org/tsconfig#strict
  Also: https://www.typescriptlang.org/docs/handbook/2/types-from-types.html

════════════════════════════════════════════════════════════════════════════ -->


<!-- ══ AUTOMATED PASS — 2026-05-12 (pass 4) ════════════════════════════════════

  No inline comment from Jax this pass. Code audit + fixes below.

  ── FIXES APPLIED ──

  ✅ A. userBadge() called without handle on index.html (bug)
     The initial render of the top-bar badge always showed "EB" and no handle
     even when a user was logged in, because index.html called EBX.userBadge()
     with no arguments. Fixed by fetching the current user first:

       const me = await EBX.Auth.fetchMe();
       document.getElementById("ebx-user-badge-mount").innerHTML =
         EBX.userBadge({ handle: me?.handle });

     This mirrors what _onLoginSuccess() already did correctly. Now the badge
     shows the real handle on every page load, not just after a fresh login.
     File: index.html

  ✅ B. Dead DOM clear-loop in Annulus._update() (pass 3 note C — now fixed)
     Removed the 7× no-op while-loop that cleared outerGroup (which is always
     empty because vote-arc rendering isn't wired yet). Replaced with a comment.
     File: frontend/src/ebx_shared.ts, _update()

  ✅ C. DOM queries inside the animation loop (pass 3 note D — now fixed)
     Cached document.getElementById('ebx-cause-name') and
     document.getElementById('ebx-cause-timer') into Annulus._nameEl /
     Annulus._timerEl during mount(). _update() now reads the cached refs
     instead of querying the DOM 60× per second.
     File: frontend/src/ebx_shared.ts, Annulus object + mount() + _update()

  ✅ D. Double semicolon cosmetic (});;  →  });)
     File: frontend/src/ebx_shared.ts, _update() method.

  All four fixes compiled successfully:
    npm run build → ../resources/js/ebx_shared.js  50.4 kb ⚡ Done in 39ms

  ── NEW INEFFICIENCIES SPOTTED ──

  E. Missing pages linked from active UI
     Two pages are referenced in the live UI but do not exist:
       • feed.html    — linked from "All posts →" in the feed strip on index.html
                        and from the footer's Platform column.
       • about.html   — linked from the footer's Platform column.
     Until these exist, those links 404 and look broken. Minimum fix: create
     skeleton pages using the same pattern as cause.html / mission.html.

  F. setInterval(render, 60000) doesn't refresh data from the API
     In index.html, render() is called every 60 s to update the clock and
     cycle state. But config.causes / config.organizations / config.feed are
     only fetched once (loadAll() at startup). Stale data is fine for now, but
     when posts are being created in real time the feed strip will be an hour
     out of date. Low priority, but worth noting for when real users are posting.
     Fix when needed: call EBX.loadFeed() inside the render interval, or use
     a small SWR-style TTL cache.

  G. Organization.logo_url still missing from the model
     models.py has no logo_url column on Organization. The backlog item tracks
     this but it's worth flagging that both the frontend component
     (initiativeCard, raceCard) and the backend schema will need updating
     together. Plan: add the column in a single Alembic migration, update the
     Pydantic schema, then add the <img> / initials-circle fallback in the
     relevant render functions.

  H. Post.id is a caller-supplied string (pass 3 note B still open)
     Post, Initiative, Cause, Organization, Mission all have string PKs the
     client must supply. The /docs seed UI makes this manageable for now, but
     any real client will need to generate UUID strings or use server-side
     defaults. Still the right thing to fix before external clients are added.

  ── SUGGESTED NEXT ──

  Two clear options (same as last pass, still open):

  1. PATCH /auth/me — persist display_name, donation_amount, and cause
     preferences server-side. Closes the last "Profile data" item.
     Effort: ~45 min (schema field + endpoint + frontend form).

  2. Create feed.html skeleton — the "All posts →" link is broken right now.
     A minimal page that calls EBX.loadAll() and renders EBX.feedCard() for
     every post would satisfy the link and give Jax a feed page to iterate on.
     Effort: ~30 min.

  ── LEARN THIS ──

  Topic: requestAnimationFrame & the browser rendering pipeline

  Three of the four fixes this pass touched the RAF loop. Understanding how
  the browser rendering pipeline works will help you reason about performance
  and avoid patterns that cause dropped frames.

  Key concepts:
    • The frame budget: browsers target 60 fps → ~16.6 ms per frame. Any work
      in a RAF callback that takes longer than that will cause visible jank.
    • Layout thrashing: reading a DOM property (offsetHeight, getBoundingClientRect,
      getElementById) after writing one forces the browser to flush its layout
      queue mid-frame. Batching reads and writes avoids this.
    • Compositor vs. main-thread animations: transform and opacity are animated
      on the GPU compositor thread and never block JS. The Annulus already uses
      group.style.transform — that's the right call.
    • When to skip a frame: if nothing changed since the last tick, you can
      return early from _update() without touching the DOM at all. A cheap
      state-hash comparison (e.g. did rotationDeg change by > 0.01?) is all you
      need.
    • will-change: transform tells the browser to promote an element to its
      own compositor layer ahead of time, reducing paint cost. Useful for the
      rotating group once the wheel is more complex.

  Start here: https://web.dev/articles/rendering-performance
  Also worth reading: https://gist.github.com/paulirish/5d52fb081b3570c81e3a
  (the classic "what forces layout/reflow" cheatsheet).

════════════════════════════════════════════════════════════════════════════ -->


<!-- ══ AUTOMATED PASS — 2026-05-11 (pass 3) ════════════════════════════════════

  No inline comment from Jax this pass. Read-only audit + notes below.

  ── CORRECTION FROM PASS 1 ──

  Pass 1, Note C stated: "The Annulus runs requestAnimationFrame on every page
  load, even pages that don't mount a wheel."
  This was WRONG. EBX.Annulus._tick() is only started from inside mount(), and
  mount() is only called in index.html. cause.html, mission.html,
  initiative.html, and profile.html do NOT call mount(). The RAF is NOT running
  on pages without the annulus. No fix needed — the architecture is already
  correct here.

  ── NEW INEFFICIENCIES SPOTTED ──

  A. Unauthenticated write endpoints
     POST /posts, POST /causes, POST /initiatives, and POST /organizations all
     lack auth guards. Any anonymous HTTP request can write to the feed or seed
     data. GET endpoints being open is correct, but writes should require a
     valid JWT. For now this is fine for dev seeding via /docs, but it must be
     locked down before real users are onboarded. Minimum fix:
       - POST /posts   → add `user: BenefactorAccount = Depends(get_current_benefactor)`
       - POST /causes  → admin-only guard (or delete endpoint, causes are fixed)
       - POST /initiatives / POST /organizations → require auth at minimum

  B. Client-supplied string IDs on all write models
     Post, Cause, Organization, Initiative, and Mission all have string PKs the
     *caller* must supply. This forces every client to generate IDs and risks
     collisions. Server-side UUID generation (`default=lambda: str(uuid4())` in
     the model, drop `id` from the Create schema) is the standard pattern and
     removes a class of 409-conflict bugs.

  C. Dead DOM clear-loop in Annulus._update() (60 fps waste)
     Every animation frame, _update() runs this for each of 7 segments:
       while (seg.outerGroup.firstChild) {
         seg.outerGroup.removeChild(seg.outerGroup.firstChild);
       }
     But outerGroup is NEVER populated — the vote-arc drawing code that would
     use it hasn't been written yet. This is 7 no-op DOM traversals per frame.
     Remove the loop now; add it back when vote arcs are actually rendered.
     File: frontend/src/ebx_shared.ts, the _update() method.

  D. DOM queries inside the animation loop (getElementById x2 per frame)
     _update() calls document.getElementById("ebx-cause-name") and
     document.getElementById("ebx-cause-timer") on every tick. These elements
     don't change. Cache the references once in mount() (e.g.
     Annulus._nameEl / Annulus._timerEl = ...) and reuse them in _update().

  E. 60-minute JWT with no refresh
     access_token_expire_minutes = 60 in config.py. No refresh token endpoint
     exists. After an hour users are silently logged out — fetchMe() clears the
     token on 401, so the UI just snaps back to the login gate without warning.
     Short fix: bump to 10080 (7 days) in config while in dev. Production fix:
     add POST /auth/refresh that issues a new access token given a longer-lived
     refresh token.

  ── SUGGESTED NEXT ──

  Two clear options, pick whichever feels more motivating:

  1. Add PATCH /auth/me (or POST /auth/prefs) to persist display_name, causes,
     and donation_amount server-side. This closes the last open item under
     "Profile data" and means prefs survive across devices/browsers.

  2. Lock down unauthenticated writes (inefficiency A above). This is a
     30-minute fix: add `Depends(get_current_benefactor)` to POST /posts,
     and decide whether POST /causes / /organizations / /initiatives should
     become admin-only or simply require any valid JWT.

  ── LEARN THIS ──

  Topic: Database Migrations with Alembic

  The schema will need to change soon — logo_url on Organization, a Vote model,
  display_name on BenefactorAccount, maybe a config table for cycleStart. Right
  now the only way to apply these is to delete the SQLite file and re-seed,
  which destroys any real user data.

  Alembic is SQLAlchemy's migration tool and it's already a natural fit since
  the project uses SQLAlchemy ORM. Key concepts:
    • alembic init alembic  — sets up the migrations/ folder
    • alembic revision --autogenerate -m "add logo_url"  — detects model
      changes and writes the migration script for you
    • alembic upgrade head  — applies pending migrations to the DB
    • alembic downgrade -1  — rolls back one step (great safety net)
    • How to configure env.py to point at your SQLAlchemy Base + DB URL

  Learning this now means you'll never have to nuke the database again when the
  schema evolves. It also unblocks the "Vote model migration" backlog item,
  which is already listed under Infra.

  Start here: https://alembic.sqlalchemy.org/en/latest/tutorial.html
════════════════════════════════════════════════════════════════════════════ -->


<!-- ══ AUTOMATED PASS — 2026-05-11 (pass 2) ════════════════════════════════════
  Comment from Jax: "Let's get this login locked in!"

  ✅ DONE — Login flow fully wired to backend API

  What changed:
  1. frontend/src/ebx_shared.ts  (rebuilt → resources/js/ebx_shared.js)
     - EBX.Auth.fetchMe()        — GET /auth/me with stored JWT; auto-clears on 401
     - EBX.Auth.openModal()      — floating Login/Sign Up modal usable from any page
     - "Log in or register" pill now opens the modal (no page navigation needed)
     - On success: badge refreshes in-place with real handle from /auth/me

  2. profile.html
     - On load: checks EBX.Auth.fetchMe() first. Valid JWT → renders real profile.
     - No valid session → shows renderAuthGate() (full-page Login/Sign Up tabs).
     - Both tabs call the real API: POST /auth/signup then POST /auth/login.
     - Settings tab has a "Log Out" button (clears JWT + localStorage, reloads).

  ── How to test ──
  1. cd backend && uvicorn app.main:app --reload
  2. Open profile.html → Login / Sign Up gate appears
  3. Sign Up with email, handle, password (8+ chars)
  4. You're logged in — profile view shows your real handle
  5. Reload — still logged in (JWT persists in localStorage)
  6. Settings → Log Out → back to the gate
  7. "Log in or register" pill on index.html also opens the modal

  ── CODE / API NOTES ──

  1. Secret key: config.py defaults to "dev-only-change-me" when no .env present.
     Create a .env with SECRET_KEY=<random> before any real user accounts go live.

  2. Profile extras (causes, donation amount, display name) still live in
     localStorage only — no prefs endpoint yet. Doesn't sync across devices.
     A PATCH /auth/me or /prefs endpoint would fix this.

  3. EBX.Votes.forCause is still mock (deterministic hash). Reminder: add the
     Vote model and replace when real vote data exists.

  4. /posts and /initiatives still use limit-only pagination. Safe for now;
     needs offset/cursor before feed scales.

  ── INEFFICIENCIES SPOTTED ──

  A. Dual identity storage: profile extras (causes, amount, display) live in
     localStorage while auth identity (handle, email) lives in the API. Should
     be unified — store all prefs server-side, or document localStorage as ephemeral.

  B. ebx_shared.js is 50 KB uncompressed, bundled into a single file loaded
     on every page. Consider code-splitting once features stabilise (auth + utils
     as one chunk; page-specific renderers as separate entry points).

  C. The Annulus runs requestAnimationFrame on every page load, even pages that
     don't mount a wheel. EBX.Annulus.stop() exists but is never called
     automatically. Add an auto-stop when no container is found.

  D. config.cycleStart is hardcoded in ebx_shared.ts (2026-01-01). Should be
     served from the API so it can be updated without a frontend rebuild.

  ── SUGGESTED NEXT ──
  Add PATCH /auth/me to persist display_name, causes, donation_amount server-side,
  so profile prefs survive across devices and browsers.
  -OR- stand up /docs and use FastAPI's built-in UI to seed votes, missions,
  and contributions as the "Admin interface" backlog item describes.

  ── LEARN THIS ──
  Topic: OAuth2 / OpenID Connect (OIDC)
  You've built a solid username+password JWT system. The natural next step is
  OAuth2 so you can offer "Log in with Google/GitHub" — removing password
  management from your responsibility and dramatically lowering signup friction.
  Key concepts:
    • Authorization Code flow (what "Log in with Google" actually does)
    • access_token vs id_token (JWT) vs refresh_token
    • PKCE (Proof Key for Code Exchange) — required for SPA/mobile clients
    • How to add a social login to FastAPI (Authlib is the standard library)
  Start here: https://fastapi.tiangolo.com/tutorial/security/
════════════════════════════════════════════════════════════════════════════ -->

<!-- ══ AUTOMATED PASS — 2026-05-11 ══════════════════════════════════════════
  Changes applied this run:

  ✅ DONE — EBX home mark (re-done, CSS now actually connected)
  - ebx_frontend.css: .ebx-home-mark rule appended (was missing entirely — that
    was why the style wasn't applying last time despite the HTML being inserted).
    Rule: fixed top:14px left:20px, Playfair Display 900 1.1rem, parchment color,
    opacity 0.7 → 1 on hover, z-index 200.
  - cause.html, profile.html, initiative.html, mission.html: <a class="ebx-home-mark">
    injected immediately after <body> on each page. CSS is in the shared stylesheet
    that every page already links, so it will apply correctly.
  - index.html topbar: tagline now reads "<strong>EBX</strong> — You donate. We follow."
    giving the wordmark prominence without a separate fixed element.

  ✅ DONE — "Home navigation" backlog item (cause/initiative/mission/profile pages)
  - The .ebx-home-mark satisfies this. Marking closed below.

  ── CODE / API NOTES (no changes made, flagging for awareness) ──

  1. EBX.Votes.forCause is entirely mock — it generates deterministic fake percentages
     from a hash of (causeIndex, cycleNum, org.id). No Vote model exists in models.py.
     This is the right call for now but means the race cards show invented numbers.

  2. Organization has no logo_url column in models.py (confirmed by reading models.py).
     The initials-circle fallback needs to be implemented in the frontend at the same
     time the column is added to avoid a migration gap.

  3. Cycle time-jump: cycleStart is hardcoded in ebx_shared.js line 9. To simulate a
     full rotation today, set cycleStart to "2025-03-10T00:00:00" (≈ 49 days before
     May 10). Each 7-day block shifts the active cause by one. Added ?simdate= feature
     as a backlog item below.

  4. /posts and /initiatives endpoints use limit-only pagination (no offset or cursor).
     If feed grows, older posts will be silently dropped. Low priority now but worth
     fixing before real data comes in.

  5. config.py secret_key defaults to "dev-only-change-me". Fine for dev but needs a
     .env check before any real user accounts are created.

  ── SUGGESTED NEXT ──
  "Profile data — walk through creating/storing user accounts and login flow."
  The BenefactorAccount model and auth router are already wired. You can create an
  account right now via POST /auth/register in /docs and log in via POST /auth/token.
  Suggest doing a full walkthrough in the next pass and marking this item done or
  splitting it into sub-tasks.
════════════════════════════════════════════════════════════════════════════ -->
---


## Cause Page
- [ ] **Link to profile** Same location as main page
- [ ] **Page design** The top part of the page toggles between causes. It is structured as follows.

EBX                                                                        profile
___Leading initiatives___  [cause] decision - [date] ___Past/Ongoing Initiatives___
|                        | Select upcoming mission*  |                             | *Dropdown selection with "[Decision date] - [Cause]" for next 7
|________________________|                           |_____________________________|

There is a brief middle section where users select which initiative to look at.

Search                                                         Propose an Initiative
Name     Rating      Location    Date conceived            ebx committed for [date]
 ____________________________________________________________________________________
|____________________________________________________________________________________|
|____________________________________________________________________________________|

And the bottom section contains more detailed information about the initiative, including ratings, posts/comments/user feedback, history (it might have been edited/improved), budget, org backing, etc.


- [ ] **Cause Annulus** Pie chart showing the leading initiatives for the upcoming vote.

- [x] **Remove supabase** Removed pass 7. submitPost/commitEbx now call FastAPI; castVote is a stub until Vote model lands.
- [ ] 


## Initiatives
- [ ] **Cards** Top section: "Initiative" 
                              leader - x % - Contribute ("Contribute" links to that cause page)
                              Total pool so far: x
               Bottom section: "Organization for [initiative]" (Note that this is the initiative for the previous cycle)
                              leader - x% - Contribute ("Contribute" links to that orgs mission page)
                              Total pool so far: x

- [ ] **Data** Initiative table needs a column for the dates that that initiative applied for the cause pool. This and the vote share will allow the cards on the main page to pull it in.

- [ ] **Initiative ratings.** `Initiative.rating` exists on the model but no endpoint to update it. Add `POST /initiatives/{id}/ratings`.
- [ ] **Initiative Logos** The other half of the credit coin. Will be complicated to define/create credit coins.

## Missions
- [ ] **Organization inputs** Organizations can fill out mission pages for whatever initiative they want. Once the election is active everything becomes linked together by election widgets.
- [ ] **Mission Annulus** Each mission gets its own ring widget. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from homepage to mission page. Will increase in complexity.

## Organizations
- [ ] **Organization logos.** Add `logo_url` to `Organization`. Until logos are uploaded, render a colored circle with the org's initials. Logos serve as a verification layer when the team approves orgs. This is 1/2 of the credit coin.
- [ ] **Organization information** All organization profiles are public and can be searched/accessed from a sidebar in the feed tab, or wherever they pop up (for example the active election, the mission pages, etc.)
- [ ] **Profile page** Organization profile pages are very similar to benefactor profile pages. Organizations do most of their work on the mission page. Once approved as a candidate, they put all important information on a mission page which continues if they win and is frozen and linked from their profile if not.

## Profile / accounts
- [ ] **Flow** To create an account should be easy. Account will have things like : Wallet, Missions, Reviews/Rating, messages, current votes and commits for each of the 7 causes, org memberships, etc.
- [ ] **Dropdown dialog** Profile logo has dropdown dialog when logged in where users can log out, view wallet, or switch to an organization account.
- [~] **Profile data** Login/signup now wired to API (pass 2 above). Next: persist display_name, causes, and donation_amount server-side via PATCH /auth/me or a /prefs endpoint.
- [ ] **Credit badge.** mission logo (or initials) in the center. Annulus fills with the cause color throughout first 49 days of mission. Turns to permanant state upon completion.
- [ ] **Org-account flow.** Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org employee.
- [ ] **Logo colorization via vote participation.** Below a donation threshold, a benefactor must have participated in the org vote to unlock the colored perk for that weeks sector. Add `verified_via_vote: bool` to `BenefactorAccount`, set after first vote.

## UI / Annulus
- [ ] **Cause label Visibility** Make annulus thicker so that cause labels are fully visible. Multi-word entries can take multiple lines.
- [ ] **org election card** Card needs more information about the election. Add leading org with the associated % of vote. Card will link you to a mission page. The initiatives are elected/debated from the cause page, and the organizations are elected/debated from the mission page in a similar way. Once the organization is elected for a particular mission, one can no longer toggle between different orgs versions of that mission page.
- [ ] **Card data** If there is no initiative/organization slotted in for a particular date, show "No votes yet"

## Credit
- [ ] **Coin generation** Coins and mission are created when org is elected. Coins have same geometry as annulus but their cause segment is the only one highlighted and the relative value to when it was created in the middle.
- [ ] **Coin details** The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission...
- [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
- [ ] **Transactional logic** Coins operate similarly to a cryptocurrency, can be exchanged for coins from other missions. All coins are donations, although can be removed which will be complex tax-law-wise.

## Feed
- [ ] **Integrate** Integrate feed into main, mission, cause, and profile pages.
- [ ] **Types of post** Benefactor posts: Initiative ratings, organization reviews, mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed). Org posts: Mission ideas, mission updates, mission proposals (When competing for an org election), problems (asking users for feedback/ideas). EBX posts: Stories, status-updates on the mission metrics.
- [ ] **Filtered feeds** By applying filters to it, the feed improves the experience of many pages across earthbux.

# About
- [ ] **Page location** Link to about page from Mechanics section on main page. Link titled "Our Mission"
- [ ] **Clarify core goals** Root out wasteful and fraudulent charity organizations/players, reorient peoples media consumption towards meaningful things, focus charity efforts on the cause rather than sponsors, democratize charioty by finding the best idea rather than the most profitable one, rewarding thoughtful ideas, pooling donations to prevent redundant/competing charity missions. And most importantly, provide unbiased and mission-oriented news coverage of every mission.
- [ ] **Financial structure** Committing to an initiative: 20% sent if your initiative wins, 10% if not. Committing to an organization: 100% if they win, 20% if not.
- [ ]  **Information about how I founded the company...**

## Verification & perks
- [ ] **Donation threshold.** Define and store the threshold amount (env var or config row). Compute on the fly per benefactor. Threshold for initiative donations moderates logo colorization and for org donations it moderates user visibility/voice.
- [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implement as either (a) a startup hook that grants on signup if `id <= 100`, or (b) a one-time admin script after the first 100 register. Decide which.

## Infra
- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only.
- [ ] **Vote model migration.** Generate via `alembic revision --autogenerate` once Vote is added.
- [ ] **cycleStart from API.** Currently hardcoded in ebx_shared.ts — should come from a config endpoint so it can change without a rebuild.

## Polish / not blocking
- [ ] **About page.** Linked from footer but doesn't exist yet.
- [ ] **Org page.** A view for an Organization's profile (missions, reviews, members).
- [ ] **Search across initiatives + orgs + causes.** A real version belongs on its own page.
- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke.

## Cycle / process modeling
- [ ] **Dual-decision week.** Each cause has TWO per-cycle decisions a week apart: an initiative-decision (week N) followed by an org-election-decision (week N+1). The current `Cycle` engine collapses both into one weekly tick; revisit when wiring real Vote/Initiative state through the race card's two halves.

## Non-conventional interfaces
- [ ] **Static off-line mode** Create an offline-mode that saves the current state of the project as an example so that I can download it on a hard drive and demonstrate it for someone without needing server access.
- [ ] **Swift** Create mobile version.