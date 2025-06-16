import logging
import openai
import asyncio
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение переменных
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_api_token = os.getenv("TELEGRAM_API_TOKEN")
admin_user_id = os.getenv("ADMIN_USER_ID")

# Проверка переменных
if not openai_api_key or not telegram_api_token or not admin_user_id:
    raise ValueError("Некоторые переменные окружения не установлены")

# Установка ключа OpenAI
openai.api_key = openai_api_key
ADMIN_USER_ID = int(admin_user_id)

# Хранилище доступов (user_id -> до какой даты)
user_access = {}

# Хранилище сообщений (user_id -> сообщения)
user_messages = {}

# FSM хранилище и бот
storage = MemoryStorage()
bot = Bot(token=telegram_api_token)
dp = Dispatcher(bot, storage=storage)

# Промпт для OpenAI
SYSTEM_PROMPT = (
    "Вы — духовный наставник, мудрый и сочувствующий, глубоко разбирающийся в религии, философии и психологии. "
    "Помогайте людям идти по пути души мягко, без осуждений, с уважением к их уникальному опыту."
)

# FSM состояние
class AdminAccess(StatesGroup):
    waiting_for_duration = State()

# Временное хранилище для ожидания подтверждения
pending_user = {}

# Проверка доступа
def has_access(user_id: int) -> bool:
    return user_id == ADMIN_USER_ID or (
        user_id in user_access and datetime.now() < user_access[user_id]
    )

# Генерация ответа
async def generate_response(user_id: int, user_message: str) -> str:
    try:
        if user_id not in user_messages:
            user_messages[user_id] = []
        user_messages[user_id].append({"role": "user", "content": user_message})

        # ограничиваем историю
        user_messages[user_id] = user_messages[user_id][-20:]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_messages[user_id]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()
        user_messages[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logging.exception("Ошибка OpenAI:")
        return "⚠️ Что-то пошло не так, попробуй позже."

# /start хендлер
@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    user_id = message.from_user.id
    if not has_access(user_id):
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Дать доступ", callback_data=f"approve:{user_id}"),
            InlineKeyboardButton("⛔ Отклонить", callback_data=f"deny:{user_id}")
        )
        await bot.send_message(ADMIN_USER_ID, f"🔔 Запрос на доступ от @{message.from_user.username or user_id} (ID: {user_id})", reply_markup=keyboard)
        await message.answer("🧘‍♂️ Запрос отправлен Наставнику. Ожидайте одобрения 🙏")
    else:
        await message.answer("✨ Привет! Я Наставник Души. Спрашивай о сокровенном, и я постараюсь помочь 🙏")

# Кнопка "Дать доступ"
@dp.callback_query_handler(lambda c: c.data.startswith("approve:"))
async def approve_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    pending_user[callback.from_user.id] = user_id
    await callback.message.answer("⏳ На сколько дней выдать доступ?")
    await state.set_state(AdminAccess.waiting_for_duration)

# Кнопка "Отклонить"
@dp.callback_query_handler(lambda c: c.data.startswith("deny:"))
async def deny_user(callback: types.CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await bot.send_message(user_id, "❌ К сожалению, доступ отклонён. Попробуйте позже.")
    await callback.message.answer(f"⛔ Запрос от пользователя {user_id} отклонён.")

# Ввод дней от админа
@dp.message_handler(state=AdminAccess.waiting_for_duration)
async def set_duration(message: Message, state: FSMContext):
    try:
        days = int(message.text.strip())
        admin_id = message.from_user.id
        if admin_id not in pending_user:
            await message.answer("⚠️ Нет ожидающего подтверждения.")
            return
        uid = pending_user.pop(admin_id)
        expires = datetime.now() + timedelta(days=days)
        user_access[uid] = expires
        await bot.send_message(uid, f"✅ Тебе открыт доступ до {expires.strftime('%Y-%m-%d')}. Добро пожаловать!")
        await message.answer(f"✅ Доступ для {uid} выдан до {expires.strftime('%Y-%m-%d')}")
        await state.finish()
    except ValueError:
        await message.answer("❗ Введите количество дней цифрой.")

# Сообщения
@dp.message_handler()
async def message_handler(message: Message):
    user_id = message.from_user.id
    if not has_access(user_id):
        await message.answer("⚠️ У тебя нет доступа. Напиши /start, чтобы отправить запрос.")
        return

    response = await generate_response(user_id, message.text)
    await message.answer(response)

# Запуск
if __name__ == "__main__":
    logging.info("🔮 Запуск Наставника Души...")
    executor.start_polling(dp, skip_updates=True)
