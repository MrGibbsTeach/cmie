# Business Review — 2026-07-19 12:57 UTC

## Revenue
- **TPT**: USD 13.45 net, 1 sale(s)
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: GBP 0.3 net, 1 sale(s)
- **Combined (not currency-converted)**: USD13.45 + AUD0 + GBP0.3

## Catalog — 11 live unit(s)
- year7_algorithms_unit1
- year7_cybersecurity_unit1
- year7_data_representation_unit1
- year7_digital_systems_unit1
- year7_game_design_unit1
- year7_networks_hardware_unit1
- year7_orientation_unit1
- year7_python_programming_unit1
- year7_spreadsheets_unit1
- year7_ux_design_unit1
- year7_web_design_unit1

## Recent activity (last 8 commits)
- 2026-07-19 Ship Back-to-School orientation unit; fix 3 dormant catalog-wide bugs
- 2026-07-18 Add Pinterest as a marketing channel (pipeline stage 5, second platform)
- 2026-07-17 Fix TES free-listing pricing bug, extend integrity checks to Gumroad + TES
- 2026-07-17 Add marketing content generator (pipeline stage 5) â€” first pass at the real gap
- 2026-07-17 Fix long-standing **bold** markdown bug on live listings, tighten checker
- 2026-07-17 Add self-verifying publish + post-publish integrity checker (pipeline stages 3-4)
- 2026-07-16 Update PROGRESS.md: catalog doubled to 10 units, 3 more root-cause bugs fixed
- 2026-07-16 Ship 5 more units (waves 2+3), fix HTML-escaping/keyword-collision/punctuation bugs

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.
