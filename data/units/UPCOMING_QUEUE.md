# Upcoming Unit Queue

Read top-to-bottom by the weekly "new unit" scheduled job. Build the first
`[ ]` entry, publish it across TPT/Gumroad/TES, then mark it `[x]` with the
date and unit_id. Do not build an entry that's already `[x]`. If every
entry is `[x]`, report "queue empty, nothing to build this cycle" and stop
— do not invent a new topic.

- [x] Robotics & Physical Computing — done 2026-08-22 (year7_robotics_physical_computing_unit1)
- [x] Databases: Organising and Querying Data — done 2026-08-26 (year7_databases_unit1)
- [ ] Digital Media & Multimedia Production (video/audio editing, digital storytelling)

## Format for each unit (matches the existing 10-unit catalog)

- 7 topics/lessons, `year_level: "Lower Secondary"`, `subject: "Digital Technologies"`
- unit_id pattern: `year7_<topic_slug>_unit1`
- Config file: `data/units/<unit_id>.json` (see any existing file in that
  folder for the exact schema — title, topics list with `title` per lesson)
- Build via: `python produce_unit.py --unit-config data/units/<unit_id>.json`
  (runs pipeline -> qa -> thumbnail -> package)
- Spot-check actual slide content before publishing (automated QA only
  catches AI-leftover language and `- -` artifacts, not real quality —
  see the 2026-07-19 Unit 1 cosmetic-bug incident in project memory for
  why this matters)
