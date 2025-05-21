from datetime import datetime, timedelta
from db.requests import *
from aiogram import Bot
import asyncio

async def run(bot: Bot):
    while True:
        now = datetime.now()
        end = now + timedelta(minutes=5)
        reminders = await get_events_by_period(now, end)
        for rem in reminders:
            try:
                await bot.send_message(rem.user_tg_id, f"🔔 Нагадування: {rem.text}")
                next_rem = get_next_rem(rem)
                if next_rem:
                    rem.next_rem = next_rem
                    await update_reminding(rem)
            except Exception as e:
                print(f"[Reminder Error] {e}")

        await asyncio.sleep(60)  