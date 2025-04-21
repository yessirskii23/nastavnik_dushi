import logging
from datetime import datetime, timedelta
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from . import user_access, ADMIN_USER_ID

async def approve_access(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    await callback.message.answer("На какое количество дней предоставить доступ пользователю?")
    await state.update_data(user_id=user_id)
    await state.set_state("waiting_for_days")
    await callback.answer()

async def reject_access(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "⛔ Ваш запрос на доступ был отклонен.")
    await callback.answer("Доступ отклонен!")

async def set_access_days(message: types.Message, state: FSMContext):
    days = int(message.text)
    data = await state.get_data()
    user_id = data.get("user_id")
    if user_id:
        user_access[user_id] = datetime.now() + timedelta(days=days)
        await bot.send_message(user_id, f"✅ Вам предоставлен доступ на {days} дней!")
        await message.answer(f"Доступ пользователю предоставлен на {days} дней.")
        await state.clear()
    else:
        await message.answer("Ошибка: не удалось определить пользователя для предоставления доступа.")