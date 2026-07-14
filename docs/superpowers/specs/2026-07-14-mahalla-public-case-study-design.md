# Public MaHalla Case-Study Page — Design

2026-07-14

## Problem

The site has two MaHalla surfaces today, and neither is a public case study:

1. `dev/nodes.html` / `work.html` — the approved nodal work canvas. The MaHalla client node expands to 3 deliverable nodes (Meta Ads, Strategy & Sourcing, Audience Reached), each opening a bottom-sheet panel. Numbers are deliberately scrubbed — qualitative status tags only ("Delivered", "Live"), no results.
2. `mahalla-results.html` — the full campaign wrap-up report. Gated behind an access code (`mh_access` localStorage check, `noindex, nofollow`), written for MaHalla themselves, includes a €500-fee Stripe CTA and climb-monthly upsell. Not meant for outside eyes.

Neither gives a prospective client landing on `/work` a reason to believe Eachtra delivers results — the node panels are result-free, and the one page with real numbers is locked away. This page closes that gap: a public, indexable case study a prospect can actually read.

## Non-goals

- Not touching the gated `mahalla-results.html` or its access flow.
- Not changing the existing 3 deliverable node panels (Meta Ads / Strategy / Audience) on the nodal canvas.
- Not disclosing absolute euro figures (spend, revenue) — numbers sign-off from MaHalla is pending; see Numbers Policy below.
- Not building a general case-study template/CMS — this is the first instance; genericizing comes later once a second client case study exists.

## Design

### File & location

New file: `case-studies/mahalla-sanctum-of-sound.html`, plus a new top-level `case-studies/` directory (first of what should become a repeatable pattern for future clients). Static HTML, matching the site's existing per-page-file convention (no build step, no templating engine).

Fully indexable: no `noindex`, no access-gate script, real `<title>`/description/canonical/OG tags (closing the same on-page SEO gaps flagged in the [2026-07-14 SEO audit](../../../eachtra-kb/audits/2026-07-14-eachtraagency-seo-geo-audit.md) — this page should not repeat those gaps).

### Content

Adapted from `mahalla-results.html`, reusing its proven structure and voice:

- Hero (image + headline), strategy narrative ("three weeks from the doors..."), creative reel strip, "three measured steps" spend narrative, audience growth block.
- **Removed:** `mh_access` gate script, `noindex` meta, the €500-fee Stripe CTA block, the climb-monthly-plan upsell section.
- **Numbers policy (see below):** the 6.8× return framing is kept; absolute euro spend/revenue figures are cut or rewritten around the ratio.
- Audience growth (39.9K → 41.3K followers) and view/engagement counts are kept — these are publicly-verifiable Instagram stats, not sensitive financials.
- Closing CTA changes from "pay the fee" / "climb the plan" to a simple link back to `/contact`.

### Numbers policy

MaHalla hasn't confirmed they're comfortable with exact spend/revenue figures appearing on a public page. Per decision: **ship with the ratio only.** "A paid campaign is usually called strong at 3× — this came back at 6.8×" stays; the €2,002-spend / €13,614-revenue line is removed or rewritten to reference the ratio without the absolute amounts. If MaHalla later signs off on full figures, this is a one-line copy change, not a re-architecture.

### Entry point from `/work`

Add a 4th child node to the existing MaHalla cluster in `work.html` (and `dev/nodes.html`), alongside `n-meta`, `n-funnel`, `n-audience`: a new `n-results` node, "Campaign Results." It follows the same expand/reveal animation and positioning pattern as the other 3 child nodes (own `--dx`/`--dy` offset, its own connector path in the SVG layer).

Behavior differs from the other 3: clicking `n-meta`/`n-funnel`/`n-audience` opens the bottom-sheet detail panel (existing behavior, untouched). Clicking `n-results` navigates directly to `case-studies/mahalla-sanctum-of-sound.html` instead of opening a panel — a simple branch in the existing child-node click handler (`if (node.dataset.panel === 'results') { location.href = '...'; return; }` before the panel-open logic).

### Visual / house DNA

Same dark-mode tokens as the rest of the site and `sanctum.html`: cream (`#EAE4D5`) ink on `#0c0b09` background, cream pill nav/CTA styling, Apple system font stack (`-apple-system, BlinkMacSystemFont, SF Pro Display`), no decorative fonts, no em dashes (per existing site conventions in STATUS.md).

## Open questions

None — all resolved during brainstorming. Numbers policy is the one item with a future dependency (MaHalla sign-off) but the design doesn't block on it; it ships conservative today and can be loosened later with a copy-only change.
