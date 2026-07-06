"""
Content engine — Bank-Only Mode.
Loads posts from pre-written JSON bank files. No AI generation.
Posts are hand-crafted in perfect Egyptian masri with MACAL brand voice.

Bank structure:
  data/bank/accent_lesson.json
  data/bank/myth_destroyer.json
  data/bank/system_reveal.json
  data/bank/social_proof.json
  data/bank/brand_story.json
  data/bank/invitation.json

Each file is a JSON array of post objects:
  [
    {
      "id": "AL-01",
      "text": "...",
      "image_topic": "The Flap T",
      "image_examples": ["water = wader", "better = bedder"],
      "used_count": 0,
      "last_used": null
    }
  ]
"""
import json
import os
import random
from datetime import datetime

BANK_DIR = "data/bank"


async def generate_post(pillar: str) -> tuple[str | None, dict | None]:
    """
    Get the next post from the bank for the given pillar.
    Returns (post_text, metadata) or (None, None) if bank is empty.
    Metadata is passed to image_engine for template rendering.
    """
    bank_path = os.path.join(BANK_DIR, f"{pillar}.json")

    try:
        with open(bank_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except FileNotFoundError:
        print(f"  ⚠️ Bank file not found: {bank_path}")
        return None, None
    except json.JSONDecodeError:
        print(f"  ⚠️ Bank file corrupted: {bank_path}")
        return None, None

    if not posts:
        print(f"  ⚠️ Bank empty: {bank_path}")
        return None, None

    # Select the least-used post (cycle through evenly)
    posts.sort(key=lambda p: (p.get("used_count", 0), p.get("last_used") or ""))
    selected = posts[0]

    # Update usage tracking
    selected["used_count"] = selected.get("used_count", 0) + 1
    selected["last_used"] = datetime.now().isoformat()

    # Save back
    with open(bank_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    text = selected["text"]
    metadata = {k: v for k, v in selected.items() if k.startswith("image_")}

    print(f"  📄 Bank post: {selected.get('id', '?')} (used {selected['used_count']}x)")
    return text, metadata


async def get_bank_post(pillar: str) -> tuple[str | None, dict | None]:
    """Alias for generate_post (bank-only mode, same thing)."""
    return await generate_post(pillar)


async def generate_weekly_batch():
    """Not needed in bank-only mode."""
    print("  ℹ️ Bank-only mode — no generation needed")
    pass
