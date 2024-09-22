import os 
import json
import dns.resolver
import datetime

from dotenv import load_dotenv
from typing import NamedTuple

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram.dispatcher.filters.state import StatesGroup, State

from bot.database.OperationsData import edit_operations_history, getting_operation_history
from bot.database.TempData import save_temp_message, get_temp_message, delete_temp_message, find_message_id
from bot.database.UserData import edit_profile, addind_vpn_count, get_balance, buy_operation, add_operation, pay_operation, get_referrer_info, check_promocode_used, save_promocode, find_user_data
from bot.database.VpnData import extend_vpn_state, get_vpn_data, update_vpn_other_info, update_vpn_half_info
from bot.database.SupportData import edit_data, getting_question

from bot.keyboards.user_keyboards import checking_message_limit, check_balance_keyboard,create_payment_keyboard, payment_type_keyboard, final_extend_some_vpn, profile_keyboard, support_to_moders, start_kb_handle, vpn_connection_type_keyboard, pay_netherlands_keyboard, help_kb, balance_handle_keyboard, find_balance_keyboard, ref_system_keyboard, support_keyboard, location_keyboard, pay_sweden_keyboard, pay_finland_keyboard, pay_germany_keyboard, replenishment_balance, back_keyboard, insturtion_keyboard, buy_keyboard, extend_keyboard, numbers_for_replenishment, addind_count_for_extend, promocode_keyboard, device_keyboard
from bot.keyboards.adm_keyboards import reply_keyboard, reply_buy_keyboard

from bot.utils.yoomoney_payment import yoomoney_check, create_yoomoney_payment
from bot.utils.nicepay_payment import nicepay_check, create_nicepay_payment
from bot.utils.outline import create_new_key, find_keys_info 

# импорт токенов из файла .env
load_dotenv('.env')
BOT_TOKEN = os.getenv("BOT_TOKEN")
BLAZER_CHAT_TOKEN = os.getenv("BLAZER_CHAT_TOKEN") 
ANUSH_CHAT_TOKEN = os.getenv("ANUSH_CHAT_TOKEN")
VPN_SWEDEN_PRICE_TOKEN = os.getenv("VPN_SWEDEN_PRICE_TOKEN") 
VPN_FINLAND_PRICE_TOKEN = os.getenv("VPN_FINLAND_PRICE_TOKEN")
VPN_GERMANY_PRICE_TOKEN = os.getenv("VPN_GERMANY_PRICE_TOKEN")
VPN_NETHERLANDS_PRICE_TOKEN = os.getenv("VPN_NETHERLANDS_PRICE_TOKEN")
PROMOCODE_TOKEN = os.getenv("PROMOCODE_TOKEN")

bot = Bot(BOT_TOKEN)

"""************************************************************* СОСТОЯНИЯ **********************************************************"""

class BuyVPNStates(StatesGroup):
    WAITING_FOR_MESSAGE_TEXT = State()

class PaymentStates(StatesGroup):
    WAITING_FOR_AMOUNT = State()
    WAITING_FOR_USER_EMAIL_HANDLE = State()
    WAINING_FOR_PAYMENT_TYPE = State()
    WAITING_FOR_MESSAGE_TEXT = State()

class SupportStates(StatesGroup):
    WAITING_FOR_QUESTION = State()
    WAITING_FOR_MODERATOR_ANSWER = State()

class PromocodeStates(StatesGroup):
    WAITING_FOR_USER_PROMOCODE = State()

class AdmCommandState(StatesGroup):
    WAITING_ID_OF_USER_FOR_DELETE = State()
    WAITING_ID_OF_USER_FOR_ADD = State()
    WAITING_ID_OF_USER_HANDLE_FOR_ADD = State()
    WAITING_ID_OF_USER_HANDLE_FOR_DELETE = State()
    WAITING_FOR_SUM_HANDLE_FOR_ADD = State()
    WAITING_FOR_SUM_HANDLE_FOR_DELETE = State()

class AdmButtonState(StatesGroup):
    WAITING_FOR_USER_ID_FOR_USER_INFO = State()
    WAITING_FOR_CALLBACK_BUTTONS = State()

class UserEmailState(StatesGroup):
    WAITING_FOR_USER_EMAIL = State()

class UserVPNInfo(StatesGroup):
    WAITING_FOR_USER_ID_FOR_USER_VPN_INFO = State()

class BanUserState(StatesGroup):
    WAITING_FOR_USER_ID = State()

class UnbanUserState(StatesGroup):
    WAITING_FOR_USER_ID = State()

class SupportRequest(NamedTuple):
    user_id: int
    user_name: str
    question: str
    answer: str = None

previous_markup = None
previous_states = {}
support_requests = []




"""************************************************* БАЗОВЫЕ КОМАНДЫ (/start, /help, /balance) *****************************************************"""
global start_message_for_reply
start_message_for_reply = """Добро пожаловать в <b>BlazerVPN</b> – ваш надежный партнер в обеспечении безопасной и анонимной связи в сети.

Наш сервис предлагает доступ к четырем локациям:<b>

• 🇸🇪 Швеция
• 🇫🇮 Финляндия
• 🇩🇪 Германия
• 🇳🇱 Нидерланды
</b>
Обеспечивая быструю и защищенную передачу данных. Независимо от того, где вы находитесь, <b>BlazerVPN</b> гарантирует конфиденциальность и безопасность вашей онлайн активности. Обеспечьте себе свободу и защиту в интернете с <b>BlazerVPN!</b>"""


