import os
from xml.sax.saxutils import escape


def make_info_card(output="info-card.svg"):

    name = "Hady Abohany"
    role = "AI Engineer"
    focus = "RAG • LLMs • AI Agents"
    stack = "Python • LangChain • FastAPI"
    databases = "PostgreSQL • ChromaDB"
    current = "Building AI systems"
    education = "Systems & Computers Engineering"

    lines = [
        ("name", name),
        ("role", role),
        ("focus", focus),
        ("stack", stack),
        ("db", databases),
        ("current", current),
        ("education", education),
    ]

    lines = [(key, escape(value)) for key, value in lines]
    safe_name = escape(name)

    width = 490
    height = 330

    # Monospace char width approximation at font-size 14px
    CHAR_W = 8.6

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {width} {height}"
width="{width}"
height="{height}">

<style>

    .bg {{
        fill: #0d1117;
    }}

    .border {{
        fill: none;
        stroke: #30363d;
        stroke-width: 1;
    }}

    .title {{
        font-family: monospace;
        font-size: 15px;
        font-weight: bold;
        fill: #58a6ff;
    }}

    .key {{
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        fill: #79c0ff;
        opacity: 0;
        animation: keyIn 0.3s ease-out forwards;
    }}

    .value {{
        font-family: monospace;
        font-size: 14px;
        fill: #8b949e;
    }}

    .prompt {{
        font-family: monospace;
        font-size: 13px;
        fill: #7ee787;
    }}

    .cursor {{
        fill: #7ee787;
    }}

    @keyframes keyIn {{
        from {{
            opacity: 0;
            transform: translateX(-6px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
    }}

</style>

<rect
    x="0"
    y="0"
    width="100%"
    height="100%"
    rx="10"
    class="bg"
/>

<rect
    x="0.5"
    y="0.5"
    width="489"
    height="329"
    rx="10"
    class="border"
/>

<!-- Terminal header -->

<circle cx="18" cy="18" r="5" fill="#ff5f56"/>
<circle cx="35" cy="18" r="5" fill="#ffbd2e"/>
<circle cx="52" cy="18" r="5" fill="#27c93f"/>

<text
    x="75"
    y="23"
    class="title"
>hady@github ~</text>

<!-- Prompt -->

<text
    x="25"
    y="58"
    class="prompt"
>$ whoami</text>

<text
    x="25"
    y="86"
    class="title"
>{safe_name}</text>
'''

    start_y = 120
    row_gap = 27

    # Typing timeline: rows start one after another, each value
    # types out over `type_dur`, cursor blinks briefly then hides.
    row_start_gap = 0.45
    type_dur = 0.35
    cursor_blink_dur = 0.4
    cursor_blinks = 2

    for i, (key, value) in enumerate(lines):

        y = start_y + i * row_gap
        row_start = round(0.15 + i * row_start_gap, 3)
        key_delay = row_start
        type_begin = round(row_start + 0.12, 3)

        text_width = len(value) * CHAR_W + 4
        cursor_x = 125 + text_width

        cursor_visible_dur = cursor_blink_dur * cursor_blinks

        svg += f'''
<g>

    <text
        x="25"
        y="{y}"
        class="key"
        style="animation-delay: {key_delay}s;"
    >{key}:</text>

    <clipPath id="clip-value-{i}">
        <rect x="120" y="{y - 14}" width="0" height="18">
            <animate
                attributeName="width"
                from="0"
                to="{text_width + 10}"
                begin="{type_begin}s"
                dur="{type_dur}s"
                fill="freeze"
                calcMode="linear"
            />
        </rect>
    </clipPath>

    <text
        x="125"
        y="{y}"
        class="value"
        clip-path="url(#clip-value-{i})"
    >{value}</text>

    <rect
        x="{cursor_x:.1f}"
        y="{y - 12}"
        width="2"
        height="14"
        class="cursor"
        opacity="0"
    >
        <animate
            attributeName="opacity"
            begin="{type_begin + type_dur}s"
            dur="{cursor_blink_dur}s"
            values="0;1;0;1;0"
            keyTimes="0;0.25;0.5;0.75;1"
            repeatCount="{cursor_blinks}"
            fill="freeze"
        />
    </rect>

</g>
'''

    svg += '''
</svg>
'''

    with open(output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Created {output}")


if __name__ == "__main__":
    make_info_card()