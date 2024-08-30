import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler

from bot.database.TempData import save_temp_message

class MessageSaverMiddleware(BaseMiddleware):
    def __init__(self):
        BaseMiddleware.__init__(self)

    async def __call__(self, handler, message: types.Message, data: dict):
        user_id = message.from_user.id
        message_text = message.text
        message_markup = message.reply_markup.as_json() if message.reply_markup else None
        photo_url = message.photo[-1].file_id if message.photo else None
        print("asdasasdas")
        try:
            print('asdasdasd')
            await save_temp_message(user_id, message_text, message_markup, photo_url)
        except Exception as e:
            print(f"Ошибка при сохранении сообщения в базу данных: {e}")
        await handler(message, data)

