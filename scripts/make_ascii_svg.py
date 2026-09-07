import cv2
import html


def convert_to_ascii_svg(
    image_path="source-prepped.png",
    output_svg="avi-ascii.svg"
):
    print("⏳ Converting image to animated ASCII SVG...")

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print(
            "❌ Could not find source-prepped.png. "
            "Run prep_photo.py first."
        )
        return

    # ASCII grid
    cols = 90
    rows = 50

    resized = cv2.resize(img, (cols, rows))

    # Bright → sparse
    # Dark → dense
    RAMP = " .`:-=+*cs#%@"

    char_width = 8
    char_height = 14

    width = cols * char_width + 20
    height = rows * char_height + 40

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {width} {height}"
width="{width}"
height="{height}">

<style>
    .bg {{
        fill: #0d1117;
    }}

    .txt {{
        font-family: "Courier New", monospace;
        font-size: 12px;
        fill: #8b949e;
        opacity: 0;
    }}

    @keyframes fadeIn {{
        from {{
            opacity: 0;
        }}
        to {{
            opacity: 1;
        }}
    }}
</style>

<rect
    width="100%"
    height="100%"
    class="bg"
    rx="8"
/>

<g transform="translate(10, 25)">
'''

    for i in range(rows):

        row_chars = []

        for j in range(cols):

            value = resized[i, j]

            index = int(
                (value / 255.0) * (len(RAMP) - 1)
            )

            char = RAMP[index]

            # SVG/XML-safe text
            if char == " ":
                char = "&#160;"
            else:
                char = html.escape(char)

            row_chars.append(char)

        row = "".join(row_chars)

        delay = i * 0.035

        svg += f'''
    <text
        x="0"
        y="{i * char_height}"
        class="txt"
        style="
            animation: fadeIn 0.35s ease-out forwards;
            animation-delay: {delay:.3f}s;
        "
    >{row}</text>
'''

    svg += '''
</g>
</svg>
'''

    with open(output_svg, "w", encoding="utf-8") as file:
        file.write(svg)

    print(
        f"✅ ASCII SVG created successfully: {output_svg}"
    )


if __name__ == "__main__":
    convert_to_ascii_svg()