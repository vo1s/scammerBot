from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext

import keyboard
router = Router()


@router.callback_query(F.data == "main_menu")
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Главное меню", reply_markup=keyboard.main_keyboard)