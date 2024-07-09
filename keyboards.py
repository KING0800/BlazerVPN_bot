from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard = InlineKeyboardMarkup()
start_keyboard.add(
            InlineKeyboardButton(text="Купить VPN 🛒", callback_data="buy_vpn"),
            InlineKeyboardButton(text="Продлить VPN ⌛️", callback_data="extension_vpn")
)
start_keyboard.add(
    InlineKeyboardButton(text="Мои VPN🛡️", callback_data="myvpn_callback")
)
start_keyboard.add(
            InlineKeyboardButton(text="Узнать баланс 💵", callback_data="balance")
)
start_keyboard.add(
    InlineKeyboardButton(text="Связь с разрабочиком 🧑‍💻", callback_data="help_callback"),
    InlineKeyboardButton(text="Поддержка 🆘", callback_data="support_callback")
)
start_keyboard.add(
    InlineKeyboardButton(text="Реферальная система 🤝", callback_data="ref_system_callback"),
    InlineKeyboardButton(text="Промокоды🎟", callback_data="promo_callback")
)

location_keyboard = InlineKeyboardMarkup()
location_keyboard.add(
            #InlineKeyboardButton(text="Швеция 🇸🇪", callback_data="Sweden_callback"),
            InlineKeyboardButton(text="Финляндия 🇫🇮", callback_data="Finland_callback")
            #InlineKeyboardButton(text="Германия 🇩🇪", callback_data="Germany_callback"),
)
location_keyboard.add(
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

pay_sweden_keyboard = InlineKeyboardMarkup()
pay_sweden_keyboard.add(
    InlineKeyboardButton(text="Купить 🛒", callback_data="Buying_sweden_VPN"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

pay_finland_keyboard = InlineKeyboardMarkup()
pay_finland_keyboard.add(
    InlineKeyboardButton(text="Купить 🛒", callback_data="Buying_finland_VPN"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)
pay_germany_keyboard = InlineKeyboardMarkup()
pay_germany_keyboard.add(
    InlineKeyboardButton(text="Купить 🛒", callback_data="Buying_germany_VPN"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

replenishment_balance = InlineKeyboardMarkup()
replenishment_balance.add(
    InlineKeyboardButton(text="Пополнить баланс 💵", callback_data="replenishment"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

back_keyboard = InlineKeyboardMarkup()
back_keyboard.add(
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

reply_buy_keyboard = InlineKeyboardMarkup()
reply_buy_keyboard.add(
    InlineKeyboardButton(text="Ответить ↩️", callback_data="reply_buy_keyboard")
)


reply_keyboard = InlineKeyboardMarkup()
reply_keyboard.add(
    InlineKeyboardButton(text="Ответить ↩️", callback_data="reply_keyboard")
)

insturtion_keyboard = InlineKeyboardMarkup()
insturtion_keyboard.add(
    InlineKeyboardButton(text="Инструкция 📖", callback_data="instruction_keyboard")
)

buy_keyboard = InlineKeyboardMarkup()
buy_keyboard.add(
    InlineKeyboardButton(text="Купить VPN 🛒", callback_data="buy_vpn"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

extend_keyboard = InlineKeyboardMarkup()
extend_keyboard.add(
    InlineKeyboardButton(text="Продлить VPN 💵", callback_data="extend_callback"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)
own_vpn_keyboard = InlineKeyboardMarkup()
own_vpn_keyboard.add(
    InlineKeyboardButton(text="Купить VPN 🛒", callback_data="buy_vpn"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)
numbers_for_replenishment = InlineKeyboardMarkup()
numbers_for_replenishment.add(
    InlineKeyboardButton(text="200 💵", callback_data="200_for_replenishment_callback"),
    InlineKeyboardButton(text="500 💵", callback_data="500_for_replenishment_callback"),
    InlineKeyboardButton(text="1000 💵", callback_data="1000_for_replenishment_callback")
)
numbers_for_replenishment.add(
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)
async def addind_count_for_extend(count):
    numbers_for_extend = InlineKeyboardMarkup()
    numbers_for_extend.row() 
    for i in range(1, count + 1):
        numbers_for_extend.insert(InlineKeyboardButton(text=f"{i}.", callback_data=f"extend_vpn_{i}"))
    numbers_for_extend.add(
        InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
    )
    return numbers_for_extend

payment_type = InlineKeyboardMarkup()
payment_type.add(
    InlineKeyboardButton(text="Банковской картой 💳", callback_data="bank_card_payment_callback"),
    InlineKeyboardButton(text="Кошелек ЮMoney", callback_data="yoomoney_payment_callback")
)
payment_type.add(
    InlineKeyboardButton(text="TinkoffPay", callback_data="TinkoffPay_callback"),
    InlineKeyboardButton(text="SberPay", callback_data="SberPay_callback")
)
payment_type.add(
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)

promocode_keyboard = InlineKeyboardMarkup()
promocode_keyboard.add(
    InlineKeyboardButton(text="Сообщество VK", url="https://vk.com/blazervpn"),
    InlineKeyboardButton(text="Назад ⬅️", callback_data="back")
)