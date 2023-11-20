from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config
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


sub_channel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подписаться", url=config.channel_link.get_secret_value())
        ]
    ]
)

admin_keyboard_to_add_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить в базу", callback_data="add_scammer_to_db"),
            InlineKeyboardButton(text="Удалить из базы", callback_data="delete_scammer_from_db")
        ],
        [
            InlineKeyboardButton(text="Написать пользователю", callback_data="write_to_reporter")
        ]
    ]
)


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int

def paginator(page: int=0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text="➡", callback_data=Pagination(action="next", page=page).pack()),
        width=2
    )
    return builder.as_markup()