# Public MaHalla Case-Study Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a public, non-gated MaHalla/Sanctum of Sound case-study page, linked from the live `/work` nodal canvas, and deploy it to eachtraagency.com.

**Architecture:** One new static HTML file (`case-studies/mahalla-sanctum-of-sound.html`) adapted from the existing gated `mahalla-results.html`, with absolute euro figures removed per the numbers policy. Wired into `work.html` by turning the MaHalla client node's existing thumbnail into a link — `work.html` already ships unused CSS (`a.node-thumb::after { content: 'View case study →' }`) and a stubbed-out child-node click handler (`if (node.dataset.client === 'mahalla') { return; }`) that make clear this exact hookup was anticipated but never finished. No new node, no new interaction pattern — just completing what's already scaffolded.

**Tech Stack:** Static HTML/CSS/vanilla JS, no build step. Deploy via `wrangler pages deploy`.

## Global Constraints

- No absolute euro spend/revenue figures on the public page (MaHalla sign-off pending) — the 6.8× ratio framing is kept, per the approved spec.
- Dark-mode house DNA: `--bg: #0c0b09`, `--cream: #EAE4D5`, Apple system font stack, no decorative fonts, no em dashes — matching `mahalla-results.html` and `sanctum.html` tokens.
- `dev/nodes.html` is a stale, undeployed dev sketch (confirmed: no `data-client` attributes, no `a.node-thumb` CSS, diverged significantly from the live file) — **do not edit it.** `work.html` is the file actually served at eachtraagency.com/work (confirmed via `curl https://eachtraagency.com/work` returning `<title>Eachtra — Work</title>`, matching `work.html`'s title, not `dev/nodes.html`'s).
- Deploy ritual (this Pages project has no Git provider connected — `git push` never deploys): archive HEAD to a clean temp dir, then `wrangler pages deploy` that dir. Never deploy the working directory directly (would leak `dev/` and other gitignored files).

---

### Task 1: Build the public case-study page

**Files:**
- Create: `case-studies/mahalla-sanctum-of-sound.html`
- Reference (read-only source to adapt from): `mahalla-results.html`

**Interfaces:**
- Produces: a standalone page at `case-studies/mahalla-sanctum-of-sound.html`, reachable relative to site root, using image/video assets already at `images/sos/*` (no new assets needed — reuses `sos-hero-performance.jpg`, `sos-feature-fiberlights.jpg`, `sos-1.mp4` through `sos-5.mp4`, all confirmed present in `images/sos/`).

- [ ] **Step 1: Copy `mahalla-results.html` as the starting point**

```bash
cd ~/agency-website
mkdir -p case-studies
cp mahalla-results.html case-studies/mahalla-sanctum-of-sound.html
```

- [ ] **Step 2: Remove the access gate and noindex, add real SEO meta**

In `case-studies/mahalla-sanctum-of-sound.html`, replace the `<head>` block from `<meta name="robots"...>` through the `<meta name="description"...>` line (originally lines 4–9) with:

```html
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sanctum of Sound: Campaign Results · Eachtra</title>
  <meta name="description" content="How a three-week paid campaign for MaHalla Berlin's Sanctum of Sound returned 6.8x on ad spend — the strategy, creative, and audience growth behind it.">
  <link rel="canonical" href="https://eachtraagency.com/case-studies/mahalla-sanctum-of-sound.html">
  <meta property="og:title" content="Sanctum of Sound: Campaign Results">
  <meta property="og:description" content="A three-week paid campaign for MaHalla Berlin that returned 6.8x on ad spend.">
  <meta property="og:type" content="article">
```

(This drops the `mh_access` gate script and `noindex, nofollow` entirely — the page is meant to be found. Image paths in this file are already relative to site root as `images/sos/...`, and since the new file lives one directory deeper at `case-studies/`, every `images/...`, `href="/"`, `href="mahalla-next.html"` etc. reference needs a `../` prefix — handled in the steps below.)

- [ ] **Step 3: Fix relative paths for the new one-level-deeper location**

Run these replacements against `case-studies/mahalla-sanctum-of-sound.html`:

