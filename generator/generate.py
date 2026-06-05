#!/usr/bin/env python3
"""
Eachtra Site Generator
Reads a client_onboarding row from Supabase and generates a complete site.

Usage:
    python generate.py --row-id <uuid>
    python generate.py --row-id <uuid> --out ./output/mybrand/index.html
    python generate.py --list          # show recent onboarding rows
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import httpx

# ── Config ────────────────────────────────────────────────────────────────────

SUPABASE_URL = "https://oowbdirzutyehjxonuug.supabase.co"
SUPABASE_KEY = "***REMOVED***"

def _load_env_key(key: str) -> str | None:
    val = os.environ.get(key)
    if val:
        return val
    env_file = Path.home() / "meta-ads-automation/.env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith(f"{key}="):
                v = line.split("=", 1)[1].strip()
                return v if v else None
    return None

OPENROUTER_API_KEY = _load_env_key("OPENROUTER_API_KEY")
OPENROUTER_MODEL   = "anthropic/claude-sonnet-4-6"   # best quality via OpenRouter

TEMPLATE_PATH = Path(__file__).parent / "template.html"
OUTPUT_DIR    = Path(__file__).parent / "output"

# ── Default design tokens (Eachtra palette) ───────────────────────────────────

DEFAULT_TOKENS = {
    "COLOR_BG":          "#EAE4D5",
    "COLOR_BG_2":        "#F0EBE0",
    "COLOR_INK":         "#16120D",
    "COLOR_INK_2":       "#3A332A",
    "COLOR_MUTED":       "#7A7165",
    "COLOR_MUTED_2":     "#A89F93",
    "COLOR_ACCENT":      "#8B1A12",
    "COLOR_ACCENT_BOLD": "#A82218",
    "COLOR_BORDER":      "rgba(22,18,13,0.1)",
    "FONT_SERIF":        "'Fraunces', Georgia, serif",
    "FONT_SANS":         "'Inter', -apple-system, sans-serif",
}

# Alternative palette presets
PALETTES = {
    "dark":     { "COLOR_BG": "#0E0E0E", "COLOR_BG_2": "#161616", "COLOR_INK": "#F2EDE4", "COLOR_INK_2": "#C8C0B4", "COLOR_MUTED": "#7A7165", "COLOR_MUTED_2": "#4A4540", "COLOR_BORDER": "rgba(242,237,228,0.1)" },
    "forest":   { "COLOR_BG": "#E8EDE3", "COLOR_BG_2": "#F0F4EC", "COLOR_INK": "#1A2417", "COLOR_INK_2": "#2D3D28", "COLOR_MUTED": "#6B7B65", "COLOR_ACCENT": "#2D6A4F", "COLOR_ACCENT_BOLD": "#1B4332" },
    "slate":    { "COLOR_BG": "#E8EBF0", "COLOR_BG_2": "#F0F2F5", "COLOR_INK": "#14181F", "COLOR_INK_2": "#2A3040", "COLOR_MUTED": "#6B7280", "COLOR_ACCENT": "#1E3A5F", "COLOR_ACCENT_BOLD": "#162D4A" },
    "warm":     { "COLOR_BG": "#F5EDE0", "COLOR_BG_2": "#FAF3EA", "COLOR_INK": "#1A1008", "COLOR_INK_2": "#3D2810", "COLOR_MUTED": "#8B6B50", "COLOR_ACCENT": "#C4622D", "COLOR_ACCENT_BOLD": "#A84A1E" },
}

# ── Supabase helpers ───────────────────────────────────────────────────────────

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def fetch_row(row_id: str) -> dict:
    res = httpx.get(
        f"{SUPABASE_URL}/rest/v1/client_onboarding?id=eq.{row_id}&select=*",
        headers=sb_headers(),
    )
    res.raise_for_status()
    rows = res.json()
    if not rows:
        sys.exit(f"No row found for id {row_id}")
    return rows[0]

def list_rows():
    res = httpx.get(
        f"{SUPABASE_URL}/rest/v1/client_onboarding?select=id,created_at,contact_name,company_name,client_type&order=created_at.desc&limit=10",
        headers=sb_headers(),
    )
    res.raise_for_status()
    rows = res.json()
    if not rows:
        print("No onboarding rows found.")
        return
    print(f"\n{'ID':<38} {'Type':<10} {'Name':<25} {'Company':<25} {'Created'}")
    print("-" * 110)
    for r in rows:
        print(f"{r['id']:<38} {(r.get('client_type') or '?'):<10} {(r.get('contact_name') or '?'):<25} {(r.get('company_name') or '?'):<25} {r.get('created_at','')[:10]}")

# ── Copy generation ────────────────────────────────────────────────────────────

COPY_PROMPT = """You are writing website copy for a client of Eachtra Agency.
Below is everything we know about this client from their onboarding.
Return ONLY a valid JSON object — no markdown, no explanation, just the JSON.

