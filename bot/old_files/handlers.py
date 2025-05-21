from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from application_parts.multi_language.phrases import first_main_keyboard_options
import application_parts.multi_language.translator as appt
import application_parts.bot_functional.keyboards as kb
from application_parts.user_info import UserInfo, NoteForm, MenuForm
import application_parts.database.requests as appdbr
import asyncio
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()


@router.message(CommandStart())  ## two starts in a row skip a language part
async def cmd_start(message:Message):
    UserInfo.id = message.from_user.id
    user_id = await appdbr.set_user(UserInfo.id, message.from_user.full_name)
    await appdbr.set_user_subscription(user_id)
    if UserInfo.language == "uk":
        UserInfo.language = message.from_user.language_code
        await message.answer(appt.check_language_accurance(UserInfo.language), reply_markup= await kb.inline_language_acception())
        UserInfo.awaiting_callback = True
    else:
        await message_output_func(message, 'introduction', keyboard= await kb.return_main_reply_keyboard())

@router.callback_query(F.data == 'inroduction') #awaiting callback check
async def introduction_callback(callback:CallbackQuery):
    UserInfo.awaiting_callback = False
    await callback.answer('')
    await message_output_func(callback.message, 'introduction', keyboard=await kb.return_main_reply_keyboard())

@router.callback_query(F.data == 'change_language')
async def change_lang_request(callback:CallbackQuery, state:FSMContext):
    UserInfo.awaiting_callback = False
    UserInfo.is_changing_lang = True
    await callback.answer('')
    await state.set_state(MenuForm.lang_changing)
    await message_output_func(callback.message, 'lang_request', True)

@router.message(MenuForm.lang_changing) ## change the logik
async def begin_change_lang_func(message:Message, state:FSMContext):
    await check_awaiting_callback(message)
    if UserInfo.is_changing_lang:
        inputted_lang_code = message.text.lower()
        if appt.check_language_code(inputted_lang_code) and inputted_lang_code != 'ru':
            UserInfo.is_changing_lang = False
            UserInfo.language = inputted_lang_code
            await message_output_func(message, 'correct_lang_input')
            await message_output_func(message, 'introduction', keyboard=await kb.return_main_reply_keyboard())
            UserInfo.is_changing_lang = False
        else:
            await state.set_state(MenuForm.lang_changing)
            await message_output_func(message, 'incorrect_lang_input', keyboard=await kb.inline_cansel_keyboard("change_cancel"))

@router.message(F.text == appt.translate_phrase("first_main_keyboard_options", UserInfo.language))
async def change_lang_func(message:Message):
    await check_awaiting_callback(message)
    if UserInfo.is_changing_lang:
        inputted_lang_code = message.text.lower()
        if appt.check_language_code(inputted_lang_code) and inputted_lang_code != 'ru':
            UserInfo.is_changing_lang = False
            UserInfo.language = inputted_lang_code
            await message_output_func(message, 'correct_lang_input', keyboard=await kb.return_main_reply_keyboard())
        else:
            await message_output_func(message, 'incorrect_lang_input', keyboard=await kb.inline_cansel_keyboard("change_cancel"))



@router.callback_query(F.data == 'change_cancel')
async def cancel_lang_change(callback:CallbackQuery):
    UserInfo.is_changing_lang = False
    await message_output_func(callback.message, 'introduction', keyboard=await kb.return_main_reply_keyboard())
    
async def message_output_func(message:Message, phrase:str, repliable:bool=False, keyboard=None):
    if not repliable:
        if keyboard:
            await message.answer(appt.translate_phrase(phrase, UserInfo.language), parse_mode="HTML", reply_markup=keyboard)
        else:
            await message.answer(appt.translate_phrase(phrase, UserInfo.language), parse_mode="HTML")
    else:
        if keyboard:
            await message.edit_text(appt.translate_phrase(phrase, UserInfo.language), parse_mode="HTML", reply_markup=keyboard)
        else:
            await message.edit_text(appt.translate_phrase(phrase, UserInfo.language), parse_mode="HTML")

async def check_awaiting_callback(message:Message):
    if UserInfo.awaiting_callback:
        await message.delete()
        return 
    


@router.message(F.text == appt.translate_phrase('second_main_keyboard_options', UserInfo.language))
async def remind_main_func(message:Message):
    await message_output_func(message, appt.return_you_choose(" працювати з нагадуваннями", UserInfo.language), keyboard= await kb.return_note_db_keyboard())

