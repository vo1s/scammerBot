from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

remove_keyboard = ReplyKeyboardRemove()

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Проверить"),
        KeyboardButton(text="Сообщить")
    ],
    [
        KeyboardButton(text="Поделиться ссылкой на бота")
    ],
[
        KeyboardButton(text="Политика конфиденциальности")
    ],
],
    selective=True,
    one_time_keyboard=False,
    resize_keyboard=True
)

scammer_inline_keyboard = InlineKeyboardBuilder()
scammer_inline_keyboard.button(
    text="Подтвердить", callback_data="confirm_scammer"
)
scammer_inline_keyboard.button(
    text="Подробнее", callback_data="display_info"
)
scammer_inline_keyboard.button(
    text="Это не скамер", callback_data="confirm_not_scammer"
)
scammer_inline_keyboard.button(
    text="Главное меню", callback_data="main_menu"
)
scammer_inline_keyboard.adjust(1)

not_scammer_inline_keyboard = InlineKeyboardBuilder()
not_scammer_inline_keyboard.button(
    text="Добавить пользователя", callback_data="add_scammer"
)
not_scammer_inline_keyboard.button(
    text="Главное меню", callback_data="main_menu"
)
not_scammer_inline_keyboard.adjust(1)