```bash
cd ~/agency-website
sed -i '' 's|src="images/sos/|src="../images/sos/|g' case-studies/mahalla-sanctum-of-sound.html
sed -i '' 's|css/fonts.css|../css/fonts.css|g' case-studies/mahalla-sanctum-of-sound.html
```

The nav logo link `<a class="nav-word" href="/">Eachtra</a>` already points at site root (`/`) so it needs no change.

- [ ] **Step 4: Remove the numbers-policy-restricted content and client-only CTA**

In `case-studies/mahalla-sanctum-of-sound.html`, make these edits:

1. Find the headline metrics grid (the `.headline-grid` block with the 4 `.big-num` cells: revenue, tickets, ROAS, cost-per-ticket). Remove the first cell (`€13,614 · Gross ticket revenue`) entirely, leaving 3 cells: tickets sold, the 6.8× ROAS, and cost-per-ticket. Change `grid-template-columns: repeat(4, 1fr)` to `repeat(3, 1fr)` in the `.headline-grid` CSS rule.

2. Find the "What €2,002 carried" section (`.sec-label` reading `What €2,002 carried`). Change the label to `What the spend carried` and remove the first metric cell (`€2,002 · Total ad spend`), leaving the other 5 cells (link clicks, ticket-page visits, cost per click, best ad sets, spend-as-share-of-revenue). Note: "Spend as share of ticket revenue: 14.71%" is a ratio, not an absolute figure — it stays.

3. Find the note paragraph below the headline grid (`Ticket revenue runs through Resident Advisor...`). It's fine as-is — no absolute figures in that paragraph.

4. Find the "What the road taught us" section, third `.worked-item` ("The return was there even compressed"). Its body reads `€13,614 in tickets on €2,002 of spend, a 6.8× return...` — rewrite to: `A 6.8× return on ad spend, earned inside a three-week window most campaigns would consider too short to start.`

5. Find the `.close` section. Replace the entire paragraph and CTA:

```html
      <p class="reveal" style="max-width:600px;margin:22px auto 0;font-size:clamp(15px,2vw,17px);font-weight:300;line-height:1.6;color:rgba(234,228,213,0.72)">A 6.8x return came from a three-week test on a locked budget: strategy, live campaign management, and creative sourced and shaped in house. This is what Eachtra does compressed into three weeks. Imagine a real runway.</p>
      <a class="close-cta reveal" href="../contact.html">Talk to Eachtra →</a>
```

(This removes the `id="stripe-link"` CTA and its Stripe URL entirely.)

6. Find the closing `<script>` block's Stripe-return-detection IIFE (`// ── Stripe return detection ──`, the whole function referencing `stripe-link`, `mh_payment_initiated`, and `mahalla-next.html`). Delete that entire IIFE — nothing in the new page needs it. Leave the two `IntersectionObserver` blocks below it (scroll-reveal and video-play-on-view) untouched.

7. Find the footnote paragraph in `.close` (`Figures reflect Meta Ads platform data...`). It's fine as written — no absolute euro figures.

- [ ] **Step 5: Verify the file is well-formed and has no leftover client-only references**

```bash
cd ~/agency-website
grep -c "€2,002\|€13,614\|stripe-link\|mh_access\|mh_payment_initiated\|buy.stripe.com" case-studies/mahalla-sanctum-of-sound.html
```

Expected: `0`

```bash
grep -c "<html\|</html>\|<head>\|</head>\|<body>\|</body>" case-studies/mahalla-sanctum-of-sound.html
```

Expected: `6` (one open+close each)

- [ ] **Step 6: Commit**

```bash
cd ~/agency-website
git add case-studies/mahalla-sanctum-of-sound.html
git commit -m "feat: add public MaHalla/Sanctum of Sound case-study page"
```

---

### Task 2: Wire the case-study link into the live /work canvas

**Files:**
- Modify: `work.html:359-378` (the `#n-mahalla` client-node block)
- Modify: `work.html` (JS section near the bottom, after the existing `expandClient`/`collapseClient` handlers, around line 920)

