from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from bot.keyboards.reply_keyboard import main_menu_keyboard 
from bot.keyboards.inline_keyboards import delete_all_keyboard 
from db.requests import delete_all_users_events_and_remindings

router = Router()

@router.message(Command("delete_all"))
@router.message(F.text == "Видалити всі події")
async def confirm_delete_all(message: Message):
    kb = delete_all_keyboard()
    await message.answer("Ви точно хочете видалити всі ваші події та нагадування?", reply_markup=kb)
    await message.reply(" ", reply_markup=ReplyKeyboardRemove())

@router.callback_query(F.data == "confirm_delete_all")
async def do_delete_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_all_users_events_and_remindings(user_id)  
    await callback.message.delete()
    await callback.message.answer("✅ Усі події було видалено. Ви повернулися в головне меню!", reply_markup=main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "cancel_delete_all")
async def cancel_delete_all(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Видалення скасовано. Ви повернулися в головне меню!", reply_markup=main_menu_keyboard())
    await callback.answer()
