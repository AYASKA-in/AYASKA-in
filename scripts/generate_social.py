import os
import sys

def get_icon(name):
    if name == 'linkedin':
        return '<rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" fill="none" stroke-width="2"/><path d="M8 11v6M8 8v.01M12 17v-4a2 2 0 0 1 4 0v4M12 11h4" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"/>'
    elif name == 'github':
        return '<path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.03-2.682-.103-.253-.447-1.27.098-2.646 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.376.202 2.394.1 2.646.64.699 1.026 1.591 1.026 2.682 0 3.841-2.337 4.687-4.565 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.161 22 16.418 22 12c0-5.523-4.477-10-10-10z" fill="currentColor"/>'
    elif name == 'email':
        return '<path d="M3 7l9 6 9-6" stroke="currentColor" fill="none" stroke-width="2" stroke-linejoin="round"/><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" fill="none" stroke-width="2"/>'
    elif name == 'portfolio':
        return '<circle cx="12" cy="12" r="9" stroke="currentColor" fill="none" stroke-width="2"/><ellipse cx="12" cy="12" rx="4" ry="9" stroke="currentColor" fill="none" stroke-width="2"/><path d="M3 12h18" stroke="currentColor" fill="none" stroke-width="2"/>'
    return ''

def generate_button(theme, link, index):
    if theme == 'dark':
        text_color = '#94A3B8'
        text_active = '#F8FAFC'
        grad_start = '#7C3AED'
        grad_end = '#22D3EE'
        border_color = 'rgba(34,211,238,0.2)'
        glow_color = '#22D3EE'
    else:
        text_color = '#475569'
        text_active = '#0F172A'
        grad_start = '#7C3AED'
        grad_end = '#0891B2'
        border_color = 'rgba(8,145,178,0.2)'
        glow_color = '#0891B2'
        
    width = 170
    height = 50
    button_width = 160
    bx = 5
    by = 5
    bh = 36
    
    icon_svg = get_icon(link['id'])
    
    delay = index * 0.2  # stagger the animations
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="{grad_start}" />
            <stop offset="100%" stop-color="{grad_end}" />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <style>
            .link-text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-size: 13px; fill: {text_color}; font-weight: 600; letter-spacing: 1px; transition: fill 0.3s ease; }}
            .icon {{ color: {text_color}; transition: color 0.3s ease; }}
            .bg-glow {{ opacity: 0; transition: opacity 0.3s ease; }}
            .border {{ stroke: {border_color}; transition: stroke 0.3s ease; }}
            .cursor-dot {{ opacity: 0; transition: opacity 0.3s ease; }}
            
            /* Native SVG Hover Interactions */
            .btn:hover .link-text {{ fill: {text_active}; }}
            .btn:hover .icon {{ color: {text_active}; }}
            .btn:hover .bg-glow {{ opacity: 0.15; }}
            .btn:hover .border {{ stroke: {glow_color}; }}
            .btn:hover .cursor-dot {{ opacity: 1; }}
        </style>
    </defs>

    <g class="btn">
        <!-- Background glow when active/hovered -->
        <rect x="{bx}" y="{by}" width="{button_width}" height="{bh}" rx="6" fill="{glow_color}" class="bg-glow" />
        
        <!-- Border -->
        <rect x="{bx}" y="{by}" width="{button_width}" height="{bh}" rx="6" fill="transparent" stroke-width="1" class="border" />
        
        <!-- Icon -->
        <svg x="{bx + 15}" y="{by + 6}" width="24" height="24" viewBox="0 0 24 24" class="icon">
            {icon_svg}
        </svg>
        
        <!-- Text -->
        <text x="{bx + 45}" y="{by + 22}" class="link-text">{link['name']}</text>
        
        <!-- Animated underline that draws in -->
        <rect x="{bx + 10}" y="{by + bh - 2}" width="0" height="2" fill="url(#accent)">
            <animate attributeName="width" from="0" to="{button_width - 20}" begin="{delay}s" dur="0.8s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />
        </rect>
        
        <!-- Interactive Hover Cursor Dot -->
        <circle cx="0" cy="{by + bh - 1}" r="3" fill="{glow_color}" filter="url(#glow)" class="cursor-dot">
            <animate attributeName="cx" values="{bx + 10}; {bx + button_width - 10}; {bx + 10}" dur="3s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1; 0.4 0 0.2 1" />
        </circle>
    </g>
</svg>"""
    return svg

def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out_dir, exist_ok=True)
    
    links = [
        {'id': 'linkedin', 'name': 'LINKEDIN', 'url': 'https://www.linkedin.com/in/moningi-rohit/'},
        {'id': 'github', 'name': 'GITHUB', 'url': 'https://github.com/AYASKA-in'},
        {'id': 'email', 'name': 'EMAIL', 'url': 'mailto:rohitmoningi@gmail.com'},
        {'id': 'portfolio', 'name': 'PORTFOLIO', 'url': 'https://rohitmoningi.in'}
    ]
    
    for theme in ['dark', 'light']:
        for i, link in enumerate(links):
            svg = generate_button(theme, link, i)
            filename = f"social-{link['id']}-{theme}.svg"
            with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
                f.write(svg)
            print(f"Generated {filename}")

if __name__ == '__main__':
    main()
