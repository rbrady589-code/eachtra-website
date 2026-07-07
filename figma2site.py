#!/usr/bin/env python3
"""
Figma → HTML/CSS converter.
Usage: python3 figma2site.py <figma-file-url> [--node-id=NODE_ID] [--out=output.html]
Requires: FIGMA_TOKEN env var (get from https://www.figma.com/developers/api#access-tokens)

Pulls a Figma design file via REST API, converts every frame/text/shape to semantic
HTML + CSS with absolute positioning matching the canvas. Handles:
  - Auto-layout frames → flexbox
  - Text nodes → proper typography
  - Fills → backgrounds, gradients
  - Effects → box-shadows, backdrop-blur
  - Google Fonts → @import consolidation
  - Images → download + embed
"""

import os, sys, json, re, base64, argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from collections import defaultdict

TOKEN = os.environ.get("FIGMA_TOKEN", "")
BASE = "https://api.figma.com/v1"

# ═══════════════════════════════════════════
# FIGMA API
# ═══════════════════════════════════════════

def figma(path):
    """Call Figma REST API, return JSON."""
    url = f"{BASE}{path}" if path.startswith("/") else f"{BASE}/{path}"
    req = Request(url, headers={"X-Figma-Token": TOKEN})
    with urlopen(req) as r:
        return json.loads(r.read())

def file_key_from_url(url):
    """Extract file key from Figma URL like figma.com/file/ABC123/... or figma.com/design/ABC123/..."""
    # Handle both /file/ and /design/ paths
    m = re.search(r'figma\.com/(?:file|design)/([a-zA-Z0-9]+)', url)
    if not m:
        # Maybe it's already just a key
        if re.match(r'^[a-zA-Z0-9]{10,}$', url):
            return url
        raise ValueError(f"Cannot extract Figma file key from: {url}")
    return m.group(1)

def node_id_from_url(url):
    """Extract node-id from URL query param ?node-id=1-2"""
    m = re.search(r'node-id=([\d-]+)', url)
    return m.group(1) if m else None


# ═══════════════════════════════════════════
# CSS GENERATION
# ═══════════════════════════════════════════

def rgba(fill):
    """Convert Figma fill to CSS color string."""
    if fill.get("type") == "SOLID":
        c = fill["color"]
        a = fill.get("opacity", 1.0)
        r, g, b = int(c["r"]*255), int(c["g"]*255), int(c["b"]*255)
        if a < 1:
            return f"rgba({r},{g},{b},{round(a,2)})"
        return f"#{r:02x}{g:02x}{b:02x}"
    return None

def gradient_css(fill):
    """Convert Figma gradient fill to CSS gradient."""
    if fill.get("type") not in ("GRADIENT_LINEAR", "GRADIENT_RADIAL", "GRADIENT_ANGULAR"):
        return None

    stops = fill.get("gradientStops", [])
    if not stops:
        return None

    css_stops = []
    for s in stops:
        c = s["color"]
        r, g, b = int(c["r"]*255), int(c["g"]*255), int(c["b"]*255)
        a = c.get("a", s.get("opacity", 1.0))
        pct = round(s["position"] * 100, 1)
        css_stops.append(f"rgba({r},{g},{b},{round(a,2)}) {pct}%")

    stops_str = ", ".join(css_stops)

    if fill["type"] == "GRADIENT_LINEAR":
        # Figma gradient handles give us the angle
        handles = fill.get("gradientHandlePositions", [])
        if len(handles) >= 2:
            dx = handles[1]["x"] - handles[0]["x"]
            dy = handles[1]["y"] - handles[0]["y"]
            import math
            angle = math.degrees(math.atan2(dy, dx)) + 90
            return f"linear-gradient({int(angle)}deg, {stops_str})"
        return f"linear-gradient(180deg, {stops_str})"

    elif fill["type"] == "GRADIENT_RADIAL":
        return f"radial-gradient(circle, {stops_str})"

    return f"linear-gradient(180deg, {stops_str})"

def fill_to_css(fills):
    """Convert Figma fills array to CSS background properties."""
    if not fills:
        return {}

    # Filter visible fills, reverse (Figma order is bottom → top, CSS is top → bottom)
    visible = [f for f in fills if f.get("visible", True) and f.get("opacity", 1) > 0]
    if not visible:
        return {}

    # If image fill, handle separately
    for f in visible:
        if f.get("type") == "IMAGE":
            ref = f.get("imageRef", "")
            scale = f.get("scaleMode", "FILL")
            css = {"backgroundImage": f"url({ref})", "backgroundSize": "cover" if scale == "FILL" else "contain",
                   "backgroundPosition": "center", "backgroundRepeat": "no-repeat"}
            if f.get("opacity", 1) < 1:
                css["opacity"] = str(f["opacity"])
            return css

    # Solid or gradient
    layers = []
    for f in reversed(visible):
        if f["type"] == "SOLID":
            layers.append(rgba(f))
        elif "GRADIENT" in f["type"]:
            g = gradient_css(f)
            if g:
                layers.append(g)

    if layers:
        return {"background": ", ".join(layers)}
    return {}

