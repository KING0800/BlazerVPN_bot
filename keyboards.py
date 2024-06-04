from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard = InlineKeyboardMarkup()
start_keyboard.add(
            InlineKeyboardButton(text="Купить VPN", callback_data="buy_vpn"),
            InlineKeyboardButton(text="Продлить VPN", callback_data="extension_vpn")
)
start_keyboard.add(
            InlineKeyboardButton(text="Узнать баланс", callback_data="balance")
)


location_keyboard = InlineKeyboardMarkup()
location_keyboard.add(
            InlineKeyboardButton(text="Швеция 🇸🇪", callback_data="Sweden_callback"),
            InlineKeyboardButton(text="Финляндия 🇫🇮", callback_data="Finland_callback"),
            InlineKeyboardButton(text="Германия 🇩🇪", callback_data="Germany_callback"),
)
location_keyboard.add(
    InlineKeyboardButton(text="Назад", callback_data="back")
)

pay_sweden_keyboard = InlineKeyboardMarkup()
pay_sweden_keyboard.add(
            InlineKeyboardButton(text="Купить", callback_data="Buying_sweden_VPN")
)

pay_finland_keyboard = InlineKeyboardMarkup()
pay_finland_keyboard.add(
            InlineKeyboardButton(text="Купить", callback_data="Buying_finland_VPN")
)

pay_germany_keyboard = InlineKeyboardMarkup()
pay_germany_keyboard.add(
            InlineKeyboardButton(text="Купить", callback_data="Buying_germany_VPN")
)
pay_sweden_keyboard.add(
    InlineKeyboardButton(text="Назад", callback_data="back")
)

replenishment_balance = InlineKeyboardMarkup()
replenishment_balance.add(
            InlineKeyboardButton(text="Пополнить баланс", callback_data="replenishment")
)
replenishment_balance.add(
    InlineKeyboardButton(text="Назад", callback_data="back")
)

back_keyboard = InlineKeyboardMarkup()
back_keyboard.add(
    InlineKeyboardButton(text="Назад", callback_data="back")
)

reply_keyboard = InlineKeyboardMarkup()
reply_keyboard.add(
    InlineKeyboardButton(text="Ответить", callback_data="reply_keyboard")
)

insturtion_keyboard = InlineKeyboardMarkup()
insturtion_keyboard.add(
    InlineKeyboardButton(text="Инструкция", callback_data="instruction_keyboard")
)

