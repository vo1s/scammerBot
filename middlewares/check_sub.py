from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from config import config
import keyboard


class CheckSubscription(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        chat_member = await event.bot.get_chat_member(config.channel_name.get_secret_value(), event.from_user.id)

        if chat_member.status == "left":
            await event.answer(
                "Подпишись на канал, чтобы пользоваться ботом!",
                reply_markup=keyboard.sub_channel
            )
        else:
            return await handler(event, data)