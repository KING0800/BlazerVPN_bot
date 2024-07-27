import os 

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

load_dotenv('.env')

BLAZER_CHAT_TOKEN = os.getenv("BLAZER_CHAT_TOKEN") 
ANUSH_CHAT_TOKEN = os.getenv("ANUSH_CHAT_TOKEN")

# стартовая клавиатура, чтобы управлять вообще ботом
def start_kb_handle(user_id) -> InlineKeyboardMarkup:
    start_keyboard = InlineKeyboardMarkup()
    start_keyboard.add(
                InlineKeyboardButton(text="🛒 Купить VPN ", callback_data="buy"),
                InlineKeyboardButton(text="⌛️ Продлить VPN", callback_data="extension_vpn")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="🛡️ Мои VPN", callback_data="myvpn_callback")
    )
    start_keyboard.add(
                InlineKeyboardButton(text="💵 Узнать баланс", callback_data="balance")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="🧑‍💻 Связь с разрабочиком", callback_data="help_callback"),
        InlineKeyboardButton(text="🆘 Поддержка", callback_data="support_callback")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="🤝 Реферальная система", callback_data="ref_system_callback"),
        InlineKeyboardButton(text="🎟 Промокоды", callback_data="promo_callback")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="📋 История операций", callback_data="history_of_operations_callback")
    )
    if int(user_id) == int(BLAZER_CHAT_TOKEN) or int(user_id) == int(ANUSH_CHAT_TOKEN):
        start_keyboard.add(
            InlineKeyboardButton(text="🤖 Админ панель", callback_data="adm_panel_callback")
        )
        return start_keyboard
    else:
        return start_keyboard
    
# клавиатура для системы поддержки
support_keyboard = InlineKeyboardMarkup()
support_keyboard.add(
        InlineKeyboardButton(text="🆘 Поддержка", callback_data="support_callback")
)

# клавиатура для выбора локаций при покупки VPN
location_keyboard = InlineKeyboardMarkup()
location_keyboard.add(
            #InlineKeyboardButton(text="🇸🇪 Швеция", callback_data="Sweden_callback"),
            InlineKeyboardButton(text="🇫🇮 Финляндия", callback_data="Finland_callback")
            #InlineKeyboardButton(text="🇩🇪 Германия", callback_data="Germany_callback"),
)
location_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# обработка покупки VPN на локации Швеция
pay_sweden_keyboard = InlineKeyboardMarkup()
pay_sweden_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить", callback_data="Buying_sweden_VPN"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# обработка покупки VPN на локации Финляндия
pay_finland_keyboard = InlineKeyboardMarkup()
pay_finland_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить", callback_data="Buying_finland_VPN"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# обработка покупки VPN на локации Германия
pay_germany_keyboard = InlineKeyboardMarkup()
pay_germany_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить", callback_data="Buying_germany_VPN"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура для пополнения баланса
replenishment_balance = InlineKeyboardMarkup()
replenishment_balance.add(
    InlineKeyboardButton(text="💵 Пополнить баланс", callback_data="replenishment"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура для перехода к предыдущему сообщению
back_keyboard = InlineKeyboardMarkup()
back_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура по обработке инструкций
insturtion_keyboard = InlineKeyboardMarkup()
insturtion_keyboard.add(
    InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction_keyboard")
)

# клавиатура по покупке VPN
buy_keyboard = InlineKeyboardMarkup()
buy_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить VPN", callback_data="buy"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура по продлению VPN
extend_keyboard = InlineKeyboardMarkup()
extend_keyboard.add(
    InlineKeyboardButton(text="💵 Продлить VPN", callback_data="extend_callback"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура для выбора суммы пополнения
numbers_for_replenishment = InlineKeyboardMarkup()
numbers_for_replenishment.add(
    InlineKeyboardButton(text="💵 200", callback_data="200_for_replenishment_callback"),
    InlineKeyboardButton(text="💵 500", callback_data="500_for_replenishment_callback"),
    InlineKeyboardButton(text="💵 1000", callback_data="1000_for_replenishment_callback")
)
numbers_for_replenishment.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# кнопка для выбора VPN, которого нужно продлить
def addind_count_for_extend(count) -> InlineKeyboardMarkup:
    numbers_for_extend = InlineKeyboardMarkup()
    numbers_for_extend.row() 
    for i in range(1, count + 1):
        numbers_for_extend.insert(InlineKeyboardButton(text=f"{i}.", callback_data=f"extend_vpn_{i}"))
    numbers_for_extend.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return numbers_for_extend

# клавиатура по выбору платежной системы
payment_type = InlineKeyboardMarkup()
payment_type.add(
    InlineKeyboardButton(text="💳 Банковской картой", callback_data="bank_card_payment_callback"),
    InlineKeyboardButton(text="💳 Кошелек ЮMoney", callback_data="yoomoney_payment_callback")
)
payment_type.add(
    InlineKeyboardButton(text="💳 TinkoffPay", callback_data="TinkoffPay_callback"),
    InlineKeyboardButton(text="💳 SberPay", callback_data="SberPay_callback")
)
payment_type.add(
    InlineKeyboardButton(text="💳 СБП", callback_data="SBP_callback")
)
payment_type.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура для системы промокодов
promocode_keyboard = InlineKeyboardMarkup()
promocode_keyboard.add(
    InlineKeyboardButton(text="Сообщество VK", url="https://vk.com/blazervpn"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура по выбору девайса, по которому человек хочет получить инструкцию
device_keyboard = InlineKeyboardMarkup()
device_keyboard.add(
    InlineKeyboardButton(text="📱 Android", callback_data="Android_device_callback"),
    InlineKeyboardButton(text="🍏 iOS", callback_data="IOS_device_callback")
)
device_keyboard.add(
    InlineKeyboardButton(text="🖥 Windows", callback_data="komp_device_callback"),
    InlineKeyboardButton(text="🍏 MacOS", callback_data="MacOS_callback")
)
device_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)

ref_system_keyboard = InlineKeyboardMarkup()
ref_system_keyboard.add(
    InlineKeyboardButton(text="🤝 Реферальная система", callback_data="ref_system_callback"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)

find_balance_keyboard = InlineKeyboardMarkup()
find_balance_keyboard.add(
    InlineKeyboardButton(text="💵 Узнать баланс", callback_data="balance"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)

balance_handle_keyboard = InlineKeyboardMarkup()
balance_handle_keyboard.add(
    InlineKeyboardButton(text="💵 Пополнить баланс", callback_data="replenishment"),
    InlineKeyboardButton(text="📋 История операций", callback_data="history_of_operations_callback")
)
balance_handle_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)

help_kb = InlineKeyboardMarkup()
help_kb.add(
    InlineKeyboardButton(text="Связь с разработчиком 🧑‍💻", url="https://t.me/KING_08001"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)