import os 
import dns.resolver
import re
import json

from dotenv import load_dotenv
from typing import NamedTuple
import datetime

from aiogram import types, Dispatcher, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.database.OperationsData import edit_operations_history, getting_operation_history
from bot.database.TempData import save_temp_message, get_temp_message, delete_temp_message, find_message_id
from bot.database.UserData import edit_profile, get_balance, buy_operation, pay_operation, get_referrer_username, check_promocode_used, save_promocode, find_user_data, ban_users_handle, unban_users_handle, is_user_ban_check
from bot.database.VpnData import save_order_id, extend_vpn_state, get_vpn_data
from bot.database.SupportData import edit_data, getting_question

from bot.keyboards.user_keyboards import start_kb_handle, help_kb, balance_handle_keyboard, find_balance_keyboard, ref_system_keyboard, support_keyboard, location_keyboard, pay_sweden_keyboard, pay_finland_keyboard, pay_germany_keyboard, replenishment_balance, back_keyboard, insturtion_keyboard, buy_keyboard, extend_keyboard, numbers_for_replenishment, addind_count_for_extend, payment_type, promocode_keyboard, device_keyboard
from bot.keyboards.adm_keyboards import reply_keyboard, reply_buy_keyboard

from bot.utils.payment import check, create_payment

# импорт токенов из файла .env
load_dotenv('.env')
BOT_TOKEN = os.getenv("BOT_TOKEN")
BLAZER_CHAT_TOKEN = os.getenv("BLAZER_CHAT_TOKEN") 
ANUSH_CHAT_TOKEN = os.getenv("ANUSH_CHAT_TOKEN")
VPN_PRICE_TOKEN = os.getenv("VPN_PRICE_TOKEN") 
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

