"""
Image generation engine — uses Cloudflare Workers AI (FLUX.1 Schnell).
Free tier: 10,000 neurons/day (we use ~1 image/day = well within limits).
"""
import aiohttp
import config
import os
import random

# Image prompts per pillar
PILLAR_IMAGE_PROMPTS = {
    "accent_lesson": [
        "Abstract sound wave visualization with gold (#D4AF37) particles on dark background (#0A0A0F). Professional educational feel. Mouth or tongue position hint. Square format.",
        "Minimal gold (#D4AF37) waveform transforming shape on matte black (#0A0A0F) background. Premium educational aesthetic. No text. Square.",
        "Gold (#D4AF37) particles forming speech pattern on dark (#0A0A0F) background. Professional, clean, abstract phonetics concept. Square.",
    ],
    "myth_destroyer": [
        "Shattered glass or broken chains in gold (#D4AF37) on dark background (#0A0A0F). Freedom from wrong beliefs concept. Bold, powerful. Square.",
        "Gold (#D4AF37) hammer striking a cracked surface on dark (#0A0A0F) background. Myth-breaking concept. Professional, dramatic. Square.",
        "Explosion of gold (#D4AF37) shards on matte black (#0A0A0F). Breaking through barriers. Powerful, minimal, premium. Square.",
    ],
    "system_reveal": [
        "Clean system diagram with gold (#D4AF37) connected nodes on dark background (#0A0A0F). Technology meets education. Professional network visualization. Square.",
        "Gold (#D4AF37) gears and circuits on dark (#0A0A0F) background. System architecture concept. Premium, minimal, professional. Square.",
        "Blueprint-style grid with gold (#D4AF37) highlights on dark (#0A0A0F) background. Engineering precision. Clean, professional. Square.",
    ],
    "social_proof": [
        "Upward trending chart with gold (#D4AF37) gradient on dark background (#0A0A0F). Achievement and progress concept. Premium, celebratory. Square.",
        "Gold (#D4AF37) trophy or star rising on dark (#0A0A0F) background. Success and achievement. Professional, aspirational. Square.",
        "Growth visualization with gold (#D4AF37) ascending steps on dark (#0A0A0F). Progress milestone. Clean, motivational. Square.",
    ],
    "brand_story": [
        "Crown or empire pillars in gold (#D4AF37) on matte black (#0A0A0F). Royal, powerful brand identity. Premium luxury feel. Square.",
        "Golden (#D4AF37) gate opening with light streaming through on dark (#0A0A0F) background. Invitation to something exclusive. Square.",
        "Gold (#D4AF37) lion or eagle silhouette on dark (#0A0A0F) background. Empire, power, authority. Minimal, premium. Square.",
    ],
}


async def generate_image(pillar: str, post_text: str = "") -> str | None:
    """Generate a branded image for a channel post."""
    if not config.CLOUDFLARE_ACCOUNT_ID or not config.CLOUDFLARE_API_TOKEN:
        return None

    prompts = PILLAR_IMAGE_PROMPTS.get(pillar, PILLAR_IMAGE_PROMPTS["accent_lesson"])
    prompt = random.choice(prompts)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.cloudflare.com/client/v4/accounts/{config.CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell",
                headers={
                    "Authorization": f"Bearer {config.CLOUDFLARE_API_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024,
                    "num_steps": 4,
                },
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status == 200:
                    # Response is raw image bytes
                    image_data = await resp.read()
                    output_path = f"data/temp_image_{random.randint(1000,9999)}.png"
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    print(f"  🖼️ Image generated: {output_path}")
                    return output_path
                else:
                    error_text = await resp.text()
                    print(f"  ⚠️ Cloudflare AI returned {resp.status}: {error_text[:200]}")
                    return None

    except Exception as e:
        print(f"  ⚠️ Image generation error: {e}")
        return None
