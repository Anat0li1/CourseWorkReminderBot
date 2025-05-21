from aiogram import types, Router, F
from datetime import datetime
from db.requests import get_user_events_by_date 
from bot.keyboards.inline_keyboards import get_day_plan_keyboard  

router = Router()

@router.callback_query(lambda c: c.data.startswith("day_plan:"))
@router.callback_query(F.data == "📅 План на день")
async def navigate_day(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    try:
        date_str = callback.data.split("day_plan:")[1]
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        await callback.answer("Невірна дата", show_alert=True)
        return

    events = await get_user_events_by_date(user_id, selected_date)

    if events:
        text = f"<b>Події на {selected_date.strftime('%d.%m.%Y')}:</b>\n"
        for event in events:
            text += f"- {event.name} о {event.start_time.strftime('%H:%M')}\n"
    else:
        text = f"На {selected_date.strftime('%d.%m.%Y')} подій не заплановано."

    keyboard = get_day_plan_keyboard(selected_date)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()