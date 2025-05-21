import datetime
from db.models import async_session, User, Event, Reminding
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple


async def set_user(tg_id, tg_name)->int:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        if user:
            pass
        else:
            session.add(User(tg_id = tg_id, user_name = tg_name))
            await session.commit()
        return await session.scalar(select(User.id).where(User.tg_id==tg_id))

async def save_event_with_reminders(user_id, event_data: dict, remindings: list, remind_end: dict | None):
    async with async_session() as session:
        now = datetime.now(timezone.utc)

        name = event_data.get("name", "")
        description = event_data.get("description", "")
        start = datetime.fromisoformat(event_data.get("start")).astimezone(timezone.utc)
        end = datetime.fromisoformat(event_data.get("end")).astimezone(timezone.utc)
        repeat_type = event_data.get("repeat_type")
        start_repeat = event_data.get("start_repeat")
        repeat_indicator = event_data.get("repeat_indicator")
        repeat_duration = event_data.get("repeat_duration")
        end_repeat = event_data.get("end_repeat")

        if start <= now + timedelta(minutes=5):
            raise ValueError("Початок події має бути не раніше ніж через 5 хвилин")
        if end <= start:
            raise ValueError("Кінець події має бути після початку")

        event = Event(
            user_id=user_id,
            name=name,
            description=description,
            start_time=start,
            end_time=end,
            repeat_type=repeat_type,
            start_repeat=start_repeat,
            repeat_indicator=repeat_indicator,
            repeat_duration=repeat_duration,
            end_repeat=end_repeat
        )

        session.add(event)
        await session.flush()  

        for r in remindings:
            remind_before = r.get("remind_before")
            remind_indicator = r.get("remind_indicator")

            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = start - delta
            if next_rem <= now + timedelta(minutes=5):
                next_rem = now + timedelta(minutes=6)

            reminder = Reminding(
                event_id=event.id,
                remind_before=remind_before,
                remind_indicator=remind_indicator,
                next_rem=next_rem,
                remind_end=False
            )
            session.add(reminder)

        if remind_end:
            remind_before = remind_end.get("remind_before")
            remind_indicator = remind_end.get("remind_indicator")

            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = end - delta
            if next_rem <= now + timedelta(minutes=5):
                next_rem = now + timedelta(minutes=6)

            reminder = Reminding(
                event_id=event.id,
                remind_before=remind_before,
                remind_indicator=remind_indicator,
                next_rem=next_rem,
                remind_end=True
            )
            session.add(reminder)

        await session.commit()
        return event.id


def calculate_timedelta(value, indicator):
    if indicator == 1:  
        return timedelta(minutes=value)
    elif indicator == 2:  
        return timedelta(hours=value)
    elif indicator == 3: 
        return timedelta(days=value)
    elif indicator == 4:  
        return timedelta(weeks=value)
    elif indicator == 5:  
        return timedelta(days=value * 30)
    elif indicator == 6:  
        return timedelta(days=value * 365)
    else:
        raise ValueError("Invalid remind_indicator")


def get_next_rem(rem: Reminding) -> Optional[datetime]:
    if rem.repeat_type == "daily":
        return rem.next_rem + timedelta(days=1)
    elif rem.repeat_type == "weekly":
        return rem.next_rem + timedelta(weeks=1)
    elif rem.repeat_type == "monthly":
        return rem.next_rem + timedelta(days=30)
    return None

async def delete_all_users_events_and_remindings(user_id: int):
    async with async_session() as session:
        await session.execute(delete(Event).where(Event.user_id == user_id))
        await session.commit()

async def delete_event_and_remindings(event_id: int):
    async with async_session() as session:
        await session.execute(delete(Reminding).where(Reminding.event_id == event_id))
        await session.execute(delete(Event).where(Event.id == event_id))
        await session.commit()


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
        result = list(await session.execute(select(Event).options(joinedload(Event.remindings)).where(Event.user_id == user_id)))
    result.sort(key=lambda e: e.remindings[0].next_rem if e.remindings else datetime.max)
    return result

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