# обработчик команды /start
async def start_cmd(message: Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    result = await find_user_data(user_id=user_id)
    if result == None or result == []: 
        start_command = message.text
        print(start_command)
        referrer_id = str(start_command[7:])
        if referrer_id != "":
            if referrer_id != str(user_id):
                await edit_profile(user_name, user_id, referrer_id)
                await message.answer_photo(photo="https://imgur.com/f9IQEVG", caption="• 🤝 <b>Реферальная система</b>:\n\nСпасибо за регистрацию! Бонусы успешно зачислились рефереру на баланс.\n\n<i>Подробнее о реферальной системе - /ref_system </i>", parse_mode="HTML", reply_markup=ref_system_keyboard)
                try:
                    await bot.send_photo(chat_id=referrer_id, photo="https://imgur.com/f9IQEVG", caption="• 🤝 <b>Реферальная система</b>:\n\nПо вашей реферальной ссылке зарегистровался новый пользователь.\nВам начислены: <code>20</code>₽ ", reply_markup=find_balance_keyboard, parse_mode="HTML")
                    await add_operation(int(20), referrer_id)
                    result = await find_user_data(user_id=referrer_id)
                    for items in result:
                        user_name = items[2]
                    await edit_operations_history(user_id=referrer_id, user_name=user_name, operations=(+int(20)), description_of_operation="🤝 Реферальная система")
                except:
                    pass
            else:
                await message.answer_photo(photo="https://imgur.com/f9IQEVG", caption="• 🤝 <b>Реферальная система</b>:\n\nВы не можете зарегистрироваться по собственной реферальной ссылке ❌\n\n<i>Подробнее о реферальной системе - /ref_system </i>", parse_mode="HTML", reply_markup=ref_system_keyboard)
                await edit_profile(user_name, user_id)
        else:
            await edit_profile(user_name, user_id)
            await message.answer_photo(photo="https://imgur.com/oaUI02P", caption=start_message_for_reply, reply_markup=start_kb_handle(user_id), parse_mode="HTML")
    else:
        await edit_profile(user_name, user_id)
        await message.answer_photo(photo="https://imgur.com/oaUI02P", caption=start_message_for_reply, reply_markup=start_kb_handle(user_id), parse_mode="HTML")
    await register_commands(message=message)

# обработчик кнопки balance (balance)
async def balance_def(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = await get_balance(user_id=user_id)
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/VfCjBuE", caption=f"• 💵 <b>Баланс</b>:\n\nВаш баланс: <code>{balance}</code> ₽\n\n<i>Чтобы пополнить свой баланс, вы можете использовать кнопку ниже, либо использовать команду - /replenishment</i>", parse_mode="HTML"), reply_markup=balance_handle_keyboard)


# обработчик кнопки help(help_callback)
async def help_kb_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/wz2wvor", caption="• 🧑‍💻 <b>Связь с разработчиком</b>:\n\nДля связи с разработчиком бота перейдите по <b><a href = 'https://t.me/KING_08001'>ссылке</a></b>", parse_mode="HTML"), reply_markup=help_kb)

"""*********************************************** ВЫБОР ЛОКАЦИИ И ПОКУПКА ВПН ************************************************************************"""
# обработка кнопки выбора локации (buy)
async def buying_VPN_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/7Qhm4tw", caption="• 📍 <b>Локация:</b>\n\nДоступные локации:", parse_mode="HTML"), reply_markup=location_keyboard)

# обработка кнопок локаций (Sweden_callback, Finland_callback, Germany_callback)
async def location_choose_def(callback: CallbackQuery, state: FSMContext):
    if callback.data == "Sweden_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: Швеция 🇸🇪\nВыберите протокол подключения вашего VPN:", parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Швеция 🇸🇪"))
    
    elif callback.data == "Netherlands_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: Нидерланды 🇳🇱\nВыберите протокол подключения вашего VPN:", parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Нидерланды 🇳🇱"))

    elif callback.data == "Finland_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: Финляндия 🇫🇮\nВыберите протокол подключения вашего VPN:",  parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Финляндия 🇫🇮"))

    elif callback.data == "Germany_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: Германия 🇩🇪\nВыберите протокол подключения вашего VPN:",  parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Германия 🇩🇪"))
    await callback.answer("")

async def choosing_vpn_connection_def(callback: CallbackQuery, state: FSMContext):
    location = callback.data.split(".")[1]
    if location == "Швеция 🇸🇪":
        price = await taking_vpn_price(country="Швеция 🇸🇪")
        kb = pay_sweden_keyboard
    elif location == "Нидерланды 🇳🇱":
        price = await taking_vpn_price(country="Нидерланды 🇳🇱")
        kb = pay_netherlands_keyboard
    elif location == "Финляндия 🇫🇮":
        price = await taking_vpn_price(country="Финляндия 🇫🇮")
        kb = pay_finland_keyboard
    elif location == "Германия 🇩🇪":
        price = await taking_vpn_price(country="Германия 🇩🇪")
        kb = pay_germany_keyboard
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/cXpphjT", caption=f"• 🛡 <b>Покупка VPN:</b>\n\nВы выбрали VPN на локации: {location}\nПротокол подключения: <code>Shadowsocks</code> 🧦\n\nСтоимость покупки данного VPN: <code>{price}</code> ₽", parse_mode="HTML"), reply_markup=kb)
    await callback.answer('')

# функция, которая обрабатывает покупку VPN.
async def buying_VPN_def(callback, country,  state):
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    balance = await get_balance(user_id=user_id)
    price = await taking_vpn_price(country=country)

    if int(balance) >= int(price):
        await buy_operation(user_id=user_id, user_name=user_name, price=price)

        expiration_date = datetime.datetime.now() + datetime.timedelta(days=28) # срок действия VPN 28 дней
        vpn_id = await update_vpn_half_info(user_id=user_id, user_name=user_name, location=country, expiration_days=expiration_date.strftime("%d.%m.%Y %H:%M:%S")) # сохранение данных пользователей и половину информации о впн в бд
        create_new_key(key_id=vpn_id, name=f"ID: {user_id}", data_limit_gb=100.0) # создание нового ключа для VPN
        vpn_key = find_keys_info(key_id=vpn_id) # получение ключа
        await update_vpn_other_info(vpn_key=vpn_key, vpn_id=vpn_id) # сохранение ключа в бд
        await addind_vpn_count(user_id=user_id)
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/cXpphjT", caption=f"• 🛒 <b>Покупка VPN</b>:\n\nТовар успешно был приобретён ✅\n\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\nОзнакомьтесь с нашей инструкцией по использованию VPN ниже по кнопке.", parse_mode="HTML"), reply_markup=insturtion_keyboard)
        await edit_operations_history(user_id=user_id, user_name=user_name, operations=(-(float(price))), description_of_operation="🛒 Покупка VPN")
        # if user_name != None:
        #     await bot.send_photo(photo="https://imgur.com/CLwDaV5", chat_id=BLAZER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\n• 🛒 <b>Заявка на активацию VPN:</b>\n\nПользователь @{user_name} \n(ID: <code>{user_id}</code>)\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        #     await bot.send_photo(photo="https://imgur.com/CLwDaV5", chat_id=ANUSH_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>:\n\n• 🛒 <b>Заявка на активацию VPN:</b>\n\nПользователь @{user_name} \n(ID: <code>{user_id}</code>)\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        #     await bot.send_photo(photo="https://imgur.com/CLwDaV5", chat_id=HELPER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>:\n\n• 🛒 <b>Заявка на активацию VPN:</b>\n\nПользователь @{user_name} \n(ID: <code>{user_id}</code>)\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        # else:
        #     await bot.send_photo(photo="https://imgur.com/CLwDaV5", chat_id=ANUSH_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>:\n\n• 🛒 <b>Заявка на активацию VPN:</b>\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id}</code>)\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        #     await bot.send_photo(photo="https://imgur.com/CLwDaV5", chat_id=BLAZER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\n• 🛒 <b>Заявка на активацию VPN:</b>\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id}</code>)\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        #     await bot.send_photo(photo="https://imgur.com/CLwDaV5", chat_id=HELPER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\n• 🛒 <b>Заявка на активацию VPN:</b>\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id}</code>)\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
    else:
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/2RUdfMp", caption="• 🛒 <b>Покупка VPN</b>:\n\nУ вас недостаточно средств ❌\n\n<i>Чтобы пополнить баланс, используйте кнопку ниже</i>", parse_mode="HTML"), reply_markup=replenishment_balance)
    await callback.answer("")
    
async def taking_vpn_price(country: str):
    price = 0
    if country == "Швеция 🇸🇪":
        price = VPN_SWEDEN_PRICE_TOKEN
        return price
    elif country == "Финляндия 🇫🇮":
        price = VPN_FINLAND_PRICE_TOKEN
        return price

    elif country == "Нидерланды 🇳🇱":
        price = VPN_NETHERLANDS_PRICE_TOKEN
        return price

    elif country == "Германия 🇩🇪":
        price = VPN_GERMANY_PRICE_TOKEN
        return price

# хендлер, который вызывает функцию, для обработки покупки VPN. Обрабатывает кнопки (Buying_sweden_VPN, Buying_finland_VPN, Buying_germany_VPN)
async def choosing_location_for_buying_VPN(callback: CallbackQuery, state: FSMContext):
    if callback.data == "Buying_sweden_VPN":
        await buying_VPN_def(callback, "Швеция 🇸🇪", state)
    elif callback.data == "Buying_finland_VPN":
        await buying_VPN_def(callback, "Финляндия 🇫🇮", state)
    elif callback.data == "Buying_germany_VPN":
        await buying_VPN_def(callback, "Германия 🇩🇪", state)
    elif callback.data == "Buying_netherlands_VPN":
        await buying_VPN_def(callback, "Нидерланды 🇳🇱", state)
    await callback.answer("")

"""******************************************************* СИСТЕМА ОБРАБОТКИ ПРОФИЛЯ ****************************************************"""

async def profile_handle(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_info = await find_user_data(user_id=user_id)
    for info in user_info:
        id = info[0]
        user_db_id = info[1]
        user_db_name = info[2]
        balance = info[3]
        time_of_registration = info[4]
        
        referrer_id = info[5]
        if referrer_id == None:
            referrer_id = "-"
        else:
            referrer_name = await find_user_data(user_id=referrer_id)
            referrer_id = f"@{referrer_name} (ID: <code>{referrer_id}</code>)"
        used_promocodes = info[6]
        if used_promocodes == None:
            used_promocodes = "<code>none</code>"
        else:
            used_promocodes = [f"<code>{promo}</code>" for promo in used_promocodes.split(",")]
            used_promocodes = ", ".join(used_promocodes)
        vpns_count = info[8]

    
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/tjRqQST", caption=f"• 👤 <b>Ваш профиль</b>:\n\n"
                                                            f"ID: <code>{id}</code>\n"
                                                            f"ID пользователя: <code>{user_db_id}</code>\n"
                                                            f"Баланс: <code>{balance}</code> ₽\n"
                                                            f"Дата регистрации: <code>{time_of_registration}</code>\n"
                                                            f"Использованные промокоды: {used_promocodes}\n"
                                                            f"Количество VPN за все время: <code>{vpns_count}</code>\n\n"
                                                            f"", parse_mode="HTML"), reply_markup=profile_keyboard)



"""******************************************************* СИСТЕМА ИНСТРУКЦИЙ ПО ИСПОЛЬЗОВАНИЮ VPN ****************************************************"""

# обработка кнопки (instruction_keyboard)
async def instruction_handle(callback: CallbackQuery):
    await callback.message.answer_photo(photo="https://imgur.com/99Kpo93", caption="• 📖 <b>Инструкция:</b>\n\nВыберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", parse_mode="HTML", reply_markup=device_keyboard)
    await callback.answer('')

"""*********************************************************** СИСТЕМА ПО ПРОДЛЕНИЮ VPN ******************************************************************"""

# хендлер для обработки кнопок для продления VPN(extend_vpn_info, extend_callback)
async def extend_vpn_handle(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data == "extend_vpn_info":
        user_id = callback.from_user.id
        vpn_data = await get_vpn_data(user_id=user_id)      
        if vpn_data is not None:      
            numbers = 0
            vpn_info_text = ""
            for id, user_db_id, user_db_name, location, expiration_date, vpn_key, days_remaining in vpn_data:
                numbers += 1
                if expiration_date is not None:
                    expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date_new - datetime.datetime.now()).days
                    vpn_info_text += f"{numbers}. ID: <code>{id}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n"
                else:
                    vpn_info_text += f"{numbers}. У вас имеется приобретенный VPN 🛡, который еще не обработан модераторами.\nОжидайте ответа модерации.\n\n"
                    numbers -= 1
            kb_for_count = addind_count_for_extend(count=numbers)
            price = await taking_vpn_price(country=location)
            if numbers == 1:
                await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Fv2UUEl", caption=f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}<b>Нажмите на кнопку, если готовы продлить VPN </b>🛡", parse_mode="HTML"), reply_markup=extend_keyboard)
            else:
                if callback.message.photo:
                    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Fv2UUEl", caption=f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}\n<b>Выберите VPN </b>🛡<b>, который хотите продлить:</b>", parse_mode="HTML"), reply_markup=kb_for_count)
                else: 
                    await callback.message.answer_photo(photo="https://imgur.com/Fv2UUEl", caption=f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}\nВыберите VPN </b>🛡<b>, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
        else: 
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/2RUdfMp", caption="• 🛡 <b>Продление VPN:</b>\n\nУ вас нету действующего VPN ❌! \n\n<i>Вам его необходимо приобрести, нажав на кнопку ниже, либо использовав команду -</i> /buy", parse_mode="HTML"), reply_markup=buy_keyboard)

    elif callback.data == "extend_sole_vpn":
        user_name = callback.from_user.username
        balance = await get_balance(user_id=user_id)
        user_id = callback.from_user.id
        id, user_db_id, user_db_name, location, expiration_date, vpn_key, days_remaining = await get_vpn_data(user_id=user_id)
        price = await taking_vpn_price(country=location)
        if int(price) <= int(balance):
            await pay_operation(price=price, user_id=user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(-(float(price))), description_of_operation="🛡 Продление VPN")
            new_expiration_date = expiration_date_new + datetime.timedelta(days=28)
            await extend_vpn_state(user_id=user_db_id, location=location, expiration_date=new_expiration_date, id=id)
            await addind_vpn_count(user_id=user_id)

            if callback.message.text is not None:
                await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/vME1ZnR", caption=f"• 🛡 <b>Продление VPN:</b>\n\nVPN продлен на <code>28</code>  дней ✅ \n\nДо окончания действия VPN осталось <code>{days_remaining + 28}</code> дней ⏳\n🔑 Ключ активации: <pre>{vpn_key}</pre>", parse_mode="HTML"), reply_markup=back_keyboard)
            vpn_info_text = f"ID: <code>{id}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date}</code>\n⏳ Осталось:   <code>{days_remaining + 28}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\n"
            if user_name != None:
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=ANUSH_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN</b>:\n\nПользователь @{user_name} \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=BLAZER_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN</b>:\n\nПользователь @{user_name} \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
            else:
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=BLAZER_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN</b>:\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=ANUSH_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN</b>:\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
        
        else:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/2RUdfMp", caption="• 💵 <b>Баланс</b>:\n\nУ вас недостаточно средств ❌\n\n<i>Чтобы пополнить свой баланс </i>💵 <i>нажмите на кнопку ниже</i>", parse_mode="HTML"), reply_markup=replenishment_balance)
    
    elif "extend_some_vpn" in callback.data:
        user_id = callback.from_user.id
        user_name = callback.from_user.username
        vpn_number = callback.data.split('_')[3]
        vpn_data = await get_vpn_data(user_id=user_id)
        vpn = vpn_data[int(vpn_number) - int(1)]
        id = vpn[0]
        location = vpn[3]
        expiration_date = datetime.datetime.strptime(vpn[4], "%d.%m.%Y %H:%M:%S")
        vpn_key = vpn[5]
        days_remaining = (expiration_date - datetime.datetime.now()).days
        price = await taking_vpn_price(country=location)
        vpn_info_text = f"ID: <code>{id}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\n"

        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Fv2UUEl", caption=f"• 🛡 <b>Продление VPN:</b>:\n\n{vpn_info_text}<b>Продление VPN на <code>28</code> дней стоит <code>{price}</code></b> ₽ 💵", parse_mode="HTML"), reply_markup=await final_extend_some_vpn(number=vpn_number))

    elif "final_extend_vpn" in callback.data:
        user_name = callback.from_user.username
        user_id = callback.from_user.id
        vpn_number = callback.data.split('_')[3]
        vpn_data = await get_vpn_data(user_id=user_id)
        vpn = vpn_data[int(vpn_number) - int(1)]
        id = vpn[0]
        location = vpn[3]
        expiration_date = datetime.datetime.strptime(vpn[4], "%d.%m.%Y %H:%M:%S")
        vpn_key = vpn[5]
        days_remaining = (expiration_date - datetime.datetime.now()).days
        new_expiration_date = expiration_date + datetime.timedelta(days=28)
        balance = await get_balance(user_id=user_id)
        price = await taking_vpn_price(country=location)
        if int(price) <= int(balance):
            await pay_operation(price=price, user_id=user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=int(-(float(price))), description_of_operation="🛡 Продление VPN")
            vpn_info_text = f"ID: <code>{id}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining + 28}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\n"
            await extend_vpn_state(user_id=user_id, location=location, expiration_date=new_expiration_date, id=id)
            await addind_vpn_count(user_id=user_id)
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/vME1ZnR", caption=f"• 🛡 <b>Продление VPN:</b>:\n\nVPN продлен на <code>28</code> дней ✅ \n\nДо окончания действия VPN осталось <code>{days_remaining + 28}</code> дней ⏳\n🔑 Ключ активации: <pre>{vpn_key}</pre>", parse_mode="HTML"), reply_markup=back_keyboard)
            if user_name != None:
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=ANUSH_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN:</b>\n\nПользователь @{user_name} \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=BLAZER_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN:</b>\n\nПользователь @{user_name} \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
            else:
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=ANUSH_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN:</b>\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_photo(photo="https://imgur.com/Fv2UUEl", chat_id=BLAZER_CHAT_TOKEN, caption=f"• 🛡 <b>Продление VPN:</b>\n\nПользователь без <b>USERNAME</b> \n(ID: <code>{user_id})</code>\nПродлил VPN 🛡 на <code>28</code> дней:\n\n{vpn_info_text}", parse_mode="HTML")
        else:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/2RUdfMp", caption="• 💵 <b>Баланс</b>:\n\nУ вас недостаточно средств ❌\nЧтобы пополнить свой баланс 💵 нажмите на кнопку ниже, либо используйте команду - /replenishment", parse_mode="HTML"), reply_markup=replenishment_balance)
    await callback.answer("")

