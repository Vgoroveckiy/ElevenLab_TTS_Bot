from elevenlabs import save
from elevenlabs.client import ElevenLabs

import config
import uuid  # добавлено для генерации уникальных имен файлов

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
    # Генерируем уникальное имя файла
    name = f"audio_{uuid.uuid4().hex}.mp3"
    save(audio, name)
    return name
