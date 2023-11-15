import re

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile
import db
import keyboard
from config import config
router = Router()

public_channel_id = config.channel_id.get_secret_value()
private_channel_id = config.private_channel_id.get_secret_value()


@router.callback_query(F.data == "main_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Главное меню", reply_markup=keyboard.main_keyboard)


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


@router.callback_query(F.data == "display_info")
async def send_random_value(callback: types.CallbackQuery, state: FSMContext):
    id_to_display = await state.get_data()
    print(id_to_display["id"])
    db.cursor.execute("""SELECT scam_caption, photo_scam FROM scammer WHERE tg_scammer_id = ?""",
                      (id_to_display["id"],))
    rows = db.cursor.fetchall()

    for row in rows:
        await callback.message.answer(f"Суть скама: {row[0]}")
        await callback.message.answer_photo(InputFile(row[1]), "фото скама")
