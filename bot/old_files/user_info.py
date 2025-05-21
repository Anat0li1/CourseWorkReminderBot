from dataclasses import dataclass
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types


@dataclass
class UserInfo():
    id:int
    language:str = "uk"
    is_changing_lang:bool = False
    awaiting_callback:bool = False

class NoteForm(StatesGroup):
    name = State()
    description = State()
    photo = State()
    year = State()
    month = State()
    day = State()
    hour = State()
    min = State()
    event_remind = State()

class MenuForm():
    lang_changing = State()