# Live Campaign Showcase — Design Spec

**Date:** 2026-06-26
**Status:** Approved (brainstorming complete)
**Repo:** `~/agency-website` (static HTML, Cloudflare Pages)

## Goal

Turn the agency website's work showcase (`work.html`) from a hardcoded case study into
a **public, data-driven** view of real client campaign performance — so prospective
businesses can see what Eachtra is running and how well it's doing. First client:
**MaHalla Berlin**. Purpose: make the site a sales asset that helps close clients.

## Decisions (locked in brainstorming)

- **Visibility:** Public + daily snapshot. Real numbers shown publicly on the showcase.
- **Privacy:** Outcome metrics are public (contacts captured, campaigns active, reach).
  **Spend and CPL are NOT rendered publicly** — they live in the data file under a
  `private` key for the future gated client report, default-off.
- **Approach C (hybrid):** Ship real numbers today via a hand-produced static JSON
  snapshot; graduate to a scheduled Supabase Edge Function (phase 2, design only).
- **Out of scope:** `index.html` dark-mode cleanup (tracked separately in STATUS.md).
  No visual/layout redesign of the canvas — it is already approved.

## Architecture / data flow

```
Meta Marketing API ──(MCP, manual today)──▶ data/campaigns.json ──fetch──▶ work.html node panels
                                                   ▲
                              phase 2: Supabase Edge Function (pg_cron daily) writes same shape
```

The JSON **contract is fixed now**. Today the producer is a manual MCP pull; in phase 2
the producer becomes a scheduled Edge Function. The consumer (`work.html`) never changes.

## Components

### 1. Data contract — `data/campaigns.json`

```json
{
  "updated": "2026-06-26T12:00:00Z",
  "clients": [
    {
      "id": "mahalla",
      "status": "live",
      "metrics": {
        "contacts_captured": 0,
        "campaigns_active": 0,
        "reach": 0
      },
      "private": { "spend_eur": 0, "cpl_eur": 0 }
    }
  ]
}
```

- `metrics.*` — public, rendered into the showcase panels.
- `private.*` — present but **never rendered** on the public site. Reserved for the
  gated client report.
- `updated` — ISO timestamp; drives the "updated Xh ago" stamp.
- Real values for v1 come from a Meta Ads MCP pull across MaHalla's active campaigns /
  adsets (some adsets known); `reach` and `campaigns_active` are aggregated from
  insights, `contacts_captured` from the lead/conversion count.

### 2. `work.html` consumer changes

- On load, `fetch('data/campaigns.json')`.
- Map `mahalla.metrics` into the existing `results` arrays (the `['2,000','Contacts
  captured']` pairs in the panel data objects) instead of hardcoding.
- Add a small **● LIVE** badge and an "updated Xh ago" line to the MaHalla overview panel.
- **Fallback (safety net):** if the fetch fails, JSON is malformed, or a metric is
  missing, render the current hardcoded values. The showcase must NEVER render blank or
  show `0`/`NaN`. This keeps the site selling even if the data file is stale or absent.

### 3. Phase 2 stub (design only — NOT built today)

`supabase/functions/refresh-campaigns/` Edge Function + `pg_cron` daily trigger that
calls the Meta Marketing API and writes the identical JSON shape (to Supabase Storage or
a table the site reads via anon key + read-only RLS). Documented here as the next step.
No code today.

## Error handling

- Fetch failure / network error → fallback to hardcoded panel values.
- Malformed JSON (parse error) → fallback.
- Missing client `id` or missing individual metric → fallback for that field only
  (per-field fallback, not all-or-nothing).
- Stale `updated` timestamp → still render; the "updated Xh ago" stamp shows honestly
  how old the data is.

## Testing

- With `data/campaigns.json` present and valid: panels show the live values and the
  ● LIVE badge + "updated Xh ago" stamp. Verified in the gstack browser (`/browse`).
- With the file deleted: panels fall back to hardcoded values, no blanks/NaN.
- With the file malformed: same clean fallback.

## Build-step-1 confirmations

- Pull MaHalla's real numbers via the Meta Ads MCP (account access confirmed by Rory).
  If a metric isn't retrievable, snapshot the known-good value and note it in the file.
