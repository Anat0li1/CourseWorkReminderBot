from datetime import datetime, timedelta
from db.models import Event, Reminding

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y")

def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def add_minutes(dt: datetime, count:int) -> datetime:
    return dt + timedelta(minutes=count)

def add_hours(dt: datetime, count:int) -> datetime:
    return dt + timedelta(hours=count)

def add_days(dt: datetime, count:int) -> datetime:
    return dt + timedelta(days=count)

def add_weeks(dt: datetime, count:int) -> datetime:
    return dt + timedelta(weeks=count)

def add_months(dt: datetime, count:int) -> datetime:
    years = dt.year + count // 12
    months = count % 12
    if dt.month + months > 12:
        years += 1  
        months = dt.month + months - 12
    day = dt.day
    if months % 2 == 0 and day > 30:
        months += 1
    if months == 2:
        if years % 4 == 0 and (years % 100 != 0 or years % 400 == 0) and day > 29:
            months += 1
        elif day > 28:
            months += 1
    return dt.replace(year=years, month=months, day=day)

def add_years(dt: datetime, count:int) -> datetime:
    try:
        return dt.replace(year=dt.year + count)
    except ValueError:
        return dt.replace(year=dt.year + count, day=dt.day - 1)
    
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def is_event_on_date(event: Event, target: datetime) -> bool:
    rep = event.repeat_type
    if not rep:
        return False

    start = event.start_time.date()

    match rep:
        case 1:
            return False
        case 2: 
            return target >= start and target.weekday() < 5
        case 3: 
            return target >= start
        case 4:  
            return target >= start and (target - start).days % 7 == 0
        case 5:  
            return target.day == start.day
        case 6:
            if start.month == 2 and start.day == 29:
                return target.month == 2 and target.day == 29 and is_leap_year(target.year)
            return target.day == start.day and target.month == start.month
        case 7: 
            unit = event.repeat_indicator 
            step = event.repeat_duration
            start = event.start_repeat.date()
            end = event.end_repeat.date() if event.end_repeat else target
            if not (start <= target <= end):
                return False

            delta_days = (target - start).days

            match unit:
                case 1: 
                    return delta_days % step == 0
                case 2:  
                    return delta_days % (step * 7) == 0
                case 3:
                    return ((target.year - start.year) * 12 + target.month - start.month) % step == 0 and target.day == start.day
                case 4: 
                    return (target.year - start.year) % step == 0 and target.month == start.month and target.day == start.day

    return False

def get_next_rem(reminding: Reminding) -> datetime:
    type_map = {
        1: lambda dt, val: add_minutes(dt, val),
        2: lambda dt, val: add_hours(dt, val),
        3: lambda dt, val: add_days(dt, val),
        4: lambda dt, val: add_weeks(dt, val),
        5: lambda dt, val: add_months(dt, val),
        6: lambda dt, val: add_years(dt, val),
    }

    update_fn = type_map.get(reminding.event.repeat_type)
    if update_fn is None:
        raise ValueError(f"Unknown repeat_type: {reminding.event.repeat_type}")

    new_reminder_time = update_fn(reminding.next_rem, reminding.event.repeat_duration)
    reminding.next_rem = new_reminder_time
    return new_reminder_time

def is_working_day(date: datetime) -> bool:
    return date.weekday() < 5 

def add_working_days(start_date: datetime, days: int) -> datetime:
    current_date = start_date
    added = 0
    while added < days:
        current_date += timedelta(days=1)
        if is_working_day(current_date):
            added += 1
    return current_date

def shift_next_rem_if_reapeatable(next_rem: datetime, event: Event) -> datetime:
    threshold = datetime.now() + timedelta(minutes=5)

    while next_rem <= threshold:
        match event.repeat_type:
            case 2:
                next_rem = add_working_days(next_rem, 1)
            case 3:
                next_rem = add_days(next_rem, 1)
            case 4:
                next_rem = add_weeks(next_rem, 1)
            case 5:
                next_rem = add_months(next_rem, 1)
            case 6:
                next_rem = add_years(next_rem, 1)
            case 7:
                match event.repeat_indicator:
                    case 1:
                        next_rem = add_days(next_rem, event.repeat_duration or 1)
                    case 2:
                        next_rem = add_weeks(next_rem, event.repeat_duration or 1)
                    case 3:
                        next_rem = add_months(next_rem, event.repeat_duration or 1)
                    case 4:
                        next_rem = add_years(next_rem, event.repeat_duration or 1)

        if event.end_repeat and next_rem.date() > event.end_repeat.date():
            raise ValueError(f"Нагадування виходить за межі допустимого періоду: {event.end_repeat}")

    return next_rem

def get_event_part_for_date(event: Event, date: datetime) -> tuple[datetime | None, datetime | None]:
    day_start = datetime(date.year, date.month, date.day, 0, 0, 0)
    day_end = datetime(date.year, date.month, date.day, 23, 59, 59)
    if event.end_time < day_start or event.start_time > day_end:
        return None, None
    part_start = max(event.start_time, day_start)
    part_end = min(event.end_time, day_end)

    return part_start, part_end

    
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
        raise ValueError(f"Invalid remind_indicator {indicator}")
    
def validate_event_repeat(event: Event):
    duration_days = (event.end_time - event.start_time).days
    if duration_days >= 2 and event.repeat_type in [2, 3]:
        raise ValueError(f"Подія триває {duration_days} дні(-в), тому не можна встановити повторення щодня або щоробочого дня")
    if duration_days >= 8 and event.repeat_type == 4:
        raise ValueError(f"Подія триває {duration_days} дні(-в), тому не можна встановити повторення щотижня")
    if duration_days >= 29 and event.repeat_type == 5:
        raise ValueError(f"Подія триває {duration_days} дні(-в), тому не можна встановити повторення щомісяця")
    if duration_days >= 366 and event.repeat_type == 6:
        raise ValueError(f"Подія триває {duration_days} дні(-в), тому не можна встановити повторення щороку")
    if event.repeat_type == 7 and event.repeat_duration:
        repeat_factor = {
            1: 1,  
            2: 7, 
            3: 30, 
            4: 365 
        }.get(event.repeat_indicator, 1) 

        total_repeat_days = event.repeat_duration * repeat_factor

        if total_repeat_days < duration_days:
            raise ValueError(f"Кастомний інтервал повторення ({total_repeat_days} дні(-в)) менший за тривалість події ({duration_days} дні(-в)). Встановіть більший інтервал повторюваності")

    return True 