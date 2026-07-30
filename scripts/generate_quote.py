import sys
import os

QUOTES = [
    "> First, solve the problem. Then, write the code.",
    "> Building the future, one commit at a time.",
    "> AI-powered developer. Cloud-native builder.",
    "> Open source contributor. IEEE researcher."
]

def generate_svg(theme='dark'):
    if theme == 'dark':
        bg_color = "#0A101F"
        titlebar_color = "#0B1222"
        text_color = "#F8FAFC"
        prompt_color = "#22D3EE"
        cursor_color = "#22D3EE"
        border_color = "rgba(34,211,238,0.3)"
    else:
        bg_color = "#F8FAFC"
        titlebar_color = "#E2E8F0"
        text_color = "#0F172A"
        prompt_color = "#0891B2"
        cursor_color = "#0891B2"
        border_color = "rgba(8,145,178,0.3)"

    width = 1180
    height = 100
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" fill="{bg_color}" rx="8" stroke="{border_color}" stroke-width="2"/>
    <!-- Title bar -->
    <rect width="{width}" height="30" fill="{titlebar_color}" rx="8"/>
    <!-- Flat bottom for title bar -->
    <rect width="{width}" height="15" y="15" fill="{titlebar_color}"/>
    
    <!-- Traffic lights -->
    <circle cx="20" cy="15" r="6" fill="#ff5f56"/>
    <circle cx="40" cy="15" r="6" fill="#ffbd2e"/>
    <circle cx="60" cy="15" r="6" fill="#27c93f"/>
    
    <!-- Title -->
    <text x="{width/2}" y="20" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" font-size="12" fill="{text_color}" text-anchor="middle" opacity="0.7">rohit@ayaska — ~/quotes</text>
    
    <!-- Border between title and body -->
    <line x1="0" y1="30" x2="{width}" y2="30" stroke="{border_color}" stroke-width="1"/>
    
    <g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" font-size="16" fill="{text_color}">
'''
    
    for i, quote in enumerate(QUOTES):
        start_time = i * 6
        
        char_width = 9.6
        quote_width = len(quote) * char_width
        
        formatted_quote = quote.replace(">", f'<tspan fill="{prompt_color}">&gt;</tspan>')
        
        # 0-3s type, 3-5.5s hold, 5.5-6s fade out
        svg += f'''
        <g opacity="0">
            <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.01;{5.5/24};{6/24};1" begin="{start_time}s" dur="24s" repeatCount="indefinite" />
            
            <clipPath id="clip-{i}-{theme}">
                <rect x="15" y="45" height="30" width="0">
                    <animate attributeName="width" values="0;{quote_width+20};{quote_width+20}" keyTimes="0;{3/24};1" begin="{start_time}s" dur="24s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1; 0 0 1 1" />
                </rect>
            </clipPath>
            
            <g clip-path="url(#clip-{i}-{theme})">
                <text x="20" y="70">{formatted_quote}</text>
            </g>
            
            <!-- Cursor for this quote -->
            <text y="70" fill="{cursor_color}">█
                <animate attributeName="x" values="20;{20 + quote_width};{20 + quote_width}" keyTimes="0;{3/24};1" begin="{start_time}s" dur="24s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1; 0 0 1 1" />
                <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
            </text>
        </g>
'''
        
    svg += f'''
    </g>
</svg>
'''
    return svg

def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out_dir, exist_ok=True)
    
    dark_svg = generate_svg('dark')
    light_svg = generate_svg('light')
    
    with open(os.path.join(out_dir, 'quote-dark.svg'), 'w', encoding='utf-8') as f:
        f.write(dark_svg)
        
    with open(os.path.join(out_dir, 'quote-light.svg'), 'w', encoding='utf-8') as f:
        f.write(light_svg)
        
    print(f"Generated quote SVGs in {out_dir}")

if __name__ == '__main__':
    main()
