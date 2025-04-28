from elevenlabs import save
from elevenlabs.client import ElevenLabs

import config

client = ElevenLabs(
    api_key=config.elevenlabs_api_key,
)


def get_all_voices():
    return client.voices.get_all()


def generate_audio(text: str, voice: str):
    audio = client.generate(
        text=text,
        voice=voice,  # здесь просто ID или имя голоса
        model="eleven_multilingual_v2",
    )
    name = "audio.mp3"
    save(audio, name)
    return name