@router.message(F.text == appt.translate_phrase('first_note_db_options', UserInfo.language)) #add
async def remind_add_func_first_step(message:Message, state:FSMContext):
    await state.set_state(NoteForm.name)
    await message_output_func(message, appt.please_choose(" назву нагадування (до 15 символів)", UserInfo.language), keyboard=await kb.inline_cansel_keyboard("add_note"))    

@router.message(NoteForm.name) 
async def remind_add_func_second_step(message:Message, state:FSMContext):
    await state.update_data(name = message.text)
    await state.set_state(NoteForm.description)
    await message_output_func(message, appt.please_choose(" опис нагадування (до 150 символів)", UserInfo.language), keyboard=await kb.inline_cansel_keyboard("add_note"))
   
@router.message(NoteForm.description) 
async def remind_add_func_third_step(message:Message, state:FSMContext):
    await state.update_data(description = message.text)
    await state.set_state(NoteForm.photo)
    await message_output_func(message, appt.translate_phrase("photo_wait"), keyboard=await kb.inline_photo_back_keyboard())

@router.message(NoteForm.photo)
async def remind_add_func_get_photo(message:Message, state = FSMContext):
    if message.content_type == ContentType.PHOTO:
        await state.update_data(photo = message.photo[-1].file_id)
    else:
        await state.update_data(photo = None)
    await state.set_state(NoteForm.event_datetime)
    await message_output_func(message, appt.please_choose(" рік події", UserInfo.language), keyboard=await kb.return_year_keyboard())

@router.callback_query(F.data == "skip_photo")
async def remind_add_func_skip_photo(callback:CallbackQuery, state:FSMContext):
    await state.update_data(photo = None)
    await state.set_state(NoteForm.year)
    await callback.answer()
    await callback.message.answer(text=appt.please_choose(" рік події", UserInfo.language), reply_markup=await kb.return_year_keyboard())

@router.callback_query(F.data.startswith("choose_year_"))
async def remind_add_func_datetime_year_set(callback:CallbackQuery, state:FSMContext):
    year_i = callback.data.split("_")[2]
    await state.update_data(year = year_i)
    await state.set_state(NoteForm.month)
    await callback.answer()
    await callback.message.edit_text(text=appt.please_choose(" місяць події", UserInfo.language), reply_markup=await kb.return_month_keyboard(year_i))

@router.callback_query(F.data.startswith("choose_month_"))
async def remind_add_func_datetime_month_set(callback:CallbackQuery, state:FSMContext):
    year_i = callback.data.split("_")[3]
    month_i = callback.data.split("_")[2]
    await state.update_data(month = month_i)
    await state.set_state(NoteForm.day)
    await callback.answer()
    await callback.message.edit_text(text=appt.please_choose(" день події", UserInfo.language), reply_markup=await kb.return_day_keyboard(year_i, month_i))

@router.callback_query(F.data.startswith("choose_day_"))
async def remind_add_func_datetime_day_set(callback:CallbackQuery, state:FSMContext):
    year_i = callback.data.split("_")[4]
    month_i = callback.data.split("_")[3]
    day_i = callback.data.split("_")[2]
    await state.update_data(day = day_i)
    await state.set_state(NoteForm.hour)
    await callback.answer()
    await callback.message.edit_text(text=appt.please_choose(" годину події", UserInfo.language), reply_markup=await kb.return_hours_keyboard(year_i, month_i, day_i))

@router.callback_query(F.data.startswith("choose_hour_"))
async def remind_add_func_datetime_hour_set(callback:CallbackQuery, state:FSMContext):
    year_i = callback.data.split("_")[5]
    month_i = callback.data.split("_")[4]
    day_i = callback.data.split("_")[3]
    hour_i = callback.data.split("_")[2]
    await state.update_data(hour = hour_i)
    await state.set_state(NoteForm.min)
    await callback.answer()
    await callback.message.edit_text(text=appt.please_choose(" хвилину події", UserInfo.language), reply_markup=await kb.return_min_keyboard(year_i, month_i, day_i, hour_i))

@router.callback_query(F.data.startswith("choose_min_"))
async def remind_add_func_datetime_min_set(callback:CallbackQuery, state:FSMContext):
    year_i = callback.data.split("_")[6]
    month_i = callback.data.split("_")[5]
    day_i = callback.data.split("_")[4]
    hour_i = callback.data.split("_")[3]
    min_i = callback.data.split("_")[2]
    max_possible_input = (int)((datetime(year_i, month_i, day_i, hour_i, min_i) - datetime.now()).total_seconds())//60
    await state.update_data(min = min_i)
    await state.set_state(NoteForm.event_remind)
    await callback.answer()
    await callback.message.edit_text(text=appt.please_choose(f" за скільки хвилин до події нагадати (не більше ніж {max_possible_input})", UserInfo.language), reply_markup=await kb.inline_cansel_keyboard())