"""**************************************************** СИСТЕМА ПОПОЛНЕНИЯ БАЛАНСА **********************************************************"""

# обработка кнопки для оплаты(replenishment)
async def replenishment_handle(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/GedgOxd", caption="• 💵 <b>Пополнение баланса</b>:\n\nВыберите сумму пополнения 💵, либо введите нужную самостоятельно: ", parse_mode="HTML"), reply_markup=numbers_for_replenishment)
    await PaymentStates.WAITING_FOR_AMOUNT.set()
    await callback.answer("")

# обработка выбора суммы пополнения баланса пользователя
async def choosing_int_for_replenishment(callback: CallbackQuery, state):
    global amount
    if callback.data == "100_for_replenishment_callback":
        amount = 100
    elif callback.data == "200_for_replenishment_callback":
        amount = 200
    elif callback.data == "500_for_replenishment_callback":
        amount = 500

    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/GedgOxd", caption="• 💵 <b>Пополнение баланса</b>:\n\nВыберите платежную систему:", parse_mode="HTML"), reply_markup=await payment_type_keyboard(price=amount))

# обработка пополнения баланса
async def handle_amount(message: Message, state):
    try:
        global amount
        amount = int(message.text)
        if amount > 2:
            await message.answer_photo(photo="https://imgur.com/GedgOxd", caption="• 💵 <b>Пополнение баланса</b>:\n\nВыберите платежную систему:", parse_mode="HTML", reply_markup=await payment_type_keyboard(price=amount))
            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nСлишком много попыток ❌ \n\nПопробуйте заново - /replenishment", reply_markup=back_keyboard, parse_mode="HTML")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nСумма пополнения должна быть больше <code>50</code> ₽ ❌", parse_mode="HTML")
    except ValueError:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nСлишком много попыток ❌\n\nПопробуйте заново - /replenishment ", reply_markup=back_keyboard, parse_mode="HTML")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nВведите корректную сумму (число) ❌", parse_mode="HTML")

