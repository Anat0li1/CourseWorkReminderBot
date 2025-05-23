from aiogram import Router, types
from aiogram.filters import Command
from bot.utils.phrases import INTRODUCTION

router = Router()

@router.message(Command("info"))
async def show_info(message: types.Message):
    text = (INTRODUCTION)
    await message.answer(text)