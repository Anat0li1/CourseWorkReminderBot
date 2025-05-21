import datetime
from db.models import async_session, User, Event, Reminding
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

"""
Функції для роботи з базою даних
Функція update_event_with_remindings() оновлює подію та нагадування не потрібна тому що при оновленні на сайті воно буде оновлювати подію, але перезаписувати нагадування
"""


async def add_event(event: Event) -> Event:
    async with async_session() as session:
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event
    
async def add_event_by_params(user_id: int, name: str, description: str, start_time: datetime, end_time: datetime, repeat_type: int = None, start_repeat: datetime = None, repeat_indicator: int = None, repeat_duration: int = None, end_repeat: datetime = None):
    async with async_session() as session:
        new_event = Event(
            user_id=user_id,
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            repeat_type=repeat_type,
            start_repeat=start_repeat,
            repeat_indicator=repeat_indicator,
            repeat_duration=repeat_duration,
            end_repeat=end_repeat
        )
        session.add(new_event)
        await session.commit()
    return new_event

async def add_reminding(reminding: Reminding) -> Reminding:
    async with async_session() as session:
        session.add(reminding)
        await session.commit()
        await session.refresh(reminding)
        return reminding
    
async def add_reminding_by_params(event_id: int, remind_before: int, remind_indicator: int, next_rem: datetime, remind_end: bool = False):
    async with async_session() as session:
        new_reminding = Reminding(
            event_id=event_id,
            remind_before=remind_before,
            remind_indicator=remind_indicator,
            next_rem=next_rem,
            remind_end=remind_end
        )
        session.add(new_reminding)
        await session.commit()
    return new_reminding

async def add_event_with_remindings(event: Event, remindings: list[Reminding]):
    async with async_session() as session:
        session.add(event)
        await session.flush()  
        for rem in remindings:
            rem.event_id = event.id
            session.add(rem)
        await session.commit()
        await session.refresh(event)
        return event
    
async def update_event(event_id: int, updated_data: dict):
    async with async_session() as session:
        await session.execute(update(Event).where(Event.id == event_id).values(**updated_data))
        await session.commit()

async def update_reminding(reminding_id: int, updated_data: dict):
    async with async_session() as session:
        await session.execute(update(Reminding).where(Reminding.id == reminding_id).values(**updated_data))
        await session.commit()

async def get_user_events_with_remindings(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(Event).options(joinedload(Event.remindings)).where(Event.user_id == user_id).order_by(Reminding.next_rem))
    return result.scalars().all()

async def get_events_by_period(start_date: datetime, end_date: datetime):
    async with async_session() as session:
        result = await session.execute(select(Event).join(Reminding).where(Reminding.next_rem.between(start_date, end_date)).order_by(Reminding.next_rem))
    return result.scalars().all()  #TODO: add computation of the next reminding and delete processed


async def get_user_events_by_date(user_id: int, date: datetime):
    async with async_session() as session:
        result = await session.execute(
            select(Event).where(
                (Event.user_id == user_id) &
                (func.date(Event.start_time) == date.date())
            )
        )
        return result.scalars().all()   #TODO: add computation of event if it is repeated