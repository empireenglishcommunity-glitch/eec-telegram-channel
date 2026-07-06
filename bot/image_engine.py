"""
Image generation engine — uses Cloudflare Workers AI (FLUX.1 Schnell).
Free tier: 10,000 neurons/day (we use ~1 image/day = well within limits).
"""
import aiohttp
import config
import os
import random

# Image prompts per pillar — STRONG EMPIRE BRAND VISUALS
# Style: Ultra-premium, gold on black, powerful, dominant, cinematic
PILLAR_IMAGE_PROMPTS = {
    "accent_lesson": [
        "Cinematic close-up of golden sound waves emanating from a human mouth silhouette, deep black background, gold metallic particles, volumetric lighting, 8k quality, ultra premium luxury brand aesthetic, dramatic, powerful",
        "Majestic golden microphone with sound waves rippling outward, matte black background, cinematic gold lighting, luxury brand photography, bokeh gold particles floating, epic dramatic atmosphere",
        "Golden tongue and lips diagram glowing with energy, dark cinematic background with gold dust particles, premium educational brand, dramatic lighting, hyper-detailed, powerful",
    ],
    "myth_destroyer": [
        "Dramatic golden hammer shattering a glass wall into a thousand pieces, matte black background, cinematic explosion of gold shards, volumetric lighting, epic powerful moment, 8k quality, luxury brand",
        "Golden chains breaking apart with explosive force, dramatic dark background, sparks and gold particles flying, cinematic lighting, powerful liberation concept, ultra premium aesthetic",
        "Massive golden fist punching through a dark wall, debris and gold particles exploding outward, volumetric god rays, cinematic dramatic moment, luxury brand photography, epic powerful",
    ],
    "system_reveal": [
        "Futuristic golden holographic interface floating in dark space, circuit patterns and data streams in gold, black background, cinematic sci-fi aesthetic, premium technology brand, ultra detailed 8k",
        "Majestic golden clockwork mechanism with interconnected gears, dark matte background, dramatic lighting revealing precision engineering, luxury brand aesthetic, cinematic, powerful",
        "Golden neural network visualization with glowing nodes and connections, deep black space background, premium tech aesthetic, dramatic volumetric lighting, 8k ultra detailed",
    ],
    "social_proof": [
        "Dramatic golden trophy on a pedestal with volumetric light beams streaming down, dark cinematic background, gold particles rising, victory and achievement concept, ultra premium luxury brand, epic",
        "Golden arrow chart breaking through a ceiling with explosive force, dark background, gold sparks and particles, dramatic upward momentum, premium brand photography, powerful cinematic",
        "Majestic golden crown floating with energy radiating outward, dark matte background, volumetric gold lighting, royalty and achievement, ultra premium luxury aesthetic, cinematic dramatic",
    ],
    "brand_story": [
        "Epic golden empire gates slowly opening with blinding light streaming through, dark dramatic atmosphere, massive pillars, gold particles in the air, cinematic luxury brand, powerful royal aesthetic, 8k",
        "Majestic golden lion head with flowing mane, dark cinematic background, volumetric gold lighting, power and authority symbol, ultra premium luxury brand, hyper-detailed, dramatic",
        "Golden throne room with dramatic lighting, massive pillars, rich dark atmosphere, gold accents everywhere, empire and power aesthetic, cinematic luxury brand photography, epic scale",
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
                    "num_steps": 8,
                },
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    output_path = f"data/temp_image_{random.randint(1000,9999)}.png"

                    if "image/" in content_type:
                        # Direct image bytes
                        image_data = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(image_data)
                    else:
                        # JSON response with base64 image
                        import base64
                        data = await resp.json()
                        if "result" in data and "image" in data["result"]:
                            image_b64 = data["result"]["image"]
                            image_data = base64.b64decode(image_b64)
                            with open(output_path, "wb") as f:
                                f.write(image_data)
                        elif isinstance(data, dict) and "image" in data:
                            image_b64 = data["image"]
                            image_data = base64.b64decode(image_b64)
                            with open(output_path, "wb") as f:
                                f.write(image_data)
                        else:
                            print(f"  ⚠️ Unexpected response format: {str(data)[:200]}")
                            return None

                    print(f"  🖼️ Image generated: {output_path}")
                    return output_path
                else:
                    error_text = await resp.text()
                    print(f"  ⚠️ Cloudflare AI returned {resp.status}: {error_text[:200]}")
                    return None

    except Exception as e:
        print(f"  ⚠️ Image generation error: {e}")
        return None
