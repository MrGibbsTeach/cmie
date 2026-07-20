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
