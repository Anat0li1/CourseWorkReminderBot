from dataclasses import dataclass
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types


@dataclass
class UserInfo():
    id:int
    tg_id:int
    user_name:str