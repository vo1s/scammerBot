from contextlib import suppress
from typing import List
import re
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram_media_group import media_group_handler
from telethon.sync import TelegramClient
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import config
from aiogram.utils.markdown import hunderline
import db
import keyboard
from main import bot
from states.states import Scammer, NotScammer
from middlewares.check_sub import CheckSubscription

router = Router()
router.message.middleware(CheckSubscription())  # проверка подписки

public_channel_id = config.channel_id.get_secret_value()
private_channel_id = config.private_channel_id.get_secret_value()


# продолжение хэндлера на кнопку "сообщить"


@router.message(Scammer.scam_id, F.text)
async def create_scammer2(message: types.Message, state: FSMContext):
    entitys = message.entities or []
    mention_exists = False
    forward_exist = False
    user_id = 123456789
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
                except ValueError:
                    await message.answer("Не удается получить id пользователя!")
                    return

    if not mention_exists and message.forward_from:
        forward_exist = True
        user_id = message.forward_from.id
    if not mention_exists and not forward_exist:
        await message.answer("Такого пользователя нет. Попробуйте еще раз!")
    else:
        db.cursor.execute(
            f"SELECT tg_scammer_id, not_scammer FROM scammer WHERE tg_scammer_id = ?",
            (user_id,))
        all_rows_with_number1 = True
        scammer_exist = db.cursor.fetchall()
        for row in scammer_exist:
            if row[1] == 0:
                all_rows_with_number1 = False
        print(scammer_exist)
        if not scammer_exist or all_rows_with_number1:
            await state.update_data(scam_id=user_id)
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

    full_message = f"""Запрос на добавление скамера.\nid скамера: {scam_id}.\nОписание скама: {scam_caption}"""

    media_group = []
    count_photos = 0

    for m in messages:
        username = m.from_user.username or "None"
        db.cursor.execute("""INSERT INTO temp_storage(tg_scammer_id, tg_scammer_nick, scam_caption, photo_scam, tg_victim_id, tg_victim_nick)
                                        VALUES(?,?,?,?,?,?)""",
                          (
                              data["scam_id"], "None", data["scam_caption"], m.photo[-1].file_id, m.from_user.id,
                              username))
        db.db.commit()

        media_group.append(
            types.InputMediaPhoto(
                media=m.photo[-1].file_id,
                caption=f"id: {scam_id}" if count_photos == 0 else '',
                caption_entities=m.caption_entities,
            )
        )
        count_photos += 1

    await messages[-1].answer("Ваш запрос на добавление отправлен на проверку. Спасибо!",
                              reply_markup=keyboard.main_keyboard)
    await bot.send_media_group(chat_id=private_channel_id, media=media_group)
    await bot.send_message(private_channel_id, full_message, reply_markup=keyboard.admin_keyboard_to_add_delete)



@router.message(Scammer.scam_photo, F.photo)
async def photo_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    scam_id = data["scam_id"]
    scam_caption = data["scam_caption"]

    full_message = f"""Запрос на добавление скамера.\nid скамера: {scam_id}.\nОписание скама: {scam_caption}"""

    username = message.from_user.username or "None"
    db.cursor.execute("""INSERT INTO temp_storage(tg_scammer_id, tg_scammer_nick, scam_caption, photo_scam, tg_victim_id, tg_victim_nick)
                                            VALUES(?,?,?,?,?,?)""",
                      (
                          data["scam_id"], "None", data["scam_caption"], message.photo[-1].file_id,
                          message.from_user.id,
                          username))
    db.db.commit()

    await message.answer("Ваш запрос на добавление отправлен на проверку. Спасибо!",
                         reply_markup=keyboard.main_keyboard)
    await bot.send_photo(chat_id=private_channel_id, photo=message.photo[-1].file_id)
    await bot.send_message(private_channel_id, full_message, reply_markup=keyboard.admin_keyboard_to_add_delete)


# -------------------------------------------------------------------------------------------------
# Колбеки расположены тут, так как используют экземпляр бота
# -------------------------------------------------------------------------------------------------


@router.callback_query(F.data == "write_to_reporter")
async def add_scammer(callback: types.CallbackQuery):
    pattern = r"id скамера: (\d+)"
    match = re.search(pattern, callback.message.text)
    if match:
        scam_id = match.group(1)
        await bot.send_message(chat_id=int(scam_id), text="Здравствуйте! Пишет администратор бота AntiScam")


