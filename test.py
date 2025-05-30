from datetime import datetime, timedelta, date
import asyncio

# Тестові імпорти моделей
from db.models import User, Event, Reminding, async_session  # або ім'я сесії

# Тестові імпортовані функції
from db.requests import (
    add_event,
    add_event_by_params,
    add_reminding,
    add_reminding_by_params,
    add_event_with_remindings,
    update_event, 
    update_reminding,
    get_user_events_with_remindings,
    get_user_events_by_date,
    delete_all_users_events_and_remindings,
    delete_event_and_remindings,
    update_reminding_after_sending,
    get_event_by_id,
    get_user_events_with_remindings
)



# async def main():
#     user_id = 1
#     event_id = 1
#     reminding_id = 1
#     event = Event(
#         user_id=user_id,
#         name="Тест подія",
#         description="Опис події",
#         start_time=datetime.now() + timedelta(hours=1),
#         end_time=datetime.now() + timedelta(hours=2),
#         repeat_type=0,
#         start_repeat=date.today(),
#         repeat_indicator=1,
#         repeat_duration=7,
#         end_repeat=date.today() + timedelta(days=30)
#     )
#     reminding = Reminding(
#         event_id=event_id,
#         remind_before=30,
#         remind_indicator=1,
#         next_rem=event.start_time - timedelta(minutes=30),
#     )

#     # upcoming_events = await get_user_events_by_date(2, datetime.now())
#     # for event in upcoming_events:
#     #     print(f"📌 Подія: {event.name}")
#     #     print(f"   - Початок: {event.start_time}")
#     #     print(f"   - Кінець: {event.end_time}")
#     #     print(f"   - Опис: {event.description}")
#     #     print(f"   - Повторювана: {'так' if event.repeat_type else 'ні'}")

#     #     # if hasattr(event, "remindings") and event.remindings:
#     #     #     print("   ⏰ Нагадування:")
#     #     #     for rem in event.remindings:
#     #     #         print(f"     • за {rem.remind_before} хвилин (на {rem.next_rem}, id={rem.id})")
#     #     # else:
#     #     #     print("   ⏰ Немає нагадувань")
#     #     print("-" * 50)

#     await delete_event_and_remindings(1)


# asyncio.run(main())


import asyncio
import datetime
from db.requests import save_event_with_reminders, get_user_events_by_date
from db.models import Event, Reminding, async_session  # твоя async session
from datetime import datetime, timedelta

async def main():
    # user_id = 1
    # # now = datetime.now(datetime.timezone.utc)

    # event_data = {
    #     "name": "Тестова подія",
    #     "description": "Опис події для ручного тесту",
    #     "start": (now + datetime.timedelta(minutes=15)).isoformat(),
    #     "end": (now + datetime.timedelta(minutes=45)).isoformat(),
    #     "repeat_type": 0,
    #     "start_repeat": None,
    #     "repeat_indicator": None,
    #     "repeat_duration": None,
    #     "end_repeat": None
    # }

    # remindings = [
    #     {"remind_before": 10, "remind_indicator": 1}, 
    #     {"remind_before": 1, "remind_indicator": 3}    
    # ]

    # remind_end = {
    #     "remind_before": 5,
    #     "remind_indicator": 1
    # }

    result = (await get_user_events_with_remindings(1081733675))[1]
    rem = result.remindings[0]
    await update_reminding_after_sending(rem)

if __name__ == "__main__":
    asyncio.run(main())