CLIENT DATA:
{client_data}

Return this exact JSON structure with all fields filled:
{{
  "meta_title": "Brand name — one-line what they do",
  "meta_description": "155 chars max. Honest, specific, no buzzwords.",
  "intro_headline": "One sentence. What they do and why it matters. No generic marketing speak. Should feel like the first line of a great story.",
  "intro_categories": ["Category 1", "Category 2", "Category 3"],
  "intro_category_subs": ["sub-line 1", "sub-line 2", "sub-line 3"],
  "manifesto_line": "One powerful sentence. The thing they believe that most people in their industry don't say out loud. Should stop the scroll.",
  "about_eyebrow": "Who we are / Who I am / About",
  "about_headline_lines": ["line one", "line two", "italic last line"],
  "about_paragraphs": ["paragraph 1 (2-3 sentences)", "paragraph 2 (2-3 sentences)"],
  "service_names": ["Service 1", "Service 2", "Service 3", "Service 4"],
  "service_descriptions": ["desc 1", "desc 2", "desc 3", "desc 4"],
  "contact_headline_lines": ["line one", "line two", "italic last line"],
  "contact_subtext": "2 sentences. Who you want to hear from. Should feel selective — not desperate.",
  "contact_placeholder": "What they should type — make it feel like a real conversation starter",
  "contact_success": "Warm, brief confirmation. Max 2 lines.",
  "footer_line": "One short line. Location, date, or a quiet statement of intent.",
  "nav_links": ["About", "Services", "Work", "Contact"]
}}

