# Autonomous Run Log

Running log for the unattended scheduled jobs (business review, new unit,
marketing push, resource drop) covering the period the business owner is
away. Newest entries at the top. Each entry: date, job name, what happened,
anything that needs a human decision.

Hard boundaries every job must respect, no exceptions, regardless of what
is found during a run:
- Never delete anything on any platform (TPT, Gumroad, TES, Pinterest)
- Never edit the Categories or Licence step on an already-published TES
  resource (a 2026-07-19 incident corrupted a live paid listing to FREE
  doing exactly this — see project memory `project_direction_change.md`)
- Never touch the off-brand Gumroad products (SWMS guide, ADHD guide)
- No new platforms, no pricing changes, no strategic direction changes
- If something needs a human decision (looks like a bug, a duplicate, an
  ambiguous state), log it clearly below and move on — do not attempt to
  resolve it unilaterally

---

(entries below this line, newest first)

## 2026-08-20 — Scheduled business review + integrity checks: all three platforms fully working, all catalogs clean, prior networks_hardware_unit1 anomaly resolved

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies pre-installed. Installed
`python-dotenv`, `browser_cookie3`, `openai`, `python-pptx`,
`python-docx`, `yt-dlp` from `requirements.txt`, plus `playwright==1.56.0`
pinned over pip-latest to match this container's pre-installed Chromium
build 1194 at `/opt/pw-browsers` — same workaround as every prior run.
Ephemeral to this container only; `requirements.txt` still doesn't pin
the playwright version.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-20 05:41
UTC):
- **TPT**: USD 8.98 net, 3 sale(s) — real figures via `TPT_SESSION_JSON`
  env var, login/session worked cleanly this run.
- **Gumroad**: AUD 0 net, 0 sale(s) — via `GUMROAD_TOKEN` API.
- **TES**: GBP 0.30 net, 1 sale(s) — real figures; `TES_EMAIL`/
  `TES_PASSWORD` form login succeeded and saved a fresh session
  (`.tes_session.json`), unlike several recent runs where TES login
  failed outright.
- **All three platforms returned genuine, credentialed figures this
  run** — first time in a while all three have worked in the same run.

