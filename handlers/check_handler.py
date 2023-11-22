from typing import List

from aiogram.enums import ContentType
from aiogram_media_group import MediaGroupFilter, media_group_handler
from telethon.errors import UsernameInvalidError
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







# продолжение хэндлера на кнопку "проверить"

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
                        f"SELECT tg_scammer_id, tg_scammer_nick FROM scammer WHERE tg_scammer_id = ? OR tg_scammer_nick = ?",
                        (user_id, mention_user))
                    scammer_exist = db.cursor.fetchall()
                    db.cursor.execute(
                        f"SELECT not_scammer FROM scammer WHERE (tg_scammer_id = ? OR tg_scammer_nick = ?) AND not_scammer = 0",
                        (user_id, mention_user))
                    ex_scammer = db.cursor.fetchall()
                    if scammer_exist and ex_scammer:
                        if ex_scammer[0][0] == 0:
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
                except UsernameInvalidError:
                    await message.answer("Такого пользователя не существует! Попробуйте еще раз!")
                except ValueError:
                    await message.answer("Такого пользователя не существует! Попробуйте еще раз!")

    if not mention_exists and message.forward_from:
        forward_exist = True
        db.cursor.execute(
            f"SELECT tg_scammer_id, tg_scammer_nick FROM scammer WHERE tg_scammer_id = ?",
            (message.forward_from.id,))
        scammer_exist = db.cursor.fetchone()

        db.cursor.execute(
            f"SELECT not_scammer FROM scammer WHERE tg_scammer_id = ?",
            (message.forward_from.id,))
        ex_scammer = db.cursor.fetchall()

        if scammer_exist and (ex_scammer[0][0] == 0):
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
