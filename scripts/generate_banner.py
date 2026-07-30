#!/usr/bin/env python3
"""
generate_banner.py — Floyd-Steinberg dither portrait → SVG banner
Exact port of the arifhaxn approach: 1×1 px dot paths, ~60 random fade-in groups,
animated asciiGrad shimmer, dark + light SVG output.
"""

import sys, os, random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# ── PROFILE DATA ────────────────────────────────────────────────────────────
NAME         = "Moningi Rohit"
TITLE_BAR    = "rohitmoningi@ayaska - % ./profile.sh --live"

# Data rows mapping exactly to arifhaxn layout spacing
ROWS = [
    # Top block
    (162, "Subject", "Moningi Rohit", 0.50),
    (185, "Role", "Full-Stack Developer", 0.62),
    (208, "Origin", "Bangalore, India", 0.74),
    (231, "Education", "B.Tech IT — VIT '26", 0.86),
    (254, "Status", "Building + Shipping 🚀", 0.98),
    (277, "Current", "AI / Backend — Prospient", 1.10),
    # Core block (spaced slightly)
    (308, "Core.Web", "Next 16, React 19, TS", 1.32),
    (331, "Core.API", "FastAPI, Node, Postgres", 1.44),
    (354, "Core.AI", "PyTorch, TF, Grad-CAM", 1.56),
    (377, "Core.Cloud", "AWS, Supabase, Vercel", 1.68),
    (400, "Research", "IEEE Published · 2024", 1.80),
]

CONTACT_ROWS = [
    (454, "Grid.Portfolio", "rohitmoningi.in", 2.14),
    (477, "Grid.LinkedIn", "moningi-rohit", 2.26),
    (500, "Grid.GitHub", "@AYASKA-in", 2.38),
    (523, "Grid.UpNext", "Bosch GST · Aug 2026", 2.50),
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
INFO_X = 470

# ── THEMES ───────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "window_fill":  "#070B16",
        "panel_start":  "#0A101F", "panel_end":    "#0C1426",
        "titlebar":     "#0B1222",
        "frame_fill":   "#0A101F", "frame_stroke": "rgba(34,211,238,0.35)",
        "frame_glow":   "#22D3EE",
        "dot_fill":     "#A78BFA",
        "grad_top":     "#60A5FA", "grad_mid":     "#A78BFA", "grad_bot":    "#22D3EE",
        "label_meta":   "#475569",
        "sys_info":     "#22D3EE",
        "live_text":    "#F87171",
        "title_text":   "#94A3B8",
        "name_fill":    "#E9D5FF",
        "name_bg":      "#4C1D95",
        "key_fill":     "#22D3EE",
        "dots_fill":    "rgba(148,163,184,0.35)",
        "val_fill":     "#F8FAFC",
        "divider":      "#94A3B8",
        "footer_text":  "#94A3B8",
        "footer_cursor":"#22D3EE",
        "accent_v1":    "#7C3AED", "accent_v2": "#22D3EE", "accent_v3": "#10B981",
        "dot_grid_fill":"#22D3EE",
    },
    "light": {
        "window_fill":  "#E2E8F0",
        "panel_start":  "#F8FAFC", "panel_end":    "#F1F5F9",
        "titlebar":     "#E2E8F0",
        "frame_fill":   "#FFFFFF", "frame_stroke": "rgba(109,40,217,0.2)",
        "frame_glow":   "#7C3AED",
        "dot_fill":     "#7C3AED",
        "grad_top":     "#7C3AED", "grad_mid":     "#4F46E5", "grad_bot":    "#0891B2",
        "label_meta":   "#94A3B8",
        "sys_info":     "#0891B2",
        "live_text":    "#DC2626",
        "title_text":   "#64748B",
        "name_fill":    "#4C1D95",
        "name_bg":      "#DDD6FE",
        "key_fill":     "#0891B2",
        "dots_fill":    "rgba(148,163,184,0.35)",
        "val_fill":     "#0F172A",
        "divider":      "#64748B",
        "footer_text":  "#64748B",
        "footer_cursor":"#0891B2",
        "accent_v1":    "#6D28D9", "accent_v2": "#0891B2", "accent_v3": "#059669",
        "dot_grid_fill":"#6D28D9",
    },
}


