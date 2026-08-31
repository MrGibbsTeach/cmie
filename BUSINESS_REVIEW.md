# Business Review — 2026-08-31 01:08 UTC

## Revenue
- **TPT**: ERROR — TPT session expired (.tpt_session.json no longer valid). Refresh it manually once: python publish_tpt.py --save-session (automated form login is disabled here — it has triggered TPT bot detection and an account lock before).
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: GBP 0.3 net, 1 sale(s)
- **Combined (not currency-converted)**: AUD0 + GBP0.3

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
- 2026-08-28 Log root cause of the 13553843/13553844 TES duplicate: concurrent runs
- 2026-08-28 Resource Drop: publish Lesson 6 lead magnet for year7_web_design_unit1
- 2026-08-27 Point free-sample marketing links at the email-gated landing pages
- 2026-08-27 Un-ignore .env.local.example (docs, not a secret)
- 2026-08-27 Add marketing-site: email-gated lead magnets + blog, and a blog draft generator
- 2026-08-26 Finish Databases unit: TPT + Gumroad live, queue marked complete
- 2026-08-26 Merge branch 'main' of https://github.com/MrGibbsTeach/cmie
- 2026-08-26 Marketing Push: post 9 Pinterest pins across 3 units (2 unblocked backlog waves + 1 new wave), verify each pin live individually

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.
