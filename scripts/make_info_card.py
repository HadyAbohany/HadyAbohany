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

    # escape XML-special characters (&, <, >) in every value
    # so raw "&" (like in "Systems & Computers Engineering")
    # doesn't break the SVG's XML parsing on GitHub
    lines = [(key, escape(value)) for key, value in lines]
    safe_name = escape(name)

    width = 490
    height = 330

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

    for i, (key, value) in enumerate(lines):

        y = start_y + i * 27
        delay = round(i * 0.12, 2)
        dur = 0.45

        svg += f'''
<g opacity="0">

    <animate
        attributeName="opacity"
        from="0"
        to="1"
        begin="{delay}s"
        dur="{dur}s"
        fill="freeze"
    />

    <animateTransform
        attributeName="transform"
        type="translate"
        from="-8 0"
        to="0 0"
        begin="{delay}s"
        dur="{dur}s"
        fill="freeze"
    />

    <text
        x="25"
        y="{y}"
        class="key"
    >{key}:</text>

    <text
        x="125"
        y="{y}"
        class="value"
    >{value}</text>

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