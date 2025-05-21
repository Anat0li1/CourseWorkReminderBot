from asyncio import run
from aiogram import Bot, Dispatcher
from config import TOKEN
import application_parts.bot_functional.handlers as apph
from application_parts.database.models import db_main

bot = Bot(token = TOKEN)
dispatcher = Dispatcher()

async def main():
    await db_main()
    dispatcher.include_router(apph.router)
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    try:
        run(main())
    except KeyboardInterrupt:
        print("Bot was stopped! It is sleeping now.")