async def handle_payment_type(callback: CallbackQuery, state):
    if "yoomoney_callback" in callback.data:
        amount = int(callback.data.split("_")[2])
        payment_url, payment_id = create_yoomoney_payment(float(amount))
        payment_button = await create_payment_keyboard(payment_url=payment_url, payment_id=payment_id, payment_type="yoomoney")
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/GedgOxd", caption="• 💵 <b>Пополнение баланса</b>:\n\nСчет на оплату сформирован. ✅", parse_mode="HTML"), reply_markup=payment_button)
        await state.finish() 

    elif "nicepay_callback" in callback.data:
        amount = int(callback.data.split("_")[2])
        await state.update_data(amount=amount)
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/GedgOxd", caption=f"• 💵 <b>Пополнение баланса</b>:\n\nВы выбрали платежную систему: 💳<code> NicePay</code>\nСумма платежа: <code>{amount}</code>\n\nДля продолжения процесса оплаты, введите свою электронную почту:", parse_mode="HTML"), reply_markup=back_keyboard) 
        await UserEmailState.WAITING_FOR_USER_EMAIL.set()
        await state.finish()

async def handle_user_email(message: Message, state):
    email = message.text
    amount = await state.get_data("amount")
    try:
        domain = email.split('@')[1]
        resolver = dns.resolver.Resolver()
        answers = resolver.query(domain, 'MX')

        if answers:
            amount = float(amount['amount'])  
            payment_url, payment_id = create_nicepay_payment(float(amount), email=email)
            payment_button = await create_payment_keyboard(payment_url=payment_url, payment_id=payment_id, payment_type="nicepay")
            await message.answer_photo(photo="https://imgur.com/GedgOxd", caption="• 💵 <b>Пополнение баланса</b>:\n\nСчет на оплату сформирован. ✅", parse_mode="HTML", reply_markup=payment_button) 
            await state.finish()
        else:
            attempts = await state.get_data("attempts")
            if attempts.get("attempts", 0) >= 3:
                await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nСлишком много попыток ❌\n\nПопробуйте заново - /replenishment ", reply_markup=back_keyboard, parse_mode="HTML")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nВведите верную почту ❌", parse_mode="HTML")

    except Exception as e:
        attempts = await state.get_data("attempts")
        if attempts.get("attempts", 0) >= 3:
            await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nСлишком много попыток ❌\n\nПопробуйте заново - /replenishment ", reply_markup=back_keyboard, parse_mode="HTML")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 💵 <b>Пополнение баланса</b>:\n\nВведите верную почту ❌", parse_mode="HTML")        
            print(f"Ошибка DNS-запроса: {e}")

          
