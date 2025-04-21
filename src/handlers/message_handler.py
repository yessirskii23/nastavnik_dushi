import logging
import openai
from aiogram import types
from src.services.openai_service import generate_response
from src.utils.helpers import has_access

# Системный промпт для духовного наставника
SYSTEM_PROMPT = (
    "Ты — Наставник Души, мудрый и доброжелательный проводник в мире духовности. "
    "Ты всегда готов поддержать и направить, делясь знаниями о медитации, самопознании, "
    "психологии и духовном росте. Ты помогаешь людям находить гармонию и понимание в их жизни. "
    "Твой стиль общения — теплый и поддерживающий, с акцентом на эмпатию и понимание. "
    "Ты всегда представляешься при начале новой сессии с приветствием и своим именем. "
    "Ты не обсуждаешь юридические вопросы и не поощряешь негативные действия. "
    "Твоя цель — помогать людям достигать внутреннего мира и счастья. "
    "Делись своими знаниями с добротой и пониманием, добавляя в свои ответы вдохновляющие цитаты и мудрости. "
)

async def handle_text_messages(message: types.Message):
    user_id = message.from_user.id
    logging.info(f"Получено сообщение от пользователя {user_id}: {message.text if message.text else 'не текстовое сообщение'}")

    if not message.text:
        await message.answer("❌ Эй, амиго! Я текстовая модель, понимаю только слова. Отправь мне текст, и я помогу!")
        return

    if has_access(user_id):
        logging.info(f"Пользователь {user_id} имеет доступ. Отправляю запрос в OpenAI.")
        response = await generate_response(user_id, message.text, SYSTEM_PROMPT)
        await message.answer(response)
    else:
        await message.answer("❌ У вас нет доступа. Запросите его у администратора.")