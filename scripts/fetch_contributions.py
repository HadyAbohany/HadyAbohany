"""
Fetch public GitHub contribution calendar data (no PAT required)
by scraping the public contributions HTML fragment GitHub serves
to render the profile heatmap.

Output: data/contributions.json
"""

import json
import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = "HadyAbohany"
CONTRIB_URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_PATH = os.path.join("data", "contributions.json")


def fetch_html(url: str) -> str:
    headers = {
        # GitHub serves the plain contributions fragment better
        # with a normal browser-like User-Agent.
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_contributions(html: str):
    soup = BeautifulSoup(html, "html.parser")

    days = []

    # GitHub renders each day as a <td> with class "ContributionCalendar-day"
    cells = soup.select("td.ContributionCalendar-day")

    if not cells:
        # Fallback for older markup: <rect> based calendar
        cells = soup.select("rect.ContributionCalendar-day")

    for cell in cells:
        date = cell.get("data-date")
        level_raw = cell.get("data-level")

        if not date:
            continue

        # data-count can appear in the accessible tooltip text instead
        count = 0
        tooltip_id = cell.get("id")
        if tooltip_id:
            tooltip = soup.find("tool-tip", attrs={"for": tooltip_id})
            if tooltip:
                text = tooltip.get_text(strip=True)
                count = extract_count_from_text(text)

        level = int(level_raw) if level_raw is not None else 0

        days.append({
            "date": date,
            "count": count,
            "level": level,
        })

    days.sort(key=lambda d: d["date"])
    return days


def extract_count_from_text(text: str) -> int:
    """
    Tooltip text looks like:
    "No contributions on January 1st."
    "3 contributions on March 4th."
    """
    text = text.strip()
    if text.lower().startswith("no contributions"):
        return 0

    parts = text.split(" ")
    if parts and parts[0].isdigit():
        return int(parts[0])

    return 0


def compute_streaks(days):
    current_streak = 0
    longest_streak = 0
    running = 0

    for day in days:
        if day["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # current streak = consecutive active days counting back from today
    for day in reversed(days):
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    return current_streak, longest_streak


def compute_monthly_totals(days):
    totals = {}
    for day in days:
        month_key = day["date"][:7]  # YYYY-MM
        totals[month_key] = totals.get(month_key, 0) + day["count"]
    return totals


def compute_best_day(days):
    if not days:
        return None
    best = max(days, key=lambda d: d["count"])
    if best["count"] == 0:
        return None
    return best


def build_summary(days):
    total_contributions = sum(d["count"] for d in days)
    current_streak, longest_streak = compute_streaks(days)
    monthly_totals = compute_monthly_totals(days)
    best_day = compute_best_day(days)

    return {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "days": days,
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")

    try:
        html = fetch_html(CONTRIB_URL)
    except requests.RequestException as e:
        print(f"❌ Failed to fetch contributions page: {e}")
        sys.exit(1)

    days = parse_contributions(html)

    if not days:
        print("❌ No contribution cells found. GitHub markup may have changed.")
        sys.exit(1)

    summary = build_summary(days)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(days)} days to {OUTPUT_PATH}")
    print(f"   Total contributions: {summary['total_contributions']}")
    print(f"   Current streak: {summary['current_streak']} days")
    print(f"   Longest streak: {summary['longest_streak']} days")


if __name__ == "__main__":
    main()