from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_start_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Новое направление")],
        [KeyboardButton(text="Проверить последнее направление")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Что будем делать...",
        one_time_keyboard=True
    )
