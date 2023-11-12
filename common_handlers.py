from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, types


import keyboard
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    await state.clear()
    await message.answer(f"""✅Привет, данный бот поможет тебе проверить человека на скам! \n
                        ⚡️Спасибо, что выбрали именно нашего бота для проверки скамеров""", reply_markup=keyboard.main_keyboard)


@router.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer("Выберите один из пунктов меню!")