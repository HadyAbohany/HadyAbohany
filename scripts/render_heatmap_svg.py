"""
Render a GitHub-style contribution heatmap SVG from data/contributions.json

Output: contrib-heatmap.svg
"""

import json
import os
from datetime import datetime, timedelta

DATA_PATH = os.path.join("data", "contributions.json")
OUTPUT_PATH = "contrib-heatmap.svg"

COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

CELL_SIZE = 11
CELL_GAP = 3
CELL_RADIUS = 2

LEFT_PADDING = 35
TOP_PADDING = 45
BOTTOM_PADDING = 45
RIGHT_PADDING = 15

MONTH_LABELS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_week_grid(days):
    day_map = {d["date"]: d for d in days}

    if not days:
        return []

    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d")

    start = first_date - timedelta(days=(first_date.weekday() + 1) % 7)

    weeks = []
    current = start
    week = []

    while current <= last_date:
        date_str = current.strftime("%Y-%m-%d")
        day = day_map.get(date_str)
        week.append(day)

        if current.weekday() == 5:
            weeks.append(week)
            week = []

        current += timedelta(days=1)

    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    return weeks


def month_label_positions(weeks):
    labels = []
    last_month = None

    for i, week in enumerate(weeks):
        for day in week:
            if day is None:
                continue
            date = datetime.strptime(day["date"], "%Y-%m-%d")
            if date.month != last_month:
                labels.append((i, MONTH_LABELS[date.month - 1]))
                last_month = date.month
            break

    return labels


def render_svg(summary):
    days = summary["days"]
    weeks = build_week_grid(days)
    total = summary["total_contributions"]

    num_weeks = len(weeks)
    width = LEFT_PADDING + num_weeks * (CELL_SIZE + CELL_GAP) + RIGHT_PADDING
    height = TOP_PADDING + 7 * (CELL_SIZE + CELL_GAP) + BOTTOM_PADDING

    svg_parts = []

    # Total time the diagonal reveal takes, used to time the scan sweep after
    max_stagger = (num_weeks + 7) * 0.006
    cell_pop_dur = 0.25
    sweep_begin = round(max_stagger + cell_pop_dur + 0.15, 3)
    sweep_dur = 0.9

    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {width} {height}"
width="{width}"
height="{height}">

<defs>
    <clipPath id="grid-clip">
        <rect x="{LEFT_PADDING}" y="{TOP_PADDING}"
              width="{num_weeks * (CELL_SIZE + CELL_GAP)}"
              height="{7 * (CELL_SIZE + CELL_GAP)}" />
    </clipPath>

    <linearGradient id="sweep-gradient" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#39d353" stop-opacity="0" />
        <stop offset="50%" stop-color="#39d353" stop-opacity="0.35" />
        <stop offset="100%" stop-color="#39d353" stop-opacity="0" />
    </linearGradient>
</defs>

<style>
    .bg {{ fill: #0d1117; }}
    .border {{ fill: none; stroke: #30363d; stroke-width: 1; }}
    .header {{
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        fill: #58a6ff;
        opacity: 0;
        animation: fadeIn 0.5s ease-out forwards;
    }}
    .month-label {{
        font-family: monospace;
        font-size: 10px;
        fill: #8b949e;
    }}
    .weekday-label {{
        font-family: monospace;
        font-size: 9px;
        fill: #8b949e;
    }}
    .legend-label {{
        font-family: monospace;
        font-size: 10px;
        fill: #8b949e;
    }}
    .day-cell {{
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        animation-name: popIn;
        animation-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1);
        animation-fill-mode: forwards;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}

    @keyframes popIn {{
        0% {{
            opacity: 0;
            transform: scale(0.3);
        }}
        100% {{
            opacity: 1;
            transform: scale(1);
        }}
    }}
</style>

<rect x="0" y="0" width="100%" height="100%" rx="10" class="bg" />
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" class="border" />

<text x="15" y="24" class="header">{total} contributions in the last year</text>
''')

    for week_index, label in month_label_positions(weeks):
        x = LEFT_PADDING + week_index * (CELL_SIZE + CELL_GAP)
        svg_parts.append(
            f'<text x="{x}" y="{TOP_PADDING - 8}" class="month-label">{label}</text>'
        )

    for weekday_index, label in WEEKDAY_LABELS.items():
        y = TOP_PADDING + weekday_index * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 2
        svg_parts.append(
            f'<text x="0" y="{y}" class="weekday-label">{label}</text>'
        )

    for week_index, week in enumerate(weeks):
        for weekday_index, day in enumerate(week):
            x = LEFT_PADDING + week_index * (CELL_SIZE + CELL_GAP)
            y = TOP_PADDING + weekday_index * (CELL_SIZE + CELL_GAP)

            level = day["level"] if day else 0
            color = COLORS.get(level, COLORS[0])

            delay = round((week_index + weekday_index) * 0.006, 3)

            title = ""
            if day:
                title = f'<title>{day["count"]} contributions on {day["date"]}</title>'

            svg_parts.append(
                f'<rect class="day-cell" x="{x}" y="{y}" '
                f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{CELL_RADIUS}" '
                f'fill="{color}" '
                f'style="animation-duration: {cell_pop_dur}s; '
                f'animation-delay: {delay}s;">'
                f'{title}'
                f'</rect>'
            )

    # One-time scan sweep across the grid after cells finish popping in
    sweep_width = 60
    grid_left = LEFT_PADDING
    grid_right = LEFT_PADDING + num_weeks * (CELL_SIZE + CELL_GAP)
    grid_top = TOP_PADDING
    grid_bottom = TOP_PADDING + 7 * (CELL_SIZE + CELL_GAP)

    svg_parts.append(f'''
<g clip-path="url(#grid-clip)">
    <rect
        x="{grid_left - sweep_width}"
        y="{grid_top}"
        width="{sweep_width}"
        height="{grid_bottom - grid_top}"
        fill="url(#sweep-gradient)"
    >
        <animate
            attributeName="x"
            from="{grid_left - sweep_width}"
            to="{grid_right}"
            begin="{sweep_begin}s"
            dur="{sweep_dur}s"
            fill="freeze"
            calcMode="spline"
            keySplines="0.4 0 0.2 1"
        />
    </rect>
</g>
''')

    # Legend
    legend_y = height - 20
    legend_x = width - RIGHT_PADDING - (5 * (CELL_SIZE + 4)) - 60

    svg_parts.append(
        f'<text x="{legend_x - 35}" y="{legend_y + 9}" class="legend-label">Less</text>'
    )

    for i, level in enumerate(sorted(COLORS.keys())):
        x = legend_x + i * (CELL_SIZE + 4)
        svg_parts.append(
            f'<rect x="{x}" y="{legend_y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="{CELL_RADIUS}" fill="{COLORS[level]}" />'
        )

    legend_more_x = legend_x + 5 * (CELL_SIZE + 4) + 6
    svg_parts.append(
        f'<text x="{legend_more_x}" y="{legend_y + 9}" class="legend-label">More</text>'
    )

    svg_parts.append("\n</svg>\n")

    return "".join(svg_parts)


def main():
    summary = load_data()
    svg = render_svg(summary)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"✅ Created {OUTPUT_PATH}")


if __name__ == "__main__":
    main()