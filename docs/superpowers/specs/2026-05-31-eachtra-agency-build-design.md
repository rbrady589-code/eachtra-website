# Eachtra Agency — Full Build Design Spec
**Date:** 2026-05-31  
**Status:** Approved  
**Scope:** Website completion + AIOS productivity layer + build sequence

---

## 1. What We're Building

A complete agency presence and AI operating system for **Eachtra Agency** — a technology-driven creative agency for music, events, and ecommerce brands. The build has two parallel tracks:

- **Track A:** Complete the existing `agency-website/dev/sketch.html` into a deployable site
- **Track B:** Build the AIOS productivity layer — reusable Claude Code skills that make every future agency task faster

These two tracks are independent and can be worked in parallel via dispatching-parallel-agents.

---

## 2. Agency Positioning

**Name:** Eachtra Agency  
**Tagline:** "We build marketing systems for creative businesses."  
**ICP:** Music labels, event brands, ecommerce companies (clean DTC — no regulated categories)  
**Differentiator:** Technology-driven infrastructure, not campaign-based retainers  
**Base:** Berlin, Germany / Dublin, Ireland  
**Tone:** Human, premium, direct. Not corporate. Not AI-branded. No expedition metaphors.

**The pitch in one sentence:**  
We use technology to do the work of a full creative agency at a fraction of the cost — and build systems that compound over time, not campaigns that reset each quarter.

---

## 3. Track A — Website

### 3.1 Foundation
- **Source file:** `~/agency-website/dev/sketch.html` (single-file static site)
- **Do not rebuild** — complete and upgrade the existing file
- **Deploy target:** Vercel (free tier) — deploy after content is approved
- **Domain:** Buy only when site is ready to go live — recommend `eachtraagency.com` (more discoverable than .agency TLD)

### 3.2 Visual Direction

**Existing design to keep:**
- Cream background (`#EAE4D5`) as the site shell
- Ink typography (`#16120D`)
- Playfair Display (serif) + Inter (sans-serif) font pairing
- Eachtra blackletter wordmark (giant, bleeds off bottom of hero)
- Fixed top-right navigation

**Changes:**
- Replace animated terrain canvas placeholders in portfolio cards with the 4 reference paintings (or Higgsfield-generated originals in that style — see §3.3)
- Extract accent colors from the paintings. Applied to: nav link hover, CTA button hover, form focus ring, value item number color, footer border. NOT applied to backgrounds or body text — cream/ink stays dominant:
  - Crimson accent: `#8B1A12` (from Richard Powers, Day of the Shield)
  - Lavender accent: `#C4A8C8` (from Richard Powers, Untitled 1991)
  - Teal accent: `#2A9B9B` (from painting 4)
  - Warm orange: `#E8834A` (from Li Hei Di)
- Current text colors stay (cream + ink) — the paintings provide the color, not the UI chrome

### 3.3 Portfolio Images

4 reference paintings provided by Rory:
- `Richard Powers, The Day of the Shield, 1973.jpeg` — deep crimson surrealism
- `Li Hei Di.jpeg` — explosive purple-blue-orange dreamscape
- `richard powers - untitled, 1991.jpeg` — soft lavender, cobalt geometry
- `download.jpeg` — teal + copper baroque surrealism

**IP decision required before deploy:** Confirm usage rights or generate Higgsfield originals in this style (preferred for a live client-facing site). For the dev build, use the reference images as placeholders.

These replace the terrain canvas animations in all 3 portfolio cards (Arête, Cuan, Fonn). The tall card gets the Richard Powers crimson (most striking, works portrait). The two stacked cards get the Li Hei Di and the teal painting.

### 3.4 Copy — Full Rewrite

All existing copy is replaced. Section by section:

**NAV:** OUR WORK / ABOUT / CONTACT (keep as-is)