# ── IMAGE PROCESSING ──────────────────────────────────────────────────────────
def load_and_dither(photo_path, dark=True, prepped=False):
    img = Image.open(photo_path).convert("RGB")
    if not prepped:
        w, h = img.size
        target_aspect = GRID_COLS / GRID_ROWS
        if w / h > target_aspect:
            new_w = int(h * target_aspect)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_aspect)
            top = max(0, int(h * 0.05))
            img = img.crop((0, top, w, min(top + new_h, h)))
    img = img.resize((GRID_COLS, GRID_ROWS), Image.LANCZOS)
    img = ImageOps.autocontrast(img, cutoff=1)
    # Boost contrast more aggressively for prepped logos to get denser dot patterns
    contrast_factor = 2.0 if prepped else 1.35
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)
    if prepped:
        img = ImageEnhance.Brightness(img).enhance(1.5)  # brighten logos for more dots
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=150, threshold=3))
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)
    if prepped:
        if not dark: arr = 255 - arr
    else:
        if dark: arr = 255 - arr
    arr = arr / 255.0
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
    return out

def split_into_groups(dither_arr, n_groups=60):
    h, w = dither_arr.shape
    ys, xs = np.where(dither_arr > 0.5)
    coords = list(zip(ys.tolist(), xs.tolist()))
    random.shuffle(coords)
    groups = [[] for _ in range(n_groups)]
    for i, (y, x) in enumerate(coords):
        groups[i % n_groups].append((y, x))
    paths = []
    for g in groups:
        if not g:
            paths.append("")
            continue
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
def build_svg(dither_arrs, theme_name, n_groups=60):
    t = THEMES[theme_name]
    random.seed(42)

    parts = []
    a = parts.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" '
      f'viewBox="0 0 {SVG_W} {SVG_H}" '
      f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
      f'role="img" aria-label="{NAME} — profile.sh --live">')

    a('<defs>')
    v1, v2, v3 = t["accent_v1"], t["accent_v2"], t["accent_v3"]
    a(f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{v1}"><animate attributeName="stop-color" values="{v1};{v2};{v3};{v1}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="0.5" stop-color="{v2}"><animate attributeName="stop-color" values="{v2};{v3};{v1};{v2}" dur="10s" repeatCount="indefinite"/></stop>'
      f'<stop offset="1" stop-color="{v3}"><animate attributeName="stop-color" values="{v3};{v1};{v2};{v3}" dur="10s" repeatCount="indefinite"/></stop>'
      f'</linearGradient>')

    gt, gm, gb = t["grad_top"], t["grad_mid"], t["grad_bot"]
    a(f'<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">'
      f'<stop offset="0" stop-color="{gt}"/>'
      f'<stop offset="0.45" stop-color="{gm}"/>'
      f'<stop offset="1" stop-color="{gb}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="0 -120; 0 120; 0 -120" dur="9s" repeatCount="indefinite"/>'
      f'</linearGradient>')

    a(f'<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{t["panel_start"]}"/>'
      f'<stop offset="1" stop-color="{t["panel_end"]}"/>'
      f'</linearGradient>')

    a('<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>')
    a('<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>')
    a('<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="0.9" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      '</filter>')

    a('<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>')
    a(f'<pattern id="dotGrid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">'
      f'<circle cx="1" cy="1" r="0.8" fill="{t["dot_grid_fill"]}" opacity="0.03"/>'
      f'</pattern>')
    a('</defs>')

    a(f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{t["window_fill"]}"/>')
    a('<g clip-path="url(#winClip)">')

    a('<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>')
    a('<rect x="2" y="2" width="1176" height="606" fill="url(#dotGrid)"/>')
    a(f'<rect x="2" y="2" width="1176" height="46" fill="{t["titlebar"]}"/>')

    a('<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/>')
    a('<circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/>')
    a('<circle cx="70" cy="25" r="5.5" fill="#27c93f"/>')

    a(f'<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{t["title_text"]}">{TITLE_BAR}</text>')

    a(f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{t["label_meta"]}">VISUAL.MAP</text>')
    a(f'<text x="470" y="106" font-size="13" letter-spacing="2" fill="{t["sys_info"]}">SYSTEM.INFO</text>')
    a(f'<text x="1125" y="106" font-size="12" font-weight="700" fill="{t["live_text"]}">● LIVE</text>')

    a(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="10" '
      f'fill="none" stroke="{t["frame_glow"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>')
    a(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="10" '
      f'fill="{t["frame_fill"]}" stroke="{t["frame_stroke"]}"/>')

    loop_dur = "16s"
    loop_begin = "3.2s"
    kt = "0.000;0.194;0.288;0.432;0.525;0.669;0.763;0.906;1.000"
    frame_vals = [
        "1;1;0;0;0;0;0;0;1",
        "0;0;1;1;0;0;0;0;0",
        "0;0;0;0;1;1;0;0;0",
        "0;0;0;0;0;0;1;1;0",
    ]

    a(f'<g transform="translate({TRANS_X},{TRANS_Y}) scale({SCALE_X},{SCALE_Y})" '
      f'fill="{t["dot_fill"]}" shape-rendering="crispEdges">')

    # Ensure we only loop over up to 4 frames
    for frame_idx, arr in enumerate(dither_arrs[:4]):
        groups = split_into_groups(arr, n_groups)
        # Wrap each frame in a looping opacity group
        a(f'<g opacity="{"1" if frame_idx == 0 else "0"}">')
        a(f'<animate attributeName="opacity" values="{frame_vals[frame_idx]}" '
          f'keyTimes="{kt}" dur="{loop_dur}" begin="{loop_begin}" repeatCount="indefinite"/>')

        for i, path_d in enumerate(groups):
            # Generate random scatter offsets — reduced range to stay within frame
            dx = random.randint(-80, 80)
            dy = random.randint(-80, 80)
            # Stagger timing slightly per group for wave-like shatter
            stagger = i * 0.02
            
            # Map the opacity values (1 or 0) to translation values (0,0 or dx,dy)
            t_vals = ";".join(["0 0" if v == "1" else f"{dx} {dy}" for v in frame_vals[frame_idx].split(";")])
            # Spline easing keyTimes for organic deceleration (9 values = 8 segments)
            scatter_splines = "0.4 0 0.2 1;" * 8
            scatter_splines = scatter_splines.rstrip(";")

            if frame_idx == 0:
                begin = 0.20 + i * 0.03
                a(f'<g opacity="0">'
                  f'<animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin:.2f}s" fill="freeze" '
                  f'calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
                  f'<animateTransform attributeName="transform" type="translate" values="{t_vals}" '
                  f'keyTimes="{kt}" dur="{loop_dur}" begin="{loop_begin}" repeatCount="indefinite" additive="sum" '
                  f'calcMode="spline" keySplines="{scatter_splines}"/>')
            else:
                a(f'<g>')
                a(f'<animateTransform attributeName="transform" type="translate" values="{t_vals}" '
                  f'keyTimes="{kt}" dur="{loop_dur}" begin="{loop_begin}" repeatCount="indefinite" additive="sum" '
                  f'calcMode="spline" keySplines="{scatter_splines}"/>')
                
            if path_d:
                a(f'<path d="{path_d}"/>')
            a('</g>')
        a('</g>')

    a('</g>')

    # Breathing neon pulse on frame border
    a(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="10" '
      f'fill="none" stroke="url(#accent)" stroke-width="1.5" opacity="0.4">'
      f'<animate attributeName="opacity" values="0.3;0.8;0.3" dur="4s" repeatCount="indefinite" '
      f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/></rect>')

    # Ambient particle dust — tiny floating dots inside the portrait frame
    for dust_i in range(25):
        dx = random.randint(FRAME_X + 15, FRAME_X + FRAME_W - 15)
        dy_start = random.randint(FRAME_Y + 15, FRAME_Y + FRAME_H - 15)
        dy_end = dy_start + random.choice([-12, -8, 8, 12])
        dur = 3 + random.random() * 4  # 3-7s
        delay = random.random() * 5
        opacity = 0.08 + random.random() * 0.15
        a(f'<circle cx="{dx}" cy="{dy_start}" r="0.8" fill="{t["frame_glow"]}" opacity="{opacity:.2f}">'
          f'<animate attributeName="cy" values="{dy_start};{dy_end};{dy_start}" dur="{dur:.1f}s" '
          f'begin="{delay:.1f}s" repeatCount="indefinite" '
          f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>'
          f'<animate attributeName="opacity" values="{opacity:.2f};{opacity*2:.2f};{opacity:.2f}" '
          f'dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/></circle>')

    a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.30s" fill="freeze"/>'
      f'<rect x="470" y="122" width="245" height="20" rx="4" fill="{t["name_bg"]}"/>'
      f'<text x="479" y="136" font-size="14" font-weight="700" fill="{t["name_fill"]}">{TITLE_BAR.split(" ")[0]}</text>'
      f'</g>')

    for (y, label, val, delay) in ROWS:
        dots = "." * (60 - len(label))
        a(f'<g opacity="0">'
          f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
          f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
          f'<text x="{INFO_X}" y="{y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
          f'<tspan fill="{t["key_fill"] if label != "Subject" else "none"}">{label} </tspan>'
          f'<tspan fill="{t["dots_fill"] if label != "Subject" else "none"}">{dots}</tspan>'
          f'<tspan fill="{t["val_fill"] if label != "Subject" else "none"}" font-weight="{"600" if label != "Subject" else "normal"}"> {val}</tspan>'
          f'</text></g>')

    a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.02s" fill="freeze"/>'
      f'<text x="{INFO_X}" y="431" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
      f'<tspan fill="{t["divider"]}">- Contact </tspan>'
      f'<tspan fill="{t["dots_fill"]}">---------------------------------------------------------------------</tspan>'
      f'</text></g>')

    for (y, label, val, delay) in CONTACT_ROWS:
        dots = "." * (60 - len(label))
        a(f'<g opacity="0">'
          f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
          f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
          f'<text x="{INFO_X}" y="{y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
          f'<tspan fill="{t["key_fill"]}">{label} </tspan>'
          f'<tspan fill="{t["dots_fill"]}">{dots}</tspan>'
          f'<tspan fill="{t["val_fill"]}" font-weight="600"> {val}</tspan>'
          f'</text></g>')

    a(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="2.90s" fill="freeze"/>'
      f'<text x="{INFO_X}" y="577" font-size="14" fill="{t["footer_text"]}">'
      f'&#9656; More about me &amp; projects below in README &#8595; '
      f'<tspan fill="{t["footer_cursor"]}">'
      f'&#9608;'
      f'<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
      f'</tspan></text></g>')

    a('</g>')

    a(f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" opacity="0.6"/>')
    a(f'<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" opacity="0.4"/>')

    a('</svg>')
    return "".join(parts)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_banner.py <dark_photo> [light_photo] [output_dir]")
        sys.exit(1)

    dark_photo = sys.argv[1]
    light_photo = sys.argv[2] if len(sys.argv) >= 3 and os.path.isfile(sys.argv[2]) else None
    out_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    prepped = True if light_photo else False

    # List of images to loop (up to 4)
    extra_logos = ["assets/nextjs.png", "assets/aws.png", "assets/docker.png"]
    
    dark_arrs = []
    light_arrs = []

    print("Processing dark mode portraits...")
    dark_arrs.append(load_and_dither(dark_photo, dark=True, prepped=prepped))
    for logo in extra_logos:
        if os.path.exists(logo):
            dark_arrs.append(load_and_dither(logo, dark=True, prepped=True))

    print("Processing light mode portraits...")
    light_src = light_photo if light_photo else dark_photo
    light_arrs.append(load_and_dither(light_src, dark=False, prepped=prepped))
    for logo in extra_logos:
        if os.path.exists(logo):
            # For light mode, we might need to invert the logo if it's white-on-black, 
            # since light mode wants black-on-white.
            # load_and_dither with prepped=True does NO inversion for light mode (not dark).
            # So a white-on-black logo stays white-on-black.
            # That means the text is 1.0 (white). In light mode, 1.0 gets dots.
            # So it actually works perfectly!
            light_arrs.append(load_and_dither(logo, dark=False, prepped=True))

    os.makedirs(out_dir, exist_ok=True)
    for theme_name, arrs in [("dark", dark_arrs), ("light", light_arrs)]:
        print(f"Building {theme_name} SVG...")
        svg = build_svg(arrs, theme_name, n_groups=60)
        out_path = os.path.join(out_dir, f"{theme_name}.svg")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)

if __name__ == "__main__":
    main()