# обработка кнопки, для проверки успешного пополнения(checking_payment_)
async def succesfull_payment(callback: CallbackQuery):
    if "yoomoney" in callback.data:
        payment_id = yoomoney_check(callback.data.split('_')[-1])
        user_name = callback.from_user.username
        user_id = callback.from_user.id
        if payment_id == True:
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/jMVwz7i", caption=f'• 💵 <b>Пополнение баланса</b>:\n\nОплата на сумму <code>{amount}</code> <b>₽</b> прошла успешно ✅ \n\nЧтобы узнать свой баланс - /balance', parse_mode="HTML"), reply_markup=check_balance_keyboard)
            await add_operation(amount, user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(amount))), description_of_operation="💵 Пополнение баланса")
        elif payment_id == False:
            await callback.answer('Оплата еще не прошла.')
    
    elif "nicepay" in callback.data:
        payment_id = nicepay_check(callback.data.split('_')[-1])
        user_name = callback.from_user.username
        user_id = callback.from_user.id
        if payment_id == True:
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/jMVwz7i", caption=f'• 💵 <b>Пополнение баланса</b>:\n\nОплата на сумму <code>{amount}</code> <b>₽</b> прошла успешно ✅ \n\nЧтобы узнать свой баланс - /balance', parse_mode="HTML"), reply_markup=check_balance_keyboard)
            await add_operation(amount, user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(amount))), description_of_operation="💵 Пополнение баланса")
        elif payment_id == False:
            await callback.answer('Оплата еще не прошла.')
    await callback.answer('')

