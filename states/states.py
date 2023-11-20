from aiogram.fsm.state import StatesGroup, State

class Scammer(StatesGroup):
    id = State()
    scam_caption = State()
    scam_photo = State()
    scam_id = State()
    resend_to_private = State()