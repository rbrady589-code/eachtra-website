# Site Generator — Upgrades & Known Mistakes

## Mistakes we made (do not repeat)

These are bugs and errors from building eachtraagency.com and the sÜave EPK.
The generator should avoid all of these by default.

| # | Mistake | Fix baked in |
|---|---|---|
| 1 | Images not committed to git — wordmark returned 404 on first live deploy | Template uses placeholder text fallback until PNG is dropped in |
| 2 | Supabase anon INSERT blocked by RLS despite `WITH CHECK (true)` — all forms failed silently | Template contact form uses service-role via edge function, not direct anon insert |
| 3 | Nav logo: text vs image confusion — changed back and forth 3 times | Template uses text by default with clear comment for PNG swap |
| 4 | Video hero on mobile — kills performance, no fallback | Template uses `<img>` by default with clear comment to swap to video |
| 5 | Google OAuth redirect URI not registered in Cloud Console before launch — OAuth broken | UPGRADES item — register before going live |
| 6 | Edge function secrets not set before testing — Stripe/email silent failures | Checklist step in deploy flow |
| 7 | `tiktok_handle` field name mismatch between form and Supabase schema | All form fields validated against schema before deploy |
| 8 | Cloudflare served cached old `onboard.html` after update — form hit wrong endpoint | Hard-reload step in QA checklist |
| 9 | `orb_build.py` (TouchDesigner) — wrong CHOP/SOP/MAT class names for TD version | Document exact TD version in any 3D build |
| 10 | Three.js blob: MeshPhysicalMaterial iridescence requires specific r152+ — broke on older CDN version | Pin Three.js version in any 3D component |
| 11 | Font preconnect missing — layout shift on load | Template includes preconnect by default |
| 12 | CSS variables not defined before first component used them — cascade failure | All tokens in `:root` at top of `<style>` |

---

## Upgrade queue (in order of impact)

### Tier 1 — High impact, buildable now

- [ ] **Anthropic API key from env** — generator reads `ANTHROPIC_API_KEY` from env, currently falls back to AdEngine `.env`. Should be a proper env var.
- [ ] **Palette auto-detection from references** — crawl the client's `ref_love` URLs, extract dominant colours, suggest a palette. Uses `Pillow` + colour extraction.
- [ ] **Multiple template variants** — current template is one layout. Add: minimal (text-only, no hero image), editorial (full-bleed typography), and portfolio (work-grid-first) as separate template files.
- [ ] **Copy iteration loop** — after first generation, allow Rory to say "make the manifesto darker" or "the about section is too corporate" and regenerate just that section.
- [ ] **Automatic Cloudflare deploy** — after generating, script creates a new GitHub repo and pushes to Cloudflare Pages via API. Client gets a live preview URL instantly.
- [ ] **Client preview link** — generated site goes to a password-protected staging URL before final approval. Client reviews live, not from a file.

### Tier 2 — Medium impact, needs design work

- [ ] **Dark mode variant** — auto-generate both light and dark versions from the same copy. Client picks.
- [ ] **Scroll-driven narrative component** — a section where text and image change as you scroll. Built as a drop-in HTML/CSS/JS block. No dependencies.
- [ ] **Video background with fallback** — template upgrade: `<video>` with `<img>` poster fallback. Switches to image on mobile via CSS.
- [ ] **Lottie animation component** — lightweight alternative to video for hero backgrounds. JSON-based, small file size.
- [ ] **Work/portfolio grid** — currently stubbed out. Build a data-driven work section: one JSON array of case studies, renders automatically.
- [ ] **Revision request system** — client annotates sections with notes (sticky-note-style overlay), submits to Supabase. Rory sees all requested changes in one place.

### Tier 3 — The 3D/immersive track

The strategy Rory proposed: 2D generative AI shape → 3D generator. Investigation needed:

- [ ] **2D shape generation** — use DALL-E 3 / Ideogram / Recraft to generate abstract 2D shapes from client brand brief. Prompt: "flat vector abstract shape, [brand colours], [brand mood], no text, white background."
- [ ] **2D → 3D conversion** — options to investigate:
  - **Tripo3D / Meshy** — text/image to 3D mesh API. Can take a 2D PNG and extrude into GLB.
  - **Stable Zero123** — image-to-3D via HuggingFace (free, slower).
  - **Shap-E (OpenAI)** — text/image to 3D. Open source.
  - Best current bet: Tripo3D API (fast, GLB output, reasonable quality).
- [ ] **Three.js GLB viewer component** — a self-contained HTML/JS block that loads a GLB file and renders it with MeshPhysicalMaterial. Based on what we proved works in the sÜave EPK. Orbits on scroll, responds to mouse.
- [ ] **Immersive hero component** — Three.js WebGL hero that replaces the image/video background for the Immersive tier. Client drops their GLB in, component does the rest.
- [ ] **GLSL shader library** — collect and document shaders that work: iridescence, grain, fluid/blob, geometric. Each as a standalone component with usage notes.

### Tier 4 — System intelligence

- [ ] **Generator trained on mistakes** — add few-shot examples to the copy prompt: good outputs, bad outputs, what makes them different. The prompt already has rules but examples teach better than rules.
- [ ] **Brand voice fingerprinting** — from the onboarding story/vision fields, classify the brand voice (minimalist, warm, direct, editorial, playful) and select copy style accordingly.
- [ ] **Automatic QA** — after generating, run a checklist: all `{{SLOTS}}` substituted, no placeholder text remaining, images referenced exist, HTML validates, links work.
- [ ] **Multi-page support** — current generator outputs single-page. Add: About page, Services page, Work page as separate files with shared tokens.
- [ ] **Component versioning** — track which component version each client site uses. When a component is improved, flag sites that could benefit from the update.

---

## Deploy checklist (run before every go-live)

- [ ] All `{{SLOT}}` markers replaced — run `grep -r "{{" output/` to check
- [ ] Hero image/video added to `images/` folder
- [ ] Images folder committed to git (check `git status`)
- [ ] Supabase edge function secrets set: `STRIPE_SECRET_KEY`, `RESEND_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- [ ] Google OAuth redirect URI registered in Cloud Console (if using Google Calendar)
- [ ] Contact form tested on staging — check Supabase `contact_leads` table
- [ ] Mobile layout reviewed at 375px
- [ ] Lighthouse score run — target 90+ performance
- [ ] Meta tags correct — check `<title>`, `<meta description>`, og tags