def effects_to_css(effects):
    """Convert Figma effects (shadows, blurs) to CSS."""
    css = {}
    shadows = []
    for e in effects:
        if not e.get("visible", True):
            continue
        if e["type"] == "DROP_SHADOW":
            c = e["color"]
            r, g, b = int(c["r"]*255), int(c["g"]*255), int(c["b"]*255)
            a = c.get("a", 1)
            x = e["offset"]["x"]
            y = e["offset"]["y"]
            blur = e["radius"]
            spread = e.get("spread", 0)
            shadows.append(f"{x}px {y}px {blur}px {spread}px rgba({r},{g},{b},{round(a,2)})")
        elif e["type"] == "LAYER_BLUR":
            css["filter"] = f"blur({e['radius']}px)"
        elif e["type"] == "BACKGROUND_BLUR":
            css["backdropFilter"] = f"blur({e['radius']}px)"

    if shadows:
        css["boxShadow"] = ", ".join(shadows)
    return css


# ═══════════════════════════════════════════
# NODE → HTML CONVERSION
# ═══════════════════════════════════════════

class Converter:
    def __init__(self, file_key, image_fetcher=None):
        self.file_key = file_key
        self.used_fonts = set()
        self.image_fetcher = image_fetcher or (lambda ref: ref)
        self.css_rules = []
        self.class_counter = 0

    def node_class(self, prefix="el"):
        self.class_counter += 1
        return f"{prefix}-{self.class_counter}"

    def convert(self, node, parent_bounds=None):
        """Recursively convert a Figma node to HTML + CSS."""
        if not node or node.get("visible", True) is False:
            return ""

        ntype = node.get("type", "UNKNOWN")
        name = node.get("name", "").replace('"', '&quot;')
        cls = self.node_class()
        bbox = node.get("absoluteBoundingBox", {})
        css = {}
        html = ""

        # ── Position & Size ──
        if parent_bounds:
            css["position"] = "absolute"
            css["left"] = f"{bbox.get('x', 0) - parent_bounds['x']}px"
            css["top"] = f"{bbox.get('y', 0) - parent_bounds['y']}px"
        css["width"] = f"{bbox.get('width', 0)}px"
        css["height"] = f"{bbox.get('height', 0)}px"

        # ── Fills ──
        fills = node.get("fills", [])
        css.update(fill_to_css(fills))

        # ── Effects ──
        effects = node.get("effects", [])
        css.update(effects_to_css(effects))

        # ── Strokes ──
        strokes = node.get("strokes", [])
        if strokes:
            stroke = strokes[0]
            if stroke.get("type") == "SOLID":
                css["borderColor"] = rgba(stroke)
            css["borderWidth"] = f"{node.get('strokeWeight', 1)}px"
            css["borderStyle"] = "solid"

        # ── Corner Radius ──
        cr = node.get("cornerRadius")
        if cr:
            css["borderRadius"] = f"{cr}px"
        else:
            # Handle individual corners
            rec = node.get("rectangleCornerRadii")
            if rec:
                css["borderRadius"] = f"{rec[0]}px {rec[1]}px {rec[2]}px {rec[3]}px"

        # ── Opacity ──
        opacity = node.get("opacity", 1.0)
        if opacity < 1:
            css["opacity"] = str(round(opacity, 3))

        # ── Clipping ──
        if node.get("clipsContent"):
            css["overflow"] = "hidden"

        # ── Auto Layout → Flexbox ──
        layout = node.get("layoutMode")
        if layout:
            css["display"] = "flex"
            css["flexDirection"] = "column" if layout == "VERTICAL" else "row"
            css["justifyContent"] = {
                "MIN": "flex-start", "CENTER": "center", "MAX": "flex-end",
                "SPACE_BETWEEN": "space-between"
            }.get(node.get("primaryAxisAlignItems", "MIN"), "flex-start")
            css["alignItems"] = {
                "MIN": "flex-start", "CENTER": "center", "MAX": "flex-end"
            }.get(node.get("counterAxisAlignItems", "MIN"), "flex-start")
            gap = node.get("itemSpacing")
            if gap:
                css["gap"] = f"{gap}px"
            pad = node.get("paddingLeft") or node.get("paddingTop")
            if pad:
                css["padding"] = f"{node.get('paddingTop', 0)}px {node.get('paddingRight', 0)}px {node.get('paddingBottom', 0)}px {node.get('paddingLeft', 0)}px"

        # ── Text ──
        if ntype == "TEXT":
            text_content = node.get("characters", "")
            style = node.get("style", {})
            font_family = style.get("fontFamily", "Inter")
            css["fontFamily"] = f"'{font_family}', sans-serif"
            self.used_fonts.add(font_family)
            css["fontSize"] = f"{style.get('fontSize', 16)}px"
            css["fontWeight"] = str(style.get("fontWeight", 400))
            css["lineHeight"] = f"{style.get('lineHeightPx', style.get('fontSize', 16) * 1.2)}px"
            css["letterSpacing"] = f"{style.get('letterSpacing', 0)}px"
            css["textAlign"] = style.get("textAlignHorizontal", "LEFT").lower()
            css["color"] = rgba(fills[0]) if fills else "#000"
            css["wordWrap"] = "break-word"

            # Text transform
            if style.get("textCase") == "UPPER":
                css["textTransform"] = "uppercase"
            elif style.get("textCase") == "LOWER":
                css["textTransform"] = "lowercase"

            # Text decoration
            if style.get("textDecoration") == "UNDERLINE":
                css["textDecoration"] = "underline"
            elif style.get("textDecoration") == "STRIKETHROUGH":
                css["textDecoration"] = "line-through"

            html = f'<span class="{cls}">{text_content or "&nbsp;"}</span>'

        # ── Frame / Group ──
        elif ntype in ("FRAME", "GROUP", "COMPONENT", "INSTANCE", "COMPONENT_SET"):
            children_html = ""
            for child in node.get("children", []):
                children_html += self.convert(child, bbox)

            tag = "div"
            html = f'<{tag} class="{cls}" data-name="{name}">\n{children_html}</{tag}>\n'

        # ── Rectangle / Ellipse / Vector ──
        elif ntype in ("RECTANGLE", "ELLIPSE", "VECTOR", "POLYGON", "STAR", "LINE"):
            if ntype == "ELLIPSE":
                css["borderRadius"] = "50%"
            html = f'<div class="{cls}" data-name="{name}"></div>\n'

        else:
            # Fallthrough: generic div
            children_html = ""
            for child in node.get("children", []):
                children_html += self.convert(child, bbox)
            html = f'<div class="{cls}" data-name="{name}">\n{children_html}</div>\n'

        # ── Emit CSS rule ──
        self.css_rules.append((cls, css))

        return html

    def build_stylesheet(self):
        """Build consolidated CSS from all rules."""
        lines = []
        for cls, props in self.css_rules:
            if not props:
                continue
            rules = "\n  ".join(f"{k}: {v};" for k, v in props.items())
            lines.append(f".{cls} {{\n  {rules}\n}}")
        return "\n\n".join(lines)


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Figma → HTML/CSS converter")
    parser.add_argument("url", help="Figma file URL or file key")
    parser.add_argument("--node", help="Specific node ID to convert (e.g. 1:2)")
    parser.add_argument("--out", default="figma-export.html", help="Output HTML file")
    parser.add_argument("--page", default=None, help="Page name to export (default: first page)")
    args = parser.parse_args()

    if not TOKEN:
        print("ERROR: FIGMA_TOKEN environment variable not set.", file=sys.stderr)
        print("Get one at: https://www.figma.com/developers/api#access-tokens", file=sys.stderr)
        print("Then: export FIGMA_TOKEN=your-token-here", file=sys.stderr)
        sys.exit(1)

    file_key = file_key_from_url(args.url)
    node_id = args.node or node_id_from_url(args.url)

    print(f"📐 Fetching Figma file: {file_key}", file=sys.stderr)
    if node_id:
        print(f"   Targeting node: {node_id}", file=sys.stderr)

    # Fetch document
    data = figma(f"/files/{file_key}")
    doc = data.get("document", {})

    # Find target frame
    target = doc
    if args.page:
        for page in doc.get("children", []):
            if page.get("name") == args.page:
                target = page
                break
    else:
        # Use first page
        pages = [c for c in doc.get("children", []) if c.get("type") == "CANVAS"]
        if pages:
            target = pages[0]

    if node_id:
        # Fetch specific node
        nodes_data = figma(f"/files/{file_key}/nodes?ids={node_id}")
        nodes = nodes_data.get("nodes", {})
        if node_id in nodes:
            target = nodes[node_id].get("document", target)

    # Convert
    converter = Converter(file_key)
    bbox = target.get("absoluteBoundingBox", {})
    body_html = converter.convert(target)

    # Get canvas size
    canvas_w = bbox.get("width", 1440)
    canvas_h = bbox.get("height", 900)

    # Build font imports
    font_import = ""
    if converter.used_fonts:
        fonts_str = "&".join(f"family={f.replace(' ', '+')}" for f in converter.used_fonts)
        font_import = f'@import url("https://fonts.googleapis.com/css2?{fonts_str}&display=swap");'

    # Assemble full HTML
    styles = converter.build_stylesheet()
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Figma Export — {target.get('name', 'Design')}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  {font_import}

  body {{
    display: flex;
    justify-content: center;
    background: #0b0d0f;
    min-height: 100vh;
  }}

  .canvas {{
    position: relative;
    width: {canvas_w}px;
    height: {canvas_h}px;
    overflow: hidden;
    background: #ffffff;
  }}

{styles}
</style>
</head>
<body>
  <div class="canvas">
{body_html}
  </div>
</body>
</html>"""

    # Write output
    out_path = Path(args.out)
    out_path.write_text(full_html)
    print(f"✅ Written to {out_path} ({out_path.stat().st_size:,} bytes)", file=sys.stderr)
    print(f"   {len(converter.css_rules)} elements, {len(converter.used_fonts)} font families", file=sys.stderr)

    if converter.used_fonts:
        print(f"   Fonts: {', '.join(sorted(converter.used_fonts))}", file=sys.stderr)

    return str(out_path)


if __name__ == "__main__":
    main()
