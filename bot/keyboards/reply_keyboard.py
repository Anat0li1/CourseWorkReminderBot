from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Додати нову подію"),
             KeyboardButton(text="Переглянути мої події")],

            [KeyboardButton(text="План на день"),
            KeyboardButton(text="Видалити всі події")]
        ],
        resize_keyboard=True
    )
