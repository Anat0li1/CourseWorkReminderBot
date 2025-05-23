from datetime import date, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def navigation_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"nav_prev:{event_id}"),
            InlineKeyboardButton(text="✏️", callback_data=f"edit:{event_id}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"delete:{event_id}"),
            InlineKeyboardButton(text="➡️", callback_data=f"nav_next:{event_id}")
        ]
    ])

def confirm_delete_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data=f"confirm_delete:{event_id}"),
            InlineKeyboardButton(text="❌ Ні", callback_data=f"cancel_delete:{event_id}")
        ]
    ])

def day_plan_nav_keyboard(offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"day_offset:{offset - 1}"),
            InlineKeyboardButton(text="➡️", callback_data=f"day_offset:{offset + 1}")
        ]
    ])

def add_reminding_keyboard(web_app_url:str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Додати", web_app=WebAppInfo(url=f"{web_app_url}/miniapp")),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="add_remind_cancel")
        ]
    ])

def delete_all_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data="confirm_delete_all"),
            InlineKeyboardButton(text="❌ Ні", callback_data="cancel_delete_all")
        ]
    ])

def get_day_plan_keyboard(current_date: date) -> InlineKeyboardMarkup:
    prev_date = current_date - timedelta(days=1)
    next_date = current_date + timedelta(days=1)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"day_plan:{prev_date.isoformat()}"),
                # InlineKeyboardButton(text=current_date.strftime("%d.%m.%Y"), callback_data="noop"),
                InlineKeyboardButton(text="➡️", callback_data=f"day_plan:{next_date.isoformat()}")
            ]
        ]
    )