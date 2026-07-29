from __future__ import annotations

import argparse
import base64
import html
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat


CANVAS = (1280, 640)
PORTRAIT_SIZE = (360, 430)

THEMES = {
    "dark": {
        "background": "#06111d",
        "window": "#0a1726",
        "window_alt": "#0e1d2d",
        "panel": "#0d1b2c",
        "panel_alt": "#12253a",
        "stroke": "#16314d",
        "title": "#f2f8ff",
        "text": "#9ab6c8",
        "muted": "#5d778c",
        "chrome": "#39d7ff",
        "accent": "#58e2a7",
        "portrait": "#f2a53d",
        "danger": "#ff6f6f",
        "card": "#081523",
        "glow": "#08202d",
        "badge_text": "#08111a",
    },
    "light": {
        "background": "#f4f7fb",
        "window": "#ffffff",
        "window_alt": "#edf3f9",
        "panel": "#f6f9fc",
        "panel_alt": "#eef4fa",
        "stroke": "#d8e3ee",
        "title": "#112234",
        "text": "#476074",
        "muted": "#7b8fa2",
        "chrome": "#0d8eb7",
        "accent": "#1f9b67",
        "portrait": "#5a3722",
        "danger": "#cf4f4f",
        "card": "#f8fbfe",
        "glow": "#dbeaf4",
        "badge_text": "#f7fbff",
    },
}

INFO_ROWS = [
    ("ORIGIN", "BANGALORE, INDIA"),
    ("EDUCATION", "B.TECH IT, VIT '26"),
    ("CURRENT", "PROSPIENT SENTINELAI"),
    ("UP NEXT", "BOSCH // AUG 2026"),
    ("CORE.WEB", "NEXT 16 / REACT 19"),
    ("CORE.API", "FASTAPI / POSTGRES"),
    ("CORE.AI", "PYTORCH / TF / XAI"),
    ("CLOUD", "AWS / SUPABASE / VERCEL"),
    ("FEATURED", "SRI LALITHA STORE"),
    ("STATUS", "BUILDING + SHIPPING"),
]

PROJECT_CARDS = [
    (
        "LIVE BUILD",
        "Sri Lalitha Signature Noodles",
        "Next.js commerce // 192-frame canvas // Razorpay",
    ),
    (
        "RESEARCH",
        "IEEE ECG Classification",
        "Deep CNN // Grad-CAM // MIT-BIH arrhythmia",
    ),
    (
        "SYSTEMS",
        "Command Center SaaS",
        "RBAC // FastAPI // PostgreSQL // multi-tenant",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate dark/light GitHub profile banners from a source photo."
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source portrait photo.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Profile repo root. Defaults to the repo containing this script.",
    )
    return parser.parse_args()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lighten(color: str, factor: float) -> str:
    r, g, b = hex_to_rgb(color)
    nr = round(r + (255 - r) * factor)
    ng = round(g + (255 - g) * factor)
    nb = round(b + (255 - b) * factor)
    return f"#{nr:02x}{ng:02x}{nb:02x}"


def prepare_base_photo(source: Path) -> Image.Image:
    image = Image.open(source).convert("RGB")
    width, height = image.size
    crop_box = (
        int(width * 0.09),
        int(height * 0.05),
        int(width * 0.88),
        int(height * 0.85),
    )
    cropped = image.crop(crop_box)
    fitted = ImageOps.fit(
        cropped,
        PORTRAIT_SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.52, 0.19),
    )
    return fitted


def make_focus_value(x: float, y: float) -> float:
    dx = (x - 0.54) / 0.43
    dy = (y - 0.43) / 0.58
    score = 1.0 - (dx * dx + dy * dy)
    return max(0.18, min(1.0, score))


def make_dot_portrait(base_photo: Image.Image, dot_color: str) -> Image.Image:
    grayscale = ImageOps.grayscale(base_photo)
    grayscale = ImageOps.autocontrast(grayscale, cutoff=1)
    grayscale = ImageEnhance.Contrast(grayscale).enhance(1.35)
    grayscale = grayscale.filter(ImageFilter.UnsharpMask(radius=2.2, percent=140, threshold=2))

    output = Image.new("RGBA", grayscale.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(output)
    color = hex_to_rgb(dot_color)
    step = 6
    width, height = grayscale.size

    for top in range(0, height, step):
        for left in range(0, width, step):
            right = min(left + step, width)
            bottom = min(top + step, height)
            tile = grayscale.crop((left, top, right, bottom))
            brightness = ImageStat.Stat(tile).mean[0] / 255
            cx = left + (right - left) / 2
            cy = top + (bottom - top) / 2
            focus = make_focus_value(cx / width, cy / height)
            lift = 1.0 - max(0.0, (cy / height - 0.72)) * 0.45
            value = max(0.0, ((brightness * focus * lift) - 0.15) / 0.85)
            radius = (value**1.82) * 2.7
            if radius < 0.45:
                continue

            alpha = int(118 + value * 120)
            draw.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=(*color, alpha),
            )
            if value > 0.82:
                glow_radius = radius + 0.8
                draw.ellipse(
                    (
                        cx - glow_radius,
                        cy - glow_radius,
                        cx + glow_radius,
                        cy + glow_radius,
                    ),
                    fill=(*color, 28),
                )

    return output.filter(ImageFilter.GaussianBlur(0.2))


