# Business Review — 2026-08-24 01:11 UTC

## Revenue
- **TPT**: ERROR — TPT session expired (.tpt_session.json no longer valid). Refresh it manually once: python publish_tpt.py --save-session (automated form login is disabled here — it has triggered TPT bot detection and an account lock before).
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: GBP 0.3 net, 1 sale(s)
- **Combined (not currency-converted)**: AUD0 + GBP0.3

## Catalog — 0 live unit(s)

## Recent activity (last 8 commits)
- 2026-08-22 Marketing Push: post 12 new Pinterest pins across 4 units, fix stale wave-2 status labels, fix verify script title-check bug
- 2026-08-22 Mark Robotics & Physical Computing unit complete — all 3 platforms live
- 2026-08-22 Fix Gumroad description clipboard-paste silently failing under automation
- 2026-08-22 Diagnose Gumroad login-bounce as 2FA, add GUMROAD_SESSION_JSON env fallback
- 2026-08-22 Complete TPT publish for Robotics unit locally; fix Chromium build crash; leave Gumroad as the one remaining blocker
- 2026-08-22 Fix 3 real TPT publish bugs found live: description paste silently failing, missing validation-error pattern, checker keyword truncation
- 2026-08-21 New Unit Production: Robotics & Physical Computing built, QA-verified, and published to TES
- 2026-08-21 Merge branch 'main' of https://github.com/MrGibbsTeach/cmie

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.
