# Smaller Resource Drop Queue

Read top-to-bottom by the weekly Friday resource-drop job. Complete the
first `[ ]` entry, mark it `[x]` with the date. If every entry is `[x]`,
report "queue empty, nothing to build this cycle" and stop — do not
invent new items.

## Additional lead magnets (2nd free lesson per unit, different from the
## existing Lesson-1 sample already live for all 10 original units)

Use the same pattern as `make_lead_magnet.py` / `publish_lead_magnets.py`,
just pointed at a different lesson number. Pick a genuinely strong,
standalone lesson (not one that depends on earlier lessons to make sense).

- [x] year7_algorithms_unit1 — Lesson 5 (Debugging: Finding and Fixing Logic Errors) — 2026-08-20
- [ ] year7_cybersecurity_unit1 — a strong standalone lesson (check config for the best fit)
- [ ] year7_web_design_unit1 — a strong standalone lesson (check config for the best fit)

## Small bundle packages (combine 2-3 existing units, reuse existing zips,
## no new content generation, one new listing per bundle)

- [ ] "Programming Foundations" bundle: Algorithms & Programming Logic + Introduction to Programming (Python)
- [ ] "Staying Safe Online" bundle: Cyber Security & Digital Footprints + Networks & Hardware

## Log

(the job appends a line here each time it completes or skips a cycle)

- 2026-08-20: Built + published the Lesson 5 lead magnet for
  year7_algorithms_unit1 ("Debugging: Finding and Fixing Logic Errors").
  TES: draft created successfully (resource 13545171), needs a human
  "Publish now" click per this project's standing TES rule. TPT: blocked —
  `TPT_SESSION_JSON` cookies had already expired (confirmed via a read-only
  `verify_tpt_listings.py` check, not a login attempt), and no
  `TPT_EMAIL`/`TPT_PASSWORD` fallback is configured, so no TPT publish was
  attempted this cycle (form-login with placeholder credentials risks bot
  detection / account lock, per `cmie/publishing/tpt.py`'s own warning).
  See AUTONOMOUS_LOG.md for full detail. A human needs to run
  `python publish_tpt.py --save-session` (or otherwise refresh
  `TPT_SESSION_JSON`) and then run
  `python publish_lead_magnets.py --unit year7_algorithms_unit1 --lesson 5 --platform tpt`
  to finish the TPT half.
