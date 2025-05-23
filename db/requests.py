import copy
import datetime
from db.models import async_session, User, Event, Reminding
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from bot.utils.date_utils import is_event_on_date, get_event_part_for_date, calculate_timedelta, get_next_rem, shift_next_rem_if_reapeatable, validate_event_repeat

async def update_event_data(event_id: int, data: dict):
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        start = datetime.fromisoformat(data.get("start")).astimezone(timezone.utc)
        end = datetime.fromisoformat(data.get("end")).astimezone(timezone.utc)

        if start <= now + timedelta(minutes=5):
            raise ValueError("Початок події має бути не раніше ніж через 5 хвилин")
        if end <= start:
            raise ValueError("Кінець події має бути після початку")

        repeat_obj = data.get("repeat")
        repeat_type = repeat_obj.get("type")
        start_repeat = repeat_obj.get("start") if repeat_type == 6 else None
        repeat_indicator = repeat_obj.get("indicator") if repeat_type == 6 else None
        repeat_duration = repeat_obj.get("duration") if repeat_type == 6 else None
        end_repeat = repeat_obj.get("end") if repeat_type == 6 else None

        stmt = (
            update(Event)
            .where(Event.id == event_id)
            .values(
                name=data.get("name"),
                description=data.get("description", ""),
                start_time=start,
                end_time=end,
                repeat_type=repeat_type,
                start_repeat=start_repeat,
                repeat_indicator=repeat_indicator,
                repeat_duration=repeat_duration,
                end_repeat=end_repeat
            )
        )
        await session.execute(stmt)
        event = await session.get(Event, event_id)
        validate_event_repeat(event)
        await session.commit()


async def save_reminders(event_id: int, data: dict):
    async with async_session() as session:
        reminders = data.get("reminders", [])
        event = await session.get(Event, event_id)
        now = datetime.now(timezone.utc)
        start = event.start_time
        end = event.end_time

        for r in reminders:
            remind_before = r.get("before")
            remind_indicator = r.get("indicator")
            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = start - delta

            if next_rem <= now + timedelta(minutes=5) and event.repeat_type == 1:
                raise ValueError("Час нагадування має бути не раніше ніж через 5 хвилин (або подія повинна повторюватися)")

            if next_rem <= now + timedelta(minutes=5) and event.repeat_type > 1:
                try:
                    next_rem = shift_next_rem_if_reapeatable(next_rem, event)
                except Exception:
                    raise ValueError("За такого налаштування часу і повторюваності нагадування не відпрацює")

            reminder = Reminding(
                event_id=event_id,
                remind_before=remind_before,
                remind_indicator=remind_indicator,
                next_rem=next_rem,
                remind_end=False
            )
            session.add(reminder)

        remind_end = data.get("remindEnd")
        if remind_end:
            remind_before = remind_end.get("before")
            remind_indicator = remind_end.get("indicator")
            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = end - delta

            if next_rem <= now + timedelta(minutes=5):
                next_rem = now + timedelta(minutes=6)

            reminder = Reminding(
                event_id=event_id,
                remind_before=remind_before,
                remind_indicator=remind_indicator,
                next_rem=next_rem,
                remind_end=True
            )
            session.add(reminder)

        await session.commit()

async def set_user(tg_id, tg_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id==tg_id))
        if user:
            pass
        else:
            session.add(User(tg_id = tg_id, user_name = tg_name))
            await session.commit()

async def save_event_with_reminders(user_id, data:dict):
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        name = data.get("name")
        description = data.get("description", "")
        start = datetime.fromisoformat(data.get("start")).astimezone(timezone.utc)
        end = datetime.fromisoformat(data.get("end")).astimezone(timezone.utc)
        repeat_obj = data.get("repeat")
        repeat_type = repeat_obj.get("type")
        start_repeat = repeat_obj.get("start") if repeat_type == 6 else None
        repeat_indicator = repeat_obj.get("indicator") if repeat_type == 6 else None
        repeat_duration = repeat_obj.get("duration") if repeat_type == 6 else None
        end_repeat = repeat_obj.get("end") if repeat_type == 6 else None
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
        validate_event_repeat(event)
        session.add(event)
        await session.flush()  
        for r in data.get("reminders", []):
            remind_before = r.get("before")
            remind_indicator = r.get("indicator")
            delta = calculate_timedelta(remind_before, remind_indicator)
            next_rem = start - delta
            if next_rem <= now + timedelta(minutes=5) and event.repeat_type == 1:
                raise ValueError("Час нагадування має бути не раніше ніж через 5 хвилин (або подія повинна повторюватися)")  #TODO: should update to the next reminding
            if next_rem <= now + timedelta(minutes=5) and event.repeat_type > 1:
                try:
                    next_rem = shift_next_rem_if_reapeatable(next_rem, event)
                except Exception:
                    raise ValueError("За такого налаштування часу і повторюваності нагадування не відпрацює")  #TODO: should update to the next reminding
            reminder = Reminding(
                event_id=event.id,
                remind_before=remind_before,
                remind_indicator=remind_indicator,
                next_rem=next_rem,
                remind_end=False
            )
            session.add(reminder)
        remind_end = data.get("remindEnd")
        if remind_end:
            remind_before = remind_end.get("before")
            remind_indicator = remind_end.get("indicator")
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