**HERO:**
- Remove: "A boutique creative agency for brands willing to explore the unknown."
- Add: "We build marketing systems for creative businesses."
- Sub (below CTA): "Not campaigns. Not one-off briefs. Infrastructure that compounds."
- CTA: "Let's build something permanent" (replaces "BEGIN THE EXPEDITION")

**ABOUT:**
- H2: "Built to compound." (replaces "The art of going somewhere new.")
- Body: "Most agencies sell time. We build infrastructure. There's a difference between a campaign that runs for three months and a system that grows your business for three years. We work with music labels, event brands, and ecommerce companies who want the second one. Technology is how we do it. Results are how you'll know."
- Remove: "Curated always. Mass-produced never." — too boutique, wrong signal
- Remove: "The work shown here is the shape of what we build. We are new..." — replace with: "We're selective about who we work with. Every client gets the full system."

**HOW WE WORK** (replaces "Study the terrain / Draw the map / Move with purpose"):
- 01 Intelligence: "Real research. Market mapping, competitor analysis, audience data. We find the angles other agencies miss because they didn't look hard enough."
- 02 System design: "We build the infrastructure: creative pipelines, campaign architecture, targeting frameworks. Everything is designed to run, iterate, and improve without starting from scratch."
- 03 Compound growth: "Month two should outperform month one. Month six should make month two look slow. That's the standard we hold ourselves to."

**WORK SECTION:**
- Label: "SELECTED WORK" (keep)
- Right label: Remove "TERRITORY IN PROGRESS — PROJECTS INCOMING" — replace with nothing (the "UNCHARTED" tag on each card is sufficient)
- Project names: Keep Arête, Cuan, Fonn — these are Irish/Greek, premium, anonymous enough for a new agency to use credibly

**CONTACT:**
- H2: "Let's build something that lasts." (replaces "Set a new coordinate.")
- Sub: "We work with a small number of clients at a time — by design. If you're a creative brand that wants a system behind it, we'd like to hear about it."
- Meta: Keep "Base: Berlin, Germany / Origin: Dublin, Ireland"
- Remove: coordinates (53.3498° N) — unnecessary detail
- Form scope options updated:
  - Paid social campaign
  - Full marketing system (strategy + creative + execution)
  - Music release campaign
  - Event campaign
  - Not sure — let's talk

**FOOTER:** "Eachtra Agency · Berlin · Dublin · Est. 2026" (keep structure, add "Agency")

### 3.5 New Sections to Add

**METRICS STRIP** (between Hero and About — one row, 3 stats):
- "3× faster than a traditional agency"
- "50% lower cost"
- "Built for creative industries"
Note: These are positioning claims, not verified data. Update with real numbers once first client is live.

**SERVICES SECTION** (between How We Work and Portfolio):
Three service cards:
1. **Paid Social Systems** — Campaign architecture, creative production, and targeting frameworks for Meta and beyond. Built to scale.
2. **Music & Event Marketing** — Release campaigns, event countdown strategies, and audience growth for artists, labels, and promoters.
3. **Creative Production** — Video, static, and motion creative at agency speed. We generate and test, fast.

### 3.6 SEO Structure
Add to `<head>`:
```html
<title>Eachtra Agency — Marketing Systems for Creative Businesses</title>
<meta name="description" content="Eachtra is a technology-driven creative agency building marketing infrastructure for music, events, and ecommerce brands. Berlin & Dublin.">
<meta property="og:title" content="Eachtra Agency">
<meta property="og:description" content="Marketing systems for creative businesses that compound over time.">
<meta property="og:image" content="/og-image.jpg">
<link rel="canonical" href="https://eachtraagency.com">
```
Schema.org: LocalBusiness markup (Berlin address, creative agency category).

### 3.7 Contact Form Backend
Replace `onsubmit="return false;"` with Formspree (free tier, no server needed):
- Create account at formspree.io → get form endpoint
- Replace form action with Formspree endpoint
- Add success state to the form UI

This avoids needing a backend server for the contact form at launch.

---

## 4. Track B — AIOS Skills

