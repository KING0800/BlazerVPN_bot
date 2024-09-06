from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update

from bot.database.TempData import save_temp_message


class MessageSaverMiddleware(BaseMiddleware):
    async def on_post_process_update(self, update: Update, data_from_handler: list, data: dict):
        if update.callback_query:
            if update.callback_query.data == "back":
                return
            user_id = update.callback_query.from_user.id
            message_text = update.callback_query.message.caption
            message_markup = update.callback_query.message.reply_markup.as_json() if update.callback_query.message.reply_markup else None
            photo_url = update.callback_query.message.photo[-1].file_id if update.callback_query.message.photo else None
            try:
                await save_temp_message(user_id, message_text, message_markup, photo_url)
            except Exception as e:
                print(f"Ошибка при сохранении сообщения в базу данных: {e}")
        elif update.message:
            user_id = update.message.from_user.id
            message_text = update.message.caption
            message_markup = update.message.reply_markup.as_json() if update.message.reply_markup else None
            photo_url = update.message.photo[-1].file_id if update.message.photo else None

            try:
                await save_temp_message(user_id, message_text, message_markup, photo_url)
            except Exception as e:
                print(f"Ошибка при сохранении сообщения в базу данных: {e}")