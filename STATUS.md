# Eachtra Agency Website — STATUS

## Current state

Dark mode transformation is in progress on `index.html`. The base palette and typography are done; a few sections (`#services`, `.os-section`, form submit button) still need background fixes before the dark state is fully clean.

The nodal work showcase (`dev/nodes.html`) is built and approved as the primary feature direction.

---

## What's done

### Dark transformation (index.html)
- `:root` variables updated: `--ink` is now cream (`#EAE4D5`), body background is `--bg` (`#0c0b09`)
- Video filter restored: `contrast(1.1) saturate(1.2)` — no grain overlay
- Synthetic grain div (`#terrain-grain`) removed
- Display heading sizes reduced (manifesto, about, intro, contact h2)
- Font: Apple system font stack throughout (`-apple-system, BlinkMacSystemFont, SF Pro Display`)
- Irish text references removed throughout
- Em dashes removed throughout
- Nav padding tightened: `right: 24px, top: 20px`
- Manifesto, about, metrics section paddings reduced to `80px 24px` / `64px 24px`

### Nodal work showcase (dev/nodes.html)
- Draggable infinite canvas (pan + scroll to zoom)
- 4 active MaHalla nodes: client anchor, Meta Ads channel, Capture Funnel strategy, 2000 Contacts outcome
- S-curve Bezier connections between connected nodes
- Per-node idle float animation (5 variants, independent phases and speeds)
- Hover: float pauses, card lifts with shadow
- Click: detail panel slides up from bottom (rounded 18px)
- Detail panel: image strip + 4 rounded sub-cards (specs / campaign description / results / credits)
- 5 dim locked nodes scattered far across canvas suggesting future work
- Eachtra dark palette, Apple system font

---

## What's next

### index.html — dark transformation remaining
- [ ] Fix `#services { background: var(--bg-elevated) }` (currently renders cream)
- [ ] Fix `.os-section { background: var(--bg-elevated) }` (same)
- [ ] Fix `.form-submit { background: var(--cream); color: var(--bg) }` (button invisible)
- [ ] Reduce remaining section paddings to match tight margins
- [ ] Expand max-widths to 1200px

### Nodal system — next steps
- [ ] Add real MaHalla thumbnail image to the main node (drop into `images/`, wire up)
- [ ] Decide: nodal canvas replaces `#work` section in index.html OR becomes standalone `/work` page
- [ ] Add real campaign images to the panel image strip when available
- [ ] Wire up for second client when onboarded

---

## Files

| File | Purpose |
|---|---|
| `index.html` | Main site — dark transformation in progress |
| `index.backup-20260604-1347.html` | Last known-good backup (pre-dark mode) |
| `dev/nodes.html` | Nodal work showcase — approved concept |
| `dev/sketch.html` | Earlier dev sketch |
| `images/painting-arete-animated.mp4` | Hero video (828x1108, 9116kbps H.264) |

---

## Decisions locked

- Font: Apple system font throughout (no decorative fonts)
- Video: no grain overlay, `contrast(1.1) saturate(1.2)` filter only
- Work showcase: nodal/canvas system (sub.global inspired, not a clone)
- Dark mode: full dark (`#0c0b09` background)
- Node click: bottom sheet panel with image strip + 4 info columns