Rules:
- Write from the brand's voice as extracted from their brief — not generic agency copy
- The manifesto line should feel like something they'd tattoo, not something they'd put in a press release
- About paragraphs should reference their actual story and specifics where possible
- Service descriptions: what it actually is, not what it sounds like
- No exclamation marks. No "passionate about". No "cutting-edge". No "bespoke".
- If client_type is "artist": write for a creative career, not a business
- If client_type is "events": write for a collective/community, not a venue
"""

def generate_copy(row: dict) -> dict:
    if not OPENROUTER_API_KEY:
        print("WARNING: No OPENROUTER_API_KEY found. Using placeholder copy.")
        return _placeholder_copy(row)

    # Build a clean data summary for the prompt
    type_data = row.get("type_data") or {}
    client_data = {
        "brand_name": row.get("company_name") or row.get("contact_name"),
        "client_type": row.get("client_type"),
        "contact_name": row.get("contact_name"),
        "website": row.get("website_url"),
        "instagram": row.get("instagram_handle"),
        "notes": row.get("notes"),
        "ideal_customer": row.get("ideal_customer"),
        "differentiation": row.get("differentiation"),
        "product_service": row.get("product_service_name"),
        **{k: v for k, v in type_data.items() if v},
    }

    res = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://eachtraagency.com",
            "X-Title": "Eachtra Site Generator",
        },
        json={
            "model": OPENROUTER_MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": COPY_PROMPT.format(client_data=json.dumps(client_data, indent=2))}],
        },
        timeout=60,
    )
    res.raise_for_status()
    text = res.json()["choices"][0]["message"]["content"].strip()
    text = re.sub(r'^```(?:json)?\n?', '', text)
    text = re.sub(r'\n?```$', '', text)
    return json.loads(text)


def _placeholder_copy(row: dict) -> dict:
    name = row.get("company_name") or row.get("contact_name") or "Brand"
    return {
        "meta_title": f"{name} — Built by Eachtra",
        "meta_description": f"{name}.",
        "intro_headline": f"What {name} does, and why it matters.",
        "intro_categories": ["Service One", "Service Two", "Service Three"],
        "intro_category_subs": ["sub one", "sub two", "sub three"],
        "manifesto_line": "The thing they believe that most people in their industry won't say.",
        "about_eyebrow": "Who we are",
        "about_headline_lines": ["We do", "the thing", "properly."],
        "about_paragraphs": ["About paragraph one.", "About paragraph two."],
        "service_names": ["Service 1", "Service 2", "Service 3", "Service 4"],
        "service_descriptions": ["Description one.", "Description two.", "Description three.", "Description four."],
        "contact_headline_lines": ["Every great", "project starts", "with a conversation."],
        "contact_subtext": "We work with people who care about doing things properly.",
        "contact_placeholder": "Tell us what you're building.",
        "contact_success": "We've got it. You'll hear from us within 24 hours.",
        "footer_line": f"{name} · Est. 2026",
        "nav_links": ["About", "Services", "Work", "Contact"],
    }


# ── Token resolution ──────────────────────────────────────────────────────────

def resolve_tokens(row: dict, palette: str = "cream") -> dict:
    tokens = dict(DEFAULT_TOKENS)
    if palette in PALETTES:
        tokens.update(PALETTES[palette])

    # Override from type_data brand colours if provided
    type_data = row.get("type_data") or {}
    if type_data.get("brand_colours"):
        colours = type_data["brand_colours"]
        # Very basic: if they gave a hex, use it as accent
        hexes = re.findall(r'#[0-9A-Fa-f]{6}', colours)
        if hexes:
            tokens["COLOR_ACCENT"] = hexes[0]
            tokens["COLOR_ACCENT_BOLD"] = hexes[0]

    tokens["SUPABASE_URL"] = SUPABASE_URL
    tokens["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9vd2JkaXJ6dXR5ZWhqeG9udXVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0MzA0NjUsImV4cCI6MjA5MDAwNjQ2NX0.dQzJsfuJtOuqVKH0hKJbqRU3DT7gKfNbrsH5CZU2CvM"
    return tokens


# ── HTML assembly ──────────────────────────────────────────────────────────────

def build_html(row: dict, copy: dict, tokens: dict) -> str:
    template = TEMPLATE_PATH.read_text()

    brand_name = row.get("company_name") or row.get("contact_name") or "Brand"
    brand_slug = re.sub(r'[^a-z0-9]', '-', brand_name.lower()).strip('-')
    contact_email = row.get("contact_email") or "hello@yourbrand.com"

    # Nav links
    nav_html = "\n  ".join(
        f'<a href="#{l.lower()}">{l}</a>'
        for l in copy.get("nav_links", ["About", "Services", "Contact"])
    )

    # Hero media — placeholder div for now (client drops in their image/video)
    hero_media = (
        f'<img id="hero-media" src="images/hero.jpg" alt="{brand_name}">'
        '<!-- Replace with: <video id="hero-media" src="videos/hero.mp4" autoplay loop muted playsinline></video> -->'
    )

    # Hero wordmark — text fallback (client drops in PNG if they have one)
    hero_wordmark = f'<div class="hero-wordmark-text">{brand_name}</div>'
    # If there's a logo reference in type_data, note it
    hero_wordmark += '\n  <!-- Drop your wordmark: <img class="hero-wordmark" src="images/wordmark.png" alt="' + brand_name + '"> -->'

    # Intro categories
    cats = copy.get("intro_categories", [])
    subs = copy.get("intro_category_subs", [""] * len(cats))
    cats_html = "\n      ".join(
        f'<div><div class="intro-cat-label">{c}</div><div class="intro-cat-sub">{subs[i] if i < len(subs) else ""}</div></div>'
        for i, c in enumerate(cats)
    )

    # About headline
    headline_lines = copy.get("about_headline_lines", [brand_name])
    if len(headline_lines) >= 3:
        about_headline = f"{headline_lines[0]}<br>{headline_lines[1]}<br><em>{headline_lines[2]}</em>"
    else:
        about_headline = "<br>".join(headline_lines)

    # About paragraphs
    about_paras = "\n      ".join(
        f"<p>{p}</p>" for p in copy.get("about_paragraphs", [])
    )

    # Service cards
    names = copy.get("service_names", [])
    descs = copy.get("service_descriptions", [])
    cards_html = "\n      ".join(
        f'''<div class="service-card">
          <span class="service-num">0{i+1}</span>
          <h3>{names[i]}</h3>
          <p>{descs[i] if i < len(descs) else ""}</p>
        </div>'''
        for i in range(len(names))
    )

    # Contact headline
    cl = copy.get("contact_headline_lines", ["Let's talk."])
    if len(cl) >= 3:
        contact_headline = f"{cl[0]}<br>{cl[1]}<br><em>{cl[2]}</em>"
    else:
        contact_headline = "<br>".join(cl)

    # Manifesto
    manifesto = copy.get("manifesto_line", "")

    # Footer
    footer_line = copy.get("footer_line", f"{brand_name} · Est. 2026")

    # Build substitution map
    subs_map = {
        **tokens,
        "META_TITLE":          copy.get("meta_title", brand_name),
        "META_DESCRIPTION":    copy.get("meta_description", ""),
        "NAV_LINKS":           nav_html,
        "HERO_MEDIA":          hero_media,
        "HERO_WORDMARK":       hero_wordmark,
        "INTRO_HEADLINE":      copy.get("intro_headline", ""),
        "INTRO_CATEGORIES":    cats_html,
        "MANIFESTO_LINE":      manifesto,
        "ABOUT_EYEBROW":       copy.get("about_eyebrow", "Who we are"),
        "ABOUT_HEADLINE":      about_headline,
        "ABOUT_PARAGRAPHS":    about_paras,
        "SERVICE_CARDS":       cards_html,
        "CONTACT_HEADLINE":    contact_headline,
        "CONTACT_SUBTEXT":     copy.get("contact_subtext", ""),
        "CONTACT_PLACEHOLDER": copy.get("contact_placeholder", "Tell us what you're building."),
        "CONTACT_SUCCESS":     copy.get("contact_success", "We've got it."),
        "CONTACT_EMAIL":       contact_email,
        "BRAND_NAME":          brand_name,
        "BRAND_SLUG":          brand_slug,
        "FOOTER_LINE":         footer_line,
    }

    # Substitute all {{SLOT}} markers
    html = template
    for key, value in subs_map.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))

    return html


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Eachtra Site Generator")
    parser.add_argument("--row-id", help="UUID of the client_onboarding row")
    parser.add_argument("--out", help="Output file path (default: output/<brand>/index.html)")
    parser.add_argument("--palette", default="cream", choices=["cream", "dark", "forest", "slate", "warm"], help="Colour palette preset")
    parser.add_argument("--list", action="store_true", help="List recent onboarding rows")
    args = parser.parse_args()

    if args.list:
        list_rows()
        return

    if not args.row_id:
        parser.print_help()
        sys.exit(1)

    print(f"Fetching onboarding row {args.row_id}…")
    row = fetch_row(args.row_id)
    brand = row.get("company_name") or row.get("contact_name") or "brand"
    print(f"  Client: {brand} ({row.get('client_type', '?')})")

    print("Generating copy with Claude…")
    copy = generate_copy(row)
    print(f"  Manifesto: {copy.get('manifesto_line', '')[:60]}…")

    print("Resolving design tokens…")
    tokens = resolve_tokens(row, args.palette)

    print("Assembling HTML…")
    html = build_html(row, copy, tokens)

    # Write output
    brand_slug = re.sub(r'[^a-z0-9]', '-', brand.lower()).strip('-')
    out_path = Path(args.out) if args.out else OUTPUT_DIR / brand_slug / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)

    print(f"\nDone. Site written to: {out_path}")
    print(f"Next steps:")
    print(f"  1. Add hero image/video to {out_path.parent}/images/hero.jpg")
    print(f"  2. Add wordmark PNG to {out_path.parent}/images/wordmark.png  (optional)")
    print(f"  3. Review copy — edit {out_path}")
    print(f"  4. Deploy: push {out_path.parent}/ to a new Cloudflare Pages repo")

if __name__ == "__main__":
    main()
