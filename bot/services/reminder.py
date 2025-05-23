from datetime import datetime, timedelta
from db.requests import *
from aiogram import Bot
import asyncio

async def run(bot: Bot):
    while True:
        print(f"Iteration: {datetime.now()}")
        now = datetime.now()
        end = now + timedelta(minutes=1)
        reminders = await get_events_by_period(now, end)
        print(f"Reminders: {reminders}")
        for rem in reminders:
            try:
                await bot.send_message(rem[0].user_id, f"🔔 Нагадування: {rem[0].description}")
                await update_reminding_after_sending(rem[1])
            except Exception as e:
                print(f"[Reminder Error] {e}")

        await asyncio.sleep(60)  