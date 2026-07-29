#!/usr/bin/env python3
"""
generate_banner.py — Floyd-Steinberg dither portrait → SVG banner
Exact port of the arifhaxn approach: 1×1 px dot paths, ~60 random fade-in groups,
animated asciiGrad shimmer, dark + light SVG output.

Usage:
    python generate_banner.py <photo_path> [output_dir]
    python generate_banner.py photo.jpg D:/github/AYASKA-in
"""

import sys, os, random, math, base64
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# ── PROFILE DATA ────────────────────────────────────────────────────────────
NAME         = "MONINGI ROHIT"
HANDLE       = "@AYASKA-in"
TITLE_BAR    = "rohit@ayaska — % ./profile.sh --live"
TAGLINE      = "full-stack systems · ai products · motion-rich interfaces"
ROWS = [
    ("ORIGIN",    "BANGALORE, INDIA"),
    ("EDUCATION", "B.TECH IT — VIT '26"),
    ("CURRENT",   "AI / BACKEND — PROSPIENT"),
    ("UP NEXT",   "BOSCH GST · AUG 2026"),
    ("CORE.WEB",  "NEXT 16 / REACT 19 / TS"),
    ("CORE.API",  "FASTAPI / NODE / POSTGRES"),
    ("CORE.AI",   "PYTORCH / TF / GRAD-CAM"),
    ("CLOUD",     "AWS / SUPABASE / VERCEL"),
    ("RESEARCH",  "IEEE PUBLISHED · 2024"),
    ("STATUS",    "BUILDING + SHIPPING 🚀"),
]
PROMPT1 = ("portfolio", "rohitmoningi.in")
PROMPT2 = ("linkedin",  "/in/moningi-rohit")
PROJECTS = [
    ("LIVE BUILD", "Sri Lalitha Noodles",  "purple"),
    ("RESEARCH",   "IEEE ECG · Grad-CAM",  "cyan"),
    ("SYSTEMS",    "Command Center SaaS",   "green"),
]

# ── DIMENSIONS (match arifhaxn exactly) ─────────────────────────────────────
SVG_W, SVG_H = 1180, 610

# Portrait grid
GRID_COLS, GRID_ROWS = 320, 340
SCALE_X = 1.2400
SCALE_Y = 1.4471
TRANS_X, TRANS_Y = 50, 86

# Portrait frame
FRAME_X, FRAME_Y, FRAME_W, FRAME_H = 36, 84, 400, 492

# Info panel
INFO_X = 460
NAME_Y = 130
TAGLINE_Y = 156
RULE1_Y = 166
ROW_START_Y = 196
ROW_PITCH = 30
RULE2_Y = 478
PROMPT1_Y = 502
PROMPT2_Y = 522
CARD_Y = 548

