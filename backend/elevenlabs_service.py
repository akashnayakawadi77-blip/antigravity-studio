import os

def generate_voiceover(text: str, output_path: str) -> str:
    """
    Generates an MP3 voiceover using ElevenLabs API.
    Returns the output file path.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        print("  ⚠️ No ElevenLabs API key set. Skipping voiceover.")
        return None

    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=api_key)

        # Use Rachel voice (warm, clear, enthusiastic)
        # Voice ID: 21m00Tcm4TlvDq8ikWAM = Rachel
        audio_generator = client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            output_format="mp3_44100_128",
            text=text[:4900],  # ElevenLabs limit per request
            model_id="eleven_multilingual_v2",
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)

        print(f"  ✅ Voiceover saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"  ❌ Voiceover generation failed: {e}")
        return None
