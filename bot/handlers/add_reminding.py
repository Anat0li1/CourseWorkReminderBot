from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from aiogram.filters import Command
from os import getenv
from bot.keyboards.reply_keyboard import main_menu_keyboard
from bot.keyboards.inline_keyboards import add_reminding_keyboard

router = Router()
BACKEND_URL = getenv("BACKEND_URL")

@router.message(Command("add_remindings"))
@router.message(F.text == "📝 Додати нову подію")
async def add_remindings_command(message: Message):
    keyboard = add_reminding_keyboard(web_app_url=BACKEND_URL)

    await message.answer("Додати нагадування?", reply_markup=keyboard)
    await message.reply("", reply_markup=ReplyKeyboardRemove())

@router.callback_query(F.data == "add_remind_cancel")
async def cancel_add_reminding(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Ви повернулись у головне меню:", reply_markup=main_menu_keyboard)
    await callback.answer()
