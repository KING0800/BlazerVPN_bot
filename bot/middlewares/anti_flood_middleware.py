import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler

last_message_times = {}

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: int):
        BaseMiddleware.__init__(self)
        self.rate_limit = limit

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dp = Dispatcher.get_current()

        try:
            await dp.throttle(key='antiflood_message', rate=self.rate_limit)
        except Throttled as _t:
            await self.msg_throttle(message=message, throttled=_t)

            raise CancelHandler()
        
    async def msg_throttle(self, message: types.Message, throttled: Throttled):
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            await message.answer(f"• ❌ <b>Ошибка:</b>\n\nПожалуйста, подождите <code>{round(delta)}</code> секунд перед отправкой следующего сообщения.", parse_mode="HTML")
        await asyncio.sleep(delta)