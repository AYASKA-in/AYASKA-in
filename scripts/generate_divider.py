import os
import sys

def generate_svg(is_dark_mode):
    bg_color = "#0A101F" if is_dark_mode else "#F8FAFC"
    cyan_accent = "#22D3EE" if is_dark_mode else "#0891B2"
    violet_accent = "#A78BFA" if is_dark_mode else "#7C3AED"
    
    main_path = "M -10,20 L 150,20 L 170,10 L 250,10 L 270,20 L 450,20 L 470,30 L 550,30 L 570,20 L 750,20 L 770,10 L 850,10 L 870,20 L 1050,20 L 1070,30 L 1150,30 L 1170,20 L 1190,20"
    
    branches = [
        ("M 170,10 L 160,5 L 140,5", 140, 5, 0),
        ("M 470,30 L 460,35 L 440,35", 440, 35, 1),
        ("M 770,10 L 760,5 L 740,5", 740, 5, 2),
        ("M 1070,30 L 1060,35 L 1040,35", 1040, 35, 3),
    ]
    
    branches_svg = ""
    nodes_svg = ""
    for path, nx, ny, idx in branches:
        branches_svg += f'    <path d="{path}" fill="none" stroke="{cyan_accent}" stroke-width="1.5" />\n'
        delay = idx * 0.75
        nodes_svg += f'''
    <circle cx="{nx}" cy="{ny}" r="2.5" fill="{violet_accent}">
        <animate attributeName="r" values="2.5;4.5;2.5" dur="3s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1"/>
        <animate attributeName="opacity" values="0.6;1;0.6" dur="3s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1"/>
    </circle>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="40" viewBox="0 0 1180 40">
    <defs>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
        <filter id="glow-small" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>
    
    <!-- Background (transparent) -->
    <rect width="1180" height="40" fill="transparent" />

    <!-- Dim base path -->
    <g opacity="0.15">
        <path d="{main_path}" fill="none" stroke="{cyan_accent}" stroke-width="2" />
{branches_svg}
    </g>

    <!-- Animated overlay path for drawing effect -->
    <path d="{main_path}" fill="none" stroke="{cyan_accent}" stroke-width="2" opacity="0.4" stroke-dasharray="1250" stroke-dashoffset="1250">
        <animate attributeName="stroke-dashoffset" values="1250;0;1250" dur="12s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1"/>
    </path>

    <!-- Branch Nodes -->
{nodes_svg}

    <!-- Travelling Particle -->
    <circle r="3" fill="{cyan_accent}" filter="url(#glow)">
        <animateMotion dur="8s" repeatCount="indefinite" path="{main_path}" calcMode="linear" />
    </circle>
    
    <!-- Trailing Particle 1 -->
    <circle r="2" fill="{cyan_accent}" opacity="0.7" filter="url(#glow-small)">
        <animateMotion dur="8s" begin="-0.2s" repeatCount="indefinite" path="{main_path}" calcMode="linear" />
    </circle>
    
    <!-- Trailing Particle 2 -->
    <circle r="1.5" fill="{cyan_accent}" opacity="0.4">
        <animateMotion dur="8s" begin="-0.4s" repeatCount="indefinite" path="{main_path}" calcMode="linear" />
    </circle>
</svg>'''
    return svg

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    dark_path = os.path.join(output_dir, 'divider-dark.svg')
    light_path = os.path.join(output_dir, 'divider-light.svg')
    
    with open(dark_path, 'w', encoding='utf-8') as f:
        f.write(generate_svg(is_dark_mode=True))
        
    with open(light_path, 'w', encoding='utf-8') as f:
        f.write(generate_svg(is_dark_mode=False))
        
    print(f"Generated {dark_path}")
    print(f"Generated {light_path}")

if __name__ == '__main__':
    main()
