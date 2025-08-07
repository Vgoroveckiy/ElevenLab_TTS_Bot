import telebot
from telebot import types

import config
import voice

API_KEY = config.bot_token

bot = telebot.TeleBot(API_KEY)

# Словарь для хранения выбранного голоса для каждого пользователя
user_voice_selection = {}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    voices = voice.get_all_voices()

    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(
        row_width=4, one_time_keyboard=True, resize_keyboard=True
    )

    buttons = [
        types.KeyboardButton(v.name) for v in voices.voices if v.name is not None
    ]
    markup.add(*buttons)  # добавляем все кнопки сразу с нужной разбивкой по рядам

    bot.send_message(
        message.chat.id,
        "Привет! Я бот для озвучивания текста.\nВыбери голос, который будет использоваться для озвучки:",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Обработчик для любых сообщений от пользователя.


    Он может быть вызван:
    - при выборе голоса;
    - при отправке текста для озвучки;
    - при выборе действия после отправки озвученного текста.


    В зависимости от типа сообщения он:
    - Проверяет, что пользователь выбрал голос;
    - Озвучивает текст;
    - Предлагает выбор — сменить голос, озвучить еще текст или отправить голосовое сообщение.
    """
    chat_id = message.chat.id

    if chat_id not in user_voice_selection:
        # Проверяем, что пользователь выбрал голос
        selected_voice_name = message.text
        voices = voice.get_all_voices()
        selected_voice = next(
            (v for v in voices.voices if v.name == selected_voice_name), None
        )
        if selected_voice:
            user_voice_selection[chat_id] = selected_voice
            bot.send_message(
                chat_id,
                f"Отлично, Вы выбрали голос {selected_voice.name}. Теперь отправьте текст, который нужно озвучить.",
                reply_markup=types.ReplyKeyboardRemove(),
            )
        else:
            bot.send_message(chat_id, "Пожалуйста, выберите голос из списка кнопок.")
    elif message.text in ["🔄 Сменить голос", "✍ Озвучить ещё текст"]:
        if message.text == "🔄 Сменить голос":
            # Сбросить выбранный голос
            user_voice_selection.pop(chat_id, None)
            send_welcome(message)  # отправляем снова выбор голосов
        elif message.text == "✍ Озвучить ещё текст":
            bot.send_message(chat_id, "Отправьте новый текст для озвучивания:")
    else:
        # Голос выбран, обрабатываем текст
        selected_voice = user_voice_selection[chat_id]
        text = message.text

        bot.send_message(chat_id, "Генерирую аудио, подождите секунду...")

        audio_path = voice.generate_audio(text, selected_voice.voice_id)

        # Отправляем аудио как голосовое сообщение
        with open(audio_path, "rb") as audio_file:
            bot.send_voice(
                message.chat.id, audio_file, caption="Ваше озвученное сообщение 🎤"
            )

        # После отправки — предлагаем выбор
        markup = types.ReplyKeyboardMarkup(
            row_width=2, one_time_keyboard=True, resize_keyboard=True
        )
        markup.add(
            types.KeyboardButton("🔄 Сменить голос"),
            types.KeyboardButton("✍ Озвучить ещё текст"),
        )

        bot.send_message(
            chat_id,
            "Что хотите сделать дальше?",
            reply_markup=markup,
        )


if __name__ == "__main__":
    bot.polling(non_stop=True)
