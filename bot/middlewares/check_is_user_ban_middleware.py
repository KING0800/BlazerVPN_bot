from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update, InputMediaPhoto
from aiogram.dispatcher.handler import CancelHandler

from bot.keyboards.user_keyboards import support_keyboard
from bot.database.UserData import is_user_ban_check, find_user_data, edit_profile

class CheckIsUserBanMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: Update, data: dict):
        if update.message:
            if update.message.text == "/support" or update.message.text.startswith("/start"):
                return
            if await find_user_data(user_id=update.message.from_user.id) == []:
                await edit_profile(update.message.from_user.username, update.message.from_user.id, referrer_id=None)
            is_ban_user = await is_user_ban_check(update.message.from_user.id)
            if is_ban_user == True:
                await update.message.answer_photo(photo="https://imgur.com/43en7Eh", caption="• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", parse_mode="HTML", reply_markup=support_keyboard)
                raise CancelHandler()
            else:
                return

        elif update.callback_query:
            if update.callback_query.data == "support_callback":
                return
            else:
                if await find_user_data(user_id=update.callback_query.from_user.id) == []:
                    await edit_profile(update.callback_query.from_user.username, update.callback_query.from_user.id, referrer_id=None)
                is_ban_user = await is_user_ban_check(update.callback_query.from_user.id)
                if is_ban_user == True:
                    await update.callback_query.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/43en7Eh", caption="• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", parse_mode="HTML"), reply_markup=support_keyboard)
                    raise CancelHandler()
                else:
                    return
        else:
            return

