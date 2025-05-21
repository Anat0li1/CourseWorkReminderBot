from datetime import datetime, timedelta

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def format_date(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y")

def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def pass_days(dt: datetime, count:int) -> datetime:
    return dt + timedelta(days=count)

def pass_week(dt: datetime, count:int) -> datetime:
    return dt + timedelta(weeks=count)

def pass_month(dt: datetime, count:int) -> datetime:
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

def pass_year(dt: datetime) -> datetime:
    try:
        return dt.replace(year=dt.year + 1)
    except ValueError:
        return dt.replace(year=dt.year + 1, day=28)