async def delete_all_users_events_and_remindings(user_id: int):
    async with async_session() as session:
        await session.execute(delete(Event).where(Event.user_id == user_id))
        await session.commit()

async def delete_event_and_remindings(event_id: int):
    async with async_session() as session:
        await session.execute(delete(Reminding).where(Reminding.event_id == event_id))
        await session.execute(delete(Event).where(Event.id == event_id))
        await session.commit()

async def delete_reminding(reminding_id: int):
    async with async_session() as session:
        await session.execute(delete(Reminding).where(Reminding.id == reminding_id))
        await session.commit()


async def delete_events_remindings(event_id:int):
    async with async_session() as session:
        await session.execute(delete(Reminding).where(Reminding.event_id == event_id))
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

async def update_reminding_after_sending(reminding: Reminding):
    # next_rem = get_next_rem(reminding)
    event = reminding.event
    try:
        next_rem = shift_next_rem_if_reapeatable(next_rem, event)
    except Exception:
        delete_reminding(reminding.id)
    change = {"next_rem": next_rem}
    await update_reminding(reminding.id, change)

# async def get_user_events_with_remindings(user_id: int):
#     async with async_session() as session:
#         result = list(await session.execute(select(Event).options(joinedload(Event.remindings)).where(Event.user_id == user_id)))
#     result.sort(key=lambda e: e.remindings[0].next_rem if e.remindings else datetime.max)
#     return result

async def get_user_events_with_remindings(user_id: int):
    async with async_session() as session:
        stmt = select(Event).options(selectinload(Event.remindings)).where(Event.user_id == user_id)
        result = await session.scalars(stmt)
        
        events = list(result)
        events.sort(key=lambda e: e.remindings[0].next_rem if e.remindings else datetime.max)
        return events


async def get_events_by_period(start_date: datetime, end_date: datetime):
    async with async_session() as session:
    #     result = await session.execute(select(Event).join(Reminding).where(Reminding.next_rem.between(start_date, end_date)).order_by(Reminding.next_rem))
    # return result.scalars().all()  #TODO: add computation of the next reminding and delete processed
        result = await session.execute(
                select(Event, Reminding)
                .join(Reminding)
                .where(Reminding.next_rem.between(start_date, end_date))
                .order_by(Reminding.next_rem)
            )
    return result.all()

async def get_event_by_id(event_id:int):
    async with async_session() as session:
        result = await session.execute(select(Event, Reminding).join(Reminding).where(Event.id == event_id))
    return result.all()

# async def get_user_events_by_date(user_id: int, date: datetime):
#     async with async_session() as session:
#         result = await session.execute(
#             select(Event).where(
#                 (Event.user_id == user_id) &
#                 (func.date(Event.start_time) == date.date())
#             )
#         )
#         return result.scalars().all()  #TODO: add computation of event if it is repeated


async def get_user_events_by_date(user_id: int, date: datetime):
    async with async_session() as session:
        result = await session.execute(
            select(Event)
            .where(
                (Event.user_id == user_id) &
                (func.date(Event.start_time) <= date) &
                (func.date(Event.end_time) >= date)
            )
        )
        events = result.scalars().all()

        result_repeatable = await session.execute(
            select(Event)
            .where(Event.user_id == user_id)
        )
        all_events = result_repeatable.scalars().all()

        for event in all_events:
            if event in events:
                continue

            if not event.repeat_type or event.repeat_type == 1:
                continue

            if not is_event_on_date(event, date):
                continue

            events.append(event)

        daily_events = []
        for event in events:
            part_start, part_end = get_event_part_for_date(event, date)
            if part_start and part_end:
                event_copy = copy.copy(event)
                event_copy.start_time = part_start
                event_copy.end_time = part_end
                daily_events.append(event_copy)

        return sorted(daily_events, key=lambda e: e.start_time)