"""**************************************************** СИСТЕМА ПОДДЕРЖКИ ********************************************************"""
### половина системы находится в файле bot.adm_handlers.py

# обработка кнопка поддержки (support_callback)
async def support_handle(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/K4hLFUD", caption="• 🆘 <b>Система поддержки</b>:\n\nЧтобы связаться с модераторами, нажмите на кнопку ниже.", parse_mode="HTML"), reply_markup=support_to_moders)
    await callback.answer("")

# обработка отправления сообщения от пользователя модераторам
# async def process_question(message: Message,  state: FSMContext):
#     user_id = message.from_user.id
#     user_name = message.from_user.username
#     question = message.text
#     await edit_data(user_name=user_name, user_id=user_id, question=question)
#     await message.answer("• 🆘 <b>Система поддержки</b>:\n\nВопрос отправлен модератору! Ожидайте ответ в этом чате.", reply_markup=start_kb_handle(user_id), parse_mode="HTML")
#     if user_name != None:
#         await bot.send_photo(BLAZER_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nЗадал вопрос:\n\n<b>{question}</b>", reply_markup=reply_keyboard(user_id), parse_mode="HTML")
#         await bot.send_photo(ANUSH_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nЗадал вопрос:\n\n<b>{question}</b>", reply_markup=reply_keyboard(user_id), parse_mode="HTML")
#     else:
#         await bot.send_photo(BLAZER_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nПользователь без <b>USERNAME</b> (ID: <code>{user_id})</code>\nЗадал вопрос:\n\n<b>{question}</b>", reply_markup=reply_keyboard(user_id), parse_mode="HTML")
#         await bot.send_photo(ANUSH_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nПользователь без <b>USERNAME</b> (ID: <code>{user_id})</code>\nЗадал вопрос:\n\n<b>{question}</b>", reply_markup=reply_keyboard(user_id), parse_mode="HTML")
#     if message.reply_markup:
#         await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
#     else:
#         await save_temp_message(message.from_user.id, message.text, None)
#     await state.finish()
    
"""************************************************* РЕФЕРАЛЬНАЯ СИСТЕМА **************************************************"""

# обработка реферальной системы 
async def ref_system(callback: CallbackQuery):
    user_id = callback.from_user.id
    text = ""
    referrals = await get_referrer_info(user_id)
    if referrals:
        text = f"• 🤝 <b>Реферальная система</b>:\n<pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\n<i>Поделитесь этой ссылкой со своими знакомыми, чтобы получить <code>20</code> ₽ себе на баланс.</i>\n\n"
        
        text += "<b>Ваши рефералы:</b>\n\n"
        for referer_id, referer_name in referrals:
            if referer_name: 
                text += f"@{referer_name} (ID: <code>{referer_id}</code>) \n"
            else:
                text += f"Пользователь без USERNAME (ID: <code>{referer_id}</code>)\n"
    else:
        text += f"• 🤝 <b>Реферальная система</b>:\n<pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\n<i>Поделитесь этой ссылкой со своими знакомыми, чтобы получить <code>20</code> ₽ себе на баланс.</i>\n\nУ вас нету рефералов."
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/UcKZLFn", caption=text, parse_mode="HTML"), reply_markup=back_keyboard)
    await callback.answer("")

# обработка ожидания промокода от пользователя
async def promo_handle(callback: CallbackQuery, state):
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/CwQn7Qv", caption="• 🎟 <b>Система промокодов</b>:\n\nВведите действующий промокод:", parse_mode="HTML"), reply_markup=back_keyboard)
    await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()
    await callback.answer("")

# обработка введенного промокода пользователя
async def handle_user_promo(message: Message, state):
    user_promo = message.text
    user_id = message.from_user.id
    user_name = message.from_user.username
    check_used_promo = await check_promocode_used(user_id, user_promo)
    if user_promo in PROMOCODE_TOKEN and check_used_promo == False:
        await message.answer_photo(photo="https://imgur.com/nkB75M2", caption="• 🎟 <b>Система промокодов</b>:\n\nВы ввели правильный промокод ✅\n\nНа ваш баланс зачислено: <code>20</code> рублей 💵!", reply_markup=back_keyboard, parse_mode="HTML")
        await add_operation(20, user_id)
        await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(20))), description_of_operation="🎟 Промокод")
        await save_promocode(user_id, user_promo)
        await state.finish()

    elif user_promo in PROMOCODE_TOKEN and check_used_promo == True:
        await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 🎟 <b>Система промокодов</b>:\n\nВы уже использовали данный промокод ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard, parse_mode="HTML")    
        await state.finish()

    else:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 🎟 <b>Система промокодов</b>:\n\nСлишком много попыток ❌\n\nПопробуйте заново - /promocode ", reply_markup=back_keyboard, parse_mode="HTML")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 🎟 <b>Система промокодов</b>:\n\nВы ввели неправильный промокод, либо он неактуален ❌\n\nСледите за новостями в нашем сообществе в вк\n\nПопробуйте ввести промокод еще раз:", reply_markup=promocode_keyboard, parse_mode="HTML")
 
"""******************************** ОБРАБОТКА ИНФОРМАЦИИ О СОБСТВЕННОМ VPN ПОЛЬЗОВАТЕЛЕЙ *******************************"""

