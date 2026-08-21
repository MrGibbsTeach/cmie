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
- [x] year7_cybersecurity_unit1 — Lesson 3 (Spotting Phishing and Social Engineering) — 2026-08-21
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
- 2026-08-21: Built + published the Lesson 3 lead magnet for
  year7_cybersecurity_unit1 ("Spotting Phishing and Social Engineering" —
  chosen over the unit's other non-Lesson-1 topics as the most standalone
  and broadly relatable: 17 slides, no dependency on earlier lessons'
  content). TES: draft created successfully (resource 13545886), needs a
  human "Publish now" click per this project's standing TES rule.
  `verify_tes_listings.py --lead-magnet-lesson 3` found no leftover-AI
  language and no literal £1.00 (the known paid-minimum mispricing bug), but
  also could not positively confirm £0.00 on reload — TES's Licence step UI
  shows the "Sell my resource" tab active by default on every page load
  regardless of what was actually saved, so this remains an inherent
  limitation of a static-HTML check, not a signal that the draft is
  mispriced. Fixed one real bug in the checker while investigating: it was
  reading the wrong uploader step page (Description, step 1) for the price
  text and could never have found it there; now reads the Licence step
  (step 4). TPT: still blocked — `TPT_SESSION_JSON` is unchanged since
  2026-08-20 and still expired (reconfirmed via the same read-only
  `verify_tpt_listings.py` check), so no TPT publish was attempted this
  cycle either; the same human follow-up from 2026-08-20 (refresh
  `TPT_SESSION_JSON` via `publish_tpt.py --save-session`, then run
  `publish_lead_magnets.py --unit year7_cybersecurity_unit1 --lesson 3
  --platform tpt`) still applies, now for both queued units. Also fixed two
  cloud-sandbox environment bugs blocking this cycle (see
  `cmie/publishing/browser.py`): the pip `playwright` package installed at
  session start no longer matches the pre-installed Chromium revision, so
  `channel="chromium"` couldn't find a binary — `cloud_launch_kwargs()` now
  passes `executable_path` at the pre-installed binary directly when
  present; and headed (`headless=False`) launches (needed for the TES
  form-fill flow) had no X server to attach to — `automation_chrome()` now
  starts a throwaway Xvfb server itself when `$DISPLAY` isn't already set.
  See AUTONOMOUS_LOG.md for full detail.