# ── THEMES ───────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "window_fill":  "#070B16",
        "panel_start":  "#0A101F", "panel_end":    "#0C1426",
        "titlebar":     "#0B1222",
        "titlebar_sep": "rgba(255,255,255,0.10)",
        "frame_fill":   "#0A101F", "frame_stroke": "rgba(34,211,238,0.35)",
        "frame_glow":   "#22D3EE",
        "dot_fill":     "#A78BFA",
        "grad_top":     "#60A5FA", "grad_mid":     "#A78BFA", "grad_bot":    "#22D3EE",
        "label_meta":   "#475569",
        "sep_stroke":   "rgba(255,255,255,0.07)",
        "name_fill":    "#F8FAFC",
        "tag_fill":     "#5D7A8C",
        "rule_stroke":  "rgba(124,58,237,0.25)",
        "label_fill":   "#475569",
        "val_default":  "#E2E8F0",
        "val_purple":   "#A78BFA",
        "val_cyan":     "#22D3EE",
        "val_green":    "#10B981",
        "rule2_stroke": "rgba(34,211,238,0.15)",
        "prompt1_fill": "#10B981",
        "prompt2_fill": "#22D3EE",
        "cursor_fill":  "#94A3B8",
        "muted_sep":    "rgba(255,255,255,0.06)",
        "card_colors":  [
            ("rgba(124,58,237,0.08)",  "rgba(124,58,237,0.3)",  "#7C3AED"),
            ("rgba(34,211,238,0.06)",  "rgba(34,211,238,0.25)", "#22D3EE"),
            ("rgba(16,185,129,0.06)",  "rgba(16,185,129,0.25)", "#10B981"),
        ],
        "card_title_fill": "#F1F5F9",
        "live_fill":    "#EF4444", "live_bg":  "rgba(239,68,68,0.12)",
        "handle_fill":  "#22D3EE", "handle_bg": "rgba(34,211,238,0.12)", "handle_stroke": "#22D3EE",
        "accent_v1":    "#7C3AED", "accent_v2": "#22D3EE", "accent_v3": "#10B981",
        "dot_grid_fill":"#22D3EE",
        "border_fill":  "#070B16",
    },
    "light": {
        "window_fill":  "#E2E8F0",
        "panel_start":  "#F8FAFC", "panel_end":    "#F1F5F9",
        "titlebar":     "#E2E8F0",
        "titlebar_sep": "rgba(0,0,0,0.08)",
        "frame_fill":   "#FFFFFF", "frame_stroke": "rgba(109,40,217,0.2)",
        "frame_glow":   "#7C3AED",
        "dot_fill":     "#7C3AED",
        "grad_top":     "#7C3AED", "grad_mid":     "#4F46E5", "grad_bot":    "#0891B2",
        "label_meta":   "#94A3B8",
        "sep_stroke":   "rgba(0,0,0,0.05)",
        "name_fill":    "#0F172A",
        "tag_fill":     "#94A3B8",
        "rule_stroke":  "rgba(109,40,217,0.15)",
        "label_fill":   "#94A3B8",
        "val_default":  "#334155",
        "val_purple":   "#6D28D9",
        "val_cyan":     "#0891B2",
        "val_green":    "#059669",
        "rule2_stroke": "rgba(8,145,178,0.15)",
        "prompt1_fill": "#059669",
        "prompt2_fill": "#0891B2",
        "cursor_fill":  "#334155",
        "muted_sep":    "rgba(0,0,0,0.04)",
        "card_colors":  [
            ("rgba(109,40,217,0.05)",  "rgba(109,40,217,0.2)",  "#6D28D9"),
            ("rgba(8,145,178,0.05)",   "rgba(8,145,178,0.2)",   "#0891B2"),
            ("rgba(5,150,105,0.05)",   "rgba(5,150,105,0.2)",   "#059669"),
        ],
        "card_title_fill": "#0F172A",
        "live_fill":    "#DC2626", "live_bg":  "rgba(220,38,38,0.08)",
        "handle_fill":  "#0891B2", "handle_bg": "rgba(8,145,178,0.10)", "handle_stroke": "#0891B2",
        "accent_v1":    "#6D28D9", "accent_v2": "#0891B2", "accent_v3": "#059669",
        "dot_grid_fill":"#6D28D9",
        "border_fill":  "#E2E8F0",
    },
}

# ── ROW VALUE COLOUR RULES ────────────────────────────────────────────────────
# Which rows get accent colours (index into ROWS list)
ROW_COLOURS = {
    0: "val_default",
    1: "val_default",
    2: "val_purple",
    3: "val_cyan",
    4: "val_default",
    5: "val_default",
    6: "val_green",
    7: "val_default",
    8: "val_purple",
    9: "val_green",
}