def encode_image(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    mime = "image/png" if suffix == "png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def dotted_row(label: str, value: str, width: int = 44) -> str:
    room = max(4, width - len(label) - len(value))
    return f"{label}{'.' * room}{value}"


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def build_rows_svg(theme: dict[str, str]) -> str:
    lines = []
    start_y = 230
    for index, (label, value) in enumerate(INFO_ROWS):
        y = start_y + index * 27
        row = dotted_row(label, value)
        begin = 0.55 + index * 0.08
        lines.append(
            f"""
      <g opacity="0">
        <text x="525" y="{y}" fill="{theme['text']}" class="row">{escape(row)}</text>
        <animate attributeName="opacity" values="0;1" dur="0.32s" begin="{begin:.2f}s" fill="freeze" />
      </g>""".rstrip()
        )
    return "\n".join(lines)


def build_cards_svg(theme: dict[str, str]) -> str:
    segments = []
    start_x = 88
    card_width = 352
    gap = 18
    for index, (label, title, subtitle) in enumerate(PROJECT_CARDS):
        x = start_x + index * (card_width + gap)
        segments.append(
            f"""
    <g transform="translate({x}, 535)" opacity="0">
      <rect width="{card_width}" height="78" rx="18" fill="{theme['card']}" stroke="{theme['stroke']}" />
      <text x="20" y="24" fill="{theme['chrome']}" class="micro">{escape(label)}</text>
      <text x="20" y="46" fill="{theme['title']}" class="cardtitle">{escape(title)}</text>
      <text x="20" y="64" fill="{theme['muted']}" class="cardsub">{escape(subtitle)}</text>
      <animate attributeName="opacity" values="0;1" dur="0.4s" begin="{1.1 + index * 0.12:.2f}s" fill="freeze" />
    </g>""".rstrip()
        )
    return "\n".join(segments)


def build_svg(theme_name: str, theme: dict[str, str], portrait_path: Path) -> str:
    portrait_data = encode_image(portrait_path)
    title_bar = theme["window_alt"]
    portrait_glow = lighten(theme["portrait"], 0.15)
    window_shadow = theme["glow"]
    rows_svg = build_rows_svg(theme)
    cards_svg = build_cards_svg(theme)

    return f"""<svg width="{CANVAS[0]}" height="{CANVAS[1]}" viewBox="0 0 {CANVAS[0]} {CANVAS[1]}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="60" y1="40" x2="1180" y2="640" gradientUnits="userSpaceOnUse">
      <stop stop-color="{theme['background']}" />
      <stop offset="1" stop-color="{lighten(theme['background'], 0.03 if theme_name == 'dark' else 0.01)}" />
    </linearGradient>
    <linearGradient id="panel" x1="0" y1="94" x2="0" y2="610" gradientUnits="userSpaceOnUse">
      <stop stop-color="{theme['panel']}" />
      <stop offset="1" stop-color="{theme['panel_alt']}" />
    </linearGradient>
    <linearGradient id="portraitFrame" x1="88" y1="140" x2="450" y2="520" gradientUnits="userSpaceOnUse">
      <stop stop-color="{theme['window_alt']}" />
      <stop offset="1" stop-color="{theme['panel']}" />
    </linearGradient>
    <filter id="shadow" x="0" y="0" width="1400" height="760" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="24" stdDeviation="24" flood-color="{window_shadow}" flood-opacity="{0.65 if theme_name == 'dark' else 0.18}" />
    </filter>
  </defs>

  <rect width="{CANVAS[0]}" height="{CANVAS[1]}" fill="url(#bg)" />

  <g filter="url(#shadow)">
    <rect x="48" y="34" width="1184" height="572" rx="28" fill="{theme['window']}" stroke="{theme['stroke']}" />
    <rect x="48" y="34" width="1184" height="54" rx="28" fill="{title_bar}" />
    <rect x="48" y="60" width="1184" height="546" rx="0" fill="{theme['window']}" />
    <rect x="48" y="34" width="1184" height="572" rx="28" stroke="{theme['stroke']}" />
  </g>

  <circle cx="84" cy="61" r="6" fill="{theme['danger']}" />
  <circle cx="106" cy="61" r="6" fill="{theme['portrait']}" />
  <circle cx="128" cy="61" r="6" fill="{theme['accent']}" />
  <text x="166" y="66" fill="{theme['muted']}" class="micro">profile.sh -- live</text>

  <g transform="translate(1090, 48)">
    <rect width="112" height="26" rx="13" fill="{theme['chrome']}" fill-opacity="{0.18 if theme_name == 'dark' else 0.12}" stroke="{theme['chrome']}" />
    <text x="20" y="17" fill="{theme['chrome']}" class="micro">@AYASKA-in</text>
  </g>

  <rect x="72" y="104" width="388" height="418" rx="24" fill="url(#portraitFrame)" stroke="{theme['stroke']}" />
  <rect x="96" y="128" width="340" height="370" rx="22" fill="{theme['panel']}" stroke="{theme['stroke']}" />
  <text x="96" y="118" fill="{theme['muted']}" class="micro">VISUAL.MAP</text>
  <text x="366" y="118" fill="{theme['accent']}" class="micro">subject.live</text>
  <rect x="114" y="148" width="304" height="334" rx="18" fill="{theme['window_alt']}" stroke="{theme['stroke']}" />
  <image href="{portrait_data}" x="136" y="162" width="260" height="310" preserveAspectRatio="xMidYMid meet" />
  <rect x="114" y="148" width="304" height="334" rx="18" fill="none" stroke="{portrait_glow}" stroke-opacity="{0.24 if theme_name == 'dark' else 0.16}" />

  <path d="M480 120H1206" stroke="{theme['stroke']}" />
  <path d="M480 512H1206" stroke="{theme['stroke']}" />
  <text x="524" y="142" fill="{theme['chrome']}" class="micro">SYSTEM.INFO</text>
  <g transform="translate(1076, 120)">
    <rect width="98" height="26" rx="13" fill="{theme['danger']}" fill-opacity="{0.12 if theme_name == 'dark' else 0.10}" stroke="{theme['danger']}" />
    <circle cx="18" cy="13" r="4" fill="{theme['danger']}">
      <animate attributeName="opacity" values="0.35;1;0.35" dur="1.8s" repeatCount="indefinite" />
    </circle>
    <text x="30" y="17" fill="{theme['danger']}" class="micro">LIVE</text>
  </g>

  <text x="520" y="188" fill="{theme['title']}" class="heading">MONINGI ROHIT</text>
  <text x="523" y="208" fill="{theme['muted']}" class="subhead">full-stack systems // ai products // motion-rich interfaces</text>

{rows_svg}

  <text x="524" y="491" fill="{theme['accent']}" class="prompt">&gt; portfolio: rohitmoningi.in</text>
  <text x="524" y="514" fill="{theme['chrome']}" class="prompt">&gt; linkedin: /in/moningi-rohit</text>
  <rect x="815" y="498" width="8" height="16" rx="2" fill="{theme['title']}">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" />
  </rect>

{cards_svg}

  <style>
    .heading {{
      font: 700 31px 'Trebuchet MS', 'Segoe UI', sans-serif;
      letter-spacing: 1.2px;
    }}
    .subhead {{
      font: 500 14px 'Trebuchet MS', 'Segoe UI', sans-serif;
      letter-spacing: 0.8px;
    }}
    .row {{
      font: 500 14px 'Consolas', 'Courier New', monospace;
      letter-spacing: 0.35px;
    }}
    .micro {{
      font: 600 12px 'Consolas', 'Courier New', monospace;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    .prompt {{
      font: 500 14px 'Consolas', 'Courier New', monospace;
      letter-spacing: 0.4px;
    }}
    .cardtitle {{
      font: 700 15px 'Trebuchet MS', 'Segoe UI', sans-serif;
      letter-spacing: 0.2px;
    }}
    .cardsub {{
      font: 500 11px 'Consolas', 'Courier New', monospace;
      letter-spacing: 0.3px;
    }}
  </style>
</svg>
"""


def main() -> None:
    args = parse_args()
    output_root = args.output_root.resolve()
    assets_dir = output_root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    base_photo = prepare_base_photo(args.source.resolve())

    for theme_name, theme in THEMES.items():
        portrait = make_dot_portrait(base_photo, theme["portrait"])
        portrait_path = assets_dir / f"portrait-{theme_name}.png"
        portrait.save(portrait_path, format="PNG")

        svg_path = output_root / f"{theme_name}.svg"
        svg_path.write_text(build_svg(theme_name, theme, portrait_path), encoding="utf-8")


if __name__ == "__main__":
    main()
