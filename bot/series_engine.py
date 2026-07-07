"""
Series engine — handles multi-part posts (Part 1/3 → 2/3 → 3/3).
When a series starts, it overrides the normal pillar schedule for consecutive days.
"""
import json
import os
import glob
from datetime import datetime

SERIES_DIR = "data/bank/series"
STATE_FILE = "data/series_state.json"


def get_series_state() -> dict:
    """Load current series state (are we mid-series?)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"active": False}


def save_series_state(state: dict):
    """Save series state."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


async def get_series_post() -> tuple[str | None, dict | None]:
    """
    Check if we're mid-series or should start a new one.
    Returns (post_text, metadata) or (None, None) if no series active.
    """
    state = get_series_state()

    if state.get("active"):
        # We're mid-series — post the next part
        return _get_next_part(state)
    else:
        # Check if it's time to start a new series
        # Start a series every 2 weeks (on Wednesday)
        today = datetime.now()
        if today.weekday() != 2:  # Only start on Wednesday
            return None, None

        week_num = today.isocalendar()[1]
        if week_num % 2 != 0:  # Only even weeks
            return None, None

        # Check if we already started one this cycle
        last_started = state.get("last_started_week", 0)
        if last_started == week_num:
            return None, None

        # Start a new series
        return _start_new_series(week_num)


def _start_new_series(week_num: int) -> tuple[str | None, dict | None]:
    """Pick and start a new series."""
    series_files = glob.glob(os.path.join(SERIES_DIR, "*.json"))
    if not series_files:
        return None, None

    # Load all series and pick least-used
    all_series = []
    for f_path in series_files:
        with open(f_path, "r", encoding="utf-8") as f:
            series = json.load(f)
            series["_path"] = f_path
            all_series.append(series)

    all_series.sort(key=lambda s: s.get("used_count", 0))
    selected = all_series[0]

    # Get Part 1
    part_1 = selected["parts"][0]

    # Save state: we're now mid-series
    state = {
        "active": True,
        "series_id": selected["id"],
        "series_path": selected["_path"],
        "current_part": 1,
        "total_parts": selected["total_parts"],
        "last_started_week": week_num,
    }
    save_series_state(state)

    print(f"  📚 Series started: {selected['title']} (Part 1/{selected['total_parts']})")
    return part_1["text"], {}


def _get_next_part(state: dict) -> tuple[str | None, dict | None]:
    """Get the next part of an active series."""
    series_path = state.get("series_path")
    current_part = state.get("current_part", 1)
    total_parts = state.get("total_parts", 3)

    if not series_path or not os.path.exists(series_path):
        # Series file gone — reset state
        save_series_state({"active": False, "last_started_week": state.get("last_started_week", 0)})
        return None, None

    with open(series_path, "r", encoding="utf-8") as f:
        series = json.load(f)

    next_part_num = current_part + 1

    if next_part_num > total_parts:
        # Series complete — mark as used and reset
        series["used_count"] = series.get("used_count", 0) + 1
        series["last_used"] = datetime.now().isoformat()
        with open(series_path, "w", encoding="utf-8") as f:
            json.dump(series, f, ensure_ascii=False, indent=2)

        save_series_state({"active": False, "last_started_week": state.get("last_started_week", 0)})
        print(f"  📚 Series complete: {series['id']}")
        return None, None

    # Get next part
    part = series["parts"][next_part_num - 1]

    # Update state
    state["current_part"] = next_part_num
    save_series_state(state)

    print(f"  📚 Series: {series['id']} — Part {next_part_num}/{total_parts}")
    return part["text"], {}
