from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.requests import get_user_events_with_remindings, delete_event_and_remindings
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
router = Router()

@router.message(Command("my_events"))
@router.message(F.text == "📋 Переглянути мої події")
async def start_review(message: types.Message):
    user_id = message.from_user.id
    reminders = await get_user_events_with_remindings(user_id)

    if not reminders:
        await message.answer("У вас ще немає нагадувань.")
        return

    await send_reminder(message, reminders, 0)


async def send_reminder(message_or_cb, reminders, index):
    reminder = reminders[index]
    total = len(reminders)

    text = (
        f"<b>Нагадування {index + 1} з {total}</b>\n\n"
        f"📌 <b>{reminder.name}</b>\n"
        f"🕒 {reminder.start_time.strftime('%d.%m.%Y %H:%M')}"
    )

    builder = InlineKeyboardBuilder()
    if index > 0:
        builder.button(text="⬅️", callback_data=f"reminder_nav:{index - 1}")
    if index < total - 1:
        builder.button(text="➡️", callback_data=f"reminder_nav:{index + 1}")

    builder.row(
        types.InlineKeyboardButton(
            text="✏️ Редагувати",
            web_app=types.WebAppInfo(url=f"{os.getenv('BACKEND_URL')}/miniapp?reminder_id={reminder.id}")
        ),
        types.InlineKeyboardButton(
            text="🗑 Видалити", callback_data=f"reminder_del:{reminder.id}:{index}"
        )
    )
    builder.row(types.InlineKeyboardButton(text="❌ Вийти", callback_data="reminder_exit"))

    await message_or_cb.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML") \
        if isinstance(message_or_cb, types.Message) \
        else await message_or_cb.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("reminder_nav:"))
async def navigate_reminder(callback: types.CallbackQuery):
    index = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    reminders = await get_user_events_with_remindings(user_id)

    if index >= len(reminders):
        await callback.answer("Немає більше нагадувань.")
        return

    await send_reminder(callback, reminders, index)
    await callback.answer()


@router.callback_query(F.data.startswith("reminder_del:"))
async def delete_reminder(callback: types.CallbackQuery):
    _, reminder_id, index = callback.data.split(":")
    reminder_id, index = int(reminder_id), int(index)
    user_id = callback.from_user.id

    await delete_event_and_remindings(reminder_id)
    reminders = await get_user_events_with_remindings(user_id)

    if not reminders:
        await callback.message.edit_text("Усі нагадування видалено.")
        return

    new_index = min(index, len(reminders) - 1)
    await send_reminder(callback, reminders, new_index)
    await callback.answer("Нагадування видалено.")


@router.callback_query(F.data == "reminder_exit")
async def exit_reminder(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
