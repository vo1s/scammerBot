from typing import List

from aiogram.enums import ContentType
from aiogram_media_group import media_group_handler
from telethon.sync import TelegramClient
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import config
from aiogram.utils.markdown import hunderline
import db
import keyboard
from main import bot
from states.states import Scammer
from middlewares.check_sub import CheckSubscription

router = Router()
router.message.middleware(CheckSubscription())  # проверка подписки

public_channel_id = config.channel_id.get_secret_value()
private_channel_id = config.private_channel_id.get_secret_value()


# хэндлер на кнопку "сообщить"
@router.message(F.text.lower() == "сообщить")
async def create_scammer(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Введите id пользователя")
    await state.set_state(Scammer.scam_id)


@router.message(Scammer.scam_id, F.text)
async def create_scammer2(message: types.Message, state: FSMContext):
    db.cursor.execute(
        f"SELECT tg_scammer_id, tg_scammer_nick FROM scammer WHERE tg_scammer_id = ?",
        (message.text,))
    scammer_exist = db.cursor.fetchone()
    if not scammer_exist:
        await state.update_data(scam_id=message.text)
        await message.answer(f"Опишите ситуацию, в которой вы столкнулись со скамером, и в чем был обман")
        await state.set_state(Scammer.scam_caption)
    else:
        await message.answer("Скамер уже есть в базе данных!")
        await state.clear()


@router.message(Scammer.scam_caption, F.text)
async def create_scammer3(message: types.Message, state: FSMContext):
    await state.update_data(scam_caption=message.text)
    await message.answer(f"Приложите скрины, подтверждающие, что пользователь является скамером")
    await state.set_state(Scammer.scam_photo)


@router.message(Scammer.scam_photo, F.media_group_id, F.content_type == ContentType.PHOTO)
@media_group_handler
async def album_handler(messages: List[types.Message], state: FSMContext):
    data = await state.get_data()
    scam_id = data["scam_id"]
    scam_caption = data["scam_caption"]
    media_group = [
        types.InputMediaPhoto(
            media=m.photo[-1].file_id,
            caption=data["scam_caption"],
            caption_entities=m.caption_entities,
        )
        for m in messages
    ]

    for m in messages:
        username = m.from_user.username or "None"
        db.cursor.execute("""INSERT INTO scammer(tg_scammer_id, tg_scammer_nick, scam_caption, photo_scam, tg_victim_id, tg_victim_nick)
                                VALUES(?,?,?,?,?,?)""",
                          (
                              data["scam_id"], "None", data["scam_caption"], m.photo[-1].file_id, m.from_user.id, username))
        db.db.commit()
    await bot.send_media_group(chat_id=private_channel_id, media=media_group)
    await bot.send_message(private_channel_id, f"Скамер добавлен в базу. Если вы хотите оставить его в ней, не выполняйте никаких действий. "
                                               f"id скамера: {scam_id}."
                                               f" Описание скама: {scam_caption}", reply_markup=keyboard.admin_keyboard_to_delete)
