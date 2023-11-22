from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram.utils.markdown import hunderline
from telethon import TelegramClient

import keyboard
from config import config
from states.states import Scammer

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    await state.clear()
    await message.answer(f"""✅Привет, данный бот поможет тебе проверить человека на скам!\n⚡️Спасибо, что выбрали именно нашего бота для проверки скамеров""", reply_markup=keyboard.main_keyboard)
# Хендлеры находтся в этом файле, так как вызываются первыми и имеют приоритет на всем остальными

# хендлер для основной кнопки проверить.
@router.message(F.text.lower() == "проверить")
async def check_scammer1(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Добавьте никнейм в формате {hunderline('@пользователь')} или перешлите сообщение от пользователя, чтобы проверить его в базе скамеров😊")
    await state.set_state(Scammer.id)

# хендлер для основной кнопки сообщить.
@router.message(F.text.lower() == "сообщить")
async def create_scammer(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Добавьте никнейм в формате {hunderline('@пользователь')} или перешлите сообщение от пользователя, чтобы добавить его в базу скамеров.")
    await state.set_state(Scammer.scam_id)


