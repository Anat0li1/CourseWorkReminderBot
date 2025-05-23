import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message

from aiogram.enums import ParseMode

from bot.handlers import (
    add_reminding,
    day_plan,
    delete_all,
    help,
    info,
    my_remindings,
)
from bot.keyboards.reply_keyboard import main_menu_keyboard
from dotenv import load_dotenv
import os
import bot.services.reminder as reminder
from db.requests import set_user

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode= 'HTML'))
router = Router()
dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(
    add_reminding.router,
    day_plan.router,
    delete_all.router,
    help.router,
    info.router,
    my_remindings.router
)
@dp.startup()
async def on_startup(bot: Bot):
    print("✅ Бот запущено")
    asyncio.create_task(reminder.run(bot))

@dp.message(Command("start"))
async def cmd_start(message:Message):
    await set_user(message.from_user.id, message.from_user.username)
    await message.answer("Привіт! Обери дію з меню 👇", reply_markup=main_menu_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