**Catalog size**: `business_review.py` again reports **0 live unit(s)** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent here). Real catalog (from `data/units/*.json`, excluding
the AI-series and bundle config files) is the same 11 units as every
recent run: year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 live
  units, session valid throughout. **All 11 units came back fully clean**,
  every listing `[OK]` — no empty/near-empty descriptions, no unrendered
  markdown, no stray HTML, no title/product mismatches.
  - Notably, **`year7_networks_hardware_unit1` is back to 9 products**
    (bundle, assessment pack, 7 lessons), all `[OK]`. The prior run
    (2026-08-19 later run) flagged this unit as returning only 1 product
    against an expected ~9 — that anomaly did not reproduce this run;
    whatever caused it (a transient dashboard search/pagination glitch,
    most likely, given the same-day commit "Fix verify_tpt_listings.py:
    handle My-Products dashboard pagination") appears resolved. Logging
    for the record, not treating as fully explained from a read-only
    check alone.
- `verify_gumroad_listings.py` — **ran clean.** Checked 10 product(s)
  matching "Unit 1" (of 10 total in the store): all 10 `[OK] (published)`,
  no corruption signals. Same 10 URLs as every prior run
  (`focuslabdigital.gumroad.com/l/` + `yyrcw`, `psbzqv`, `hmntzx`,
  `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`, `kezhjt`, `bpvevc`).
- `verify_tes_listings.py` — **ran clean.** Logged in via saved TES
  session cookies. Found 30 resource(s) total on the dashboard; 21
  matched "Unit 1" (the other 9 are the shelved AI-series Unit 1
  resources, out of this checker's filter scope, consistent with the
  documented "9 resources, Unit 1 only" open item below). All 21 checked
  `[OK]` — no corruption signals. This checker does not cover the known
  TES duplicate pair or the permanently-broken resource noted below,
  since neither matches "Unit 1" text filtering; not re-verified this
  run.

**Open items** (unchanged from `BUSINESS_REVIEW.md`'s maintained list,
none actioned; the networks_hardware_unit1 anomaly above appears resolved
but is not being removed from tracking without another clean run to
confirm): TES Unit 1 AI-series presenter-placeholder cosmetic bug, TES
duplicate resource pair (13432831 / 13432796), TES resource 13445828
permanently broken, off-brand Gumroad products still on the storefront,
shelved AI-series Units 3-8 still live on TES.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-19 (later run) — Marketing push blocked: no Pinterest credentials in this container, and no local release artifacts to read wave history from

Task: check each live unit's `07_Marketing/marketing_content.md` for its
highest existing Pinterest wave number, pick 2-3 units most due for a fresh
wave, draft 3 new distinct-angle pins each, and post via
`publish_pinterest.py --unit <id> --wave N`. Did not get past the
pre-flight checks — nothing was drafted or posted.

**Blocker 1 — no local release artifacts to read.** `releases/` is
gitignored (build output, never committed) and does not exist at all in
this fresh clone, same as every prior session's finding for the
`business_review.py` catalog count. That means no unit's
`07_Marketing/marketing_content.md` is present locally, so there is no way
to read prior wave numbers or prior pin angles for any unit. Regenerating
that file with `generate_marketing_content.py` would only ever produce a
fresh "wave 1" section (it has no memory of what waves were posted in past
sessions) — using that to decide "genuinely distinct from prior waves"
would be guessing, not checking, so I did not generate or post anything on
that basis.

**Blocker 2 — no Pinterest credentials at all, independent of blocker 1.**
Checked this container's full environment (`env`) and the repo root: no
`.pinterest_session.json` (the cookies file `publish_pinterest.py` requires
and exits immediately without — `COOKIES_FILE.exists()` is the very first
check in `main()`), and no `PINTEREST_*` variable of any kind. This is
unlike today's earlier business-review run in this same log, which found
`GUMROAD_TOKEN`, `TES_EMAIL`/`TES_PASSWORD`, and `TPT_SESSION_JSON` all
newly present as container env vars — Pinterest has no equivalent, here or
in any prior logged run I can find. `publish_pinterest.py` has no
env-var fallback for its cookies (unlike `publish_tpt.py`'s
`TPT_SESSION_JSON` pattern), so even if one existed it wouldn't currently
be picked up — not changed here since there's no secret to wire up and
this is a report-only run.

**Net effect**: even with real Gumroad-thumbnail and unit-config access,
there is currently no path in this cloud environment from "draft new
Pinterest pins" to "actually post them" — the credential this specific job
needs has never been provisioned, in contrast to the other three
platforms which now have working (if sometimes broken) credentials. Worth
a human decision: either add a `.pinterest_session.json` /
`PINTEREST_SESSION_JSON`-style secret to this environment (mirroring how
`TPT_SESSION_JSON` was set up), or accept that the Marketing Push job
cannot run unattended until that exists.

No files changed, no pins drafted, nothing posted, nothing deleted. Only
change this run is this log entry.

## 2026-08-19 (second run) — Scheduled business review + integrity checks: cookie-normalization fix landed, TPT now fully working (revenue + all 11 units verified clean); TES still blocked; one unit's product count looks anomalous

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies pre-installed (`dotenv`, `playwright`,
`browser_cookie3`, etc. all missing) — installed via `requirements.txt`
plus `playwright==1.56.0` pinned over the pip-latest 1.62.0 (which again
does not match this container's pre-installed Chromium build 1194), same
workaround as every prior run. Ephemeral to this container only —
`requirements.txt` still doesn't pin the playwright version.

**This is the second business-review run today.** The `Normalize raw
Cookie-Editor exports before Playwright add_cookies()` commit that landed
between the first run (11:03 UTC) and this one fixed the exact `sameSite`
parse error that broke `TPT_SESSION_JSON` in that run — TPT authentication
now works end-to-end here, both for revenue and for the integrity
checkers.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-19 11:14
UTC):
- **TPT**: USD 7.91 net, 2 sale(s) — real figures, first successful TPT
  revenue check in several runs.
- **Gumroad**: AUD 0 net, 0 sale(s) — via `GUMROAD_TOKEN` API, unchanged.
- **TES**: ERROR — still "TES login failed. Check TES_EMAIL/TES_PASSWORD in
  .env, or the login form's selectors may have changed -- check
  releases/debug_tes_login_error.png." `TES_EMAIL`/`TES_PASSWORD` are set
  in the environment, so this remains a genuine login failure (wrong/stale
  credentials, a CAPTCHA, or a changed selector), unchanged from the first
  run today. The referenced debug screenshot is still never written on
  this failure path (same dead troubleshooting pointer noted in the first
  run's entry — tool bug, not touched, report only). No `releases/`
  directory exists in this fresh clone at all.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent here). Real catalog (from `data/units/*.json`, excluding
the AI-series and bundle config files) is the same 11 units used for the
integrity checks below: year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran successfully against all
  11 live units (session now valid, per the fix above). 10 of 11 units
  returned a product count consistent with prior runs (5-11 products
  each — bundle, assessment pack, and individual lessons) and every single
  listing on every unit came back `[OK]` — no empty/near-empty
  descriptions, no unrendered markdown, no stray HTML, no title/product
  mismatches.
  - **Flagging for review, not touched**: `year7_networks_hardware_unit1`
    returned only **1 product** this run — `Networks & Hardware: Unit 1 –
    Building and Securing a Network — Lesson 1 FREE...`
    (https://www.teacherspayteachers.com/Product/Networks-Hardware-Unit-1-Building-and-Securing-a-Network-Lesson-1-FREE-17033469),
    itself `[OK]` with no corruption signals. Per `PROGRESS.md`'s build
    history this unit should have ~9 TPT products (7 lessons + assessment
    pack + bundle), and every other unit checked this run returned 5-11.
    This unit already has a documented history of a live-listing
    corruption incident (2026-07-19, licence step edit turned a paid
    listing FREE — see the boundary note at the top of this log). Whether
    the other ~8 products are deactivated, retitled (so the keyword search
    no longer matches them), or something else is unknown from this
    read-only check alone — flagging for a human look, not investigated
    further and nothing changed.
- `verify_gumroad_listings.py` — **ran clean.** Checked 10 product(s)
  matching "Unit 1" (of 10 total in the store): all 10 `[OK] (published)`,
  no corruption signals. Same 10 URLs as prior runs
  (`focuslabdigital.gumroad.com/l/` + `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`,
  `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`, `kezhjt`, `bpvevc`).
- `verify_tes_listings.py` — could not run; failed at the same TES login
  step as the revenue check above (`TES_EMAIL`/`TES_PASSWORD` are set but
  login still fails). No TES listings checked this run.

**Open items** (unchanged from `BUSINESS_REVIEW.md`'s maintained list,
none actioned): TES Unit 1 AI-series presenter-placeholder cosmetic bug,
TES duplicate resource pair (13432831 / 13432796), TES resource 13445828
permanently broken, off-brand Gumroad products still on the storefront,
shelved AI-series Units 3-8 still live on TES. Plus the new
`year7_networks_hardware_unit1` product-count anomaly flagged above.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-19 — Scheduled business review + integrity checks: credentials present for the first time, but TPT and TES both fail for new reasons; Gumroad verified clean

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies pre-installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`, `playwright`,
and `browser_cookie3` for this run only (not committed, ephemeral to this
container; `requirements.txt` still doesn't pin these). One new wrinkle
this run: the pip-latest `playwright` (1.62.0) does not match the
pre-installed Chromium binary in this container (build 1194 on disk vs.
build 1234 expected) and fails with "Executable doesn't exist" — pinned
`playwright==1.56.0` (the version whose bundled `browsers.json` targets
build 1194) to work around it, ephemeral to this container only.

**Unlike every prior logged run, this container DOES have credentials**:
`GUMROAD_TOKEN`, `TES_EMAIL`/`TES_PASSWORD`, and `TPT_SESSION_JSON` are all
set in the environment (no `.env` file, but the env vars are populated
directly). This is new — worth flagging since it means the recurring
"no credentials in this container" blocker from every prior entry
(2026-07-31 through 2026-08-17) is no longer the root cause of the TPT/TES
failures below; there are now two distinct, more specific problems.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-19 11:03
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)." Root cause is more specific than "no session" this time: the
  `TPT_SESSION_JSON` env var IS set, but fails to parse before the
  fallback: `Could not parse TPT_SESSION_JSON: BrowserContext.add_cookies:
  cookies[0].sameSite: expected one of (Strict|Lax|None)` — the first
  cookie's `sameSite` value in that secret is not one of Playwright's
  accepted casings (Playwright requires exactly `Strict`/`Lax`/`None`,
  title-cased). The Chrome-cookie fallback also isn't usable (no real
  Chrome profile / `DBUS_SESSION_BUS_ADDRESS` in this container).
- **Gumroad**: AUD 0 net, 0 sale(s) — real check via `GUMROAD_TOKEN`
  against the Gumroad API (not a credentials error this time).
- **TES**: ERROR — "TES login failed. Check TES_EMAIL/TES_PASSWORD in
  .env, or the login form's selectors may have changed -- check
  releases/debug_tes_login_error.png." `TES_EMAIL`/`TES_PASSWORD` ARE set,
  so this is a genuine login failure (wrong/stale credentials, a CAPTCHA,
  or a changed selector), not a missing-credentials case. Note: the
  referenced debug screenshot is never actually written on this failure
  path — `publish_tes.py`'s `_login()` raises `RuntimeError` directly with
  no `_take_debug_screenshot()` call before it, so the error message's own
  troubleshooting pointer is currently dead; nothing to check at that
  path. (Tool bug, not touched — report only.)
- **No revenue figures obtained this run for TPT or TES.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Real catalog (from `data/units/*.json`,
excluding the AI-series and bundle config files) is still the same 11
units used for the integrity checks below: year7_algorithms_unit1,
year7_cybersecurity_unit1, year7_data_representation_unit1,
year7_digital_systems_unit1, year7_game_design_unit1,
year7_networks_hardware_unit1, year7_orientation_unit1,
year7_python_programming_unit1, year7_spreadsheets_unit1,
year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically with the same
  `TPT_SESSION_JSON` sameSite parse error described above (plus
  `browser_cookie3`'s Chrome-cookie fallback failing separately). No
  listings were actually checked this run — same practical outcome as
  prior runs, different root cause.
- `verify_gumroad_listings.py` — **ran successfully, all clean.** Checked
  10 product(s) matching "Unit 1" (of 10 total in the store): all 10
  showed `[OK] (published)` with no corruption signals (empty
  description, unrendered markdown, stray HTML, title/product mismatch).
  Listed products/URLs: Digital Technologies Orientation Unit 1
  (https://focuslabdigital.gumroad.com/l/yyrcw), Game Design Unit 1
  (https://focuslabdigital.gumroad.com/l/psbzqv), Introduction to
  Programming Unit 1 (https://focuslabdigital.gumroad.com/l/hmntzx),
  Digital Systems Unit 1 (https://focuslabdigital.gumroad.com/l/caqcw),
  Websites & Web Design Unit 1
  (https://focuslabdigital.gumroad.com/l/dvjrck), Spreadsheets & Data
  Analysis Unit 1 (https://focuslabdigital.gumroad.com/l/yqnok), UX &
  Interface Design Unit 1 (https://focuslabdigital.gumroad.com/l/ivmbkk),
  Cyber Security & Digital Footprints Unit 1
  (https://focuslabdigital.gumroad.com/l/llfnfx), Data Representation
  Unit 1 (https://focuslabdigital.gumroad.com/l/kezhjt), Algorithms &
  Programming Logic Unit 1 (https://focuslabdigital.gumroad.com/l/bpvevc).
  This is the first run in this log with a genuine, credentialed Gumroad
  listing check (not just a revenue-API check) — all clean.
- `verify_tes_listings.py` — **could not run**: same `RuntimeError: TES
  login failed...` as the business-review TES check above. No listings
  were actually checked this run.

**Nothing was verified this run for TPT or TES.** No confidence statement
can be made about TPT or TES listing integrity today. Gumroad listings are
newly confirmed clean as of this run. The last clean TES check remains the
2026-07-31 (third run) entry below.

**New open items from this run** (in addition to the carried-forward list
in `BUSINESS_REVIEW.md`, unchanged below):
- `TPT_SESSION_JSON` (as currently set in this container's environment)
  has a malformed cookie — `sameSite` value isn't `Strict`/`Lax`/`None` —
  so it fails to parse and TPT falls back to "not logged in" even though a
  session secret is present. Needs the secret regenerated/reformatted, or
  `publish_tpt.py --save-session` re-run with a real browser.
- TES login is failing with real `TES_EMAIL`/`TES_PASSWORD` credentials
  present (not a missing-credentials case) — cause not diagnosed further
  (report-only; no fix or retry with different logic attempted). Worth a
  human checking those credentials are current and TES hasn't added a
  CAPTCHA/2FA step.
- `publish_tes.py`'s login-failure error message references a debug
  screenshot (`releases/debug_tes_login_error.png`) that is never actually
  written on that code path — the message is misleading for anyone
  debugging this. Not fixed (report only).

**Open items / decisions carried forward unresolved** (see
`BUSINESS_REVIEW.md` for the full current list): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-17 — Scheduled business review + integrity checks: all three platforms blocked again, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0`, and `browser_cookie3` for this run only (not
committed, ephemeral to this container; `requirements.txt` still doesn't
pin these, so this keeps recurring every fresh session). This container
again has **no `.env` file** (only `.env.example`), no `GUMROAD_TOKEN` env
var, no `.tpt_session.json`, no `.tes_session.json`, and no real Chrome
profile for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing).

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-17 01:10
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)."
- **Gumroad**: ERROR — "Not logged in and no Gumroad credentials in
  .env."
- **TES**: ERROR — "No TES_EMAIL/TES_PASSWORD in .env and no saved
  session."
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "ERROR: not
  logged in to TPT (no valid session found) -- cannot check listings."
  (Chrome-cookie fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`.) Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue.
- `verify_gumroad_listings.py` — **could not run**: `ERROR:
  GUMROAD_TOKEN not set (checked .env and environment variables)`. No
  listings were actually checked this run.
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run.

**Nothing was verified this run.** No confidence statement can be made
about TPT, Gumroad, or TES listing integrity today — the last clean
checks remain the 2026-07-31 (third run) entry below (Gumroad clean, TES
clean).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-10 — Scheduled business review + integrity checks: all three platforms blocked again, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same recurring pattern as every prior fresh-clone
session — no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0`, and `browser_cookie3` for this run only (not
committed, ephemeral to this container; `requirements.txt` still doesn't
pin these, so this keeps recurring every fresh session). This container
again has **no `.env` file** (only `.env.example`), no `GUMROAD_TOKEN` env
var, no `.tpt_session.json`, no `.tes_session.json`, and no real Chrome
profile for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing).

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-10 04:44
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)."
- **Gumroad**: ERROR — "Not logged in and no Gumroad credentials in
  .env."
- **TES**: ERROR — "No TES_EMAIL/TES_PASSWORD in .env and no saved
  session."
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "ERROR: not
  logged in to TPT (no valid session found) -- cannot check listings."
  (Chrome-cookie fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`.) Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue. Still
  needs a human to run `python publish_tpt.py --save-session` once with a
  real browser (or set `TPT_SESSION_JSON`) to unblock future automated
  checks.
- `verify_gumroad_listings.py` — **could not run**: `ERROR:
  GUMROAD_TOKEN not set (checked .env and environment variables)`. No
  listings were actually checked this run.
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run.

**Nothing was verified this run.** No confidence statement can be made
about TPT, Gumroad, or TES listing integrity today — the last clean
checks remain the 2026-07-31 (third run) entry below (Gumroad clean, TES
clean).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-08-03 — Scheduled business review + integrity checks: all three platforms blocked again, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per known
live unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`).
Report-only run — nothing found below was touched, edited, or deleted.

**Environment note**: same as every prior fresh-clone session, this
container had no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0`, and `browser_cookie3` for this run only (not
committed, ephemeral to this container; `requirements.txt` still doesn't
pin these, so this keeps recurring every fresh session). This container
again has **no `.env` file** (only `.env.example`), no `GUMROAD_TOKEN` env
var, no `.tpt_session.json`, no `.tes_session.json`, and no real Chrome
profile for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing).

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-08-03 01:05
UTC):
- **TPT**: ERROR — "TPT session expired (.tpt_session.json no longer
  valid)."
- **Gumroad**: ERROR — "Not logged in and no Gumroad credentials in
  .env."
- **TES**: ERROR — "No TES_EMAIL/TES_PASSWORD in .env and no saved
  session."
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "ERROR: not
  logged in to TPT (no valid session found) -- cannot check listings."
  (Chrome-cookie fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`.) Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue. Still
  needs a human to run `python publish_tpt.py --save-session` once with a
  real browser (or set `TPT_SESSION_JSON`) to unblock future automated
  checks.
- `verify_gumroad_listings.py` — **could not run**: `ERROR:
  GUMROAD_TOKEN not set (checked .env and environment variables)`. No
  listings were actually checked this run.
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run.

**Nothing was verified this run.** No confidence statement can be made
about TPT, Gumroad, or TES listing integrity today — the last clean
checks remain the 2026-07-31 (third run) entry above (Gumroad clean, TES
clean).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-07-31 (fourth run) — Scheduled business review + integrity checks: all three platforms blocked, no credentials or sessions available in this container

Ran the standard routine: `python business_review.py --save`, then the
three post-publish integrity checkers (`verify_tpt_listings.py` per live
unit, `verify_gumroad_listings.py`, `verify_tes_listings.py`). Report-only
run — nothing found below was touched, edited, or deleted.

**Environment note**: fresh clone again had no Python dependencies
installed (`dotenv`, `playwright`, `browser_cookie3` all missing).
Installed `python-dotenv`, `playwright==1.56.0` (pinned to match the
sandbox's pre-installed Chromium revision 1194 — same fix logged in prior
runs; still not pinned in `requirements.txt`, so this keeps recurring),
and `browser_cookie3`. Unlike every prior run, this container has **no
`.env` file at all** (only `.env.example`), no `GUMROAD_TOKEN` env var, no
`.tpt_session.json`, no `.tes_session.json`, and no real Chrome profile
for the cookie fallback (`DBUS_SESSION_BUS_ADDRESS` missing). Net effect:
every one of the three platforms failed to authenticate this run — worse
than prior sessions, where at least Gumroad (via API token) and/or TES
(via saved session) usually worked.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 06:16
UTC):
- **TPT**: ERROR — session expired / no `.tpt_session.json` found.
- **Gumroad**: ERROR — not logged in, no `GUMROAD_TOKEN` in `.env` or
  environment.
- **TES**: ERROR — no `TES_EMAIL`/`TES_PASSWORD` in `.env` and no saved
  session.
- **No revenue figures obtained this run on any platform.** Last confirmed
  full snapshot (all 3 platforms) remains 2026-07-19: TPT $13.45 USD / 1
  sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale. Most recent partial
  snapshot (2026-07-31, third run): Gumroad A$0.00 / 0 sales, TES £0.30
  GBP / 1 sale (TPT still blocked that run too).

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output
directory, absent in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known
  live units above. Every single one failed identically: "not logged in
  to TPT (no valid session found) -- cannot check listings" (Chrome-cookie
  fallback also failed: `Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'`). Same root cause as prior runs — no
  session/login available in this container, not a per-unit issue.
- `verify_gumroad_listings.py` — **could not run**: `ERROR: GUMROAD_TOKEN
  not set (checked .env and environment variables)`. No listings were
  actually checked this run (differs from the third run's "ran clean"
  result — that run had `GUMROAD_TOKEN` available via the environment,
  this one does not).
- `verify_tes_listings.py` — **could not run**: raised `RuntimeError: No
  TES_EMAIL/TES_PASSWORD in .env and no saved session.` No listings were
  actually checked this run (differs from the third run's "ran clean,
  cookie-banner fix confirmed working" result — that run had a saved
  session, this one does not).

**Nothing was verified this run.** No confidence statement can be made
about Gumroad or TES listing integrity today — the last clean checks for
both remain the third run's (2026-07-31, earlier today).

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8
still live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration.

---

## 2026-07-31 (third run) — Scheduled business review + integrity checks: Gumroad clean, TES clean (cookie-banner fix confirmed working), TPT still blocked by missing session

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers (`verify_tpt_listings.py` per live unit,
`verify_gumroad_listings.py`, `verify_tes_listings.py`). Report-only run —
nothing found below was touched, edited, or deleted.

**Environment note**: same as every prior fresh-clone session, this
container had no Python dependencies installed (`dotenv`, `playwright`,
`browser_cookie3` all missing) — installed `python-dotenv`,
`playwright==1.56.0` (pinned to match the sandbox's pre-installed Chromium
revision 1194, per the pin recommended in the previous log entry — still
not actually added to `requirements.txt`, so future sessions will keep
hitting this cold until someone does), and `browser_cookie3`.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 03:28 UTC):
- **TPT**: could not check — session expired, see TPT blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN`).
- **TES**: £0.30 GBP net, 1 sale — checked successfully (form login
  succeeded, session re-saved to `.tes_session.json`).
- Last confirmed full snapshot (all 3 platforms) remains 2026-07-19: TPT
  $13.45 USD / 1 sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session (derives catalog
size from the gitignored `releases/public/*_v001/` build-output directory,
which doesn't exist in a fresh clone). Last real count: 11 units
(2026-07-19 snapshot): year7_algorithms_unit1, year7_cybersecurity_unit1,
year7_data_representation_unit1, year7_digital_systems_unit1,
year7_game_design_unit1, year7_networks_hardware_unit1,
year7_orientation_unit1, year7_python_programming_unit1,
year7_spreadsheets_unit1, year7_ux_design_unit1, year7_web_design_unit1.

**Integrity checkers**:
- `verify_tpt_listings.py --unit <unit_id>` — ran against all 11 known live
  units above. Every single one failed identically with the (now-fixed,
  no-longer-misleading) explicit error: "not logged in to TPT (no valid
  session found) -- cannot check listings" (exit code 2). No
  `TPT_SESSION_JSON` env var is set in this container and no
  `.tpt_session.json` file exists in this fresh clone (gitignored); the
  Chrome-cookie fallback also failed (`Could not extract Chrome cookies:
  'DBUS_SESSION_BUS_ADDRESS'` — no real Chrome profile in this sandbox).
  Root cause is login/session-level, not per-unit, so all 11 failures are
  the same issue, not 11 separate ones. Still needs a human to run
  `python publish_tpt.py --save-session` once with a real browser (or set
  `TPT_SESSION_JSON`) to unblock future automated checks.
- `verify_gumroad_listings.py` — **ran clean.** All 10 Gumroad products
  matching "Unit 1" checked; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage. All "(published)". Same 10 URLs as
  every prior run (`focuslabdigital.gumroad.com/l/` + `yyrcw`, `psbzqv`,
  `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`, `llfnfx`, `kezhjt`,
  `bpvevc`).
- `verify_tes_listings.py` — **ran clean, and the cookie-banner fix from
  commit `deda456` is confirmed working**: login via saved session
  succeeded, the OneTrust consent banner no longer blocked the "Show all"
  click, and the check completed end-to-end (previous run's blocker is
  resolved). Found 30 resources total on the dashboard, 21 matching
  "Unit 1" (the other 9 are the known shelved AI-series Units 2–8
  resources, which don't carry a literal "Unit 1" string in their titles).
  All 21 checked clean — no empty descriptions, no literal HTML tags. Two
  resource IDs matched most topic titles (e.g. Networks & Hardware:
  13517745 and 13517664); read as separate per-lesson resources sharing
  the "Unit 1" title prefix, not new duplicates — distinct from the
  already-logged genuine duplicate pair below, which was flagged because
  the two IDs share the *exact same* title, not just a shared prefix.

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8 still
live on TES. None of these were touched.

No code changes this run beyond the environment-level dependency installs
(not committed — ephemeral to this container) and the `BUSINESS_REVIEW.md`
regeneration. Working branch (`claude/practical-ride-bbgxt7`) was already
even with `main` at the start of this run, so nothing needed re-applying.

---

## 2026-07-31 (later run) — Scheduled business review + integrity checks: Gumroad clean, TES verified logged-in but blocked by cookie banner, TPT blocked by missing session

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers. Report-only run — nothing found below was
touched, edited, or deleted.

**Environment note**: this session's clone had no Python dependencies
installed at all (`dotenv`, `playwright` missing) and the pip-installed
`playwright` defaulted to the latest release (1.61.0), which expects
Chromium revision 1228 while the sandbox's pre-installed browser is
revision 1194 — every browser-based check failed with "Executable doesn't
exist at /opt/pw-browsers/chromium-1228/..." until `playwright` was pinned
to 1.56.0 (the version that matches revision 1194) as an environment-level
fix, no project code touched. Worth carrying into `requirements.txt` as a
`playwright==1.56.0` pin so future sessions don't hit this cold — logging
it here rather than doing it unilaterally since it's a dependency-pin
decision, not a bug fix.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 03:13 UTC):
- **TPT**: could not check — see TPT blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN`).
- **TES**: £0.30 GBP net, 1 sale — checked successfully this run (browser
  fix above got TES working again; login via saved-then-refreshed session
  succeeded and the earnings page loaded cleanly).
- Last confirmed full snapshot (all 3 platforms) remains 2026-07-19: TPT
  $13.45 USD / 1 sale, Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` again reports **0 live units** —
same known artifact as every prior fresh-clone session: it derives catalog
size from `releases/public/*_v001/` on local disk, which this session's
clone doesn't have (build artifacts, gitignored). Last real count: 11
units (2026-07-19 snapshot).

**Integrity checkers**:
- `verify_gumroad_listings.py` — **ran clean.** All 10 Gumroad products
  matching "Unit 1" checked; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage, no 0-byte zips. All "(published)".
  URLs unchanged from prior runs (`focuslabdigital.gumroad.com/l/` +
  `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`,
  `llfnfx`, `kezhjt`, `bpvevc`).
- `verify_tpt_listings.py` — **could not run a real check.** Tried
  `--unit year7_algorithms_unit1`. It launched and reached TPT fine (the
  browser fix worked), but `.tpt_session.json` does not exist in this
  session's clone (gitignored, and automated form login is deliberately
  disabled — it has triggered TPT bot detection and an account lock
  before per `cmie/publishing/tpt.py`). The Chrome-cookie fallback also
  failed (`browser_cookie3` not installed / no real Chrome profile in this
  container). Net effect: the script found 0 products and printed "All
  checked listings look clean" — **that message is misleading here**, it
  did not actually check anything, it just found nothing because it
  wasn't logged in. Flagging this as a script gap worth a human look: it
  should distinguish "0 products because not logged in" from "0 products,
  genuinely nothing to check." Needs `python publish_tpt.py --save-session`
  run once by a human with a real browser to refresh the session file.
- `verify_tes_listings.py --keyword "Unit 1"` — **login succeeded** (used
  the session file `business_review.py` had just refreshed earlier in this
  same run), but the check itself failed: clicking the dashboard's "Show
  all" button timed out after 30s because TES's OneTrust cookie-consent
  banner (`#onetrust-consent-sdk`) kept intercepting the click — full
  traceback ends in `playwright._impl._errors.TimeoutError:
  Locator.click: Timeout 30000ms exceeded` on
  `page.get_by_text("Show all", exact=False).first.click()` in
  `find_resource_ids()`. This is a fresh failure mode (not the TLS-reset
  issue from earlier today) — worth a human look at whether the script
  should dismiss/accept the cookie banner before clicking. No resource
  data was read, so no findings to report either way this run.

**Open items carried forward unresolved** (see `BUSINESS_REVIEW.md` for
the full current list — unchanged this run): TES presenter-placeholder
cosmetic bug on Unit 1 (AI series), TES duplicate resource pair
(13432831 / 13432796), TES resource 13445828 permanently broken, off-brand
Gumroad products still on the storefront, shelved AI-series Units 3-8 still
live on TES. None of these were touched.

The prior 2026-07-31 entry below (commit `a136294`) already made it to
`main` before this run started, so no stranded-branch work needed porting
forward this time.

---

## 2026-07-31 — Scheduled business review + integrity checks: Gumroad clean, TPT/TES blocked again by browser TLS reset

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers. Report-only run — nothing found below was
touched, edited, or deleted.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 02:13 UTC):
- **TPT**: could not check — see browser blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN` — reliable).
- **TES**: could not check — see browser blocker below.
- Last confirmed full snapshot remains 2026-07-19: TPT $13.45 USD / 1 sale,
  Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` reports **0 live units** this run —
this is an artifact of the fresh checkout, not a real catalog change. It
derives catalog size from `releases/public/*_v001/` on local disk, which
does not exist in this session's clone (build artifacts, not committed to
git). The last real count was 11 units (2026-07-19 snapshot, still the best
available reference — see that entry in `BUSINESS_REVIEW.md`'s git history
or the list below).

**Integrity checkers**:
- `verify_gumroad_listings.py` — **ran clean.** Checked all 10 Gumroad
  products matching "Unit 1"; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage, no 0-byte zips. All show status
  "(published)". Product URLs (all OK): `focuslabdigital.gumroad.com/l/`
  `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`,
  `llfnfx`, `kezhjt`, `bpvevc`.
- `verify_tpt_listings.py` — **could not run.** Tried
  `--unit year7_algorithms_unit1` as a representative check; failed before
  it even reached the dashboard (fails on the initial login-state check,
  `https://www.teacherspayteachers.com/` → `net::ERR_CONNECTION_RESET`).
  Since the failure is at browser/network level, not unit-specific, did not
  repeat it across the other 10 known units (year7_cybersecurity_unit1,
  year7_data_representation_unit1, year7_digital_systems_unit1,
  year7_game_design_unit1, year7_networks_hardware_unit1,
  year7_orientation_unit1, year7_python_programming_unit1,
  year7_spreadsheets_unit1, year7_ux_design_unit1,
  year7_web_design_unit1) — same root cause would apply to all.
- `verify_tes_listings.py` — **could not run**, same failure
  (`https://www.tes.com/authn/sign-in` → `net::ERR_CONNECTION_RESET`).

**Browser blocker — status update on the 2026-07-31-earlier TLS fix**: the
TLS-1.2-cap fix from earlier today (`cloud_launch_kwargs()` in
`cmie/publishing/browser.py`, commit `12b07a7`) did **not** resolve the
issue in this session — same `ERR_CONNECTION_RESET` on every HTTPS
navigation through the proxy (reproduced even on `https://example.com`, not
just the target sites). Netlog capture (`--log-net-log`) shows the CONNECT
tunnel itself succeeds (`200 Connection Established`), then the reset
happens immediately after Chromium sends its TLS ClientHello — `net_error
-101` / `os_error 104` (ECONNRESET), before any server response.
`--ssl-version-max=tls1.2` is very likely a no-op on this Chromium build
(141.0.7390.37) — Chrome removed that flag's effect years ago — which would
explain why the earlier fix appeared to work in one diagnostic session but
not here. `plain curl` through the same proxy to the same hosts (TLS 1.3,
HTTP/2) succeeds every time, so this looks Chromium-client-specific, not a
blanket proxy outage. Not fixed here (out of scope for a report-only run,
and the proxy README says client-specific TLS failures need
administrator/Anthropic-support attention, not a code workaround). Also
separately note: this session's `pip install -r requirements.txt` pulled
Playwright 1.61.0, whose bundled Chromium build (revision 1228) doesn't
match what's pre-installed in this container (revision 1194) — had to pin
`playwright==1.56.0` locally in this session just to get Chromium to launch
at all (a session-local pip choice, not a repo change; every fresh
container will hit this same mismatch until `requirements.txt` pins a
compatible version — a decision for a human, not made here).

**No integrity issues found on anything that could actually be checked.**
Open items list unchanged from 2026-07-19 (see below in this file's
history / `BUSINESS_REVIEW.md`) — still waiting on human decisions for the
TES cosmetic bug, the TES duplicate pair (13432831 / 13432796), the
permanently-broken TES resource 13445828, the off-brand Gumroad products,
and real unattended scheduling.

## 2026-07-31 — Cloud Chromium/proxy fix landed and verified; git push permission still blocking

Session goal: get the 4 paused routines (Business Review, New Unit Production,
Marketing Push, Resource Drop — all `enabled: false` since 2026-07-20) back to
a genuinely working state, not just re-enabled and failing quietly again.

**Root cause #1, fixed and verified live**: every Playwright launch site in
the repo either hardcoded `channel="chrome"` (no real Chrome binary in the
cloud container) or had no way to pass the sandbox's egress proxy explicitly
(Chromium doesn't auto-read `HTTP_PROXY`/`HTTPS_PROXY` the way curl/urllib
do). Added `cloud_launch_kwargs()`/`cloud_context_kwargs()` in
`cmie/publishing/browser.py` (no-op locally, activates only when a proxy env
var is present) and wired it into every launch site: `browser.py`,
`cmie/publishing/tpt.py`, `check_revenue.py`, `publish_pinterest.py`,
`verify_tpt_listings.py`, `verify_tes_listings.py`, `verify_pinterest_pins.py`,
`cmie/connectors/tpt.py`. Commit `cd7354e`.

A live diagnostic session run directly in the Claude Code cloud environment
(`env_01DJK4aBcVAJB3m7hdsLorh1`) found this first fix was necessary but not
sufficient: the proxy resets the connection right after Chromium's TLS 1.3
ClientHello, *before* any certificate is exchanged — so
`--ignore-certificate-errors` never got a chance to matter. Isolated via
netlog analysis (ruled out the PQ/Kyber key-share extension specifically);
capping Chromium to TLS 1.2 (`--ssl-version-max=tls1.2`) fixed it cleanly for
both a plain test URL and a real teacherspayteachers.com page load. Added to
the same shared helper. Commit `12b07a7`. **Chromium can now genuinely reach
the internet from this cloud environment — confirmed by a real page load, not
inferred.**

**Root cause #2, found, NOT fixed — needs a human to check GitHub/environment
settings**: `git push origin main` from inside the cloud environment still
returns a 403, on any branch, not just main (matches the 2026-07-20 finding —
this is a distinct, older issue from the Chromium/proxy one, first reported
during that session's routine test-run). This means even a fully-working
routine cannot persist its own work or update this log — everything it does
dies with the container. **This is very likely the single biggest remaining
blocker to real unattended automation** — a routine could now (with the TLS
fix) actually read TPT/Gumroad/TES/Pinterest and act, but has no way to save
what it did. Needs checking on the GitHub side (does the GitHub App/token
backing this Claude Code environment's repo connection actually have
`contents: write` on `MrGibbsTeach/cmie`?) and/or the environment's own
repository-connection settings in the claude.ai/code UI. Not something fixable
via a code change or a tool call from a normal Claude Code session — needs the
account owner's direct action.

**Not yet re-attempted this session**: re-enabling the 4 paused routines. Do
not flip any of them back to `enabled: true` until the git push 403 is
resolved and confirmed with a real push from inside that environment — a
routine that can read but not write is worse than one that's off, because a
clean-looking "success" log message would be lying about whether anything
actually got saved.
PUSH TEST 2026-07-31 -- confirming GitHub App write access after reinstall.
