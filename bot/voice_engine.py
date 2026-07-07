"""
Voice engine — generates pronunciation audio via Kokoro TTS.
Sends a voice note to the channel after accent lesson posts (Saturday).

Kokoro TTS API: http://localhost:8880/v1/audio/speech (OpenAI-compatible)
Voice: af_heart (female, warm, professional American English)
"""
import aiohttp
import os
import random
import config


async def generate_voice_note(post_text: str, metadata: dict) -> str | None:
    """Generate a pronunciation voice note from the post's examples."""

    # Extract what to speak from metadata or post
    examples = metadata.get("image_examples", [])
    topic = metadata.get("image_topic", "")

    if not examples and not topic:
        return None

    # Build the speech text — demonstrate the pronunciations
    speech_parts = []
    if topic:
        speech_parts.append(f"Today's sound: {topic}.")
        speech_parts.append("Listen carefully.")

    for ex in examples[:4]:
        # Clean up the example (remove = signs and quotes)
        clean = ex.replace("=", "...").replace('"', '').replace("≠", "... not ...")
        speech_parts.append(clean)

    if not speech_parts:
        return None

    speech_text = " ... ".join(speech_parts)

    # Call Kokoro TTS
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.KOKORO_URL}/v1/audio/speech",
                json={
                    "model": "kokoro",
                    "input": speech_text,
                    "voice": "af_heart",
                    "response_format": "mp3",
                    "speed": 0.85,
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    output_path = f"data/voice_{random.randint(1000,9999)}.mp3"
                    with open(output_path, "wb") as f:
                        f.write(audio_data)
                    print(f"  🎧 Voice note generated: {output_path} ({len(audio_data)} bytes)")
                    return output_path
                else:
                    error = await resp.text()
                    print(f"  ⚠️ Kokoro returned {resp.status}: {error[:100]}")
                    return None

    except aiohttp.ClientConnectorError:
        print("  ⚠️ Kokoro TTS not reachable (container might be stopped)")
        return None
    except Exception as e:
        print(f"  ⚠️ Voice generation error: {e}")
        return None
