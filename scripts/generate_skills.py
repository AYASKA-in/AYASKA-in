import sys
import os

def create_svg(mode, output_dir):
    is_dark = mode == "dark"
    bg_color = "#0A101F" if is_dark else "#F8FAFC"
    text_color = "#94A3B8" if is_dark else "#475569"
    percent_color = "#F8FAFC" if is_dark else "#0F172A"
    track_color = "rgba(148,163,184,0.1)" if is_dark else "rgba(100,116,139,0.15)"

    categories = [
        {
            "name": "FRONTEND",
            "color": "#22D3EE",
            "color_end": "#67E8F9",
            "skills": [("Next.js", 90), ("React", 88), ("TypeScript", 85), ("HTML/CSS", 82)]
        },
        {
            "name": "BACKEND",
            "color": "#A78BFA",
            "color_end": "#C4B5FD",
            "skills": [("FastAPI", 87), ("Node.js", 80), ("PostgreSQL", 78), ("Python", 92)]
        },
        {
            "name": "CLOUD / DEVOPS",
            "color": "#10B981",
            "color_end": "#34D399",
            "skills": [("AWS", 75), ("Docker", 72), ("Vercel", 85), ("Supabase", 78)]
        },
        {
            "name": "AI / ML",
            "color": "#F59E0B",
            "color_end": "#FBBF24",
            "skills": [("PyTorch", 80), ("TensorFlow", 70), ("Grad-CAM", 75), ("LangChain", 68)]
        }
    ]

    width = 1180
    height = 320
    font_family = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="{bg_color}" />
  <style>
    text {{ font-family: {font_family}; }}
    .title {{ font-size: 18px; font-weight: bold; fill: {percent_color}; }}
    .cat-title {{ font-size: 14px; font-weight: bold; letter-spacing: 2px; }}
    .skill-label {{ font-size: 13px; fill: {text_color}; }}
    .skill-percent {{ font-size: 13px; font-weight: bold; fill: {percent_color}; }}
  </style>
  <defs>
    <linearGradient id="grad-title-{mode}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22D3EE" />
      <stop offset="100%" stop-color="#A78BFA" />
    </linearGradient>
"""
    for i, cat in enumerate(categories):
        svg_content += f"""    <linearGradient id="grad-{i}-{mode}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{cat['color']}" />
      <stop offset="100%" stop-color="{cat['color_end']}" />
    </linearGradient>
"""
    svg_content += """  </defs>

  <!-- Header -->
  <text x="60" y="45" class="title">SKILL.MATRIX</text>
  <rect x="60" y="55" width="120" height="2" fill="url(#grad-title-{mode})" />

"""

    for i, cat in enumerate(categories):
        col = i % 2
        row = i // 2
        
        x_base = 60 + col * 540
        y_base = 90 + row * 120
        
        svg_content += f"""  <g transform="translate({x_base}, {y_base})">
    <text x="0" y="0" class="cat-title" fill="{cat['color']}">{cat['name']}</text>
"""
        for j, skill in enumerate(cat['skills']):
            skill_name, skill_percent = skill
            y_skill = 20 + j * 24
            bar_max_width = 240
            bar_width = (skill_percent / 100.0) * bar_max_width
            delay = (i * 4 + j) * 0.15
            
            svg_content += f"""    <g transform="translate(0, {y_skill})">
      <text x="0" y="9" class="skill-label">{skill_name}</text>
      <!-- Track -->
      <rect x="120" y="0" width="{bar_max_width}" height="8" rx="4" fill="{track_color}" />
      <!-- Fill -->
      <rect x="120" y="0" width="0" height="8" rx="4" fill="url(#grad-{i}-{mode})">
        <animate attributeName="width" from="0" to="{bar_width}" begin="{delay}s" dur="1s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1" />
      </rect>
      <!-- Percent -->
      <text x="{130 + bar_max_width}" y="9" class="skill-percent">{skill_percent}%</text>
      
      <!-- Pulsing Dot -->
      <circle cx="120" cy="4" r="4" fill="#FFFFFF" opacity="0">
        <animate attributeName="cx" from="120" to="{120 + bar_width}" begin="{delay}s" dur="1s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1" />
        <animate attributeName="opacity" values="0;1;0.5;1" keyTimes="0;0.5;0.75;1" begin="{delay + 1}s" dur="1.5s" repeatCount="indefinite" />
      </circle>
    </g>
"""
        svg_content += "  </g>\n"
        
    svg_content += "</svg>"

    file_name = f"skills-{mode}.svg"
    output_path = os.path.join(output_dir, file_name)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Created {output_path} (Size: {os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    create_svg("dark", out_dir)
    create_svg("light", out_dir)
