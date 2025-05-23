from aiogram import types, Router, F
from datetime import datetime
from db.requests import get_user_events_by_date 
from bot.keyboards.inline_keyboards import get_day_plan_keyboard  

router = Router()

@router.callback_query(lambda c: c.data.startswith("day_plan:"))
@router.message(F.text == "План на день")
async def navigate_day(triger: types.CallbackQuery | types.Message):
    user_id = triger.from_user.id
    selected_date = datetime.now().date()
    if isinstance(triger, types.CallbackQuery):
        try:
            date_str = triger.data.split("day_plan:")[1]
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            await triger.answer("Невірна дата", show_alert=True)
            return
    events = await get_user_events_by_date(user_id, selected_date)
    if events:
        text = f"<b>Події на {selected_date.strftime('%d.%m.%Y')}:</b>\n"
        for event in events:
            text += f"- {event.name} \nз {event.start_time.strftime('%H:%M')}\nпо {event.end_time.strftime('%H:%M')}\n"
    else:
        text = f"На {selected_date.strftime('%d.%m.%Y')} подій не заплановано."
    keyboard = get_day_plan_keyboard(selected_date)
    if isinstance(triger, types.CallbackQuery):
        await triger.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await triger.answer()
    else:
        await triger.answer(text, reply_markup=keyboard, parse_mode="HTML")


# @router.callback_query(lambda c: c.data.startswith("day_plan:"))
# @router.message(F.text == "План на день")
# async def navigate_day(callback: types.CallbackQuery):
#     print(0)
#     user_id = callback.from_user.id
#     print(1)
#     print(callback.data)
#     if callback.data == "План на день":
#         selected_date = datetime.now().date()
#     else:
#         try:
#             date_str = callback.data.split("day_plan:")[1]
#             selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         except ValueError:
#             await callback.answer("Невірна дата", show_alert=True)
#             return
#     print(2, selected_date)
#     events = await get_user_events_by_date(user_id, selected_date)
#     print(3, events)
#     if events:
#         text = f"<b>Події на {selected_date.strftime('%d.%m.%Y')}:</b>\n"
#         for event in events:
#             text += f"- {event.name} \nз {event.start_time.strftime('%H:%M')}\nпо {event.end_time.strftime('%H:%M')}\n"
#     else:
#         text = f"На {selected_date.strftime('%d.%m.%Y')} подій не заплановано."
#     print(4, text)
#     keyboard = get_day_plan_keyboard(selected_date)

#     await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
#     await callback.answer()