**Interfaces:**
- Consumes: `case-studies/mahalla-sanctum-of-sound.html` from Task 1 (must exist before this task's link resolves).
- Produces: no new interface — this task only changes markup/behavior inside `work.html`, nothing else depends on it.

- [ ] **Step 1: Wrap the MaHalla node's thumbnail in the existing `a.node-thumb` pattern**

In `work.html`, replace lines 361–363:

```html
        <div class="node-thumb">
          <video src="images/sos/sos-5.mp4" muted loop autoplay playsinline preload="metadata"></video>
        </div>
```

with:

```html
        <a class="node-thumb" href="case-studies/mahalla-sanctum-of-sound.html" id="mahalla-case-study-link">
          <video src="images/sos/sos-5.mp4" muted loop autoplay playsinline preload="metadata"></video>
        </a>
```

This activates CSS that already exists in this file (`a.node-thumb { cursor: pointer; position: relative; }` and `a.node-thumb::after { content: 'View case study →'; ... opacity: 0; }` / `.client-node:hover a.node-thumb::after { opacity: 1; }`, `work.html:208-211`) — the hover-to-reveal "View case study →" label was already built for exactly this link and was unused until now.

- [ ] **Step 2: Stop the thumbnail click from also triggering expand/collapse**

Clicking inside `#n-mahalla` currently bubbles to the `.client-node` click listener (`work.html:915-920`) that toggles `expandClient`/`collapseClient`. Without a stop, clicking the thumbnail both expands the node AND navigates away — harmless since the page unloads, but it causes a visible flash of the expand animation first. Add a dedicated listener.

In `work.html`, immediately after the existing block:

```javascript
    document.querySelectorAll('.client-node').forEach(node => {
      node.addEventListener('click', () => {
        const id = node.dataset.client;
        node.classList.contains('expanded') ? collapseClient(id) : expandClient(id);
      });
    });
```

add:

```javascript
    // Case-study link inside the MaHalla node shouldn't also toggle expand/collapse
    document.getElementById('mahalla-case-study-link').addEventListener('click', e => {
      e.stopPropagation();
    });
```

- [ ] **Step 3: Verify locally before deploying**

```bash
cd ~/agency-website
python3 -m http.server 8000 &
sleep 1
curl -s http://localhost:8000/work.html | grep -o 'href="case-studies/mahalla-sanctum-of-sound.html"'
curl -s http://localhost:8000/case-studies/mahalla-sanctum-of-sound.html | grep -o '<title>[^<]*</title>'
kill %1
```

Expected: the `href` line prints, and the title prints `<title>Sanctum of Sound: Campaign Results · Eachtra</title>`.

- [ ] **Step 4: Commit**

```bash
cd ~/agency-website
git add work.html
git commit -m "feat: link MaHalla node thumbnail to public case-study page"
```

---

### Task 3: Deploy to eachtraagency.com

**Files:** none (deploy step only)

**Interfaces:**
- Consumes: the committed state of the repo from Tasks 1–2 (deploy ships `git archive HEAD`, so both prior commits must exist before this runs).

- [ ] **Step 1: Archive HEAD to a clean temp directory**

```bash
rm -rf /tmp/site-deploy
mkdir -p /tmp/site-deploy
cd ~/agency-website && git archive HEAD | tar -x -C /tmp/site-deploy
```

- [ ] **Step 2: Verify the archive contains the new page and excludes dev/**

```bash
ls /tmp/site-deploy/case-studies/mahalla-sanctum-of-sound.html
ls /tmp/site-deploy/dev/ 2>&1
```

Expected: first command prints the file path; second command's behavior matches whatever `dev/` gitignore status already is in this repo (if `dev/` is tracked in git, it will be present in the archive too — that's pre-existing repo behavior, not something this task changes).

- [ ] **Step 3: Deploy**

```bash
wrangler pages deploy /tmp/site-deploy --project-name=eachtra-website --commit-dirty=true
```

Expected: wrangler prints a deployment URL ending in `.eachtra-website.pages.dev` and reports success.

- [ ] **Step 4: Verify live**

```bash
curl -s https://eachtraagency.com/case-studies/mahalla-sanctum-of-sound.html | grep -o '<title>[^<]*</title>'
curl -s https://eachtraagency.com/work | grep -o 'href="case-studies/mahalla-sanctum-of-sound.html"'
```

Expected: both commands print matching output (title tag, href attribute) confirming the new page and its link are live.