Five Claude Code skills built to `~/.claude/skills/` as SKILL.md format files (same pattern as the existing superpowers and gstack skills). Each gets its own directory: `~/.claude/skills/eachtra-brief/SKILL.md` etc.

### 4.1 `eachtra-brief`
**Trigger:** Client URL or notes  
**Output:** Structured creative brief (target audience, key messages, platform strategy, budget tier, vertical category)  
**Used for:** Every new client intake before any campaign work begins

### 4.2 `eachtra-research`
**Trigger:** Brand URL or client name  
**Output:** Competitor analysis + market gaps (uses YARS for Reddit pain points + AdEngine's AutoResearcher)  
**Used for:** Pre-brief research before the brief skill runs

### 4.3 `eachtra-outreach`
**Trigger:** Target brand URL or description  
**Output:** Personalised cold email draft — references their specific market, positions Eachtra's value prop, includes CTA for a free audit  
**Used for:** Sales prospecting (Trevesto and every lead after)

### 4.4 `eachtra-report`
**Trigger:** Client name + date range  
**Output:** Performance summary for client — campaign metrics, wins, next actions, in Eachtra tone  
**Used for:** Weekly/monthly client reporting

### 4.5 `eachtra-handoff`
**Trigger:** End of any Claude Code session working on agency tasks  
**Output:** Session summary — decisions made, files changed, open questions, what to do next  
**Used for:** Context continuity across sessions (based on the session-handoff pattern from the SKILL.md reference)

### 4.6 LLM Wiki (`~/eachtra-kb/`)
Flat folder of markdown files:
- `clients/` — one file per client, updated after every session
- `verticals/music.md`, `verticals/events.md`, `verticals/ecom.md` — vertical-specific knowledge
- `competitors.md` — running competitor intelligence
- `campaigns/` — one file per campaign with results
- `INDEX.md` — auto-loaded by referencing in CLAUDE.md session startup

CLAUDE.md addition: at session start, Claude reads `~/eachtra-kb/INDEX.md` to orient to current client state.

---

## 5. Build Sequence

### Phase 0 — This session (free, no subscriptions)
1. Integrate paintings into portfolio cards (dev/ only, placeholder usage)
2. Rewrite all copy in sketch.html
3. Add metrics strip + services section
4. Add SEO meta tags
5. Wire Formspree contact form (free account)
6. Build 5 AIOS skills
7. Create `~/eachtra-kb/` structure

### Phase 1 — When site is approved visually
1. Buy domain (eachtraagency.com — ~€12/year via Google Domains or Namecheap)
2. Set up Google Workspace (~€6/month — rory@eachtraagency.com)
3. Deploy to Vercel (free)
4. Point domain to Vercel

### Phase 2 — First client prep
1. Higgsfield content day — generate originals to replace reference paintings
2. Record Loom demo (show AdEngine + Eachtra site together)
3. Run `eachtra-outreach` skill for Trevesto
4. Sales automation: target list of 20 music/events/ecom brands

### Phase 3 — Post first client
1. Replace "UNCHARTED" with real case study
2. Add verified metrics to the strip
3. Cadence layer: scheduled agents on Railway

---

## 6. What Is NOT in Scope

- Backend server for the website (Formspree handles contact)
- CMS (static HTML is the right call until content volume demands otherwise)
- Railway deploy for the website (Vercel is simpler and free)
- Sales automation pipeline (Phase 2 — after site is live)
- SEO content strategy / blog (Phase 3)
- Google Ads / organic SEO campaigns (after first revenue)

---

## 7. Success Criteria

- [ ] Site loads at a custom domain with no broken links
- [ ] Contact form delivers submissions to rbrady589@gmail.com
- [ ] All 4 paintings visible in portfolio cards
- [ ] New copy live across all sections
- [ ] 5 AIOS skills callable from Claude Code
- [ ] `~/eachtra-kb/` populated with initial structure
- [ ] First outreach email drafted using `eachtra-outreach` skill
