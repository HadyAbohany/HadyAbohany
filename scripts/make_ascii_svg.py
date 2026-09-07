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

    # Sparse → Dense
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
        fill: #c9d1d9;
    }}
</style>

<rect
    width="100%"
    height="100%"
    class="bg"
    rx="8"
/>

<defs>
'''

    row_start_delay = 0.05    # gap between when each row starts typing
    row_type_dur = 0.28       # how long a single row takes to fully type

    rows_svg = []

    for i in range(rows):

        row_chars = []

        for j in range(cols):

            value = resized[i, j]

            # Dark pixel (face/hair details) → dense char
            # Bright pixel (white background) → space (invisible)
            index = int(
                ((255 - value) / 255.0) * (len(RAMP) - 1)
            )

            char = RAMP[index]

            # SVG/XML-safe text
            if char == " ":
                char = "&#160;"
            else:
                char = html.escape(char)

            row_chars.append(char)

        row = "".join(row_chars)

        delay = round(i * row_start_delay, 3)
        y = i * char_height

        # clipPath grows left → right, revealing the row like typing
        svg += f'''
    <clipPath id="clip-row-{i}">
        <rect x="0" y="{y - char_height + 3}" width="0" height="{char_height}">
            <animate
                attributeName="width"
                from="0"
                to="{width}"
                begin="{delay}s"
                dur="{row_type_dur}s"
                fill="freeze"
                calcMode="linear"
            />
        </rect>
    </clipPath>
'''

        rows_svg.append(
            f'    <text x="0" y="{y}" class="txt" '
            f'clip-path="url(#clip-row-{i})">{row}</text>'
        )

    svg += '''
</defs>

<g transform="translate(10, 25)">
'''

    svg += "\n".join(rows_svg)

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