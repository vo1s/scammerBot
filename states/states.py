from aiogram.fsm.state import StatesGroup, State

class Scammer(StatesGroup):
    id = State()
    username_mention = State()
    scam_caption = State()
    scam_photo = State()
    scam_id = State()
    resend_to_private = State()

class NotScammer(StatesGroup):
    not_scammer_id = State()
    not_scammer_caption = State()
    not_scammer_photo = State()