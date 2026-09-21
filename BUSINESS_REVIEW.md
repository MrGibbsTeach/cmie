# Business Review — 2026-09-21 01:13 UTC

## Revenue
- **TPT**: ERROR — TPT session expired (.tpt_session.json no longer valid). Refresh it manually once: python publish_tpt.py --save-session (automated form login is disabled here — it has triggered TPT bot detection and an account lock before).
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: GBP 6.29 net, 2 sale(s)
- **Combined (not currency-converted)**: AUD0 + GBP6.29

## Catalog — 13 live unit(s)
- year7_algorithms_unit1
- year7_cybersecurity_unit1
- year7_data_representation_unit1
- year7_databases_unit1
- year7_digital_systems_unit1
- year7_game_design_unit1
- year7_networks_hardware_unit1
- year7_orientation_unit1
- year7_python_programming_unit1
- year7_robotics_physical_computing_unit1
- year7_spreadsheets_unit1
- year7_ux_design_unit1
- year7_web_design_unit1

## Recent activity (last 8 commits)
- 2026-09-19 Merge branch 'main' of https://github.com/MrGibbsTeach/cmie
- 2026-09-19 Build and launch flagship full-curriculum bundle across TPT, Gumroad, TES
- 2026-09-18 Resource Drop: Lesson 4 lead magnet for year7_networks_hardware_unit1, TES live
- 2026-09-17 Fix make_bundle.py missing thumbnail (blocked all TPT bundle publishes), publish both queued bundles, update revenue tracker
- 2026-09-16 Marketing Push: draft Pinterest wave 3 for UX Design, Orientation, Networks & Hardware
- 2026-09-15 New Unit Production: resume Digital Media unit, TPT still blocked (3rd cycle)
- 2026-09-14 Scheduled review: business_review.py + integrity checks, no new issues
- 2026-09-11 Resource Drop: Lesson 4 lead magnet for year7_orientation_unit1, TES live

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.
