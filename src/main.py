import logging
import openai
import asyncio
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Проверка переменных окружения
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_api_token = os.getenv("TELEGRAM_API_TOKEN")
admin_user_id = os.getenv("ADMIN_USER_ID")

if not openai_api_key:
    logging.error("OPENAI_API_KEY не установлен")
    raise ValueError("OPENAI_API_KEY не установлен")
if not telegram_api_token:
    logging.error("TELEGRAM_API_TOKEN не установлен")
    raise ValueError("TELEGRAM_API_TOKEN не установлен")
if not admin_user_id:
    logging.error("ADMIN_USER_ID не установлен")
    raise ValueError("ADMIN_USER_ID не установлен")

# Установка API-ключа OpenAI
openai.api_key = openai_api_key

# ID администратора
ADMIN_USER_ID = int(admin_user_id)

# Хранилище доступа пользователей (ID -> срок окончания)
user_access = {}

# Хранилище истории сообщений пользователей (ID -> список сообщений)
user_messages = {}

# Создание объектов бота и диспетчера
bot = Bot(token=telegram_api_token)
dp = Dispatcher(bot)

def has_access(user_id: int) -> bool:
    """Проверка доступа пользователя."""
    access = user_id == ADMIN_USER_ID or (user_id in user_access and datetime.now() < user_access[user_id])
    logging.info(f"Проверка доступа для пользователя {user_id}: {access}")
    return access

# Промпт для духовного наставника
SYSTEM_PROMPT = (
    "Вы являетесь духовным наставником по имени [имя], известным своим глубоким знанием мировых религий, философии, психологии, мистицизма и оккультизма. "
    "Ваша роль заключается в том, чтобы предоставлять руководство и поддержку людям, ищущим духовного совета или изучающим различные системы верований. "
    "Вы должны подходить к каждому взаимодействию с сочувствием, уважением и неосуждающим отношением. "
    "Помните, что ваша главная цель – помочь пользователям на их уникальном духовном пути."
)

async def generate_response(user_id: int, user_message: str) -> str:
    """Генерация ответа от OpenAI."""
    try:
        logging.info(f"Отправка запроса в OpenAI с сообщением: {user_message}")

        # Добавление нового сообщения в историю пользователя
        if user_id not in user_messages:
            user_messages[user_id] = []
        user_messages[user_id].append({"role": "user", "content": user_message})

        # Хранить только последние 20 сообщений
        if len(user_messages[user_id]) > 20:
            user_messages[user_id] = user_messages[user_id][-20:]

        # Подготовка сообщений для OpenAI
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_messages[user_id]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

        logging.info("Ответ от OpenAI получен")
        reply = response.choices[0].message.content.strip()

        # Добавление ответа бота в историю сообщений
        user_messages[user_id].append({"role": "assistant", "content": reply})

        return reply
    except Exception as e:
        logging.error(f"Ошибка при генерации ответа: {e}")
        return "Произошла ошибка при генерации ответа."

@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    """Обработчик команды /start."""
    await message.answer("Привет! Я Наставник Души. Задайте мне любой духовный вопрос.")

@dp.message_handler()
async def message_handler(message: Message):
    """Обработчик текстовых сообщений."""
    user_id = message.from_user.id
    if not has_access(user_id):
        await message.answer("У вас нет доступа. Обратитесь к администратору.")
        return

    response = await generate_response(user_id, message.text)
    await message.answer(response)

if __name__ == "__main__":
    logging.info("Запуск бота...")
    executor.start_polling(dp, skip_updates=True)