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
                InlineKeyboardButton(text="⌛️ Продлить VPN", callback_data="extend_vpn_info")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="🛡️ Список моих VPN", callback_data="myvpn_callback")
    )
    start_keyboard.add(
                InlineKeyboardButton(text="💵 Узнать свой баланс", callback_data="balance")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="🧑‍💻 Разработчик", callback_data="help_callback"),
        InlineKeyboardButton(text="🆘 Поддержка", callback_data="support_callback")
    )
    start_keyboard.add(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile_callback")
    )
    if int(user_id) == int(BLAZER_CHAT_TOKEN) or int(user_id) == int(ANUSH_CHAT_TOKEN):
        start_keyboard.add(
            InlineKeyboardButton(text="🤖 Панель администратора", callback_data="adm_panel_callback")
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
        # InlineKeyboardButton(text="🇫🇮 Финляндия", callback_data="Finland_callback"),   
        InlineKeyboardButton(text="🇩🇪 Германия", callback_data="Germany_callback"),
        InlineKeyboardButton(text="🇸🇪 Швеция", callback_data="Sweden_callback"),
        InlineKeyboardButton(text="🇳🇱 Нидерланды", callback_data="Netherlands_callback")
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

pay_netherlands_keyboard = InlineKeyboardMarkup()
pay_netherlands_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить", callback_data="Buying_netherlands_VPN"),
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
    InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction_keyboard.answer"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура по покупке VPN
buy_keyboard = InlineKeyboardMarkup()
buy_keyboard.add(
    InlineKeyboardButton(text="🛒 Купить VPN", callback_data="buy"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)
buy_keyboard.add(
    InlineKeyboardButton(text="📖 Инструкция", callback_data="instruction_keyboard.edit")
)

# клавиатура по продлению VPN
extend_keyboard = InlineKeyboardMarkup()
extend_keyboard.add(
    InlineKeyboardButton(text="💵 Продлить VPN", callback_data="extend_sole_vpn"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура для выбора суммы пополнения
numbers_for_replenishment = InlineKeyboardMarkup()
numbers_for_replenishment.add(
    InlineKeyboardButton(text="💵 100", callback_data="100_for_replenishment_callback"),
    InlineKeyboardButton(text="💵 200", callback_data="200_for_replenishment_callback"),
    InlineKeyboardButton(text="💵 500", callback_data="500_for_replenishment_callback")
)
numbers_for_replenishment.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# кнопка для выбора VPN, которого нужно продлить
def addind_count_for_extend(count) -> InlineKeyboardMarkup:
    numbers_for_extend = InlineKeyboardMarkup()
    numbers_for_extend.row() 
    for i in range(1, count + 1):
        numbers_for_extend.insert(InlineKeyboardButton(text=f"{i}.", callback_data=f"extend_some_vpn_{i}"))
    numbers_for_extend.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return numbers_for_extend

async def final_extend_some_vpn(number) -> InlineKeyboardMarkup:    
    final_extend_some_vpn = InlineKeyboardMarkup()
    final_extend_some_vpn.add(
        InlineKeyboardButton(text="⌛️ Продлить VPN", callback_data=f"final_extend_vpn_{number}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return final_extend_some_vpn

# клавиатура по выбору платежной системы
async def payment_type_keyboard(price: int) -> InlineKeyboardMarkup:
    payment_type = InlineKeyboardMarkup()
    payment_type.add(
        InlineKeyboardButton(text="💳 YooMoney", callback_data=f"yoomoney_callback_{price}"),
        InlineKeyboardButton(text="💳 YooKassa", callback_data=f"yookassa_callback_{price}")
        # InlineKeyboardButton(text="💳 NicePay", callback_data=f"nicepay_callback_{price}"),
    )
    payment_type.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return payment_type

async def create_payment_keyboard(payment_id: str, payment_url: str, payment_type: str) -> InlineKeyboardMarkup:
    payment_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", url=payment_url),
                InlineKeyboardButton(text="Проверить оплату", callback_data=f"checking_{payment_type}_payment_{payment_id}")
            ]
        ]
    )
    print(payment_id)
    payment_button.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return payment_button

# клавиатура для системы промокодов
promocode_keyboard = InlineKeyboardMarkup()
promocode_keyboard.add(
    InlineKeyboardButton(text="Канал", url="https://t.me/blazervpn"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
)

# клавиатура по выбору девайса, по которому человек хочет получить инструкцию
device_keyboard = InlineKeyboardMarkup()
device_keyboard.add(
    InlineKeyboardButton(text="📱 Android", url="https://telegra.ph/Nastrojka-dlya-Android-08-28"),
    InlineKeyboardButton(text="🍏 iOS", url="https://telegra.ph/Nastrojka-dlya-IOS-08-28")
)
device_keyboard.add(
    InlineKeyboardButton(text="🖥  Windows", url="https://telegra.ph/Nastrojka-dlya-Windows-08-28"),
    InlineKeyboardButton(text="🍏 MacOS", url="https://telegra.ph/Nastrojka-dlya-MacOS-08-28")
)
device_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)

ref_system_keyboard = InlineKeyboardMarkup()
ref_system_keyboard.add(
    InlineKeyboardButton(text="🤝 Рефералка", callback_data="ref_system_callback"),
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
    InlineKeyboardButton(text="🧑‍💻 Разработчик", url="https://t.me/KING_08001"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)

support_to_moders = InlineKeyboardMarkup()
support_to_moders.add(
    InlineKeyboardButton(text="🆘 Модерация", url="https://t.me/blazer_helper"),
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)
async def vpn_connection_type_keyboard(location) -> InlineKeyboardMarkup:
    vpn_connection_type_keyboard = InlineKeyboardMarkup()
    vpn_connection_type_keyboard.add(
        InlineKeyboardButton(text="🧦 Shadowsocks", callback_data=f"vpn_connection_type_callback.{location}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
    )
    return vpn_connection_type_keyboard

profile_keyboard = InlineKeyboardMarkup()
profile_keyboard.add(
    InlineKeyboardButton(text="🤝 Рефералка", callback_data="ref_system_callback"),
    InlineKeyboardButton(text="🎟 Промокоды", callback_data="promo_callback")
)
profile_keyboard.add(
    InlineKeyboardButton(text="📋 История операций", callback_data="history_of_operations_callback"),
    InlineKeyboardButton(text="💵 Пополнить баланс", callback_data="replenishment")

)    
profile_keyboard.add(
    InlineKeyboardButton(text="⬅️ Назад", callback_data="back") 
)    

check_balance_keyboard = InlineKeyboardMarkup()
check_balance_keyboard.add(
    InlineKeyboardButton(text="💵 Узнать баланс", callback_data="balance")
)
check_balance_keyboard.add(
    InlineKeyboardButton(text="❓ Проблема с оплатой?", url="https://t.me/blazer_helper")
)

def checking_message_limit(current_message_part: int) -> InlineKeyboardMarkup:
    check_message_limit_kb = InlineKeyboardMarkup()
    check_message_limit_kb.add(
        InlineKeyboardButton(text=f"Следующая страница ({current_message_part + 1})", callback_data=f'vpn_info_{current_message_part + 1}')
)
    check_message_limit_kb.add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
) 
    
    return check_message_limit_kb

def verify_user(ref_id: int) -> InlineKeyboardMarkup:
    verify_user_kb = InlineKeyboardMarkup()
    verify_user_kb.add(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"verify_user.{ref_id}"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
    )
    return verify_user_kb