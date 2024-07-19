import os 
import dns.resolver
import re
import json

from dotenv import load_dotenv
from typing import NamedTuple
from datetime import datetime

from aiogram import types, Dispatcher, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.database.OperationsData import edit_operations_history, getting_operation_history
from bot.database.TempData import save_temp_message, get_temp_message, delete_temp_message, find_message_id
from bot.database.UserData import edit_profile, get_balance, buy_operation, pay_operation, get_referrer_username, check_promocode_used, save_promocode, find_user_data, ban_users_handle, unban_users_handle, is_user_ban_check
from bot.database.VpnData import extend_vpn_state, get_vpn_data
from bot.database.SupportData import edit_data, getting_question

from bot.keyboards.user_keyboards import start_kb_handle, support_keyboard, location_keyboard, pay_sweden_keyboard, pay_finland_keyboard, pay_germany_keyboard, replenishment_balance, back_keyboard, insturtion_keyboard, buy_keyboard, extend_keyboard, numbers_for_replenishment, addind_count_for_extend, payment_type, promocode_keyboard, device_keyboard
from bot.keyboards.adm_keyboards import reply_keyboard, reply_buy_keyboard

from bot.utils.payment import check, create_payment

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

# обработчик команды /start
async def start_cmd(message: types.Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    result = await find_user_data(user_id=user_id)
    if result == None: 
        start_command = message.text
        referrer_id = str(start_command[7:])
        if referrer_id != "":
            if referrer_id != str(user_id):
                await edit_profile(user_name, user_id, referrer_id)
                await message.answer("Спасибо за регистрацию! Бонусы успешно зачислились рефереру на баланс. ")
                try:
                    await bot.send_message(referrer_id, "По вашей реферальной ссылке зарегистровался новый пользователь, вам начислены 15 ₽ ")
                    await pay_operation(int(5), referrer_id)
                except:
                    pass
            else:
                await message.answer("Вы не можете зарегистрироваться по собственной реферальной ссылке! ")
                await edit_profile(user_name, user_id)
    else:
        await edit_profile(user_name, user_id)
        if await is_user_ban_check(user_id=user_id):
            await message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
            return
        else:
            start_kb = start_kb_handle(user_id)
            await message.answer("""Добро пожаловать в <b>BlazerVPN</b> – ваш надежный партнер в обеспечении безопасной и анонимной связи в сети.

Наш сервис предлагает доступ к трем локациям 📍:<b>
• 🇸🇪 Швеция
• 🇫🇮 Финляндия
• 🇩🇪 Германия
</b>
Обеспечивая быструю и защищенную передачу данных. Независимо от того, где вы находитесь, <b>BlazerVPN</b> гарантирует конфиденциальность и безопасность вашей онлайн активности. Обеспечьте себе свободу и защиту в интернете с <b>BlazerVPN!</b>""", reply_markup=start_kb, parse_mode="HTML")

    await save_temp_message(user_id, None, None)


# обработчик кнопки balance (balance)
async def balance_def(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        balance = await get_balance(user_name)
        await callback.message.edit_text(f"Ваш баланс 💵: {balance} ₽", reply_markup=replenishment_balance)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработчик кнопки help(help_callback)
async def help_kb_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("Для связи с разработчиком бота 🧑‍💻 перейдите по ссылке: \n\nhttps://t.me/KING_08001", reply_markup=back_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

"""*********************************************** ВЫБОР ЛОКАЦИИ И ПОКУПКА ВПН ************************************************************************"""
# обработка кнопки выбора локации (buy)
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("Выберите локацию 📍:\n\n<tg-spoiler><i>В скором времени будут добавлены дополнительные локации</i></tg-spoiler>", reply_markup=location_keyboard, parse_mode="HTML")
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработка кнопок локаций (Sweden_callback, Finland_callback, Germany_callback)
async def location_choose_def(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id    
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "Sweden_callback":
            await callback.message.edit_text(f"Вы выбрали локацию 📍: Швеция 🇸🇪\nVPN на данной локации сейчас нету в наличии ❌", reply_markup=back_keyboard)
            #await callback.message.edit_text(f"Вы выбрали локацию: Швеция 🇸🇪\nСтоимость данного товара {VPN_PRICE_TOKEN} ₽", reply_markup=pay_sweden_keyboard)
            #await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            #await callback.answer("")

        elif callback.data == "Finland_callback":
            await callback.message.edit_text(f"Вы выбрали локацию 📍: Финляндия 🇫🇮\nСтоимость данного товара {VPN_PRICE_TOKEN} ₽", reply_markup=pay_finland_keyboard)
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            await callback.answer("")

        elif callback.data == "Germany_callback":
            await callback.message.edit_text(f"Вы выбрали локацию 📍: Германия 🇩🇪\nVPN на данной локации сейчас нету в наличии ❌", reply_markup=back_keyboard)
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
        await callback.message.edit_text("Чтобы пополнить свой баланс 💵, нажмите на кнопку.", reply_markup=replenishment_balance)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        payment_key = await buy_operation(user_id=user_id, user_name=user_name)
        await callback.message.edit_text("Вы купили товар ✅! Ожидайте подготовки товара модераторами. Ключ активации VPN будет отправлен в этом чате.")
        user_id = callback.from_user.id
        async with state.proxy() as data:
            data['payment_key'] = payment_key
        await edit_operations_history(user_id=user_id, user_name=user_name, operations=(-(float(VPN_PRICE_TOKEN))), description_of_operation="Покупка VPN")
        await bot.send_message(BLAZER_CHAT_TOKEN, f"Пользователь @{user_name} (ID: {user_id})\nЗаказал VPN на локации 📍: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard)
        await bot.send_message(ANUSH_CHAT_TOKEN, f"Пользователь @{user_name} (ID: {user_id})\nЗаказал VPN на локации 📍: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# хендлер, который вызывает функцию, для обработки покупки VPN. Обрабатывает кнопки (Buying_sweden_VPN, Buying_finland_VPN, Buying_germany_VPN)
async def choosing_location_for_buying_VPN(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "Buying_sweden_VPN":
            await buying_VPN_def(callback, "Швеция 🇸🇪", state)
            await state.update_data(country="Швеция 🇸🇪") 
        elif callback.data == "Buying_finland_VPN":
            await buying_VPN_def(callback, "Финляндия 🇫🇮", state)
            await state.update_data(country="Финляндия 🇫🇮")
        elif callback.data == "Buying_germany_VPN":
            await buying_VPN_def(callback, "Германия 🇩🇪", state)
            await state.update_data(country="Германия 🇩🇪")


# обработка кнопки (instruction_keyboard)
async def instruction_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.answer("Выберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", reply_markup=device_keyboard)
        await callback.answer('')

# обработка выбора девайса пользователя для получения инструкции по использованию VPN
async def device_instruction_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
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

# хендлер для обработки кнопок для продления VPN(extension_vpn, extend_callback)
async def extend_vpn_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
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
                    vpn_info_text += f"{numbers}. Локация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n"
                kb_for_count = addind_count_for_extend(count=numbers)
                if numbers == 1:
                    await callback.message.edit_text("<b>• У вас один VPN 🛡:</b>\n\n" + vpn_info_text + f"<b>Продление VPN на 30 дней стоит {VPN_PRICE_TOKEN} ₽ 💵\nНажмите на кнопку, если готовы продлить VPN 🛡</b>", reply_markup=extend_keyboard, parse_mode="HTML")
                else:
                    await callback.message.edit_text(f"<b>• Ваши VPN 🛡:</b>\n\n{vpn_info_text}<b>Продление VPN на 30 дней стоит {VPN_PRICE_TOKEN} ₽ 💵. Выберите VPN 🛡, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else: 
                await callback.message.edit_text("У вас нету действующего VPN ❌! Вам его необходимо приобрести ", reply_markup=buy_keyboard)
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

        elif callback.data == "extend_callback":
            user_name = callback.from_user.username
            balance = await get_balance(user_name)
            user_id = callback.from_user.id
            if float(balance) >= float(VPN_PRICE_TOKEN):
                await pay_operation(VPN_PRICE_TOKEN, user_id)
                await edit_operations_history(user_id=user_id, user_name=user_name, operations=(-(float(VPN_PRICE_TOKEN))), description_of_operation="Продление VPN")
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
                await callback.message.edit_text(f"VPN 🛡 продлен на 30 дней ✅ \n\nДо окончания действия VPN 🛡 осталось {days_remaining + 30} дней ⏳", reply_markup=back_keyboard)
                vpn_info_text = f"Локация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n"
                await bot.send_document(ANUSH_CHAT_TOKEN, vpn_config, caption=f"<b>Пользователь @{user_name} (ID: {user_id})\nПродлил VPN 🛡 на 30 дней:</b>\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_document(BLAZER_CHAT_TOKEN, vpn_config, caption=f"<b>Пользователь @{user_name} (ID: {user_id})\nПродлил VPN 🛡 на 30 дней:</b>\n\n{vpn_info_text}")
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            else:
                await callback.answer("У вас недостаточно средств ❌")
                await callback.message.edit_text("Чтобы пополнить свой баланс 💵, нажмите на кнопку.", reply_markup=replenishment_balance)
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
                await edit_operations_history(user_id=user_id, user_name=user_name, operations=int(-(float(VPN_PRICE_TOKEN))), description_of_operation="Продление VPN")
                id = vpn[0]
                location = vpn[3]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                name_of_vpn = vpn[6]
                vpn_config = vpn[7]
                days_remaining = (expiration_date - datetime.datetime.now()).days
                new_expiration_date = expiration_date + datetime.timedelta(days=30)
                vpn_info_text = f"Локация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n"
                await extend_vpn_state(user_id=user_id, location=location, active=True, expiration_date=new_expiration_date, id=id)
                await callback.message.edit_text(f"VPN 🛡 продлен на 1 месяц ✅ \n\nДо окончания действия VPN 🛡 осталось {days_remaining + 30} дней ⏳", reply_markup=back_keyboard)
                await bot.send_document(ANUSH_CHAT_TOKEN, vpn_config, caption=f"<b>Пользователь @{user_name} (ID: {user_id})\nПродлил VPN 🛡 на 30 дней:</b>\n\n{vpn_info_text}", parse_mode="HTML")
                await bot.send_document(BLAZER_CHAT_TOKEN, vpn_config, caption=f"<b>Пользователь @{user_name} (ID: {user_id})\nПродлил VPN 🛡 на 30 дней:</b>\n\n{vpn_info_text}")
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            else:
                await callback.answer("У вас недостаточно средств ❌")
                await callback.message.edit_text("Чтобы пополнить свой баланс 💵, нажмите на кнопку.", reply_markup=replenishment_balance)
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработка кнопки для оплаты(replenishment)
async def replenishment_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("Выберите сумму пополнения 💵, либо введите нужную самостоятельно: ", reply_markup=numbers_for_replenishment)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await PaymentStates.WAITING_FOR_AMOUNT.set()
        await callback.answer("")

# обработка выбора суммы пополнения баланса пользователя
async def choosing_int_for_replenishment(callback: types.CallbackQuery, state):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        global amount
        if callback.data == "200_for_replenishment_callback":
            amount = 200
            await callback.message.edit_text("Введите адрес своей электронной почты 📩:", reply_markup=back_keyboard)
        elif callback.data == "500_for_replenishment_callback":
            amount = 500
            await callback.message.edit_text("Введите адрес своей электронной почты 📩:", reply_markup=back_keyboard)
        elif callback.data == "1000_for_replenishment_callback":
            amount = 1000
            await callback.message.edit_text("Введите адрес своей электронной почты 📩: ", reply_markup=back_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await PaymentStates.WAITING_FOR_USER_EMAIL_HANDLE.set()           

# обработка пополнения баланса
async def handle_amount(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        try:
            global amount
            amount = int(message.text)
            if amount > 0:
                await message.answer("Введите адрес своей электронной почты 📩: ", reply_markup=back_keyboard)
                await PaymentStates.WAITING_FOR_USER_EMAIL_HANDLE.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("Слишком много попыток ❌ \nПопробуйте заново /replenishment", back_keyboard)
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("Сумма пополнения должна быть больше 0 ❌")
        except ValueError:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /replenishment ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("Введите корректную сумму (число).")

# обработка электронной почты пользователя
async def user_email_handle(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        global user_email
        user_email = message.text
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", user_email):
            await message.answer("Некорректный адрес электронной почты 📩. Пожалуйста, введите его снова ❌", reply_markup=back_keyboard)
            return
        
        if len(user_email) > 254:
            await message.answer("Адрес электронной почты слишком длинный ❌ Пожалуйста, введите его снова.", reply_markup=back_keyboard)
            return

        try:
            dns.resolver.resolve(user_email.split('@')[1], 'MX')
        except dns.resolver.NXDOMAIN:
            await message.answer("Домен не существует ❌ Пожалуйста, введите его снова.", reply_markup=back_keyboard)
            return

        await message.answer("Ваш адрес электронной почты принят ✅ \n\nВыберите платежную систему:", reply_markup=payment_type)
        await PaymentStates.WAINING_FOR_PAYMENT_TYPE.set()

# обработка выбора платежной системы пользователем
async def payment_type_handle(callback: types.CallbackQuery, state):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if callback.data == "bank_card_payment_callback":
            try:
                payment_url, payment_id = create_payment(float(amount), callback.from_user.id, "bank_card", user_email)
            except Exception as e:
                await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌", reply_markup=back_keyboard)
                return
        elif callback.data == "yoomoney_payment_callback":
            try:
                payment_url, payment_id = create_payment(float(amount), callback.from_user.id, "yoo_money", user_email)
            except Exception as e:
                await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌", reply_markup=back_keyboard)
                return
        elif callback.data == "TinkoffPay_callback":
            try:
                payment_url, payment_id = create_payment(float(amount), callback.from_user.id, "tinkoff_bank", user_email)
            except Exception as e:
                await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌", reply_markup=back_keyboard)
                return
        elif callback.data == "SberPay_callback":
            try:
                payment_url, payment_id = create_payment(float(amount), callback.from_user.id, "sberbank", user_email)
            except Exception as e:
                await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌", reply_markup=back_keyboard)
                return
        elif callback.data == "SBP_callback":
            try:
                payment_url, payment_id = create_payment(float(amount), callback.from_user.id, "sbp", user_email)
            except Exception as e:
                await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌", reply_markup=back_keyboard)
                return
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            
        payment_button = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Оплатить", url=payment_url),
                        InlineKeyboardButton(text="Проверить оплату", callback_data=f"checking_payment_{payment_id}")
                    ]
                ]
            )
        await callback.message.edit_text("Счет на оплату сформирован. ✅", reply_markup=payment_button) 
        await state.finish() 

# обработка кнопки, для проверки успешного пополнения(checking_payment_)
async def succesfull_payment(callback: types.CallbackQuery):
    payment_id = check(callback.data.split('_')[-1])
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if payment_id:
            await callback.message.edit_text('Оплата прошла успешно ✅ \nЧтобы узнать свой баланс /balance')
            await pay_operation(amount, user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(amount))), description_of_operation="Пополнение баланса")
            await callback.answer("")
        else:
            await callback.answer('Оплата еще не прошла.')

# обработка кнопка поддержки (support_callback)
async def support_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    info_question = await getting_question(user_id=user_id)
    if info_question != []:
        await callback.message.edit_text("Вы уже задавали вопрос ❌\n\nДождитесь пока модераторы ответят на ваш предыдущий вопрос.", reply_markup=back_keyboard)
        await callback.answer('')
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        return
    else:
        await callback.message.edit_text("Здравствуйте. Чем можем быть полезны?", reply_markup=back_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await SupportStates.WAITING_FOR_QUESTION.set()
        await callback.answer("")

# обработка отправления сообщения от пользователя модераторам
async def process_question(message: types.Message,  state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    question = message.text
    await edit_data(user_name=user_name, user_id=user_id, question=question)
    await message.answer("Вопрос отправлен модератору! Ожидайте ответ в этом чате.", reply_markup=start_kb_handle(user_id))
    await bot.send_message(BLAZER_CHAT_TOKEN, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n\n{question}", reply_markup=reply_keyboard(user_id))
    await bot.send_message(ANUSH_CHAT_TOKEN, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n\n{question}", reply_markup=reply_keyboard(user_id))
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:
        await save_temp_message(message.from_user.id, message.text, None)
    await state.finish()
    
# обработка реферальной системы 
async def ref_system(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        referrals = await get_referrer_username(user_id)
        if referrals != None:
            referrals = referrals.split("\n")
        else:
            referrals = referrals
        text = f"<b>• Ваша реферальная ссылка:</b> <pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\n<i>Поделитесь этой ссылкой со своими знакомыми, чтобы получить 5 ₽ себе на баланс.</i>\n\n"
        if referrals:
            text += "Ваши рефералы:\n"
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
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("Введите действующий промокод 🎟:", reply_markup=back_keyboard)
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
        await message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        check_used_promo = await check_promocode_used(user_id, PROMOCODE_TOKEN)
        if str(user_promo) == str(PROMOCODE_TOKEN) and check_used_promo == False:
            await message.answer("Вы ввели правильный промокод ✅ \nНа ваш баланс зачислено: 20 рублей 💵!", reply_markup=back_keyboard)
            await pay_operation(20, user_id)
            await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(20))), description_of_operation="Промокод")
            await save_promocode(user_id, user_promo)
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
        elif str(user_promo) == str(PROMOCODE_TOKEN) and check_used_promo == True:
            await message.answer("Вы уже использовали данный промокод ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard)    
        else:
            await message.answer("Вы ввели неправильный промокод 🎟, либо он неактуален ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard)
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
        await state.finish()

# обработка информации о личных VPN пользователей
async def myvpn_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        vpn_data = await get_vpn_data(user_id)
        if vpn_data:
            vpn_info_text = "<b>• Ваши VPN 🛡</b>:\n\n"
            for vpn in vpn_data:
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                vpn_info_text += f"Локация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n"
            await callback.message.edit_text(vpn_info_text, reply_markup=buy_keyboard, parse_mode="HTML")
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
        else:
            await callback.message.edit_text(f"Вы не имеете действующего VPN ❌", reply_markup=buy_keyboard)
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)

# обработка информации о истории операций пользователя
async def history_of_opeartions_handle(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        operation_history = await getting_operation_history(user_id=user_id)
        if operation_history is None:
            await callback.message.answer("У вас нет истории операций ❌", reply_markup=replenishment_balance)
            return
        message_text = "<b>• 📋 История операций:</b>\n\n"
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
        await callback.message.answer("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await state.finish()
        user_id = callback.from_user.id
        message_id = await find_message_id(user_id)
        message_text, message_markup = await get_temp_message(user_id, message_id)
        start_kb = start_kb_handle(user_id) 
        try:
            if message_text and message_markup:
                message_markup = deserialize_keyboard(message_markup)
                await callback.message.edit_text(message_text, reply_markup=message_markup)
                await delete_temp_message(user_id, message_id)
            else:
                await callback.message.edit_text("Вы возвращены на начальное меню.", reply_markup=start_kb)
        except Exception as e:
            await callback.message.answer("Вы возвращены на начальное меню.", reply_markup=start_kb)
    await callback.answer("")


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
    dp.register_message_handler(user_email_handle, state=PaymentStates.WAITING_FOR_USER_EMAIL_HANDLE)
    dp.register_callback_query_handler(payment_type_handle, lambda c: c.data == "bank_card_payment_callback" or c.data == "yoomoney_payment_callback" or c.data == "TinkoffPay_callback" or c.data == "SberPay_callback" or c.data == "SBP_callback", state=PaymentStates.WAINING_FOR_PAYMENT_TYPE)
    dp.register_callback_query_handler(succesfull_payment, lambda c: "checking_payment" in c.data)
    dp.register_callback_query_handler(support_handle, lambda c: c.data == "support_callback", state="*")
    dp.register_message_handler(process_question, state=SupportStates.WAITING_FOR_QUESTION)
    dp.register_callback_query_handler(ref_system, lambda c: c.data == "ref_system_callback", state="*")
    dp.register_callback_query_handler(promo_handle, lambda c: c.data == "promo_callback", state="*")
    dp.register_message_handler(handle_user_promo, state=PromocodeStates.WAITING_FOR_USER_PROMOCODE)
    dp.register_callback_query_handler(myvpn_handle, lambda c: c.data == "myvpn_callback", state="*")
    dp.register_callback_query_handler(history_of_opeartions_handle, lambda c: c.data == "history_of_operations_callback")
    dp.register_callback_query_handler(back_handle, lambda c: c.data == "back", state="*")
