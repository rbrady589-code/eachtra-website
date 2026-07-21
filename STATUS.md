# Eachtra Agency Website — STATUS

## Last updated: 2026-07-21 (regenerated from code/git — previous file described pre-launch state)

## Current state

- **Live** on Cloudflare Pages at eachtraagency.com. Dark site shipped.
- **`work.html` nodal canvas is SHIPPED** (promoted from `dev/nodes.html`): pan/zoom canvas, expand-in-place nodes, bezier connectors, bottom detail panel, responsive (mobile card-stack fix 2026-07-16). This canvas is also the approved **Jarvis frontend reference**.
- Onboarding: `dev/website-onboard.html` full engagement intake (Supabase RPC `submit_onboarding`, storage bucket `onboarding-assets`) — verified e2e but **`dev/` is gitignored → not deployed**.
- `generator/` client-site generator: unchanged since June; still scaffold-grade.

## ⚠️ Deploy ritual (bus-factor — memorise)
**git push does NOT deploy.** Deploy = `wrangler pages deploy` of a git-archive snapshot (see `reference_agency_site_deploy` memory). Repo pushed ≠ site updated.

## Next
- [ ] MaHalla public case study — plan at `docs/superpowers/plans/2026-07-14-mahalla-public-case-study.md`
- [ ] Promote onboarding out of gitignored `dev/` when prices are Rory-approved (client-facing)
- [ ] Wire second client node into work.html canvas when onboarded

## Decisions locked
- Font: Apple system stack; full dark `#0c0b09`; no grain overlay
- Work showcase: nodal/canvas system (sub.global inspired, not a clone)
- Node click: bottom sheet panel with image strip + info columns
