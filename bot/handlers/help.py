from aiogram import Router, types
from aiogram.filters import Command
import bot.phrases as phrases

router = Router()

@router.message(Command("help"))
async def show_help(message: types.Message):
    text = (phrases.COMMANDS)
    await message.answer(text)