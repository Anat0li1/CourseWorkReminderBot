from datetime import datetime
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from application_parts.user_info import UserInfo
import application_parts.multi_language.translator as appt

async def return_lang_codes_keyboard():
    keyboard = InlineKeyboardBuilder()
    for language in appt.return_all_lang_codes():
        keyboard.add(InlineKeyboardButton(text=language, callback_data=f"change_to_{language}"))
    keyboard = keyboard.adjust(10)
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="reject_lang_changes"))
    return keyboard.as_markup()


async def return_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=appt.translate_phrase("first_main_keyboard_options", UserInfo.language)), KeyboardButton(text=appt.translate_phrase('second_main_keyboard_options', UserInfo.language))], 
    [KeyboardButton(text=appt.translate_phrase("third_main_keyboard_options", UserInfo.language))],
    [KeyboardButton(text=appt.translate_phrase("fourth_main_keyboard_options", UserInfo.language))],
    [KeyboardButton(text=appt.translate_phrase("fifth_main_keyboard_options", UserInfo.language))]
    ], resize_keyboard=True, input_field_placeholder=appt.translate_phrase("option_request", UserInfo.language))
    return keyboard

async def inline_language_acception():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("accept", UserInfo.language), callback_data="inroduction"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("reject", UserInfo.language), callback_data="change_language"))
    return keyboard.adjust(1).as_markup()

async def inline_cansel_keyboard(callback_name:str):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data=callback_name))
    return keyboard.as_markup()

async def inline_photo_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text = appt.translate_phrase("photo_reject", UserInfo.language), callback_data="skip_photo"))
    keyboard.add(InlineKeyboardButton(text= appt.translate_phrase("back", UserInfo.language), callback_data="add_note"))
    return keyboard.adjust(2).as_markup()


async def return_note_db_keyboard():
    keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=appt.translate_phrase("first_note_db_options", UserInfo.language)), KeyboardButton(text=appt.translate_phrase('second_note_db_options', UserInfo.language))], 
    [KeyboardButton(text=appt.translate_phrase("third_note_db_options", UserInfo.language)), KeyboardButton(text=appt.translate_phrase("fouth_note_db_options", UserInfo.language))],
    [KeyboardButton(text=appt.translate_phrase("fifth_note_db_options", UserInfo.language)), KeyboardButton(text=appt.translate_phrase("sixth_note_db_options", UserInfo.language))]
    ], resize_keyboard=True, input_field_placeholder= appt.translate_phrase("option_request", UserInfo.language))
    return keyboard
# note_db_keyboard = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text=appt.translate_phrase("note_db_options[0]", UserInfo.language)), KeyboardButton(text=appt.translate_phrase('note_db_options[1]', UserInfo.language))], 
#     [KeyboardButton(text=appt.translate_phrase("note_db_options[2]", UserInfo.language)), KeyboardButton(text=appt.translate_phrase("note_db_options[3]", UserInfo.language))],
#     [KeyboardButton(text=appt.translate_phrase("note_db_options[4]", UserInfo.language)), KeyboardButton(text=appt.translate_phrase("note_db_options[5]", UserInfo.language))]
# ], resize_keyboard=True, input_field_placeholder= appt.translate_phrase("option_request", UserInfo.language))\

async def return_year_keyboard():
    keyboard = InlineKeyboardBuilder()
    current_year = datetime.now().year
    for step in range(0, 5):
        option = current_year + step
        keyboard.add(InlineKeyboardButton(text=f"{option}", callback_data=f"choose_year_{option}"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="return_to_photo")) ##possibly change name
    return keyboard.adjust(3).as_markup()

async def return_month_keyboard(year):
    current_year = datetime.now().year
    start_month = 1
    if year == current_year:
        start_month = datetime.now().month
    keyboard = InlineKeyboardBuilder()
    for month_code in range(start_month, 13):
        keyboard.add(InlineKeyboardButton(text=f"{month_code}", callback_data=f"choose_month_{month_code}_{year}"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="return_to_year")) ##possibly change name
    return keyboard.adjust(4).as_markup()   #give time parts in callbacks (fe for min it is choose_min_hour_day_month_year) and in body receive and split them

async def return_day_keyboard(year, month):
    current_year = datetime.now().year
    current_month = datetime.now().month
    keyboard = InlineKeyboardBuilder()
    start_day = 1
    end_day = return_days_in_month(year, month)
    if current_year == year and current_month == month:
        start_day = datetime.now().day
    for day_code in range(start_day, end_day+1):
        keyboard.add(InlineKeyboardButton(text=f"{day_code}", callback_data=f"choose_day_{day_code}_{month}_{year}"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="return_to_month")) ##possibly change name
    return keyboard.adjust(8).as_markup()

def return_hours_keyboard(year, month, day):
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    keyboard = InlineKeyboardBuilder()
    start_hour = 0
    end_hour = 23
    if current_year == year and current_month == month and current_day == day:
        start_hour = datetime.now().time().hour
    for hour_code in range(start_hour, end_hour+1):
        keyboard.add(InlineKeyboardButton(text=f"{hour_code}", callback_data=f"choose_hour_{hour_code}_{day}_{month}_{year}"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="return_to_day")) ##possibly change name
    return keyboard.adjust(8).as_markup()

def return_min_keyboard(year, month, day, hour):
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    current_hour = datetime.now().time().hour
    keyboard = InlineKeyboardBuilder()
    start_min = 0
    end_min = 59
    if current_year == year and current_month == month and current_day == day and current_hour == hour:
        start_min = datetime.now().time().minute
    for min_code in range(start_min, end_min+1):
        keyboard.add(InlineKeyboardButton(text=f"{min_code}", callback_data=f"choose_min_{min_code}_{hour}_{day}_{month}_{year}"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="return_to_hour")) ##possibly change name
    return keyboard.adjust(10).as_markup()

def return_days_in_month(year:int, month:int)->int:
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        if is_leap(year):
            return 29
        else:
            return 28

def is_leap(year)->bool:
    return year%4==0 and (year%100!=0 or year%400==0)

async def return_final_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("accept_action", UserInfo.language), callback_data="final_note_accept"))
    keyboard.add(InlineKeyboardButton(text=appt.translate_phrase("cancel", UserInfo.language), callback_data="return_to_main"))
    return keyboard.adjust(2).as_markup()










ways = ['way1', 'way2', 'way3', 'way4'] #database request
async def return_inline_keyboard(): #awaik + return_keyboard()
    builder = InlineKeyboardBuilder()
    for way in ways:
        builder.add(InlineKeyboardButton(text=way, callback_data='way_choosing')) #handler to catch it
    return builder.adjust(1).as_markup()

# language_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text=appt.translate_phrase("accept", UserInfo.language), callback_data="inroduction")],
#     [InlineKeyboardButton(text=appt.translate_phrase("reject", UserInfo.language), callback_data="change_language")]
# ])