# обработка информации о личных VPN пользователей
async def my_vpn_handle(callback: CallbackQuery):
    user_id = callback.from_user.id
    vpn_data = await get_vpn_data(user_id=user_id)

    if vpn_data != []:
        vpn_info_text = "• 🛡 <b>Ваши VPN</b>:\n\n"
        numbers = 0
        is_send = False
        for vpn in vpn_data:
            numbers += 1
            location = vpn[3]
            expiration_date = vpn[4]
            vpn_key = vpn[5]
            expiration_date_new = datetime.datetime.strptime(str(expiration_date), "%d.%m.%Y %H:%M:%S")
            days_remaining = (expiration_date_new - datetime.datetime.now()).days
            vpn_info_text += f"{numbers}. ID: <code>{vpn[0]}</code>\n📍 Локация: <code>{location}</code>\n"
            vpn_info_text += f"🕘 Дата окончания:   <code>{expiration_date}</code>\n"
            vpn_info_text += f"⏳ Осталось:   <code>{days_remaining}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\n"

            if numbers > 4:
                await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/4NwMie5", caption=vpn_info_text, parse_mode="HTML"), reply_markup=checking_message_limit(0))
                is_send = True
                break

        if is_send == False:
            await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/4NwMie5", caption=vpn_info_text, parse_mode="HTML"), reply_markup=buy_keyboard)
    else:
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/weO3juR", caption=f"• 🛡 <b>Ваши VPN</b>:\n\nВы не имеете действующего VPN ❌\n\n<i>Чтобы купить VPN, воспользуйтесь кнопкой ниже, либо используйте команду</i> - /buy", parse_mode="HTML"), reply_markup=buy_keyboard)
    await callback.answer("")

async def handle_continue_myvpn(callback: CallbackQuery):
    user_id = callback.from_user.id
    vpn_data = await get_vpn_data(user_id=user_id)

    part_number = int(callback.data.split('_')[2])
    if part_number == 1:
        number = 5
    elif part_number == 2:
        number = 9
    elif part_number == 3:
        number = 13
    vpn_info_text = "• 🛡 <b>Ваши VPN</b>:\n\n"
    numbers = 4
    if vpn_data != None or vpn_data != []:
        for vpn in enumerate(vpn_data[number - 1:], start=number):
            numbers += 1
            location = vpn[1][3]
            expiration_date = vpn[1][4]
            vpn_key = vpn[1][5]
            expiration_date_new = datetime.datetime.strptime(str(expiration_date), "%d.%m.%Y %H:%M:%S")
            days_remaining = (expiration_date_new - datetime.datetime.now()).days
            vpn_info_text += f"{numbers}. ID: <code>{vpn[1][0]}</code>\n📍 Локация: <code> {location}</code>\n"
            vpn_info_text += f"🕘 Дата окончания:   <code>{expiration_date}</code>\n"
            vpn_info_text += f"⏳ Осталось:   <code>{days_remaining}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\n"

            if number >= 8:
                await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/4NwMie5", caption=vpn_info_text, parse_mode="HTML"), reply_markup=checking_message_limit(1))
                break
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/4NwMie5", caption=vpn_info_text, parse_mode="HTML"), reply_markup=buy_keyboard)
    else:
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/weO3juR", caption=f"• 🛡 <b>Ваши VPN</b>:\n\nВы не имеете действующего VPN ❌\n\n<i>Чтобы купить VPN, воспользуйтесь кнопкой ниже, либо используйте команду</i> - /buy", parse_mode="HTML"), reply_markup=buy_keyboard)
    await callback.answer("")
            
"""***************************************** СИСТЕМА ИСТОРИИ ОПЕРАЦИЙ *****************************************"""
# обработка информации о истории операций пользователя
async def history_of_opeartions_handle(callback: CallbackQuery):
    user_id = callback.from_user.id
    operation_history = await getting_operation_history(user_id=user_id)
    if operation_history is None or operation_history == []:
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/weO3juR", caption="• 📋 <b>История операций</b>:\n\nУ вас нет истории операций ❌", parse_mode="HTML"), reply_markup=replenishment_balance)
        return
    message_text = "• 📋 <b>История операций</b>:\n\n"
    for operation in operation_history:
        id, user_db_id, user_db_name, operations, time_of_operation, description_of_operation = operation
        operations = operations.split(",")
        time_of_operation = time_of_operation.split(",")
        description_of_operation = description_of_operation.split(",")

        for i in range(len(operations)):
            operation_value = operations[i]
            if "-" not in operation_value:
                operation_value = "+" + operation_value

            message_text += f"<i>{time_of_operation[i]}</i> - <b>{description_of_operation[i]}</b>:  <code>{operation_value}</code> ₽\n"
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/QnZumh4", caption=message_text, parse_mode="HTML"), reply_markup=back_keyboard)
    await callback.answer("")

"""************************************************ СИСТЕМА ВОЗВРАЩЕНИЯ К ПРЕДЫДУЩИМ СООБЩЕНИЯМ ********************************************"""

# команда для сохранения положения кнопок при возвращении к предыдущему сообщению
def deserialize_keyboard(keyboard_json: str) -> InlineKeyboardMarkup:
    keyboard_data = json.loads(keyboard_json)
    keyboard = InlineKeyboardMarkup()

    for row in keyboard_data['inline_keyboard']:
        keyboard.row(*[
            InlineKeyboardButton(text=button['text'], callback_data=button['callback_data'])
            for button in row
        ])

    return keyboard

# система возвращения к предыдущим сообщениям
async def back_handle(callback: CallbackQuery, state):
    user_id = callback.from_user.id
    await state.finish()
    user_id = callback.from_user.id
    message_id = await find_message_id(user_id)
    
    if message_id:
        message_text, message_markup, photo_url = await get_temp_message(user_id, message_id)
        try:
            if message_text and message_markup and photo_url:
                message_markup = deserialize_keyboard(message_markup)
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=photo_url, caption=message_text, parse_mode="HTML"), 
                    reply_markup=message_markup
                )
            else:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media="https://imgur.com/oaUI02P", caption=start_message_for_reply, parse_mode="HTML"), 
                    reply_markup=start_kb_handle(user_id)
                )
        except Exception as e:
            await callback.message.answer_photo(
                photo="https://imgur.com/oaUI02P", 
                caption=start_message_for_reply, 
                reply_markup=start_kb_handle(user_id), 
                parse_mode="HTML"
            )
    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(media="https://imgur.com/oaUI02P", caption=start_message_for_reply, parse_mode="HTML"), 
            reply_markup=start_kb_handle(user_id)
        )
    await callback.answer("")

