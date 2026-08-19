# Business Review — 2026-08-19 11:24 UTC

## Revenue
- **TPT**: USD 7.91 net, 2 sale(s)
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: ERROR — TES login failed. Check TES_EMAIL/TES_PASSWORD in .env, or the login form's selectors may have changed -- check releases/debug_tes_login_error.png.
- **Combined (not currency-converted)**: USD7.91 + AUD0

## Catalog — 0 live unit(s)

## Recent activity (last 8 commits)
- 2026-08-19 Log Marketing Push blocker: no Pinterest credentials or local release artifacts in this container
- 2026-08-19 Normalize raw Cookie-Editor exports before Playwright add_cookies()
- 2026-08-19 Log scheduled business review + integrity checks: credentials present for the first time, TPT/TES fail on new specific errors, Gumroad verified clean
- 2026-08-17 Log scheduled business review + integrity checks: all platforms blocked again, no credentials/sessions in this container
- 2026-08-10 Log scheduled business review + integrity checks: all platforms blocked again, no credentials/sessions in this container
- 2026-08-03 Log scheduled business review + integrity checks: all platforms blocked again, no credentials/sessions in this container
- 2026-07-31 Log scheduled business review + integrity checks: all platforms blocked, no credentials/sessions in this container
- 2026-07-31 Log scheduled business review + integrity checks: Gumroad and TES clean, TPT still blocked by missing session

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.