Наш сервис предлагает доступ к трем локациям 📍:<b>
• 🇸🇪 Швеция
• 🇫🇮 Финляндия
• 🇩🇪 Германия
</b>
Обеспечивая быструю и защищенную передачу данных. Независимо от того, где вы находитесь, <b>BlazerVPN</b> гарантирует конфиденциальность и безопасность вашей онлайн активности. Обеспечьте себе свободу и защиту в интернете с <b>BlazerVPN!</b>"""


# обработчик команды /start
async def start_cmd(message: types.Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    result = await find_user_data(user_id=user_id)
    if result == None or result == []: 
        start_command = message.text
        referrer_id = str(start_command[7:])
        if referrer_id != "":
            if referrer_id != str(user_id):
                await edit_profile(user_name, user_id, referrer_id)
                await message.answer("• 🤝 <b>Реферальная система</b>:\n\nСпасибо за регистрацию! Бонусы успешно зачислились рефереру на баланс.\n\n<i>Подробнее о реферальной системе - /ref_system </i>", parse_mode="HTML", reply_markup=ref_system_keyboard)
                try:
                    await bot.send_message(referrer_id, "• 🤝 <b>Реферальная система</b>:\n\nПо вашей реферальной ссылке зарегистровался новый пользователь.\nВам начислены: <code>15</code>₽ ", reply_markup=find_balance_keyboard, parse_mode="HTML")
                    await pay_operation(int(15), referrer_id)
                    result = await find_user_data(user_id=referrer_id)
                    for items in result:
                        user_name = items[2]
                    await edit_operations_history(user_id=referrer_id, user_name=user_name, operations=(+int(15)), description_of_operation="🤝 Реферальная система")
                except:
                    pass
            else:
                await message.answer("• 🤝 <b>Реферальная система</b>:\n\nВы не можете зарегистрироваться по собственной реферальной ссылке ❌\n\n<i>Подробнее о реферальной системе - /ref_system </i>", parse_mode="HTML", reply_markup=ref_system_keyboard)
                await edit_profile(user_name, user_id)
        else:
            await edit_profile(user_name, user_id)
            await message.answer(start_message_for_reply, reply_markup=start_kb_handle(user_id), parse_mode="HTML")
    else:
        await edit_profile(user_name, user_id)
        await message.answer(start_message_for_reply, reply_markup=start_kb_handle(user_id), parse_mode="HTML")

    await save_temp_message(user_id, None, None)


# обработчик кнопки balance (balance)
async def balance_def(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        balance = await get_balance(user_name)
        await callback.message.edit_text(f"• 💵 <b>Баланс</b>:\n\nВаш баланс: <code>{balance}</code> ₽\n\n<i>Чтобы пополнить свой баланс, вы можете использовать кнопку ниже, либо использовать команду - /replenishment</i>", reply_markup=balance_handle_keyboard, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработчик кнопки help(help_callback)
async def help_kb_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("• 🧑‍💻 <b>Связь с разработчиком</b>:\n\nДля связи с разработчиком бота перейдите по <b><a href = 'https://t.me/KING_08001'>ссылке</a></b>", reply_markup=help_kb, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

"""*********************************************** ВЫБОР ЛОКАЦИИ И ПОКУПКА ВПН ************************************************************************"""
# обработка кнопки выбора локации (buy)
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("• 📍 <b>Выбор локации</b>:\n\nВыберите подходящую для вас локацию:\n\n<tg-spoiler><i>В скором времени будут добавлены дополнительные локации</i></tg-spoiler>", reply_markup=location_keyboard, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработка кнопок локаций (Sweden_callback, Finland_callback, Germany_callback)
async def location_choose_def(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id    
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "Sweden_callback":
            await callback.message.edit_text(f"📍 Вы выбрали локацию: Швеция 🇸🇪\nVPN на данной локации сейчас нету в наличии ❌", reply_markup=back_keyboard)
            #await callback.message.edit_text(f"Вы выбрали локацию: Швеция 🇸🇪\nСтоимость данного товара {VPN_PRICE_TOKEN} ₽", reply_markup=pay_sweden_keyboard)
            #await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            #await callback.answer("")

        elif callback.data == "Finland_callback":
            await callback.message.edit_text(f"• 📍 <b>Выбор локации</b>:\n\nВы выбрали локацию 📍: Финляндия 🇫🇮\nСтоимость данного товара <code>{VPN_PRICE_TOKEN}</code> ₽", reply_markup=pay_finland_keyboard, parse_mode="HTML")
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            await callback.answer("")

        elif callback.data == "Germany_callback":
            await callback.message.edit_text(f"📍 Вы выбрали локацию: Германия 🇩🇪\nVPN на данной локации сейчас нету в наличии ❌", reply_markup=back_keyboard)
            #await callback.message.edit_text(f"Вы выбрали локацию: Германия 🇩🇪\nСтоимость данного товара {VPN_PRICE_TOKEN} ₽", reply_markup=pay_germany_keyboard)
            #await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            #await callback.answer("")

# функция, которая обрабатывает покупку VPN.
async def buying_VPN_def(callback, country,  state):
    """Обработчик покупки VPN для заданной страны"""
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    balance = await get_balance(user_name)
    if float(balance) < float(VPN_PRICE_TOKEN):
        await callback.answer("У вас недостаточно средств ❌")
        await callback.message.edit_text("• 💵 <b>Баланс</b>:\n\nЧтобы пополнить свой баланс 💵 нажмите на кнопку, либо используйте команду - /replenishment", reply_markup=replenishment_balance, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        await buy_operation(user_id=user_id, user_name=user_name)
        await callback.message.edit_text("• 🛒 <b>Покупка VPN</b>:\n\nВы купили товар ✅! Ожидайте подготовки товара модераторами. Ключ активации VPN будет отправлен в этом чате.", parse_mode="HTML")
        user_id = callback.from_user.id
        order_id = await save_order_id(user_id=user_id, user_name=user_name, location=country)
        await edit_operations_history(user_id=user_id, user_name=user_name, operations=(-(float(VPN_PRICE_TOKEN))), description_of_operation="🛒 Покупка VPN")
        await bot.send_message(BLAZER_CHAT_TOKEN, f"• 🛒 <b>Покупка VPN</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nЗаказал VPN на локации 📍: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        await bot.send_message(ANUSH_CHAT_TOKEN, f"• 🛒 <b>Покупка VPN</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nЗаказал VPN на локации 📍: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard(pay_id=order_id, country=country, user_id=user_id), parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# хендлер, который вызывает функцию, для обработки покупки VPN. Обрабатывает кнопки (Buying_sweden_VPN, Buying_finland_VPN, Buying_germany_VPN)
async def choosing_location_for_buying_VPN(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "Buying_sweden_VPN":
            await buying_VPN_def(callback, "Швеция 🇸🇪", state)
        elif callback.data == "Buying_finland_VPN":
            await buying_VPN_def(callback, "Финляндия 🇫🇮", state)
        elif callback.data == "Buying_germany_VPN":
            await buying_VPN_def(callback, "Германия 🇩🇪", state)

"""******************************************************* СИСТЕМА ИНСТРУКЦИЙ ПО ИСПОЛЬЗОВАНИЮ VPN ****************************************************"""

# обработка кнопки (instruction_keyboard)
async def instruction_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.answer("• 📖 <b>Инструкция:</b>\n\nВыберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", reply_markup=device_keyboard, parse_mode="HTML")
        await callback.answer('')
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработка выбора девайса пользователя для получения инструкции по использованию VPN
async def device_instruction_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "Android_device_callback":
            await callback.message.answer_photo(photo="https://i.imgur.com/0feN5h0.jpeg", caption="""
        Настройка для Android:
        1. Загрузите приложение WireGuard из Google Play.
        2. Для добавления туннеля WireGuard нажмите на кнопку «плюс» в нижнем углу экрана и выберите опцию. Здесь можно загрузить конфигурацию из скачанного файла конфигурации (которую мы прикрепили к этой ниже) или ввести данные вручную.""")
            await callback.message.answer_photo(photo="https://i.imgur.com/MvB2M5t.png", caption="""
        3. Нажмите на переключатель рядом с появившимся именем туннеля. Система Android попросит выдать WireGuard разрешения для работы в качестве VPN. Дайте разрешение. После этого соединение будет установлено, в статус-баре будет отображаться знак в виде ключа""", reply_markup=back_keyboard)
            
        elif callback.data == "IOS_device_callback":
            await callback.message.answer_photo(photo="https://i.imgur.com/x6Cawdu.png", caption="1. Скачайте приложение из AppStore."
    "2. Откройте ссылку на конфигурационный файл или отсканируйте QR-код. Конфиг и QR-код можно найти в письме, которое пришло после установки сервера, или в панели управления, если вы используете готовый сервис VPN."
    "3. Далее выберите опцию «Открыть в приложении “WireGuard”».")
            await callback.message.answer_photo(photo="https://i.imgur.com/fj5p8dJ.png", caption="4. Отобразится окно подтверждения на разрешение конфигурации. Выберите «Разрешить» (конфигурационный файл будет добавлен в исключения брандмауэра).")
            await callback.message.answer_photo(photo="https://i.imgur.com/scb4Or8.png", caption="1. Перейдите приложение «WireGuard»."
    "2. Найдите созданное подключение и переведите его статус в положение «Включено».", reply_markup=back_keyboard)

        elif callback.data == "komp_device_callback":
            await callback.message.answer_photo(photo="https://i.imgur.com/rzF9gGw.png", caption="Настройка для Windows:"
    "1. Скачайте приложение WireGuard с официального сайта."
    "2. Скачайте конфигурационный файл — из письма, которое пришло после установки сервера, или из панели управления, если вы используете готовый сервис VPN."
    "3. В приложении WireGuard нажмите кнопку «Импорт туннелей из файла» (либо «Добавить туннель») и выберите файл с расширением .conf.")  
            await callback.message.answer_photo(photo="https://i.imgur.com/Hk7mmoc.png", caption="4. Нажмите кнопку «Подключить» для соединения с VPN-сервером.", reply_markup=back_keyboard)
        
        elif callback.data == "MacOS_callback":
            await callback.message.answer_photo(photo="https://i.imgur.com/2SjrQTL.png", caption="Настройка для MacOS:"
    "1. Скачайте приложение Wireguard с официального сайта или из AppStore."
    "2. Скачайте конфигурационный файл — из письма, которое пришло после установки сервера, или из панели управления, если вы используете готовый сервис VPN."
    "3. Откройте приложение WireGuard и выберите «Управлять туннелями Wireguard»."
    "4. Нажмите кнопку «Импорт туннелей из файла».")
            await callback.message.answer_photo(photo="https://i.imgur.com/ZGpSp5V.png", caption="5. Выберите скачанный ранее конфигурационный файл .conf. Далее отобразится окно подтверждения на разрешение конфигурации.")
            await callback.message.answer_photo(photo="https://i.imgur.com/tRCkXZf.png", caption="Готово. Для подключения к VPN нажмите кнопку «Подключить».", reply_markup=back_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

"""*********************************************************** СИСТЕМА ПО ПРОДЛЕНИЮ VPN ******************************************************************"""

# хендлер для обработки кнопок для продления VPN(extension_vpn, extend_callback)
async def extend_vpn_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "extension_vpn":
            user_id = callback.from_user.id
            vpn_data = await get_vpn_data(user_id)
            if vpn_data:
                numbers = 0
                vpn_info_text = ""
                for vpn in vpn_data:
                    numbers += 1
                    location = vpn[3]
                    active = vpn[4]
                    expiration_date = datetime.datetime.strptime(str(vpn[5]), "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date - datetime.datetime.now()).days
                    vpn_info_text += f"{numbers}. 📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n"
                kb_for_count = addind_count_for_extend(count=numbers)
                if numbers == 1:
                    await callback.message.edit_text(f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}<b>Продление VPN на 30 дней стоит <code>{VPN_PRICE_TOKEN}</code> ₽ 💵\nНажмите на кнопку, если готовы продлить VPN </b>🛡", reply_markup=extend_keyboard, parse_mode="HTML")
                else:
                    await callback.message.edit_text(f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}<b>Продление VPN на 30 дней стоит <code>{VPN_PRICE_TOKEN}</code> ₽ 💵. \nВыберите VPN </b>🛡<b>, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else: 
                await callback.message.edit_text("• 🛡 <b>Продление VPN:</b>\n\nУ вас нету действующего VPN ❌! \n\n<i>Вам его необходимо приобрести, нажав на кнопку ниже, либо использовав команду -</i> /buy", reply_markup=buy_keyboard, parse_mode="HTML")
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

        elif callback.data == "extend_callback":
            user_name = callback.from_user.username
            balance = await get_balance(user_name)
            user_id = callback.from_user.id
            if float(balance) >= float(VPN_PRICE_TOKEN):
                await pay_operation(VPN_PRICE_TOKEN, user_id)
                await edit_operations_history(user_id=user_id, user_name=user_name, operations=(-(float(VPN_PRICE_TOKEN))), description_of_operation="🛡 Продление VPN")
                vpn_data = await get_vpn_data(user_id)
                days_remaining = ""
                for vpn in vpn_data:
                    id = vpn[0]
                    location = vpn[3]
                    active = vpn[4]
                    expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                    name_of_vpn = vpn[6]
                    vpn_config = vpn[7]
                    days_remaining = (expiration_date - datetime.datetime.now()).days
                new_expiration_date = expiration_date + datetime.timedelta(days=30)
                await extend_vpn_state(user_id=user_id, location=location, active=True, expiration_date=new_expiration_date, id=id)    
                await callback.message.edit_text(f"• 🛡 <b>Продление VPN:</b>\n\nVPN продлен на <code>30</code>  дней ✅ \n\nДо окончания действия VPN осталось <code>{days_remaining + 30}</code> дней ⏳", reply_markup=back_keyboard, parse_mode="HTML")
                vpn_info_text = f"📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining + 30}</code> дней\n\n"
                await bot.send_document(ANUSH_CHAT_TOKEN, vpn_config, caption=f"• 🛡 <b>Продление VPN</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nПродлил VPN 🛡 на 30 дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_document(BLAZER_CHAT_TOKEN, vpn_config, caption=f"• 🛡 <b>Продление VPN</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nПродлил VPN 🛡 на 30 дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            else:
                await callback.answer("У вас недостаточно средств ❌")
                await callback.message.edit_text("• 💵 <b>Баланс</b>:\n\nУ вас недостаточно средств ❌\n\n<i>Чтобы пополнить свой баланс </i>💵 <i>нажмите на кнопку ниже, либо используйте команду - </i>/replenishment", reply_markup=replenishment_balance, parse_mode="HTML")
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        
        elif "extend_vpn" in callback.data:
            user_id = callback.from_user.id
            user_name = callback.from_user.username
            vpn_number = callback.data.split('_')[2]
            vpn_data = await get_vpn_data(user_id)
            vpn = vpn_data[int(vpn_number) - int(1)]
            balance = await get_balance(user_name)
            if float(balance) >= float(VPN_PRICE_TOKEN):
                await pay_operation(VPN_PRICE_TOKEN, user_id)
                await edit_operations_history(user_id=user_id, user_name=user_name, operations=int(-(float(VPN_PRICE_TOKEN))), description_of_operation="🛡 Продление VPN")
                id = vpn[0]
                location = vpn[3]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                name_of_vpn = vpn[6]
                vpn_config = vpn[7]
                days_remaining = (expiration_date - datetime.datetime.now()).days
                new_expiration_date = expiration_date + datetime.timedelta(days=30)
                vpn_info_text = f"📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining + 30}</code> дней\n\n"
                await extend_vpn_state(user_id=user_id, location=location, active=True, expiration_date=new_expiration_date, id=id)
                await callback.message.edit_text(f"• 🛡 <b>Продление VPN:</b>:\n\nVPN продлен на <code>30</code> дней ✅ \n\nДо окончания действия VPN осталось <code>{days_remaining + 30}</code> дней ⏳", reply_markup=back_keyboard, parse_mode="HTML")
                await bot.send_document(ANUSH_CHAT_TOKEN, vpn_config, caption=f"• 🛡 <b>Продление VPN:</b>\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nПродлил VPN 🛡 на 30 дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_document(BLAZER_CHAT_TOKEN, vpn_config, caption=f"• 🛡 <b>Продление VPN:</b>\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nПродлил VPN 🛡 на 30 дней:\n\n{vpn_info_text}", parse_mode="HTML")
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            else:
                await callback.answer("У вас недостаточно средств ❌")
                await callback.message.edit_text("• 💵 <b>Баланс</b>:\n\nУ вас недостаточно средств ❌\nЧтобы пополнить свой баланс 💵 нажмите на кнопку ниже, либо используйте команду - /replenishment", reply_markup=replenishment_balance, parse_mode="HTML")
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

"""**************************************************** СИСТЕМА ПОПОЛНЕНИЯ БАЛАНСА **********************************************************"""

# обработка кнопки для оплаты(replenishment)
async def replenishment_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("• 💵 <b>Пополнение баланса</b>:\n\nВыберите сумму пополнения 💵, либо введите нужную самостоятельно: ", reply_markup=numbers_for_replenishment, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await PaymentStates.WAITING_FOR_AMOUNT.set()
        await callback.answer("")

# обработка выбора суммы пополнения баланса пользователя
async def choosing_int_for_replenishment(callback: types.CallbackQuery, state):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        global amount
        if callback.data == "200_for_replenishment_callback":
            amount = 200
            payment_url, payment_id = create_payment(float(amount))
        elif callback.data == "500_for_replenishment_callback":
            amount = 500
            payment_url, payment_id = create_payment(float(amount))
        elif callback.data == "1000_for_replenishment_callback":
            amount = 1000
            payment_url, payment_id = create_payment(float(amount))

        payment_button = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Оплатить", url=payment_url),
                        InlineKeyboardButton(text="Проверить оплату", callback_data=f"checking_payment_{payment_id}")
                    ]
                ]
            )
        await callback.message.edit_text("• 💵 <b>Пополнение баланса</b>:\n\nСчет на оплату сформирован. ✅", reply_markup=payment_button, parse_mode="HTML") 

        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await state.finish()          

# обработка пополнения баланса
async def handle_amount(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        try:
            global amount
            amount = int(message.text)
            if amount > 50:
                payment_url, payment_id = create_payment(float(amount))
                payment_button = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Оплатить", url=payment_url),
                        InlineKeyboardButton(text="Проверить оплату", callback_data=f"checking_payment_{payment_id}")
                    ]
                ]
            )
                await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nСчет на оплату сформирован. ✅", reply_markup=payment_button, parse_mode="HTML") 
                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nСлишком много попыток ❌ \n\nПопробуйте заново - /replenishment", reply_markup=back_keyboard, parse_mode="HTML")
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nСумма пополнения должна быть больше 50 ₽ ❌", parse_mode="HTML")
        except ValueError:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nСлишком много попыток ❌\n\nПопробуйте заново - /replenishment ", reply_markup=back_keyboard, parse_mode="HTML")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nВведите корректную сумму (число) ❌", parse_mode="HTML")

# обработка кнопки, для проверки успешного пополнения(checking_payment_)
async def succesfull_payment(callback: types.CallbackQuery):
    payment_id = check(callback.data.split('_')[-1])
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if payment_id == True:
            await callback.message.edit_text(f'• 💵 <b>Пополнение баланса</b>:\n\nОплата на сумму <code>{amount}</code> <b>₽</b> прошла успешно ✅ \n\nЧтобы узнать свой баланс - /balance', parse_mode="HTML")
            await pay_operation(amount, user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(amount))), description_of_operation="💵 Пополнение баланса")
            await callback.answer("")
        elif payment_id == False:
            await callback.answer('Оплата еще не прошла.')

"""**************************************************** СИСТЕМА ПОДДЕРЖКИ ********************************************************"""
### половина системы находится в файле bot.adm_handlers.py

# обработка кнопка поддержки (support_callback)
async def support_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    info_question = await getting_question(user_id=user_id)
    if info_question != []:
        await callback.message.edit_text("• 🆘 <b>Система поддержки</b>:\n\nВы уже задавали вопрос ❌\n<i>Дождитесь пока модераторы ответят на ваш предыдущий вопрос</i>", reply_markup=back_keyboard, parse_mode="HTML")
        await callback.answer('')
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        return
    else:
        await callback.message.edit_text("• 🆘 <b>Система поддержки</b>:\n\nЗдравствуйте. Чем можем помочь?", reply_markup=back_keyboard, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await callback.answer("")
        await SupportStates.WAITING_FOR_QUESTION.set()

# обработка отправления сообщения от пользователя модераторам
async def process_question(message: types.Message,  state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    question = message.text
    await edit_data(user_name=user_name, user_id=user_id, question=question)
    await message.answer("• 🆘 <b>Система поддержки</b>:\n\nВопрос отправлен модератору! Ожидайте ответ в этом чате.", reply_markup=start_kb_handle(user_id), parse_mode="HTML")
    await bot.send_message(BLAZER_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nЗадал вопрос:\n\n<b>{question}</b>", reply_markup=reply_keyboard(user_id), parse_mode="HTML")
    await bot.send_message(ANUSH_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nПользователь @{user_name} (ID: <code>{user_id})</code>\nЗадал вопрос:\n\n<b>{question}</b>", reply_markup=reply_keyboard(user_id), parse_mode="HTML")
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:
        await save_temp_message(message.from_user.id, message.text, None)
    await state.finish()
    
"""************************************************* РЕФЕРАЛЬНАЯ СИСТЕМА **************************************************"""

# обработка реферальной системы 
async def ref_system(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        referrals = await get_referrer_username(user_id)
        if referrals != None:
            referrals = referrals.split("\n")
        else:
            referrals = referrals
        text = f"• 🤝 <b>Реферальная система</b>:\n<pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\n<i>Поделитесь этой ссылкой со своими знакомыми, чтобы получить 5 ₽ себе на баланс.</i>\n\n"
        if referrals:
            text += "<b>Ваши рефералы:</b>\n"
            for username in referrals:
                text += f"@{username} \n" 
        else:
            text += "У вас еще нет рефералов."
        await callback.message.edit_text(text, reply_markup=back_keyboard, parse_mode="HTML")
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)

# обработка ожидания промокода от пользователя
async def promo_handle(callback: types.CallbackQuery, state):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("• 🎟 <b>Система промокодов</b>:\n\nВведите действующий промокод:", reply_markup=back_keyboard, parse_mode="HTML")
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()

# обработка введенного промокода пользователя
async def handle_user_promo(message: types.Message, state):
    user_promo = message.text
    user_id = message.from_user.id
    user_name = message.from_user.username
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        check_used_promo = await check_promocode_used(user_id, PROMOCODE_TOKEN)
        if user_promo in PROMOCODE_TOKEN and check_used_promo == False:
            await message.answer("• 🎟 <b>Система промокодов</b>:\n\nВы ввели правильный промокод ✅\n\nНа ваш баланс зачислено: <code>20</code> рублей 💵!", reply_markup=back_keyboard, parse_mode="HTML")
            await pay_operation(20, user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(20))), description_of_operation="🎟 Промокод")
            await save_promocode(user_id, user_promo)
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
        elif user_promo in PROMOCODE_TOKEN and check_used_promo == True:
            await message.answer("• 🎟 <b>Система промокодов</b>:\n\nВы уже использовали данный промокод ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard, parse_mode="HTML")    
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("• 🎟 <b>Система промокодов</b>:\n\nСлишком много попыток ❌\n\nПопробуйте заново - /promocode ", reply_markup=back_keyboard, parse_mode="HTML")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 🎟 <b>Система промокодов</b>:\n\nВы ввели неправильный промокод, либо он неактуален ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
        await state.finish()

"""******************************** ОБРАБОТКА ИНФОРМАЦИИ О СОБСТВЕННОМ VPN ПОЛЬЗОВАТЕЛЕЙ *******************************"""

# обработка информации о личных VPN пользователей
async def myvpn_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        vpn_data = await get_vpn_data(user_id)
        if vpn_data:
            vpn_info_text = "• 🛡 <b>Ваши VPN</b>:\n\n"
            for vpn in vpn_data:
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                vpn_info_text += f"📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n"
            await callback.message.edit_text(vpn_info_text, reply_markup=buy_keyboard, parse_mode="HTML")
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
        else:
            await callback.message.edit_text(f"• 🛡 <b>Ваши VPN</b>:\n\nВы не имеете действующего VPN ❌\n\n<i>Чтобы купить VPN, воспользуйтесь кнопкой ниже, либо используйте команду</i> - /buy", reply_markup=buy_keyboard, parse_mode="HTML")
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)

"""***************************************** СИСТЕМА ИСТОРИИ ОПЕРАЦИЙ *****************************************"""

# обработка информации о истории операций пользователя
async def history_of_opeartions_handle(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        operation_history = await getting_operation_history(user_id=user_id)
        if operation_history is None or operation_history == []:
            await callback.message.edit_text("• 📋 <b>История операций</b>:\n\nУ вас нет истории операций ❌", reply_markup=replenishment_balance, parse_mode="HTML")
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

        await callback.message.edit_text(message_text, reply_markup=back_keyboard, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

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
async def back_handle(callback: types.CallbackQuery, state):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы</b>:\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await state.finish()
        user_id = callback.from_user.id
        message_id = await find_message_id(user_id)
        message_text, message_markup = await get_temp_message(user_id, message_id)
        try:
            if message_text and message_markup:
                message_markup = deserialize_keyboard(message_markup)
                await callback.message.edit_text(message_text, reply_markup=message_markup, parse_mode="HTML")
                await delete_temp_message(user_id, message_id)
            else:
                await callback.message.edit_text(start_message_for_reply, reply_markup=start_kb_handle(user_id), parse_mode="HTML")
        except Exception as e:
            await callback.message.answer(start_message_for_reply, reply_markup=start_kb_handle(user_id), parse_mode="HTML")
    await callback.answer("")

"""**************************************************** СИСТЕМА РЕГИСТРИРОВАНИЯ ВСЕХ ХЕНДЛЕРОВ *****************************************************"""

def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_cmd, commands=['start'], state="*")
    dp.register_callback_query_handler(balance_def, lambda c: c.data == "balance", state="*")
    dp.register_callback_query_handler(help_kb_handle, lambda c: c.data == "help_callback", state="*")
    dp.register_callback_query_handler(buying_VPN_handle, lambda c: c.data == "buy", state="*")
    dp.register_callback_query_handler(location_choose_def, lambda c: c.data == "Sweden_callback" or c.data == "Finland_callback" or c.data == "Germany_callback")
    dp.register_callback_query_handler(choosing_location_for_buying_VPN, lambda c: c.data == "Buying_sweden_VPN" or c.data == "Buying_finland_VPN" or c.data == "Buying_germany_VPN")
    dp.register_callback_query_handler(instruction_handle, lambda c: c.data == "instruction_keyboard")
    dp.register_callback_query_handler(device_instruction_handle, lambda c: c.data == "Android_device_callback" or c.data == "IOS_device_callback" or c.data == "komp_device_callback" or c.data == "MacOS_callback")
    dp.register_callback_query_handler(extend_vpn_handle, lambda c: c.data == "extension_vpn" or c.data == "extend_callback" or "extend_vpn" in c.data, state="*")
    dp.register_callback_query_handler(replenishment_handle, lambda c: c.data == "replenishment", state="*")
    dp.register_callback_query_handler(choosing_int_for_replenishment, lambda c: c.data == "200_for_replenishment_callback" or c.data == "500_for_replenishment_callback" or c.data == "1000_for_replenishment_callback", state="*")
    dp.register_message_handler(handle_amount, state=PaymentStates.WAITING_FOR_AMOUNT)
    dp.register_callback_query_handler(succesfull_payment, lambda c: "checking_payment" in c.data)
    dp.register_callback_query_handler(support_handle, lambda c: c.data == "support_callback", state="*")
    dp.register_message_handler(process_question, state=SupportStates.WAITING_FOR_QUESTION)
    dp.register_callback_query_handler(ref_system, lambda c: c.data == "ref_system_callback", state="*")
    dp.register_callback_query_handler(promo_handle, lambda c: c.data == "promo_callback", state="*")
    dp.register_message_handler(handle_user_promo, state=PromocodeStates.WAITING_FOR_USER_PROMOCODE)
    dp.register_callback_query_handler(myvpn_handle, lambda c: c.data == "myvpn_callback", state="*")
    dp.register_callback_query_handler(history_of_opeartions_handle, lambda c: c.data == "history_of_operations_callback")
    dp.register_callback_query_handler(back_handle, lambda c: c.data == "back", state="*")
