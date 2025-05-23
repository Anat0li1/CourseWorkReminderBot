from db.models import Event

def format_event_text(event: Event) -> str:
    """Форматує інформацію про подію та всі її нагадування"""
    text = (
        f"<b>Подія:</b> {event.name}\n"
        f"📅 Дата: {event.start_time.strftime('%d.%m.%Y')}\n"
        f"🕒 Час: {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
        f"🔄 Повторення: {event.repeat_type}\n\n"
    )
    
    if event.remindings:
        text += "<b>Нагадування:</b>\n"
        for reminder in event.remindings:
            text += f"⏰ За {reminder.remind_before} {get_reminder_unit(reminder.remind_indicator)}\n"
    else:
        text += "❌ Нагадувань немає.\n"

    return text

def get_reminder_unit(indicator: int) -> str:
    """Конвертує числовий індикатор нагадування у текстове значення"""
    units = {
        1: "хвилин",
        2: "годин",
        3: "днів",
        4: "тижнів",
        5: "місяців",
        6: "років"
    }
    return units.get(indicator, "невідомих одиниць")