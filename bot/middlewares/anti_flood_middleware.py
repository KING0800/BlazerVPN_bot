import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler

last_message_times = {}

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: int, cooldown: int):
        BaseMiddleware.__init__(self)
        self.rate_limit = limit
        self.cooldown = cooldown

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dp = Dispatcher.get_current()

        try:
            await dp.throttle(key='antiflood_message', rate=self.rate_limit)
        except Throttled as _t:
            if _t.exceeded_count >= self.rate_limit:
                await self.msg_throttle(message=message, throttled=_t)
                await asyncio.sleep(self.cooldown)
                raise CancelHandler()
            
    async def msg_throttle(self, message: types.Message, throttled: Throttled):
        delta = throttled.rate - throttled.delta
        await message.answer(f"• ❌ <b>Ошибка:</b>\n\nСлишком много сообщений. Пожалуйста, подождите <code>{round(delta)}</code> секунд.", parse_mode="HTML")
        await asyncio.sleep(delta)