from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.requests import get_user_events_with_remindings, delete_event_and_remindings
from bot.utils.fotmatter import format_event_text
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
router = Router()

@router.message(Command("my_events"))
@router.message(F.text == "Переглянути мої події")
async def start_review(message: types.Message):
    user_id = message.from_user.id
    events = await get_user_events_with_remindings(user_id)
    if not events:
        await message.answer("У вас ще немає подій.")
        return
    await send_event(message, events, 0)

async def send_event(message_or_cb, events, index):
    event = events[index]
    total = len(events)
    text = format_event_text(event)  
    builder = InlineKeyboardBuilder()
    if index > 0:
        builder.button(text="⬅️", callback_data=f"event_nav:{index - 1}")
    if index < total - 1:
        builder.button(text="➡️", callback_data=f"event_nav:{index + 1}")

    builder.row(
        types.InlineKeyboardButton(
            text="✏️ Редагувати",
            web_app=types.WebAppInfo(url=f"{os.getenv('BACKEND_URL')}/miniapp/{event.id}")
        ),
        types.InlineKeyboardButton(
            text="🗑 Видалити", callback_data=f"event_del:{event.id}:{index}"
        )
    )
    builder.row(types.InlineKeyboardButton(text="❌ Вийти", callback_data="event_exit"))

    await message_or_cb.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML") \
        if isinstance(message_or_cb, types.Message) \
        else await message_or_cb.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("event_nav:"))
async def navigate_event(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    events = await get_user_events_with_remindings(user_id)

    if index >= len(events):
        await callback.answer("Немає більше подій.")
        return

    await send_event(callback, events, index)
    await callback.answer()

@router.callback_query(F.data.startswith("event_del:"))
async def delete_event(callback: types.CallbackQuery):
    _, event_id, index = callback.data.split(":")
    event_id, index = int(event_id), int(index)
    user_id = callback.from_user.id

    await delete_event_and_remindings(event_id)
    events = await get_user_events_with_remindings(user_id)

    if not events:
        await callback.message.edit_text("Усі події видалено.")
        return

    new_index = min(index, len(events) - 1)
    await send_event(callback, events, new_index)
    await callback.answer("Подію видалено.")

@router.callback_query(F.data == "reminder_exit")
async def exit_reminder(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
