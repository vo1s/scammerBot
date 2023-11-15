from typing import List

from aiogram.enums import ContentType
from aiogram_media_group import MediaGroupFilter, media_group_handler
from telethon.sync import TelegramClient
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import config
from aiogram.utils.markdown import hunderline
import db
import keyboard

from states.states import Scammer
from middlewares.check_sub import CheckSubscription

router = Router()
router.message.middleware(CheckSubscription())  # проверка подписки

count = 0

public_channel_id = config.channel_id.get_secret_value()
private_channel_id = config.private_channel_id.get_secret_value()







# хэндлер на кнопку "проверить"
@router.message(F.text.lower() == "проверить")
async def check_scammer1(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Добавьте никнейм в формате {hunderline('@пользователь')} или перешлите сообщение от пользователя, чтобы проверить его в базе скамеров😊")
    await state.set_state(Scammer.id)


@router.message(Scammer.id)
async def check_scammer2(message: types.Message, state: FSMContext):
    entitys = message.entities or []
    mention_exists = False
    forward_exist = False
    for entity in entitys:
        # берем ник пользователя
        if entity.type == "mention":
            mention_exists = True
            mention_user = entity.extract_from(message.text)[1:]
            # ищем его id
            async with TelegramClient('session_name', config.api_id.get_secret_value(),
                                      config.api_hash.get_secret_value()) as client:
                try:
                    user = await client.get_entity(mention_user)
                    user_id = user.id
                    #  проверяем по базе

                    db.cursor.execute(
                        f"SELECT tg_scammer_id, tg_scammer_nick FROM scammer WHERE tg_scammer_id = ? AND tg_scammer_nick = ?",
                        (user_id, mention_user))
                    scammer_exist = db.cursor.fetchone()
                    print(scammer_exist)
                    if scammer_exist:
                        await message.answer(f"id данного пользователя: {user_id}",
                                             reply_markup=keyboard.remove_keyboard)
                        await message.answer("⚠️Пользователь СКАМЕР, будьте осторожны!⚠️",
                                             reply_markup=keyboard.scammer_inline_keyboard.as_markup())
                    else:
                        await message.answer(f"id данного пользователя: {user_id}",
                                             reply_markup=keyboard.remove_keyboard)
                        await message.answer("Пользователь не найден в базе скамеров, добавить?",
                                             reply_markup=keyboard.not_scammer_inline_keyboard.as_markup())
                    await state.update_data(id=user_id)
                    break

                except ValueError:
                    await message.answer("Такого пользователя не существует! Попробуйте еще раз!")

    if message.forward_from.id:
        forward_exist = True
        db.cursor.execute(
            f"SELECT tg_scammer_id, tg_scammer_nick FROM scammer WHERE tg_scammer_id = ?",
            (message.forward_from.id,))
        scammer_exist = db.cursor.fetchone()
        if scammer_exist:
            await message.answer(f"id данного пользователя: {message.forward_from.id}",
                                 reply_markup=keyboard.remove_keyboard)
            await message.answer("⚠️Пользователь СКАМЕР, будьте осторожны!⚠️",
                                 reply_markup=keyboard.scammer_inline_keyboard.as_markup())
        else:
            await message.answer(f"id данного пользователя: {message.forward_from.id}",
                                 reply_markup=keyboard.remove_keyboard)
            await message.answer("Пользователь не найден в базе скамеров, добавить?",
                                 reply_markup=keyboard.not_scammer_inline_keyboard.as_markup())
        await state.update_data(id=message.forward_from.id)

    if not mention_exists and not forward_exist:
        await message.answer("Такого пользователя нет. Попробуйте еще раз!")