@router.callback_query(F.data == "add_scammer_to_db")
async def add_scammer(callback: types.CallbackQuery):
    pattern = r"id скамера: (\d+)"
    match = re.search(pattern, callback.message.text)
    media_group = []

    if match:
        scam_id = match.group(1)

        db.cursor.execute(
            f"SELECT tg_scammer_id, tg_scammer_nick, scam_caption, photo_scam, tg_victim_id, tg_victim_nick FROM temp_storage WHERE tg_scammer_id = ?",
            (scam_id,))
        scammers = db.cursor.fetchall()

        db.cursor.execute("""DELETE FROM temp_storage WHERE tg_scammer_id = ?""", (scam_id,))
        db.db.commit()
        count_photos = 0
        lines = callback.message.text.split('\n')
        text_to_public_channel = f"❌Пользователь с id{scam_id} СКАМЕР❌\n{lines[1]}\n{lines[2]}"


        for row in scammers:
            media_group.append(
                types.InputMediaPhoto(
                    media=row[3],
                    caption=text_to_public_channel if count_photos == 0 else ''
                )
            )
            count_photos += 1

            db.cursor.execute("""INSERT INTO scammer(tg_scammer_id, tg_scammer_nick, scam_caption, photo_scam, tg_victim_id, tg_victim_nick)
                                                   VALUES(?,?,?,?,?,?)""",
                              (
                                  row[0], row[1], row[2], row[3], row[4], row[5]))
            db.db.commit()
        await callback.message.answer(f"Пользователь с  id {scam_id} успешно добавлен в базу!")
        await bot.send_media_group(chat_id=public_channel_id, media=media_group)
    else:
        await callback.message.answer("Произошла ошибка! Не найден id пользователя!")
        with suppress(TelegramBadRequest):
            await callback.answer()


# -------------------------------------------------------------------------------------------------
# Хендлеры для обработки "НЕ СКАМЕРОВ"
# -------------------------------------------------------------------------------------------------


@router.callback_query(F.data == "confirm_not_scammer")
async def add_scammer(callback: types.CallbackQuery, state: FSMContext):
    id_to_display = await state.get_data()
    await state.update_data(not_scammer_id=id_to_display["id"])
    await callback.message.answer("Приведите аргументы, что пользователь не является скамером.")
    await state.set_state(NotScammer.not_scammer_caption)


@router.message(NotScammer.not_scammer_caption, ~F.text)
async def create_scammer3(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите текст!")


@router.message(NotScammer.not_scammer_caption, F.text)
async def create_scammer3(message: types.Message, state: FSMContext):
    await state.update_data(not_scam_caption=message.text)
    await message.answer("Приложите скриншоты, что пользователь не является скамером")
    await state.set_state(NotScammer.not_scammer_photo)


@router.message(NotScammer.not_scammer_photo, F.media_group_id, F.content_type == ContentType.PHOTO)
@media_group_handler
async def album_handler1(messages: List[types.Message], state: FSMContext):
    data = await state.get_data()
    not_scam_id = data["not_scammer_id"]
    not_scam_caption = data["not_scam_caption"]

    full_message = f"""Запрос на изменение статуса скамера.\nid скамера: {not_scam_id}.\nПочему пользователь не скамер: {not_scam_caption}"""

    media_group = []
    count_photos = 0

    for m in messages:
        media_group.append(
            types.InputMediaPhoto(
                media=m.photo[-1].file_id,
                caption=f"id: {not_scam_id}" if count_photos == 0 else '',
                caption_entities=m.caption_entities,
            )
        )
        count_photos += 1

    await messages[-1].answer("Ваш запрос на добавление отправлен на проверку. Спасибо!",
                              reply_markup=keyboard.main_keyboard)
    await bot.send_media_group(chat_id=private_channel_id, media=media_group)
    await bot.send_message(private_channel_id, full_message, reply_markup=keyboard.change_scammer_status)


@router.message(NotScammer.not_scammer_photo, F.photo)
async def photo_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    not_scam_id = data["not_scammer_id"]
    not_scam_caption = data["not_scam_caption"]

    full_message = f"""Запрос на изменение статуса скамера.\nid скамера: {not_scam_id}.\nПочему пользователь не скамер: {not_scam_caption}"""

    await message.answer("Ваш запрос на добавление отправлен на проверку. Спасибо!",
                         reply_markup=keyboard.main_keyboard)
    await bot.send_photo(chat_id=private_channel_id, photo=message.photo[-1].file_id)
    await bot.send_message(private_channel_id, full_message, reply_markup=keyboard.change_scammer_status)


@router.callback_query(F.data == "change_scammer_status")
async def add_scammer(callback: types.CallbackQuery):
    pattern = r"id скамера: (\d+)"
    match = re.search(pattern, callback.message.text)

    if match:
        scam_id = match.group(1)
        db.cursor.execute("""UPDATE scammer set not_scammer = 1 WHERE tg_scammer_id = ?""", (scam_id,))
        db.db.commit()
        await callback.message.answer(f"Статус скамера с id {scam_id} успешно изменен!")
    else:
        await callback.message.answer("Ошибка при поиске id в сообщении!")
