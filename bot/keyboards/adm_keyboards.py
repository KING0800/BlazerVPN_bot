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
    InlineKeyboardButton(text="❌ Заблокировать", callback_data="ban_user_callback"),
    InlineKeyboardButton(text="✅ Разблокировать", callback_data="unban_user_callback")
)
adm_panel_keyboard.add(
    InlineKeyboardButton(text="🛡️ Добавить VPN", callback_data="add_vpn_callback"),
    InlineKeyboardButton(text="🛡️ Удалить VPN", callback_data="delete_vpn_callback")
)
adm_panel_keyboard.add(
    InlineKeyboardButton(text="📋 История операций пользователя", callback_data="user_history_callback")
)
adm_panel_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# кнопки по управлению определенным пользователем
user_find_data = InlineKeyboardMarkup()
user_find_data.add(
    InlineKeyboardButton(text="❌ Заблокировать", callback_data="ban_user2_callback"),
    InlineKeyboardButton(text="✅ Разблокировать", callback_data="unban_user2_callback")
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
def reply_buy_keyboard(pay_id, country, user_id) -> InlineKeyboardMarkup:
    reply_buy_keyboard = InlineKeyboardMarkup()
    reply_buy_keyboard.add(
        InlineKeyboardButton(text="↩️ Ответить", callback_data=f"reply_buy_keyboard.{pay_id}.{country}.{user_id}")
    )
    return reply_buy_keyboard


about_yourself_to_add_keyboard = InlineKeyboardMarkup()
about_yourself_to_add_keyboard.add(
    InlineKeyboardButton(text="💵 Для себя", callback_data="about_yourself_callback")
)
about_yourself_to_add_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

about_yourself_to_delete_keyboard = InlineKeyboardMarkup()
about_yourself_to_delete_keyboard.add(
    InlineKeyboardButton(text="💵 Для себя", callback_data="about_yourself_to_delete_callback")

)
about_yourself_to_delete_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

finish_buy_vpn = InlineKeyboardMarkup()
finish_buy_vpn.add(
    InlineKeyboardButton(text="⌛️ Продлить VPN", callback_data="extend_vpn_info"),
    InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction_keyboard")
)

extension_keyboard = InlineKeyboardMarkup()
extension_keyboard.add(
    InlineKeyboardButton(text="⌛️ Продлить VPN", callback_data="extend_vpn_info")
)

buy_info_keyboard = InlineKeyboardMarkup()
buy_info_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить VPN", callback_data="buy")
)

def location_kb(user_id: int | str, user_name: str) -> InlineKeyboardMarkup:
    location_keyboard = InlineKeyboardMarkup()
    location_keyboard.add(
            # InlineKeyboardButton(text="🇫🇮 Финляндия", callback_data=f"Finland_callback_{user_id}_{user_name}"),   
            # InlineKeyboardButton(text="🇩🇪 Германия", callback_data=f"Germany_callback_{user_id}_{user_name}"),
            InlineKeyboardButton(text="🇸🇪 Швеция", callback_data=f"Sweden_callback_{user_id}_{user_name}"),
            # InlineKeyboardButton(text="🇳🇱 Нидерланды", callback_data="fNetherlands_callback_{user_id}_{user_name}"),
    )        
    location_keyboard.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return location_keyboard

async def vpn_connection_type_keyboard(location, user_id) -> InlineKeyboardMarkup:
    vpn_connection_type_keyboard = InlineKeyboardMarkup()
    vpn_connection_type_keyboard.add(
        InlineKeyboardButton(text="🧦 Shadowsocks", callback_data=f"vpn_connection_type_adm.{location}.{user_id}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
    )
    return vpn_connection_type_keyboard

def pay_sweden_keyboard(user_id) -> InlineKeyboardMarkup:
    pay_sweden_keyboard = InlineKeyboardMarkup()
    pay_sweden_keyboard.add(
        InlineKeyboardButton(text="🛒 Купить", callback_data=f"Buying_sweden_adm.{user_id}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return pay_sweden_keyboard

# обработка покупки VPN на локации Финляндия
def pay_finland_keyboard(user_id) -> InlineKeyboardMarkup:
    pay_finland_keyboard = InlineKeyboardMarkup()
    pay_finland_keyboard.add(
        InlineKeyboardButton(text="🛒 Купить", callback_data=f"Buying_finland_adm.{user_id}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return pay_finland_keyboard

# обработка покупки VPN на локации Германия
def pay_germany_keyboard(user_id) -> InlineKeyboardMarkup:
    pay_germany_keyboard = InlineKeyboardMarkup()
    pay_germany_keyboard.add(
        InlineKeyboardButton(text="🛒 Купить", callback_data=f"Buying_germany_adm.{user_id}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return pay_germany_keyboard

def pay_netherlands_keyboard(user_id) -> InlineKeyboardMarkup:
    pay_netherlands_keyboard = InlineKeyboardMarkup()
    pay_netherlands_keyboard.add(
        InlineKeyboardButton(text="🛒 Купить", callback_data=f"Buying_netherlands_adm.{user_id}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return pay_netherlands_keyboard