@router.message(F.text.isdigit())
async def remind_add_func_last_step(message:Message, state:FSMContext):
    ceil = (int)((datetime(NoteForm.year, NoteForm.month, NoteForm.day, NoteForm.hour, NoteForm.min) - datetime.now()).total_seconds())//60
    await state.update_data(event_remind = int(message.text)%ceil)
    await message.answer(text=appt.translate_phrase(f"Додати нотатку {NoteForm.name} {NoteForm.year}/{NoteForm.month}/{NoteForm.day} {NoteForm.hour}:{NoteForm.min}?"
                                                    , UserInfo.language), reply_markup=await kb.return_final_inline_keyboard())

@router.callback_query(F.data == "final_note_accept")
async def access_note_add(callback:CallbackQuery, state = FSMContext):
    event_time = datetime(NoteForm.year, NoteForm.month, NoteForm.day, NoteForm.hour, NoteForm.day)
    remind_time = event_time - timedelta(minutes=NoteForm.event_remind) #check if rem_tim and eve_tim are smaller than noW()
    await appdbr.insert_note(UserInfo.id, NoteForm.name, NoteForm.description, NoteForm.photo,
                              event_time, remind_time)
    await state.clear()
    await callback.answer()
    await callback.message.answer(appt.translate_phrase("access_note_add", UserInfo.language), reply_markup=await kb.return_main_reply_keyboard())

@router.callback_query(F.data == "return_to_main")
async def access_note_add(callback:CallbackQuery, state = FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer(appt.translate_phrase("action_reject", UserInfo.language), reply_markup=await kb.return_main_reply_keyboard())





# @router.message(F.text == appt.translate_phrase(note_db_options[1], UserInfo.language)) #change
# async def remind_main_func(message:Message):
#     await message_output_func(message, appt.return_you_choose(" працювати з нагадуваннями", UserInfo.language), keyboard=kb.note_db_keyboard)     
    
# @router.message(F.text == appt.translate_phrase(note_db_options[2], UserInfo.language)) #delete
# async def remind_main_func(message:Message):
#     await message_output_func(message, appt.return_you_choose(" працювати з нагадуваннями", UserInfo.language), keyboard=kb.note_db_keyboard)    
    
# @router.message(F.text == appt.translate_phrase(note_db_options[3], UserInfo.language)) #delete all
# async def remind_main_func(message:Message):
#     await message_output_func(message, appt.return_you_choose(" працювати з нагадуваннями", UserInfo.language), keyboard=kb.note_db_keyboard) 

# @router.message(F.text == appt.translate_phrase(note_db_options[4], UserInfo.language)) #show all
# async def remind_main_func(message:Message):
#     await message_output_func(message, appt.return_you_choose(" працювати з нагадуваннями", UserInfo.language), keyboard=kb.note_db_keyboard)    
    
# @router.message(F.text == appt.translate_phrase(note_db_options[5], UserInfo.language)) #back
# async def remind_main_func(message:Message):
#     await message_output_func(message, appt.return_you_choose(" працювати з нагадуваннями", UserInfo.language), keyboard=kb.note_db_keyboard) 
    
    
    
    
    
    
    
    
    
    
    #await message.answer(GoogleTranslator(source='uk', target=Registration.language).translate(lang_request.format(arg1 = Language.get(Registration.language).display_name())))
    #print(message.from_user.language_code)
    #Registration.language = 'ua' if message.from_user.language_code == 'ru' else message.from_user.language_code
    #await message.answer(GoogleTranslator(source='uk', target=Registration.language).translate(introduction), parse_mode="HTML") 
    
    
    #message.reply

#@router.message(Command('help'))
#@router.message(F.text == 'sth')
#@router.message(F.photo) : message.photo[-1].get_id (return unique photo id - and can be got by it)
#answer_photo(photo = 'id', caption = 'text under photo')
#message.from_user.get_sth (everything also from sended message)



#@router.callback_query(F.data == 'cq_name') : ... (callback_query:CallbackQuery)
@router.callback_query(F.data == 'cq_name')
async def way(callback:CallbackQuery):
    callback.answer('sth')   #show_allert like table
    callback.message.answer('it`s in message') #edit_text() change current message param reply_markup cannot be inline