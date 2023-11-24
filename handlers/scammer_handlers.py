import re
from contextlib import suppress
from typing import List

from aiogram import F, types, Router
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile, InputMediaPhoto
from aiogram.utils.markdown import hunderline


import db
import keyboard
from config import config
from states.states import Scammer

router = Router()

public_channel_id = config.channel_id.get_secret_value()
private_channel_id = config.private_channel_id.get_secret_value()


@router.callback_query(F.data == "main_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Главное меню", reply_markup=keyboard.main_keyboard)


@router.callback_query(F.data == "add_scammer")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    id_to_display = await state.get_data()
    await state.update_data(scam_id=id_to_display["id"])
    await callback.message.answer(f"Опишите ситуацию, в которой вы столкнулись со скамером, и в чем был обман")
    await state.set_state(Scammer.scam_caption)

@router.callback_query(F.data == "confirm_scammer")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    id_to_display = await state.get_data()
    await state.update_data(scam_id=id_to_display["id"])
    await callback.message.answer(f"Опишите ситуацию, в которой вы столкнулись со скамером, и в чем был обман")
    await state.set_state(Scammer.scam_caption)

@router.callback_query(F.data == "delete_scammer_from_db")
async def delete_scammer(callback: types.CallbackQuery, state: FSMContext):
    pattern = r"id скамера: (\d+)"
    match = re.search(pattern, callback.message.text)

    if match:
        scam_id = match.group(1)
        try:
            db.cursor.execute("""DELETE FROM scammer WHERE tg_scammer_id = ?""", (scam_id,))
            db.db.commit()
            await callback.message.answer(f"Пользователь с id {scam_id} успешно удален из базы скамеров")
            #bot.send_message(private_channel_id, f"Пользователь с id {scam_id} успешно удален из базы скамеров")
        except:
            await callback.message.answer(f"При удалении пользователя с id {scam_id} возникла ошибка. Возможно пользователь был удален ранее.")
            #bot.send_message(private_channel_id, f"При удалении пользователя с id {scam_id} возникла ошибка. Возможно пользователь был удален ранее.")
    else:
        await callback.message.answer("Ошибка удаления!")


@router.callback_query(keyboard.Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(callback: types.CallbackQuery, callback_data: keyboard.Pagination,  state: FSMContext):
    id_to_display = await state.get_data()
    db.cursor.execute("""SELECT scam_caption, photo_scam FROM scammer WHERE tg_scammer_id = ?""",
                      (id_to_display["id"],))
    rows = db.cursor.fetchall()

    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else (len(rows)-1)

    if callback_data.action == "next":
        page = page_num + 1 if page_num < (len(rows)-1) else 0
    photo = InputMediaPhoto(type="photo", media=rows[page][1], caption=rows[page][0])
    with suppress(TelegramBadRequest):
        await callback.message.edit_media(media=photo, reply_markup=keyboard.paginator(page))
    await callback.answer()

@router.callback_query(F.data == "display_info")
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    id_to_display = await state.get_data()
    print(id_to_display["id"])
    db.cursor.execute("""SELECT scam_caption, photo_scam FROM scammer WHERE tg_scammer_id = ?""",
                      (id_to_display["id"],))
    rows = db.cursor.fetchall()
    print(type(rows[0][1]))

    await callback.message.answer_photo(rows[0][1], caption=rows[0][0], reply_markup=keyboard.paginator())
    await callback.answer()