async def register_commands(message: Message) -> None:
    if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN):
        await bot.set_my_commands(commands=[
            BotCommand("start", "🔁 Обновить бота"),
            BotCommand("help", "📋 Узнать список команд"),
            BotCommand("balance", "💵 Узнать свой баланс"),
            BotCommand("connect_with_dev", "🧑‍💻 Связаться с разработчиком бота"),
            BotCommand("buy", "🛒 Купить VPN"),
            BotCommand("extend_vpn", "⌛️ Продлить VPN"),
            BotCommand("replenishment", "💵 Пополнить баланс"),
            BotCommand("support", "🆘 Задать вопрос"),
            BotCommand("my_vpn", "🛡 Мои VPN"),
            BotCommand("ref_system", "🤝 Реферальная система"),
            BotCommand("history_of_operations", "📋 История операций"),
            BotCommand("instruction", "📄 Инструкция по использованию VPN"),
            BotCommand("profile", "👤 Профиль"),
            BotCommand("user_info", "🗃 Данные о пользователях"),
            BotCommand("user_vpn", "🛡️ VPN пользователей"),
            BotCommand("add", "💵 Пополнение баланса"),
            BotCommand("delete", "💵 Удаление баланса"),
            BotCommand("ban", "❌ Заблокировать пользователя"),
            BotCommand("unban", "✅ Разблокировать пользователя"),
            BotCommand("add_vpn", "🛡️ Добавить VPN"),
            BotCommand("delete_vpn", "🛡️ Удалить VPN"),
            BotCommand("user_history", "📋 История операций пользователя")
            ])
    else:
        await bot.set_my_commands(commands=[
            BotCommand("start", "🔁 Обновить бота"),
            BotCommand("help", "📋 Узнать список команд"),
            BotCommand("balance", "💵 Узнать свой баланс"),
            BotCommand("connect_with_dev", "🧑‍💻 Связаться с разработчиком бота"),
            BotCommand("buy", "🛒 Купить VPN"),
            BotCommand("extend_vpn", "⌛️ Продлить VPN"),
            BotCommand("replenishment", "💵 Пополнить баланс"),
            BotCommand("support", "🆘 Задать вопрос"),
            BotCommand("my_vpn", "🛡 Мои VPN"),
            BotCommand("ref_system", "🤝 Реферальная система"),
            BotCommand("history_of_operations", "📋 История операций"),
            BotCommand("instruction", "📄 Инструкция по использованию VPN"),
            BotCommand("profile", "👤 Профиль")
            ])


"""**************************************************** СИСТЕМА РЕГИСТРИРОВАНИЯ ВСЕХ ХЕНДЛЕРОВ *****************************************************"""

def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_cmd, commands=['start'], state="*")
    dp.register_callback_query_handler(balance_def, lambda c: c.data == "balance", state="*")
    dp.register_callback_query_handler(help_kb_handle, lambda c: c.data == "help_callback", state="*")
    dp.register_callback_query_handler(buying_VPN_handle, lambda c: c.data == "buy", state="*")
    dp.register_callback_query_handler(profile_handle, lambda c: c.data == "profile_callback", state="*")
    dp.register_callback_query_handler(location_choose_def, lambda c: c.data == "Sweden_callback" or c.data == "Finland_callback" or c.data == "Germany_callback" or c.data == "Netherlands_callback", state="*")
    dp.register_callback_query_handler(choosing_vpn_connection_def, lambda c: "vpn_connection_type_callback" in c.data, state="*")
    dp.register_callback_query_handler(choosing_location_for_buying_VPN, lambda c: c.data == "Buying_sweden_VPN" or c.data == "Buying_finland_VPN" or c.data == "Buying_germany_VPN" or c.data == "Buying_netherlands_VPN")
    dp.register_callback_query_handler(instruction_handle, lambda c: c.data == "instruction_keyboard")
    dp.register_callback_query_handler(extend_vpn_handle, lambda c: c.data == "extend_vpn_info" or c.data == "extend_sole_vpn" or "extend_some_vpn" in c.data or "final_extend_vpn" in c.data, state="*")
    dp.register_callback_query_handler(replenishment_handle, lambda c: c.data == "replenishment", state="*")
    dp.register_callback_query_handler(choosing_int_for_replenishment, lambda c: c.data == "100_for_replenishment_callback" or c.data == "200_for_replenishment_callback" or c.data == "500_for_replenishment_callback", state="*")
    dp.register_message_handler(handle_amount, state=PaymentStates.WAITING_FOR_AMOUNT)
    dp.register_callback_query_handler(handle_payment_type, lambda c: "yoomoney_callback" in c.data or "nicepay_callback" in c.data, state="*")
    dp.register_callback_query_handler(succesfull_payment, lambda c: "checking_nicepay_payment" in c.data or "checking_yoomoney_payment" in c.data, state="*")
    dp.register_callback_query_handler(support_handle, lambda c: c.data == "support_callback", state="*")
    dp.register_message_handler(handle_user_email, state=UserEmailState.WAITING_FOR_USER_EMAIL)
    # dp.register_message_handler(process_question, state=SupportStates.WAITING_FOR_QUESTION)
    dp.register_callback_query_handler(ref_system, lambda c: c.data == "ref_system_callback", state="*")
    dp.register_callback_query_handler(promo_handle, lambda c: c.data == "promo_callback", state="*")
    dp.register_message_handler(handle_user_promo, state=PromocodeStates.WAITING_FOR_USER_PROMOCODE)
    dp.register_callback_query_handler(my_vpn_handle, lambda c: c.data == "myvpn_callback", state="*")
    dp.register_callback_query_handler(handle_continue_myvpn, lambda c: "vpn_info_" in c.data, state="*")
    dp.register_callback_query_handler(history_of_opeartions_handle, lambda c: c.data == "history_of_operations_callback", state="*")
    dp.register_callback_query_handler(back_handle, lambda c: c.data == "back", state="*")
