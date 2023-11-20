from aiogram import types, Router

import keyboard

router = Router()


@router.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer("Выберите один из пунктов меню!", reply_markup=keyboard.main_keyboard)