- Publish: `publish_tpt.py --part all --publish`, `publish_gumroad.py`,
  `publish_tes.py` (TES needs a manual-equivalent Publish-now step after
  drafting — see `publish_tes.py`'s own help text)
- Add the new unit's bundle URL to `data/units/bundle_urls.json`
- Generate marketing content: `generate_marketing_content.py --unit <id>`
- Run post-publish integrity checkers on all 3 platforms before marking
  this entry `[x]`

## Log

(the job appends a line here each time it completes or skips a cycle)

- 2026-09-01: Started "Digital Media & Multimedia Production"
  (`year7_digital_media_unit1`) — config written, built + QA-verified +
  packaged successfully via `produce_unit.py` (7 lessons, assessment,
  workbook, roadmap, teacher guide). Spot-checked real content (not just
  automated QA): lesson slides, essential questions, and the assessment
  task are technically accurate, on-topic, and well-scoped; no AI-leftover
  artifacts. Also caught and fixed a real bug while spot-checking the
  thumbnail: `cmie/publishing/thumbnail.py`'s font fallback only checked
  `C:/Windows/Fonts/...` paths, so on this Linux cloud container it fell
  back to Pillow's tiny default bitmap font, which has no glyph for the
  en dash used in every unit title — rendered as a visible tofu box on
  the cover image. Added Liberation Sans / DejaVu Sans as Linux fallbacks
  and regenerated a clean thumbnail (commit `59170e7`).
  **Published live**: Gumroad (`https://focuslabdigital.gumroad.com/l/xmhbi`,
  $12.99 AUD, verified `published: true` via API) and TES (resource
  `13559319`, £9.99, "Publish now" completed — TES notes live resources
  can take up to 3 working days to appear in on-site search, which is
  normal). Both verified clean via `verify_gumroad_listings.py` and
  `verify_tes_listings.py`.
  **Not marking `[x]` yet** — **TPT blocked** by the accepted cloud
  Cloudflare/session limitation documented above (2026-08-24): session
  cookies loaded from `TPT_SESSION_JSON` but the logged-in check failed,
  and there's no `TPT_EMAIL`/`TPT_PASSWORD` fallback in this container
  (deliberately disabled — a blind form-login attempt has triggered bot
  detection/an account lock before). No login workaround attempted, per
  standing project policy. Marketing content generated
  (`data/units/marketing/year7_digital_media_unit1_marketing_content.md`)
  with the bundle URL left as a placeholder until TPT is live. Bundle URL
  not yet added to `bundle_urls.json` (no TPT product URL exists yet).
  This item is still in-flight, not abandoned — finish TPT for this same
  unit (and then add the bundle URL + fill in marketing placeholders)
  before picking a new topic next cycle.

- 2026-08-21: Started "Robotics & Physical Computing" — config written
  (`year7_robotics_physical_computing_unit1`), built + QA-verified +
  packaged successfully, published live to TES (resource `13546444`).
  **Not marking `[x]` yet**: TPT (expired session) and Gumroad (no
  credentials/session) are both blocked in this container — see
  `AUTONOMOUS_LOG.md`'s 2026-08-21 "New Unit Production" entry for exact
  human steps needed. This item is still in-flight, not abandoned — finish
  publishing TPT+Gumroad for this same unit before picking a new topic.
- 2026-08-22: Finished locally (this machine has working local credentials
  for all 3 platforms). **TPT: fully live**, all 9 parts (7 lessons +
  assessment + bundle), verified clean via `verify_tpt_listings.py`. Bundle
  URL added to `bundle_urls.json`, marketing content generated. Found and
  fixed 3 real bugs in `cmie/publishing/tpt.py`/`verify_tpt_listings.py`
  along the way (description-paste silently failing, a missing validation-
  error pattern, and a checker keyword-truncation false-negative) — see
  `AUTONOMOUS_LOG.md` for detail. **Gumroad: still blocked**, but for a
  different, deeper reason than "no credentials" — a real product exists
  (`https://focuslabdigital.gumroad.com/l/iuunxn`, draft, empty) but every
  attempt to reach its edit page bounces back to `gumroad.com/login` even
  immediately after a reportedly-successful login, reproduced 3 times, not
  a timing fluke. Also found and fixed a separate, real local environment
  bug along the way (`cmie/publishing/browser.py::automation_chrome()` was
  crashing on Chromium build 1208 specifically for persistent-context
  launches; added a self-healing fallback to another local build). The
  Gumroad login-bounce itself is NOT fixed — needs either a deeper look at
  Gumroad's session/cookie handling for the edit-page route specifically,
  or a human to log in to Gumroad directly and finish product `iuunxn`
  manually (upload `releases/artifacts/year7_robotics_physical_computing_unit1_v001_PUBLIC.zip`,
  the description from `data/units/marketing/year7_robotics_physical_computing_unit1_marketing_content.md`,
  and the thumbnail). **Still not marking `[x]`** — Gumroad is the one
  remaining piece.
- 2026-08-22 (later same day): **Gumroad finished.** Root cause of the
  login-bounce was Gumroad 2FA silently defeating the automated form-login
  (found by the human, not by automation) — fixed by reusing a
  human-completed session cookie instead of disabling 2FA. That surfaced a
  second real bug: the description field's clipboard-paste can silently
  no-op under automation exactly like the earlier TPT bug, so the same
  verify+typing-fallback was added to `publish_gumroad.py::_fill_description`.
  Product `iuunxn` now has title, description, zip, and thumbnail all
  live and verified (`published: true` via the Gumroad API) —
  https://focuslabdigital.gumroad.com/l/iuunxn. **Marking `[x]`** — all 3
  platforms (TPT, TES, Gumroad) are live for this unit.
- 2026-08-25: Started "Databases: Organising and Querying Data"
  (`year7_databases_unit1`) — config written, built + QA-verified +
  packaged successfully via `produce_unit.py`, content spot-checked (7
  lessons, assessment, slide decks all technically accurate and on-topic,
  no AI-leftover artifacts). **Published live to TES** (resource
  `13550116`), verified clean via `verify_tes_listings.py`.
  **Not marking `[x]` yet** — TPT and Gumroad both blocked in this cloud
  container:
  - **Gumroad**: no `GUMROAD_SESSION_JSON` env var set here (only the
    read-only `GUMROAD_TOKEN` API key is present) — the browser-based
    publish flow needs a human-completed session cookie because of
    Gumroad 2FA, same root cause as the 2026-08-22 entry above. Did not
    attempt a workaround. A human needs to refresh/set
    `GUMROAD_SESSION_JSON` (or run `publish_gumroad.py` locally).
  - **TPT**: found and fixed 2 real bugs in `cmie/publishing/tpt.py`
    along the way (a blank-credential guard that blocked the
    cookie-session login path entirely before it could even try, and a
    missing Xvfb display start that crashed headed Chromium launches in
    this cloud sandbox) — see `AUTONOMOUS_LOG.md` for detail. With both
    fixed, `TPT_SESSION_JSON` now loads and is attempted, but the
    resulting page still shows logged-out (plain TPT homepage, not a
    Cloudflare challenge screen this time) — the session itself appears
    stale/invalid rather than a live Cloudflare block. Worth a human
    trying `python publish_tpt.py --save-session` to refresh it before
    assuming this is the same hard Cloudflare limit as before.
  This item is still in-flight, not abandoned — finish TPT + Gumroad for
  this same unit before picking a new topic next cycle.
- 2026-08-26: **Finished locally.** Rebuilt the unit fresh (local build
  output isn't tracked in git, so the cloud session's work wasn't
  available here) — same config, QA passed clean again. **TPT: all 9
  parts published and verified clean** via `verify_tpt_listings.py`, no
  Cloudflare issue this time (yesterday's `upload_unit()` fix — trusted
  persistent browser profile instead of a throwaway one — held up for a
  full real 9-part publish run). Bundle URL added to `bundle_urls.json`.
  **Gumroad: published**, but the API created it at the stale `.env`
  default price (A$29.99, not the catalog's A$12.99) — caught and fixed
  via a direct API price update immediately after, verified clean via
  `verify_gumroad_listings.py`. Fixed the root cause too:
  `.env`'s `GUMROAD_PRICE` was still 29.99 (this had apparently been
  hand-corrected per-listing for years without anyone fixing the actual
  default). Marketing content generated. **Marking `[x]`** — all 3
  platforms (TPT, TES, Gumroad) are live for this unit.
