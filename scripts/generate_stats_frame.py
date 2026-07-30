import os
import sys

def generate_svg(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    themes = {
        'dark': {
            'bg': '#0C1426',
            'titlebar': '#0B1222',
            'text': '#94A3B8',
            'border_start': '#7C3AED',
            'border_end': '#22D3EE',
            'shimmer': 'rgba(167,139,250,0.08)'
        },
        'light': {
            'bg': '#FFFFFF',
            'titlebar': '#E2E8F0',
            'text': '#64748B',
            'border_start': '#7C3AED',
            'border_end': '#0891B2',
            'shimmer': 'rgba(124,58,237,0.06)'
        }
    }

    font_family = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

    for theme_name, colors in themes.items():
        # Top frame
        top_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="50">
    <defs>
        <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="{colors['border_start']}" />
            <stop offset="100%" stop-color="{colors['border_end']}" />
        </linearGradient>
        <linearGradient id="shimmer-grad" x1="0%" y1="0%" x2="100%" y2="0%" gradientTransform="rotate(45)">
            <stop offset="0%" stop-color="transparent" />
            <stop offset="50%" stop-color="{colors['shimmer']}" />
            <stop offset="100%" stop-color="transparent" />
        </linearGradient>
        <clipPath id="top-clip">
            <rect x="0" y="0" width="1180" height="62" rx="12" />
        </clipPath>
    </defs>
    
    <g clip-path="url(#top-clip)">
        <rect width="1180" height="50" fill="{colors['bg']}" />
        
        <!-- Shimmer -->
        <rect x="-100%" y="-100" width="300" height="300" fill="url(#shimmer-grad)">
            <animateTransform attributeName="transform" type="translate" from="-200 0" to="1400 0" dur="4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1" />
        </rect>
        
        <!-- Traffic lights -->
        <circle cx="20" cy="25" r="6" fill="#FF5F56" />
        <circle cx="40" cy="25" r="6" fill="#FFBD2E" />
        <circle cx="60" cy="25" r="6" fill="#27C93F" />
        
        <!-- Title -->
        <text x="590" y="30" font-family="{font_family}" font-size="14" fill="{colors['text']}" text-anchor="middle">rohit@ayaska — ~/stats</text>
        
        <!-- Border line -->
        <rect x="0" y="48" width="1180" height="2" fill="url(#border-grad)" />
    </g>
</svg>"""
        
        with open(os.path.join(output_dir, f'stats-frame-top-{theme_name}.svg'), 'w') as f:
            f.write(top_svg)
        
        # Bottom frame
        bottom_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="8">
    <defs>
        <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="{colors['border_start']}" />
            <stop offset="100%" stop-color="{colors['border_end']}" />
        </linearGradient>
        <linearGradient id="shimmer-grad" x1="0%" y1="0%" x2="100%" y2="0%" gradientTransform="rotate(45)">
            <stop offset="0%" stop-color="transparent" />
            <stop offset="50%" stop-color="{colors['shimmer']}" />
            <stop offset="100%" stop-color="transparent" />
        </linearGradient>
        <clipPath id="bottom-clip">
            <rect x="0" y="-12" width="1180" height="20" rx="12" />
        </clipPath>
    </defs>
    
    <g clip-path="url(#bottom-clip)">
        <rect width="1180" height="8" fill="{colors['bg']}" />
        
        <!-- Shimmer -->
        <rect x="-100%" y="-10" width="300" height="100" fill="url(#shimmer-grad)">
            <animateTransform attributeName="transform" type="translate" from="-200 0" to="1400 0" dur="4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1" />
        </rect>
        
        <!-- Border line (top edge) -->
        <rect x="0" y="0" width="1180" height="2" fill="url(#border-grad)" />
    </g>
</svg>"""

        with open(os.path.join(output_dir, f'stats-frame-bottom-{theme_name}.svg'), 'w') as f:
            f.write(bottom_svg)
            
    print("SVG generation complete.")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_svg(out_dir)
