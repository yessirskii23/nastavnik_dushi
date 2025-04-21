import logging
import os
from aiogram import types
from aiogram.filters import Command
from aiogram.router import Router
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание роутера
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    logging.info(f"Команда /start от пользователя {user_id}")
    
    welcome_message = (
        "Привет, дорогой друг! 🌟\n"
        "Я — Наставник Души, твой проводник в мире духовного роста и самопознания. "
        "Здесь ты можешь найти поддержку, советы и вдохновение на пути к гармонии и счастью.\n\n"
        "Как я могу помочь тебе сегодня? Просто напиши свой вопрос или поделись своими мыслями, "
        "и я постараюсь дать тебе мудрый совет. 💫"
    )
    
    await message.answer(welcome_message)