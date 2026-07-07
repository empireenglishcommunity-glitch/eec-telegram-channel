"""
Image generation engine — uses HTML templates + HTML2IMG service.
Produces consistent, branded Empire visuals for every post.

Service: empire-html2img (Puppeteer) at http://localhost:3200/convert
Output: 1080x1080 PNG, 2x device scale (2160x2160 actual pixels)
"""
import aiohttp
import os
import random
from templates.pillars import (
    accent_lesson,
    myth_destroyer,
    system_reveal,
    social_proof,
    brand_story,
    invitation,
)
import config

# HTML2IMG service URL (running on same server)
HTML2IMG_URL = "http://localhost:3200/convert"


async def generate_image(pillar: str, post_text: str = "", metadata: dict = None) -> str | None:
    """Generate a branded image using HTML templates + HTML2IMG service."""

    metadata = metadata or {}

    # Build HTML from the appropriate template
    html = _build_template(pillar, post_text, metadata)
    if not html:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                HTML2IMG_URL,
                json={
                    "html": html,
                    "width": 1080,
                    "height": 1080,
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    output_path = f"data/temp_image_{random.randint(1000, 9999)}.png"
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    print(f"  🖼️ Image generated: {output_path} ({len(image_data)} bytes)")
                    return output_path
                else:
                    error_text = await resp.text()
                    print(f"  ⚠️ HTML2IMG returned {resp.status}: {error_text[:200]}")
                    return None

    except aiohttp.ClientConnectorError:
        print("  ⚠️ HTML2IMG service not reachable (is empire-html2img container running?)")
        return None
    except Exception as e:
        print(f"  ⚠️ Image generation error: {e}")
        return None


def _build_template(pillar: str, post_text: str, metadata: dict) -> str | None:
    """Select the right template and fill it with content."""

    if pillar == "accent_lesson":
        topic = metadata.get("image_topic", _extract_english_topic(post_text))
        examples = metadata.get("image_examples", _extract_examples(post_text))
        return accent_lesson(topic, examples)

    elif pillar == "myth_destroyer":
        myth = metadata.get("image_myth", _extract_first_line(post_text))
        return myth_destroyer(myth)

    elif pillar == "system_reveal":
        title = metadata.get("image_title", _extract_arabic_hook(post_text))
        bullets = metadata.get("image_bullets", _extract_bullets(post_text))
        return system_reveal(title, bullets)

    elif pillar == "social_proof":
        stat = metadata.get("image_stat", _extract_number(post_text))
        label = metadata.get("image_label", _extract_arabic_hook(post_text))
        return social_proof(stat, label)

    elif pillar == "brand_story":
        quote = metadata.get("image_quote", _extract_short_quote(post_text))
        return brand_story(quote)

    elif pillar == "invitation":
        cta = metadata.get("image_cta", "ابدأ رحلتك دلوقتي")
        subtitle = metadata.get("image_subtitle", "امتحان مجاني — ٢٠ دقيقة")
        return invitation(cta, subtitle)

    elif pillar == "empire_word":
        # Empire Word uses the accent_lesson template (same visual style)
        topic = metadata.get("image_topic", _extract_english_topic(post_text))
        examples = metadata.get("image_examples", _extract_examples(post_text))
        return accent_lesson(topic, examples)

    return None


# ─── Text extraction helpers ─────────────────────────────────

def _extract_english_topic(text: str) -> str:
    """Extract English topic/sound name from post text."""
    lines = text.split("\n")
    for line in lines:
        # Look for English words in the post (capitalized or technical)
        stripped = line.strip()
        if stripped and any(c.isascii() and c.isalpha() for c in stripped):
            # Find the English part
            words = stripped.split()
            eng_words = [w for w in words if all(c.isascii() or c in "/-()'" for c in w) and len(w) > 1]
            if eng_words:
                return " ".join(eng_words[:4])
    return "American English"


def _extract_examples(text: str) -> list[str]:
    """Extract example words/phrases from post."""
    examples = []
    for line in text.split("\n"):
        stripped = line.strip()
        if "=" in stripped and len(stripped) < 40:
            examples.append(stripped)
        elif stripped.startswith("✅") and len(stripped) < 40:
            examples.append(stripped.replace("✅ ", ""))
    return examples[:4] if examples else None


def _extract_first_line(text: str) -> str:
    """Get the first meaningful line (for myth text)."""
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("💣"):
            # Remove the emoji prefix if any
            for prefix in ["💣", "❌", "✅", "🔥", "🏛️", "👑", "📢", "🎯"]:
                stripped = stripped.replace(prefix, "").strip()
            if len(stripped) > 10:
                return stripped[:60]
    return "Myth"


def _extract_arabic_hook(text: str) -> str:
    """Extract the Arabic hook/title from the post."""
    for line in text.split("\n"):
        stripped = line.strip()
        # Skip emoji-only lines and empty lines
        if stripped and len(stripped) > 10:
            # Remove leading emojis
            for prefix in ["💣", "❌", "✅", "🔥", "🏛️", "👑", "📢", "🎯", "⚡"]:
                stripped = stripped.replace(prefix, "").strip()
            if any("\u0600" <= c <= "\u06FF" for c in stripped):
                return stripped[:80]
    return ""


def _extract_bullets(text: str) -> list[str]:
    """Extract bullet points from post."""
    bullets = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("•") or stripped.startswith("⚡"):
            clean = stripped.lstrip("•⚡ ").strip()
            if clean:
                bullets.append(clean[:50])
    return bullets[:5] if bullets else None


def _extract_number(text: str) -> str:
    """Extract a prominent number from the post."""
    import re
    # Look for numbers (Arabic or Western)
    numbers = re.findall(r'[\d٠-٩]+[,.]?[\d٠-٩]*', text)
    if numbers:
        # Return the largest/most prominent one
        return max(numbers, key=len)
    return "🔥"


def _extract_short_quote(text: str) -> str:
    """Extract a short punchy quote for brand story."""
    lines = text.split("\n")
    # Look for short, punchy Arabic lines
    for line in lines:
        stripped = line.strip()
        for prefix in ["💣", "❌", "✅", "🔥", "🏛️", "👑", "📢", "🎯", "⚡", "━━━"]:
            stripped = stripped.replace(prefix, "").strip()
        if stripped and 15 < len(stripped) < 80 and any("\u0600" <= c <= "\u06FF" for c in stripped):
            return stripped
    # Fallback: first Arabic line
    for line in lines:
        stripped = line.strip()
        if any("\u0600" <= c <= "\u06FF" for c in stripped) and len(stripped) > 10:
            return stripped[:70]
    return "Empire English"
