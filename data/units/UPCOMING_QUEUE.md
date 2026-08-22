# Upcoming Unit Queue

Read top-to-bottom by the weekly "new unit" scheduled job. Build the first
`[ ]` entry, publish it across TPT/Gumroad/TES, then mark it `[x]` with the
date and unit_id. Do not build an entry that's already `[x]`. If every
entry is `[x]`, report "queue empty, nothing to build this cycle" and stop
— do not invent a new topic.

- [ ] Robotics & Physical Computing
- [ ] Databases: Organising and Querying Data
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
