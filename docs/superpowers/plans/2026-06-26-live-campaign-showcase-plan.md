# Live Campaign Showcase — Implementation Plan

Spec: `../specs/2026-06-26-live-campaign-showcase-design.md`. Approach C.

## Tasks (ordered)

1. **Pull real MaHalla Meta numbers** — via Meta Ads MCP: find MaHalla ad account →
   list campaigns/adsets → get insights (reach, active campaign count) + lead/contact
   count. Record spend/CPL into `private` (not rendered).
2. **Write `data/campaigns.json`** — to the contract in the spec, with real values +
   `updated` timestamp.
3. **Wire `work.html`** — fetch `data/campaigns.json` on load; map `mahalla.metrics`
   into the existing panel `results` arrays; per-field fallback to hardcoded values on
   any failure; add ● LIVE badge + "updated Xh ago" to the MaHalla overview panel.
4. **Verify in browser** (`/browse`) — live values render with file present; clean
   fallback (no blanks/NaN) with file deleted/malformed.
5. **Commit.**

## Notes
- Spend/CPL stay out of public render (spec privacy decision).
- No `index.html` changes. No canvas redesign.
