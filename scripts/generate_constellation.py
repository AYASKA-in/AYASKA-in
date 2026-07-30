import sys
import os
import random

def generate_constellation(mode, out_dir):
    width = 1180
    height = 280
    
    # Theme configuration
    if mode == "dark":
        bg_color = "#0A101F"
        star_color = "#22D3EE"
        line_color = "rgba(167, 139, 250, 0.2)"
        label_color = "#94A3B8"
        header_color = "#22D3EE"
        bg_star_color = "#ffffff"
    else:
        bg_color = "#F8FAFC"
        star_color = "#0891B2"
        line_color = "rgba(124, 58, 237, 0.15)"
        label_color = "#475569"
        header_color = "#0891B2"
        bg_star_color = "#0f172a"

    # SVG header
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<rect width="100%" height="100%" fill="{bg_color}"/>
<defs>
    <filter id="glow-{mode}" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <linearGradient id="header-grad-{mode}" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="{header_color}" stop-opacity="0.8"/>
        <stop offset="100%" stop-color="{header_color}" stop-opacity="0"/>
    </linearGradient>
</defs>
'''

    # Ambient dots
    random.seed(42) # fixed seed for reproducibility across runs
    svg += '<g id="ambient-dots">\n'
    for _ in range(40):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        opacity = random.uniform(0.05, 0.2)
        svg += f'    <circle cx="{cx}" cy="{cy}" r="0.8" fill="{bg_star_color}" opacity="{opacity}"/>\n'
    svg += '</g>\n'

    # Main rotating group
    svg += f'''<g>
    <animateTransform attributeName="transform" type="rotate" values="-1.5 {width/2} {height/2}; 1.5 {width/2} {height/2}; -1.5 {width/2} {height/2}" dur="25s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
'''

    # Header text
    svg += f'''
    <text x="40" y="40" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace" font-size="14" font-weight="bold" fill="{header_color}" letter-spacing="2">TECH.STACK</text>
    <rect x="40" y="48" width="80" height="2" fill="url(#header-grad-{mode})"/>
'''

    # Tech nodes
    nodes = {
        "Next.js": (150, 150),
        "React": (230, 110),
        "TypeScript": (320, 180),
        "Vercel": (200, 220),
        
        "Python": (520, 130),
        "FastAPI": (610, 80),
        "PyTorch": (490, 210),
        "Node.js": (430, 150),
        
        "AWS": (900, 140),
        "Docker": (840, 200),
        "Supabase": (980, 100),
        "PostgreSQL": (750, 160)
    }

    # Connections
    edges = [
        ("Next.js", "React"),
        ("React", "TypeScript"),
        ("Next.js", "Vercel"),
        ("TypeScript", "Vercel"),
        ("React", "Node.js"),
        
        ("Python", "FastAPI"),
        ("Python", "PyTorch"),
        ("Node.js", "Python"),
        
        ("FastAPI", "PostgreSQL"),
        ("PostgreSQL", "AWS"),
        ("AWS", "Docker"),
        ("AWS", "Supabase"),
        ("PostgreSQL", "Docker"),
        ("Supabase", "Node.js")
    ]

    # Draw lines
    svg += '    <g id="lines">\n'
    for n1, n2 in edges:
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        dur = random.uniform(4, 7)
        svg += f'''        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{line_color}" stroke-width="0.5">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="{dur:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
        </line>\n'''
    svg += '    </g>\n'

    # Draw nodes
    svg += '    <g id="stars">\n'
    for name, (cx, cy) in nodes.items():
        dur = random.uniform(2, 5)
        # Glow ring
        svg += f'''        <g>
            <circle cx="{cx}" cy="{cy}" r="8" fill="{star_color}" opacity="0.2" filter="url(#glow-{mode})">
                <animate attributeName="opacity" values="0.1;0.4;0.1" dur="{dur:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
            </circle>
            <circle cx="{cx}" cy="{cy}" r="3" fill="{star_color}">
                <animate attributeName="opacity" values="0.4;1;0.4" dur="{dur:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1; 0.45 0 0.55 1"/>
            </circle>
            <text x="{cx}" y="{cy + 18}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace" font-size="11" fill="{label_color}" text-anchor="middle">{name}</text>
        </g>\n'''
    svg += '    </g>\n'

    svg += '</g>\n</svg>'
    
    out_file = os.path.join(out_dir, f'constellation-{mode}.svg')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out_dir, exist_ok=True)
    generate_constellation('dark', out_dir)
    generate_constellation('light', out_dir)