# ── IMAGE PROCESSING ──────────────────────────────────────────────────────────
def load_and_dither(photo_path, dark=True, prepped=False):
    """
    Load photo, crop to portrait grid, enhance, dither.
    If prepped=True: the image already has background removed and composited
    on the correct background (black for dark, white for light) — skip inversion.
    """
    img = Image.open(photo_path).convert("RGB")

    if not prepped:
        # Auto-crop to head + shoulders portrait aspect
        w, h = img.size
        target_aspect = GRID_COLS / GRID_ROWS  # ~0.94
        if w / h > target_aspect:
            new_w = int(h * target_aspect)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_aspect)
            top = max(0, int(h * 0.05))
            img = img.crop((0, top, w, min(top + new_h, h)))

    # Resize to dither grid
    img = img.resize((GRID_COLS, GRID_ROWS), Image.LANCZOS)

    # Enhance contrast + sharpness
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.35)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=150, threshold=3))

    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)

    if prepped:
        # Dark mode: black bg → face is bright → high values = dots → no invert needed
        # Light mode: white bg → face is dark → low values → invert to make face = dots
        if not dark:
            arr = 255 - arr
    else:
        # Raw photo: dark mode needs invert (bright face → more dots on dark bg)
        if dark:
            arr = 255 - arr

    # Normalise 0-1
    arr = arr / 255.0

    # Floyd-Steinberg dither (serpentine order)
    out = np.zeros_like(arr)
    h, w = arr.shape
    for y in range(h):
        left_to_right = (y % 2 == 0)
        xs = range(w) if left_to_right else range(w - 1, -1, -1)
        for x in xs:
            old = arr[y, x]
            new = 1.0 if old > 0.5 else 0.0
            out[y, x] = new
            err = old - new
            if left_to_right:
                if x + 1 < w:              arr[y,     x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0:         arr[y + 1, x - 1] += err * 3 / 16
                    arr[y + 1, x]          += err * 5 / 16
                    if x + 1 < w:          arr[y + 1, x + 1] += err * 1 / 16
            else:
                if x - 1 >= 0:             arr[y,     x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w:          arr[y + 1, x + 1] += err * 3 / 16
                    arr[y + 1, x]          += err * 5 / 16
                    if x - 1 >= 0:         arr[y + 1, x - 1] += err * 1 / 16

    return out  # 1 = draw dot, 0 = no dot

def dots_to_path(dither_arr):
    """Convert 1-bit array to SVG run-length <path> string (same format as arifhaxn)."""
    h, w = dither_arr.shape
    segments = []
    for y in range(h):
        x = 0
        while x < w:
            if dither_arr[y, x] > 0.5:
                # find run length
                run = 1
                while x + run < w and dither_arr[y, x + run] > 0.5:
                    run += 1
                if run == 1:
                    segments.append(f"M{x} {y}h1v1h-1z")
                else:
                    segments.append(f"M{x} {y}h{run}v1h-{run}z")
                x += run
            else:
                x += 1
    return "".join(segments)

def split_into_groups(dither_arr, n_groups=60):
    """
    Split ALL lit pixels into n_groups groups scattered evenly across the image
    (not by spatial region — this gives the shimmer effect not a wipe).
    Verify evenness: each 4×4 macro-cell should have ~equal coverage across groups.
    """
    h, w = dither_arr.shape
    # Collect all lit pixel coords
    ys, xs = np.where(dither_arr > 0.5)
    coords = list(zip(ys.tolist(), xs.tolist()))
    random.shuffle(coords)

    groups = [[] for _ in range(n_groups)]
    for i, (y, x) in enumerate(coords):
        groups[i % n_groups].append((y, x))

    # Convert each group to run-length paths
    paths = []
    for g in groups:
        if not g:
            paths.append("")
            continue
        # Sort by y then x for run compression
        g.sort()
        seg = []
        i = 0
        while i < len(g):
            y, x = g[i]
            run = 1
            while i + run < len(g) and g[i + run][0] == y and g[i + run][1] == x + run:
                run += 1
            if run == 1:
                seg.append(f"M{x} {y}h1v1h-1z")
            else:
                seg.append(f"M{x} {y}h{run}v1h-{run}z")
            i += run
        paths.append("".join(seg))
    return paths

# ── SVG GENERATION ────────────────────────────────────────────────────────────
def leader_dots(label, val, total_chars=66):
    """Compute dotted leader between label and value to fill total_chars width."""
    n = max(1, total_chars - len(label) - len(val))
    return "." * n

def row_svg(x, y, label, val, val_color, t, delay):
    dots = leader_dots(label, val)
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="0;1" dur="0.32s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="{x}" y="{y}" font-size="13" fill="{t["label_fill"]}">'
        f'{label}'
        f'<tspan fill="rgba(71,85,105,0.35)">{dots}</tspan>'
        f'<tspan fill="{t[val_color]}">{val}</tspan>'
        f'</text>'
        f'</g>'
    )

def build_svg(dither_arr, theme_name, n_groups=60):
    t = THEMES[theme_name]
    random.seed(42)  # deterministic shuffle per theme

    # Split dots into groups
    groups = split_into_groups(dither_arr, n_groups)

    parts = []
    a = parts.append

    # SVG header
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" '
      f'viewBox="0 0 {SVG_W} {SVG_H}" '
      f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
      f'role="img" aria-label="{NAME} — profile.sh --live">')

    # Defs
    a('<defs>')

    # Animated accent gradient (border)
    v1, v2, v3 = t["accent_v1"], t["accent_v2"], t["accent_v3"]
    a(f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{v1}"><animate attributeName="stop-color" values="{v1};{v2};{v3};{v1}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="0.5" stop-color="{v2}"><animate attributeName="stop-color" values="{v2};{v3};{v1};{v2}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="1" stop-color="{v3}"><animate attributeName="stop-color" values="{v3};{v1};{v2};{v3}" dur="10s" repeatCount="indefinite"/></stop>'
      f'</linearGradient>')

    # Portrait dot gradient (animated shimmer — same as asciiGrad in reference)
    gt, gm, gb = t["grad_top"], t["grad_mid"], t["grad_bot"]
    a(f'<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">'
      f'<stop offset="0" stop-color="{gt}"/>'
      f'<stop offset="0.45" stop-color="{gm}"/>'
      f'<stop offset="1" stop-color="{gb}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="0 -120; 0 120; 0 -120" dur="9s" repeatCount="indefinite"/>'
      f'</linearGradient>')

    # Panel gradient
    a(f'<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{t["panel_start"]}"/>'
      f'<stop offset="1" stop-color="{t["panel_end"]}"/>'
      f'</linearGradient>')

    # Glow filters
    a('<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>')
    a('<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>')
    a('<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="0.9" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      '</filter>')

    # Clip path
    a('<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>')

    # Dot grid pattern
    a(f'<pattern id="dotGrid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">'
      f'<circle cx="1" cy="1" r="0.8" fill="{t["dot_grid_fill"]}" opacity="0.03"/>'
      f'</pattern>')

    a('</defs>')

    # Terminal base
    a(f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{t["window_fill"]}"/>')

    a('<g clip-path="url(#winClip)">')

    # Panel + texture
    a('<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>')
    a('<rect x="2" y="2" width="1176" height="606" fill="url(#dotGrid)"/>')

    # Titlebar
    a(f'<rect x="2" y="2" width="1176" height="46" fill="{t["titlebar"]}"/>')
    a(f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{t["titlebar_sep"]}"/>')

    # Traffic lights
    a('<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/>')
    a('<circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/>')
    a('<circle cx="70" cy="25" r="5.5" fill="#27c93f"/>')

    # Title bar text
    a(f'<text x="590" y="29" text-anchor="middle" font-size="12" fill="#94A3B8">{TITLE_BAR}</text>')

    # Handle pill
    a(f'<g transform="translate(1058,12)">'
      f'<rect width="110" height="24" rx="12" fill="{t["handle_bg"]}" stroke="{t["handle_stroke"]}" stroke-width="0.8"/>'
      f'<circle cx="16" cy="12" r="3.5" fill="{t["handle_fill"]}" opacity="0.9">'
      f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>'
      f'</circle>'
      f'<text x="28" y="16" font-size="11" letter-spacing="1" fill="{t["handle_fill"]}">{HANDLE}</text>'
      f'</g>')

    # ── VISUAL.MAP panel ──────────────────────────────────────────────────────

    a(f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{t["label_meta"]}">VISUAL.MAP</text>')

    # Portrait frame glow
    a(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="10" '
      f'fill="none" stroke="{t["frame_glow"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>')
    # Portrait frame
    a(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="10" '
      f'fill="{t["frame_fill"]}" stroke="{t["frame_stroke"]}"/>')

    # Portrait dots — fill is the gradient, shape-rendering crispEdges
    # Exact scale/translate from reference: translate(50,86) scale(1.2400,1.4471)
    a(f'<g transform="translate({TRANS_X},{TRANS_Y}) scale({SCALE_X},{SCALE_Y})" '
      f'fill="url(#asciiGrad)" shape-rendering="crispEdges">')
    # After intro (~3.2s) the portrait fades out to let logo morph play
    a('<set attributeName="opacity" to="0" begin="3.2s"/>')

    # 60 fade-in groups — each staggered by 0.03s, 0.9s duration, spline easing
    for i, path_d in enumerate(groups):
        begin = 0.20 + i * 0.03
        a(f'<g opacity="0">'
          f'<animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin:.2f}s" fill="freeze" '
          f'calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>')
        if path_d:
            a(f'<path d="{path_d}"/>')
        a('</g>')

    a('</g>')  # end dots group

    # Portrait frame animated border
    a(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="10" '
      f'fill="none" stroke="url(#accent)" stroke-width="1.5" opacity="0.7"/>')

    # Vertical separator
    a(f'<line x1="446" y1="60" x2="446" y2="582" stroke="rgba(124,58,237,0.3)" stroke-width="1"/>')

    # ── SYSTEM.INFO panel ─────────────────────────────────────────────────────

    a(f'<text x="{INFO_X}" y="74" font-size="10" letter-spacing="3" fill="{t["label_meta"]}">SYSTEM.INFO</text>')

    # LIVE badge
    a(f'<g transform="translate(1050,60)">'
      f'<rect width="88" height="22" rx="11" fill="{t["live_bg"]}" stroke="{t["live_fill"]}" stroke-width="0.8"/>'
      f'<circle cx="16" cy="11" r="3.5" fill="{t["live_fill"]}">'
      f'<animate attributeName="opacity" values="0.3;1;0.3" dur="1.6s" repeatCount="indefinite"/>'
      f'</circle>'
      f'<text x="28" y="15.5" font-size="11" letter-spacing="2" fill="{t["live_fill"]}">LIVE</text>'
      f'</g>')

    # Top separator
    a(f'<line x1="456" y1="84" x2="1160" y2="84" stroke="{t["sep_stroke"]}"/>')

    # Name
    a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.30s" fill="freeze"/>'
      f'<text x="{INFO_X}" y="{NAME_Y}" font-size="36" font-weight="800" letter-spacing="3" '
      f'fill="{t["name_fill"]}" filter="url(#txtGlow)">{NAME}</text>'
      f'</g>')

    # Tagline
    a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.40s" fill="freeze"/>'
      f'<text x="{INFO_X + 2}" y="{TAGLINE_Y}" font-size="13" font-style="italic" '
      f'fill="{t["tag_fill"]}" letter-spacing="0.8">{TAGLINE}</text>'
      f'</g>')

    # Dashed rule under name
    a(f'<line x1="456" y1="{RULE1_Y}" x2="1160" y2="{RULE1_Y}" '
      f'stroke="{t["rule_stroke"]}" stroke-dasharray="4,8"/>')

    # Info rows
    for i, (label, val) in enumerate(ROWS):
        y = ROW_START_Y + i * ROW_PITCH
        delay = 0.50 + i * 0.08
        col_key = ROW_COLOURS.get(i, "val_default")
        a(row_svg(INFO_X, y, label, val, col_key, t, delay))

    # Dashed rule above prompts
    a(f'<line x1="456" y1="{RULE2_Y}" x2="1160" y2="{RULE2_Y}" '
      f'stroke="{t["rule2_stroke"]}" stroke-dasharray="2,6"/>')

    # Prompt lines
    p1k, p1v = PROMPT1
    p2k, p2v = PROMPT2
    a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.4s" begin="1.30s" fill="freeze"/>'
      f'<text x="{INFO_X}" y="{PROMPT1_Y}" font-size="13" fill="{t["prompt1_fill"]}">❯ {p1k}</text>'
      f'<text x="{INFO_X + 76}" y="{PROMPT1_Y}" font-size="13" fill="{t["label_fill"]}"> ·· </text>'
      f'<text x="{INFO_X + 96}" y="{PROMPT1_Y}" font-size="13" fill="{t["label_fill"]}">{p1v}</text>'
      f'</g>')
    a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.4s" begin="1.38s" fill="freeze"/>'
      f'<text x="{INFO_X}" y="{PROMPT2_Y}" font-size="13" fill="{t["prompt2_fill"]}">❯ {p2k}</text>'
      f'<text x="{INFO_X + 68}" y="{PROMPT2_Y}" font-size="13" fill="{t["label_fill"]}"> ·· </text>'
      f'<text x="{INFO_X + 88}" y="{PROMPT2_Y}" font-size="13" fill="{t["label_fill"]}">{p2v}</text>'
      # Blinking cursor
      f'<rect x="{INFO_X + 228}" y="{PROMPT2_Y - 13}" width="8" height="14" rx="1" fill="{t["cursor_fill"]}">'
      f'<animate attributeName="opacity" values="1;0;1" dur="1.0s" repeatCount="indefinite"/>'
      f'</rect>'
      f'</g>')

    # Bottom separator
    a(f'<line x1="456" y1="538" x2="1160" y2="538" stroke="{t["muted_sep"]}"/>')

    # Project cards
    card_w = 218
    card_starts = [460, 690, 920]
    card_begins = [1.10, 1.20, 1.30]
    for i, ((cat, title, _), cx, cb) in enumerate(zip(PROJECTS, card_starts, card_begins)):
        bg, stroke, label_col = t["card_colors"][i]
        a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.4s" begin="{cb}s" fill="freeze"/>'
          f'<rect x="{cx}" y="{CARD_Y}" width="{card_w}" height="50" rx="10" '
          f'fill="{bg}" stroke="{stroke}" stroke-width="0.8"/>'
          f'<text x="{cx+16}" y="{CARD_Y+19}" font-size="9" letter-spacing="2" fill="{label_col}">{cat}</text>'
          f'<text x="{cx+16}" y="{CARD_Y+37}" font-size="12" font-weight="600" fill="{t["card_title_fill"]}">{title}</text>'
          f'</g>')

    a('</g>')  # end clip-path

    # Terminal window border (animated gradient)
    a('<rect x="2" y="2" width="1176" height="606" rx="18" fill="none" '
      'stroke="url(#accent)" stroke-width="1.2" opacity="0.6"/>')

    a('</svg>')
    return "".join(parts)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    """
    Usage:
        # Two pre-processed portraits (recommended after running preprocess_photo.py):
        python generate_banner.py assets/portrait-dark.png assets/portrait-light.png [output_dir]

        # Single raw photo (auto-crop + dither):
        python generate_banner.py photo.jpeg [output_dir]
    """
    if len(sys.argv) < 2:
        print("Usage: python generate_banner.py <dark_photo> [light_photo] [output_dir]")
        sys.exit(1)

    # Detect if first arg is a prepped portrait-dark.png or a raw photo
    arg1 = sys.argv[1]
    if not os.path.exists(arg1):
        print(f"Error: photo not found: {arg1}")
        sys.exit(1)

    # Check for two-portrait mode
    dark_photo = arg1
    light_photo = None
    out_dir = "."
    prepped = False

    if len(sys.argv) >= 3 and os.path.isfile(sys.argv[2]):
        # Two photos provided
        light_photo = sys.argv[2]
        out_dir = sys.argv[3] if len(sys.argv) > 3 else "."
        prepped = True
        print(f"Two-portrait mode (pre-processed)")
        print(f"  Dark portrait:  {dark_photo}")
        print(f"  Light portrait: {light_photo}")
    else:
        out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        print(f"Single-photo mode: {dark_photo}")

    print(f"Processing dark mode dither...")
    dark_arr = load_and_dither(dark_photo, dark=True, prepped=prepped)
    dark_dots = int(np.sum(dark_arr > 0.5))
    print(f"  Dark: {dark_dots} lit pixels")

    print(f"Processing light mode dither...")
    light_src = light_photo if light_photo else dark_photo
    light_arr = load_and_dither(light_src, dark=False, prepped=prepped)
    light_dots = int(np.sum(light_arr > 0.5))
    print(f"  Light: {light_dots} lit pixels")

    os.makedirs(out_dir, exist_ok=True)
    for theme_name, arr in [("dark", dark_arr), ("light", light_arr)]:
        print(f"Building {theme_name} SVG...")
        random.seed(42)
        svg = build_svg(arr, theme_name, n_groups=60)
        out_path = os.path.join(out_dir, f"{theme_name}.svg")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  Wrote {out_path} ({len(svg)//1024}KB)")

    print("Done! Open dark.svg and light.svg in a browser to verify.")

if __name__ == "__main__":
    main()
