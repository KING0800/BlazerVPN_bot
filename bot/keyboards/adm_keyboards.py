from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# кнопки, отображающиеся в админ панели
adm_panel_keyboard = InlineKeyboardMarkup()
adm_panel_keyboard.add(
    InlineKeyboardButton(text="💵 Пополнение баланса", callback_data="addind_balance_callback"),
    InlineKeyboardButton(text="💵 Удаление баланса", callback_data="deleting_balance_callback")
)
adm_panel_keyboard.add(
    InlineKeyboardButton(text="🗃 Данные о пользователе", callback_data="user_data_callback"), 
    InlineKeyboardButton(text="🛡️ VPN пользователей", callback_data="vpn_user_callback")
)
adm_panel_keyboard.add(
    InlineKeyboardButton(text="❌ Заблокировать пользователя", callback_data="ban_user_callback"),
    InlineKeyboardButton(text="✅ Разблокировать пользователя", callback_data="unban_user_callback")
)
adm_panel_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# кнопки по управлению определенным пользователем
user_find_data = InlineKeyboardMarkup()
user_find_data.add(
    InlineKeyboardButton(text="❌ Заблокировать пользователя", callback_data="ban_user2_callback"),
    InlineKeyboardButton(text="✅ Разблокировать пользователя", callback_data="unban_user2_callback")
)
user_find_data.add(
    InlineKeyboardButton(text="🛡️ VPN пользователя", callback_data="vpn_user2_callback")
)
user_find_data.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# кнопка ответа для админов, чтобы ответить на вопрос пользователя
def reply_keyboard(user_id) -> InlineKeyboardMarkup: 
    reply_keyboard = InlineKeyboardMarkup()
    reply_keyboard.add(
        InlineKeyboardButton(text="↩️ Ответить", callback_data=f"reply_keyboard_{user_id}")
    )
    return reply_keyboard

# кнопки по ответу пользователю после покупки пользователем VPN
reply_buy_keyboard = InlineKeyboardMarkup()
reply_buy_keyboard.add(
    InlineKeyboardButton(text="↩️ Ответить", callback_data="reply_buy_keyboard")
)
