import sqlite3 as sq
import os
import datetime
import json
import re
import dns.resolver

from aiogram import types, Dispatcher, Bot
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext 
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound
from dotenv import load_dotenv, find_dotenv
from typing import NamedTuple
from functools import wraps
from keyboards import support_keyboard, user_find_data, adm_panel_keyboard, device_keyboard, addind_count_for_extend, own_vpn_keyboard, numbers_for_replenishment, location_keyboard, reply_buy_keyboard, pay_sweden_keyboard, replenishment_balance, start_kb_handle, back_keyboard, reply_keyboard, insturtion_keyboard, pay_finland_keyboard, pay_germany_keyboard, buy_keyboard, extend_keyboard, payment_type, promocode_keyboard
from database import is_user_ban_check, unban_users_handle, ban_users_handle, find_user_data, db_start, edit_profile, getting_operation_history, extend_vpn_state, edit_operations_history, get_balance, buy_operation, pay_operation, get_vpn_data, update_vpn_state, get_temp_message, delete_temp_message, save_temp_message, find_message_id, find_user, get_referrer_username, save_promocode, check_promocode_used, delete_sum_operation
from payment import create_payment, check

load_dotenv(find_dotenv())
BOT_TOKEN = os.getenv("bot_token") 
BLAZER_CHAT_TOKEN = os.getenv("Blazer_chat_token") 
ANUSH_CHAT_TOKEN = os.getenv("Anush_chat_token")
PAYMASTER_TOKEN = os.getenv("Payment_token") 
VPN_PRICE_TOKEN = os.getenv("VPN_price_token") 
ACCOUNT_PAYMENT_ID_TOKEN = os.getenv("Account_payment_id_token") 
SECRET_PAYMENT_KEY_TOKEN = os.getenv("SECRET_PAYMENT_KEY_TOKEN")
PROMOCODE_TOKEN = os.getenv("Promocode_token")

bot = Bot(BOT_TOKEN)

async def on_startup(dp):
    await db_start()

dp = Dispatcher(bot, storage=MemoryStorage())
previous_states = {}
support_requests = []

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

def deserialize_keyboard(keyboard_json: str) -> InlineKeyboardMarkup:
    keyboard_data = json.loads(keyboard_json)
    keyboard = InlineKeyboardMarkup()

    for row in keyboard_data['inline_keyboard']:
        keyboard.row(*[
            InlineKeyboardButton(text=button['text'], callback_data=button['callback_data'])
            for button in row
        ])

    return keyboard

def block_check(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        user_id = message.from_user.id
        if await is_user_ban_check(user_id):
            await message.reply("<b>Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
            return
        return await func(message, *args, *kwargs)
    return wrapper

"""************************************************* БАЗОВЫЕ КОМАНДЫ (/start, /help, /balance) *****************************************************"""
# обработчик команды /start
@dp.message_handler(commands=['start'], state="*")
@block_check
async def start_cmd(message: types.Message, state):
    user_name = message.from_user.username
    user_id = message.from_user.id
    if not await find_user(user_id):
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
    start_kb = await start_kb_handle(user_id)
    await message.answer("""Добро пожаловать в <b>BlazerVPN</b> – ваш надежный партнер в обеспечении безопасной и анонимной связи в сети.
 
Наш сервис предлагает доступ к трем локациям 📍:<b>
• 🇸🇪 Швеция
• 🇫🇮 Финляндия
• 🇩🇪 Германия
</b>
Обеспечивая быструю и защищенную передачу данных. Независимо от того, где вы находитесь, <b>BlazerVPN</b> гарантирует конфиденциальность и безопасность вашей онлайн активности. Обеспечьте себе свободу и защиту в интернете с <b>BlazerVPN!</b>""", reply_markup=start_kb, parse_mode="HTML")
 
    await save_temp_message(user_id, None, None)


# обработчик всех входящий сообщений
@dp.message_handler(content_types=['text'])
@block_check
async def handle_text(message: types.Message, state):
    user_id = message.from_user.id
    start_kb = await start_kb_handle(user_id)
    if message.text == "/help":
        await message.answer("<b>• Доступные команды:</b>\n"
                           "/start - Обновить бота\n"
                           "/help - Узнать список команд\n"
                           "/balance - Узнать свой баланс\n"
                           "/connect_with_dev - Связаться с разработчиком бота\n"
                           "/buy - Купить VPN\n"
                           "/extend_vpn - Продлить VPN\n"
                           "/replenishment - Пополнить баланс\n"
                           "/support - Задать вопрос\n"
                           "/my_vpn - Мои VPN\n"
                           "/ref_system - Реферальная система\n"
                           "/promocode - Промокоды\n"
                           "/history_of_operations - История операций\n"
                           "/instruction - Инструкция по использованию VPN", reply_markup=start_kb, parse_mode="HTML")
         
    elif message.text == "/balance":
        user_name = message.from_user.username
        balance = await get_balance(user_name)
        await message.answer(f"Ваш баланс: {balance} ₽", reply_markup=replenishment_balance)

    elif message.text == "/connect_with_dev":
        await message.answer("Для связи с разработчиком бота перейдите по ссылке: \n\nhttps://t.me/KING_08001", reply_markup=back_keyboard)

    elif message.text == "/buy":
        await message.answer("Выберите локацию 📍:\n\n<tg-spoiler><i>В скором времени будут добавлены дополнительные локации</i></tg-spoiler>", reply_markup=location_keyboard, parse_mode="HTML")
        
    elif message.text == "/extend_vpn":
        user_id = message.from_user.id
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
                vpn_info_text += f"{numbers}. Локация:   {location}\nДата окончания:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось:   {days_remaining} дней\n\n"
            kb_for_count = await addind_count_for_extend(count=numbers)
            if numbers == 1:
                await message.answer("<b>• У вас один VPN:</b>\n\n" + vpn_info_text + f"<b>Продление VPN 🛡 на 30 дней стоит {VPN_PRICE_TOKEN} ₽ 💵\nНажмите на кнопку, если готовы продлить VPN</b>", reply_markup=extend_keyboard, parse_mode="HTML")
            else:
                await message.answer(f"<b>• Ваши VPN 🛡:</b>\n\n{vpn_info_text}<b>Продление VPN 🛡 на 30 дней стоит {VPN_PRICE_TOKEN} ₽ 💵. Выберите VPN, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
        else:
            await message.answer("У вас нету действующего VPN ❌! Вам его необходимо приобрести ", reply_markup=buy_keyboard)
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

    elif message.text == "/replenishment":
        await message.answer("Выберите сумму пополнения, либо введите нужную самостоятельно: ", reply_markup=numbers_for_replenishment)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await PaymentStates.WAITING_FOR_AMOUNT.set()

    elif message.text == "/support":
        await message.answer("Здравствуйте. Чем можем быть полезны?", reply_markup=back_keyboard)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await SupportStates.WAITING_FOR_QUESTION.set()

    elif message.text == "/ref_system":
        user_id = message.from_user.id
        referrals = await get_referrer_username(user_id)
        text = f"• Ваша реферальная ссылка: <pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\nПоделитесь этой ссылкой со своими знакомыми, чтобы получить 15 ₽ себе на баланс.\n\n"
        if referrals:
            text += "Ваши рефералы:\n"
            for username in referrals:
                text += f"@{username}\n"
        else:
            text += "У вас еще нет рефералов."
        await message.answer(text, reply_markup=back_keyboard, parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)

    elif message.text == "/promocode":
        await message.answer("Введите действующий промокод:", reply_markup=back_keyboard)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()

    elif message.text == "/instruction":
        await message.answer("Выберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", reply_markup=device_keyboard)

    elif message.text == "/my_vpn":
        user_id = message.from_user.id
        vpn_data = await get_vpn_data(user_id)
        if vpn_data:
            vpn_info_text = "<b>• Ваши VPN 🛡</b>:\n\n"
            for vpn in vpn_data:
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                vpn_info_text += f"Локация:   {location}\nДата окончания:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось:   {days_remaining} дней\n\n"
            await message.answer(vpn_info_text, reply_markup=back_keyboard, parse_mode="HTML")
        else:
            await message.answer(f"Вы не имеете действующего VPN ❌", reply_markup=own_vpn_keyboard)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
    
    elif message.text == "/history_of_operations":
        user_id = message.from_user.id
        user_name = message.from_user.username
        operation_history = await getting_operation_history(user_id=user_id)
        if operation_history is None:
            await message.answer("У вас нет истории операций ❌", reply_markup=replenishment_balance)
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

        await message.answer(message_text, reply_markup=back_keyboard, parse_mode="HTML")
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    ##### ADM COMMANDS
    elif message.text == "/add":
        await message.answer("• <b>Пополнение баланса: </b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=back_keyboard, parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await AdmCommandState.WAITING_ID_OF_USER_FOR_ADD.set()
    elif message.text == "/delete":
        await message.answer("• <b>Удаление баланса: </b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=back_keyboard, parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE.set()
    else:
        start_kb = await start_kb_handle(user_id)
        await message.answer("Неверная команда. Пожалуйста, используйте одну из доступных команд (/help)", reply_markup=start_kb)   
    
        
# обработчик кнопки balance(balance)
@dp.callback_query_handler(lambda c: c.data == "balance", state="*")
@block_check
async def balance_def(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    balance = await get_balance(user_name)
    await callback.message.edit_text(f"Ваш баланс 💵: {balance} ₽", reply_markup=replenishment_balance)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработчик кнопки help(help_callback)
@dp.callback_query_handler(lambda c: c.data == "help_callback", state="*")
@block_check
async def help_kb_handle(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Для связи с разработчиком бота 🧑‍💻 перейдите по ссылке: \n\nhttps://t.me/KING_08001", reply_markup=back_keyboard)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

"""*********************************************** ВЫБОР ЛОКАЦИИ И ПОКУПКА ВПН ************************************************************************"""
# обработка кнопки выбора локации (buy)
@dp.callback_query_handler(lambda c: c.data == "buy", state="*")
@block_check
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите локацию 📍:\n\n<tg-spoiler><i>В скором времени будут добавлены дополнительные локации</i></tg-spoiler>", reply_markup=location_keyboard, parse_mode="HTML")
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработка кнопок локаций (Sweden_callback, Finland_callback, Germany_callback)
@dp.callback_query_handler(lambda c: c.data == "Sweden_callback" or c.data == "Finland_callback" or c.data == "Germany_callback")
@block_check
async def location_choose_def(callback: types.CallbackQuery, state: FSMContext):
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
@dp.callback_query_handler(lambda c: c.data == "Buying_sweden_VPN" or c.data == "Buying_finland_VPN" or c.data == "Buying_germany_VPN")
@block_check
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "Buying_sweden_VPN":
        await buying_VPN_def(callback, "Швеция 🇸🇪", state)
        await state.update_data(country="Швеция 🇸🇪") 
    elif callback.data == "Buying_finland_VPN":
        await buying_VPN_def(callback, "Финляндия 🇫🇮", state)
        await state.update_data(country="Финляндия 🇫🇮")
    elif callback.data == "Buying_germany_VPN":
        await buying_VPN_def(callback, "Германия 🇩🇪", state)
        await state.update_data(country="Германия 🇩🇪")

# обработка ответа пользователю от модератора.
@dp.callback_query_handler(lambda c: c.data == "reply_buy_keyboard")
@block_check
async def send_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Скиньте конфиг активации VPN для пользователя: ")
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    await BuyVPNStates.WAITING_FOR_MESSAGE_TEXT.set()

@dp.message_handler(content_types=['text', 'document'],  state=BuyVPNStates.WAITING_FOR_MESSAGE_TEXT)
@block_check
async def send_message_handle(message: types.Message, state):
    user_name = message.from_user.username
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        async with state.proxy() as data:
            payment_key = str(data.get('payment_key'))
            country = data.get('country')
        if payment_key:
            try:
                db = sq.connect('UserINFO.db')
                cur = db.cursor()
                cur.execute(
                    "SELECT user_id FROM TempData WHERE payment_key = ?",
                    (payment_key,)
                )
                row = cur.fetchone()
                db.close()
                if row:
                    user_id = row[0]
                    await bot.send_document(user_id, file_id, caption="Спасибо за покупку!\nСледуйте инструкции для активации VPN", reply_markup=insturtion_keyboard)
                    await update_vpn_state(user_id=user_id, user_name=user_name, location=country, active=True, expiration_days=30, name_of_vpn=file_name, vpn_config=file_id)
                    await bot.send_document(BLAZER_CHAT_TOKEN, file_id, caption=f"Файл для @{user_name} отправлен ✅")
                    await bot.send_document(ANUSH_CHAT_TOKEN, file_id, caption=f"Файл для @{user_name} отправлен ✅")
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                else:
                    await message.answer("Не удалось отправить сообщение покупателю. Неверный ID заказа. ❌")
            except ChatNotFound:
                await message.answer("Не удалось отправить сообщение покупателю. Неверный ID пользователя ❌")
        else:
            await message.answer(f"Пользователь не найден ❌", reply_markup=back_keyboard)
        await state.finish()
    else:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток. Попробуйте заново ❌")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("Нужно скинуть файл конфига VPN ❌")

"""*********************************************************** ОБРАБОТКА ИНСТРУКЦИИ ПО ПОЛЬЗОВАНИЮ VPN *********************************************"""

# обработка кнопки (instruction_keyboard)
@dp.callback_query_handler(lambda c: c.data == "instruction_keyboard")
@block_check
async def instruction_handle(callback: types.CallbackQuery):
    await callback.message.answer("Выберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", reply_markup=device_keyboard)
    await callback.answer('')

@dp.callback_query_handler(lambda c: c.data == "Android_device_callback" or c.data == "IOS_device_callback" or c.data == "komp_device_callback" or c.data == "MacOS_callback")
@block_check
async def device_instruction_handle(callback: types.CallbackQuery):
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
"""****************************************************************** ПРОДЛЕНИЕ VPN *************************************************************************"""
# хендлер для обработки кнопок для продления VPN(extension_vpn, extend_callback)
@dp.callback_query_handler(lambda c: c.data == "extension_vpn" or c.data == "extend_callback" or "extend_vpn" in c.data, state="*")
@block_check
async def extend_vpn_handle(callback: types.CallbackQuery, state: FSMContext):
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
            kb_for_count = await addind_count_for_extend(count=numbers)
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

            
"""************************************************** СИСТЕМА ПОПОЛНЕНИЯ БАЛАНСА *************************************************"""

# обработка кнопки для оплаты(replenishment)
@dp.callback_query_handler(lambda c: c.data == "replenishment", state="*")
@block_check
async def replenishment_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите сумму пополнения 💵, либо введите нужную самостоятельно: ", reply_markup=numbers_for_replenishment)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    await PaymentStates.WAITING_FOR_AMOUNT.set()
    await callback.answer("")

@dp.callback_query_handler(lambda c: c.data == "200_for_replenishment_callback" or c.data == "500_for_replenishment_callback" or c.data == "1000_for_replenishment_callback", state="*")
@block_check
async def rubls_200_for_replenishment(callback: types.CallbackQuery, state):
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
@dp.message_handler(state=PaymentStates.WAITING_FOR_AMOUNT)
@block_check
async def handle_amount(message: types.Message, state):
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

@dp.message_handler(state=PaymentStates.WAITING_FOR_USER_EMAIL_HANDLE)
@block_check
async def user_email_handle(message: types.Message, state: FSMContext):
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

       
@dp.callback_query_handler(lambda c: c.data == "bank_card_payment_callback" or c.data == "yoomoney_payment_callback" or c.data == "TinkoffPay_callback" or c.data == "SberPay_callback" or c.data == "SBP_callback", state=PaymentStates.WAINING_FOR_PAYMENT_TYPE)
@block_check
async def payment_type_handle(callback: types.CallbackQuery, state):
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
@dp.callback_query_handler(lambda c: "checking_payment" in c.data)
@block_check
async def succesfull_payment(callback: types.CallbackQuery):
    payment_id = check(callback.data.split('_')[-1])
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    if payment_id:
        await callback.message.edit_text('Оплата прошла успешно ✅ \nЧтобы узнать свой баланс /balance')
        await pay_operation(amount, user_id)
        await edit_operations_history(user_id=user_id, user_name=user_name, operations=(+(int(amount))), description_of_operation="Пополнение баланса")
        await callback.answer("")
    else:
        await callback.answer('Оплата еще не прошла.')

"""****************************************************** СИСТЕМА ПОДДЕРЖКИ *******************************************************"""
# обработка кнопка поддержки (support_callback)
@dp.callback_query_handler(lambda c: c.data == "support_callback", state="*")
async def support_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Здравствуйте. Чем можем быть полезны?", reply_markup=back_keyboard)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    await SupportStates.WAITING_FOR_QUESTION.set()
    await callback.answer("")

# обработка отправления сообщения от пользователя модераторам
@dp.message_handler(state=SupportStates.WAITING_FOR_QUESTION)
async def process_question(message: types.Message,  state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    question = message.text

    support_request = SupportRequest(user_id=user_id, user_name=user_name, question=question)
    support_requests.append(support_request)
    start_kb = await start_kb_handle(user_id)
    await message.answer("Вопрос отправлен модератору! Ожидайте ответ в этом чате.", reply_markup=start_kb)
    await bot.send_message(BLAZER_CHAT_TOKEN, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n{question}", reply_markup=reply_keyboard)
    await bot.send_message(ANUSH_CHAT_TOKEN, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n{question}", reply_markup=reply_keyboard)
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:
        await save_temp_message(message.from_user.id, message.text, None)
    await state.finish()

# обработка кнопки, для пересылания ответа модератора пользователю (reply_keyboard)
@dp.callback_query_handler(lambda c: c.data == "reply_keyboard")
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    for i, support_request in enumerate(support_requests):
        if support_request.user_id == callback.from_user.id and support_request.answer:
            await callback.message.edit_text("На этот вопрос уже дан ответ. ❌")
            return
        else:
            await callback.message.answer("Напишите свой ответ:", reply_markup=back_keyboard)
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            await callback.answer("")
            await SupportStates.WAITING_FOR_MODERATOR_ANSWER.set()


# обработка пересылания сообщения от модератора пользователю.
@dp.message_handler(state=SupportStates.WAITING_FOR_MODERATOR_ANSWER, content_types=['text', 'document'])
async def replying_for_moder(message: types.Message, state):
    user_name = message.from_user.username
    user_id = message.from_user.id
    answer = message.text

    for i, support_request in enumerate(support_requests):
        if support_request.user_id == message.from_user.id:
            support_requests[i] = SupportRequest(
                user_id=support_request.user_id,
                user_name=support_request.user_name,
                question=support_request.question,
                answer=answer
            )
            try:
                await bot.send_message(support_request.user_id, f"<b>• Ответ от модератора:</b>\n\n{answer}", reply_markup=back_keyboard, parse_mode="HTML")
                await bot.send_message(ANUSH_CHAT_TOKEN, f"Ответ отправлен пользователю @{user_name} (ID: {user_id})")
                await bot.send_message(BLAZER_CHAT_TOKEN, f"Ответ отправлен пользователю @{user_name} (ID: {user_id})")
            except ChatNotFound:
                await message.answer("Пользователь не найден!")
            break
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:  
        await save_temp_message(message.from_user.id, message.text, None)
    await state.finish()


"""********************************************************* РЕФЕРАЛЬНАЯ СИСТЕМА *************************************************"""

@dp.callback_query_handler(lambda c: c.data == "ref_system_callback", state="*")
@block_check
async def ref_system(callback: types.CallbackQuery):
    user_id = callback.message.from_user.id
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


"""********************************************************** СИСТЕМА ПРОМОКОДОВ **************************************************************"""

@dp.callback_query_handler(lambda c: c.data == "promo_callback", state="*")
@block_check
async def promo_handle(callback: types.CallbackQuery, state):
    await callback.message.edit_text("Введите действующий промокод 🎟:", reply_markup=back_keyboard)
    if callback.message.reply_markup:
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        await save_temp_message(callback.from_user.id, callback.message.text, None)
    await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()

@dp.message_handler(state=PromocodeStates.WAITING_FOR_USER_PROMOCODE)
@block_check
async def handle_user_promo(message: types.Message, state):
    user_promo = message.text
    user_id = message.from_user.id
    user_name = message.from_user.username
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

"""*********************************************** ОБРАБОТКА ИНФОРМАЦИИ О VPN ПОЛЬЗОВАТЕЛЕЙ ******************************************"""

@dp.callback_query_handler(lambda c: c.data == "myvpn_callback", state="*")
@block_check
async def myvpn_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
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
        await callback.message.edit_text(f"Вы не имеете действующего VPN ❌", reply_markup=own_vpn_keyboard)
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)

"""**************************************************** ОБРАБОТКА ИСТОРИИ ОПЕРАЦИЙ ***********************************************"""

@dp.callback_query_handler(lambda c: c.data == "history_of_operations_callback")
@block_check
async def history_of_opeartions_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.username
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


"""************************************************************* ВРЕМЕННЫЕ АДМИН КОМАНДЫ ******************************************************"""
@dp.callback_query_handler(lambda c: c.data == "adm_panel_callback")
@block_check
async def adm_panel_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("<b>• Админ панель 🤖: </b>\n\nВыберите нужно действие: ", reply_markup=adm_panel_keyboard, parse_mode="HTML")
    if callback.message.reply_markup:
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        await save_temp_message(callback.from_user.id, callback.message.text, None)
    await callback.answer('')


@dp.callback_query_handler(lambda c: c.data == "addind_balance_callback" or c.data == "deleting_balance_callback" or c.data == "user_data_callback" or c.data == "vpn_user_callback" or c.data == "ban_user_callback" or c.data == "unban_user_callback")
@block_check
async def adm_panel_buttons_handler(callback: types.CallbackQuery):
    # удаление и пополнение баланса
    if callback.data == "addind_balance_callback":
        await callback.message.edit_text("• <b>Пополнение баланса: </b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=back_keyboard, parse_mode="HTML")
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await AdmCommandState.WAITING_ID_OF_USER_FOR_ADD.set()
    elif callback.data == "deleting_balance_callback":
        await callback.message.edit_text("• <b>Удаление баланса: </b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=back_keyboard, parse_mode="HTML")
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE.set()

    elif callback.data == "user_data_callback":
        await callback.message.edit_text("<b>• Данные о пользователе 🗃:</b> \n\nВведите ID или USERNAME пользователя, информацию про которого хотите узнать: ", reply_markup=back_keyboard, parse_mode="HTML")
        await callback.answer('')
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO.set()

    elif callback.data == "vpn_user_callback":
        await callback.message.edit_text("<b>• VPN пользователя 🛡️: </b>\n\nВведите ID или USERNAME пользователя, информацию о VPN которого хотите узнать: ", reply_markup=back_keyboard, parse_mode="HTML")
        await callback.answer('')
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO.set()
    elif callback.data == "ban_user_callback":
        await callback.message.edit_text("<b>• Блокировка пользователя ❌:</b>\n\nВведите ID или USERNAME пользователя, которого хотите заблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
        await callback.answer('')
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await BanUserState.WAITING_FOR_USER_ID.set()
    elif callback.data == "unban_user_callback":
        await callback.message.edit_text("<b>• Разблокировка пользователя ✅:</b>\n\nВведите ID или USERNAME пользователя, которого хотите разблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
        await callback.answer('')
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await UnbanUserState.WAITING_FOR_USER_ID.set()

@dp.callback_query_handler(state=AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS)
@block_check
async def unban_user2_handle(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        user_id = int(data.get("user_id"))
        user_name = None
        is_registrated_user = await find_user_data(user_id=user_id)
        if is_registrated_user:
            result = await unban_users_handle(user_id=user_id)
            if result != "unbanned":
                await callback.message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                await callback.message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await callback.message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
    except Exception as e:
        user_name = data.get("user_name")
        user_id = None
        is_registrated_user = await find_user_data(user_name=user_name)
        if is_registrated_user:
            result = await unban_users_handle(user_name=user_name)
            if result != "unbanned":
                await callback.message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                await callback.message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)

            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await callback.message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)



@dp.message_handler(state=UnbanUserState.WAITING_FOR_USER_ID)
@block_check
async def unban_user_handle(message: types.Message, state):
    try:
        user_id = int(message.text)
        user_name = None
        is_registrated_user = await find_user_data(user_id=user_id)
        if is_registrated_user:
            result = await unban_users_handle(user_id=user_id)
            if result != "unbanned":
                await message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                await message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
    except Exception as e:
        user_name = message.text
        user_id = None
        is_registrated_user = await find_user_data(user_name=user_name)
        if is_registrated_user:
            result = await unban_users_handle(user_name=user_name)
            if result != "unbanned":
                await message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                await message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)

            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("<b>• Разблокировка пользователя ✅:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)




@dp.callback_query_handler(lambda c: c.data == "ban_user2_callback", state=AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS)
@block_check
async def ban_user2_handle(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        try:
            user_id = int(data.get("user_id"))
            user_name = None
            is_registrated_user = await find_user_data(user_id=user_id)
            if is_registrated_user:
                result = await ban_users_handle(user_id=user_id)
                if result != "banned":
                    await callback.message.answer("<b>• Блокировка пользователя ❌:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                else:
                    await callback.message.answer("<b>• Блокировка пользователя ❌:</b>\n\nЭтот пользователь уже находится в бане.", parse_mode="HTML", reply_markup=back_keyboard)
                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("<b>• Блокировка пользователя ❌:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
        except Exception as e:
            user_name = data.get("user_name")
            user_id = None
            is_registrated_user = await find_user_data(user_name=user_name)
            if is_registrated_user:
                result = await ban_users_handle(user_name=user_name)
                if result != "banned":
                    await callback.message.answer("<b>• Блокировка пользователя ❌:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                else:
                    await callback.message.answer("<b>• Блокировка пользователя ❌:</b>\n\nЭтот пользователь уже находится в бане.", parse_mode="HTML", reply_markup=back_keyboard)

                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("<b>• Блокировка пользователя ❌:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)


@dp.message_handler(state=BanUserState.WAITING_FOR_USER_ID)
@block_check
async def ban_user_handle(message: types.Message, state):
    try:
        user_id = int(message.text)
        user_name = None
        is_registrated_user = await find_user_data(user_id=user_id)
        if is_registrated_user:
            result = await ban_users_handle(user_id=user_id)
            if result != "banned":
                await message.answer("<b>• Блокировка пользователя ❌:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                await message.answer("<b>• Блокировка пользователя ❌:</b>\n\nЭтот пользователь уже находится в бане.", parse_mode="HTML", reply_markup=back_keyboard)
            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("<b>• Блокировка пользователя ❌:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
    except Exception as e:
        user_name = message.text
        user_id = None
        is_registrated_user = await find_user_data(user_name=user_name)
        if is_registrated_user:
            result = await ban_users_handle(user_name=user_name)
            if result != "banned":
                await message.answer("<b>• Блокировка пользователя ❌:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                await message.answer("<b>• Блокировка пользователя ❌:</b>\n\nЭтот пользователь уже находится в бане.", parse_mode="HTML", reply_markup=back_keyboard)

            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("<b>• Блокировка пользователя ❌:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)



# поиск информации о VPN пользователей
@dp.message_handler(state=UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO)
@block_check
async def find_info_about_users_vpn(message: types.Message, state):
    try:
        user_id = int(message.text)
        user_name = None
        vpn_data = await get_vpn_data(user_id=user_id)
        if vpn_data != None:
            for vpn in vpn_data:
                id = vpn[0]
                user_id = vpn[1]
                user_name = vpn[2]
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                name_of_vpn = vpn[6]
                vpn_config = vpn[7]
                await bot.send_document(message.from_user.id, vpn_config, caption=f"<b>• VPN пользователя 🛡️: </b>\n\nЛокация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n", parse_mode="HTML")
        else:
            await message.answer("<b>• VPN пользователя 🛡️: </b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
    except Exception as e:
        user_name = message.text
        user_id = None
        vpn_data = await get_vpn_data(user_name=user_name)
        user_info = await find_user_data(user_name=user_name)
        if user_info != None:
            if vpn_data != None:
                for vpn in vpn_data:
                    id = vpn[0]
                    user_id = vpn[1]
                    user_name = vpn[2]
                    location = vpn[3]
                    active = vpn[4]
                    expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date - datetime.datetime.now()).days
                    name_of_vpn = vpn[6]
                    vpn_config = vpn[7]
                    await bot.send_document(message.from_user.id, vpn_config, caption=f"<b>• VPN пользователя 🛡️: </b>\n\nЛокация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n", parse_mode="HTML")
            else:
                await message.answer("<b>• VPN пользователя 🛡️: </b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("<b>• Данные о пользователе 🗃</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново: ", parse_mode="HTML", reply_markup=back_keyboard)
        
            await message.answer("<b>• VPN пользователя 🛡️: </b>\n\nПользователь с таким USERNAME не найдет ❌\nПопробуйте ввести USERNAME или ID заново:", parse_mode="HTML", reply_markup=back_keyboard)
            
# Поиск информации о пользователе
@dp.message_handler(state=AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO)
@block_check
async def find_user_info_for_adm_panel(message: types.Message, state: FSMContext):
    try:
        user_id_for_find_info = int(message.text)
        user_name_for_find_info = None
        user_info = await find_user_data(user_id=user_id_for_find_info)
    except Exception as e:
        user_name_for_find_info = message.text
        user_id_for_find_info = None
        user_info = await find_user_data(user_name=user_name_for_find_info)
    await state.update_data(user_name=user_name_for_find_info, user_id=user_id_for_find_info)
    if user_info != []:
        used_promocodes, referrer_id, id, user_id, user_name, balance, time_of_registration = None, None, None, None, None, None, None
        for info in user_info:
            id = info[0]
            user_id = info[1]
            user_name = info[2]
            balance = info[3]
            time_of_registration = info[4]
            referrer_id = info[5]
            used_promocodes = info[6]
            is_banned = info[7]

        used_promocodes_text = "-"
        if used_promocodes:
            used_promocodes_list = used_promocodes.split(",")
            used_promocodes_text = ", ".join(used_promocodes_list)[:-2]

        if is_banned == "False":
            is_banned = "-"
        else:
            is_banned = "+"

        if referrer_id == None:
            referrer_id = "-"
            user_info_text = f"<b>• Данные о пользователе 🗃</b>:\n\nID в базе данных: <code>{id}</code>\nTelegram ID: <code>{user_id}</code>\nUsername пользователя: <code>{user_name}</code>\nБаланс: <code>{balance}</code> ₽\nВремя регистрации: <code>{time_of_registration}</code>\nРеферер: <code>-</code>\nИспользованные промокоды: <code>{used_promocodes_text}</code>\nЗабанен ли пользователь: <code>{is_banned}</code>"
        else:
            referrer_username = await get_referrer_username(user_id=referrer_id)
            user_info_text = f"<b>• Данные о пользователе 🗃</b>:\n\nID в базе данных: <code>{id}</code>\nTelegram ID: <code>{user_id}</code>\nUsername пользователя: <code>{user_name}</code>\nБаланс: <code>{balance}</code> ₽\nВремя регистрации: <code>{time_of_registration}</code>\nРеферер: {referrer_username}({referrer_id})\nИспользованные промокоды: <code>{used_promocodes_text}</code>\nЗабанен ли пользователь: <code>{is_banned}</code>"
        await message.answer(user_info_text, reply_markup=user_find_data, parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()

    elif user_id_for_find_info == None and user_info == []:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
            await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("<b>• Данные о пользователе 🗃</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново: ", parse_mode="HTML", reply_markup=back_keyboard)
    elif user_name_for_find_info == None and user_info == []:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ", reply_markup=back_keyboard)
            await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("<b>• Данные о пользователе 🗃</b>:\n\nПользователь с таким <b>ID</b> не найден ❌", parse_mode="HTML", reply_markup=back_keyboard)

# информация о VPN пользователя уже без узнавания user_id, через поиск информации о пользователе
@dp.callback_query_handler(lambda c: c.data == "vpn_user2_callback", state=AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS)
@block_check
async def vpn_info_handle(callback: types.CallbackQuery, state: FSMContext):   
    data = await state.get_data()
    try:
        user_id = int(data.get("user_id"))
        user_name = None
        vpn_data = await get_vpn_data(user_id=user_id)
        if vpn_data != None:
            for vpn in vpn_data:
                id = vpn[0]
                user_id = vpn[1]
                user_name = vpn[2]
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                name_of_vpn = vpn[6]
                vpn_config = vpn[7]
                await bot.send_document(callback.from_user.id, vpn_config, caption=f"<b>• VPN пользователя 🛡️: </b>\n\nЛокация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n", parse_mode="HTML")
        else:
            await callback.message.answer("<b>• VPN пользователя 🛡️: </b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
    except Exception as e:
        user_name = data.get("user_name")
        user_id = None
        vpn_data = await get_vpn_data(user_name=user_name)
        user_info = await find_user_data(user_name=user_name)
        if user_info != None:
            if vpn_data != None:
                for vpn in vpn_data:
                    id = vpn[0]
                    user_id = vpn[1]
                    user_name = vpn[2]
                    location = vpn[3]
                    active = vpn[4]
                    expiration_date = datetime.datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date - datetime.datetime.now()).days
                    name_of_vpn = vpn[6]
                    vpn_config = vpn[7]
                    await bot.send_document(callback.from_user.id, vpn_config, caption=f"<b>• VPN пользователя 🛡️: </b>\n\nЛокация 📍:   {location}\nДата окончания 🕘:   {expiration_date.strftime('%d.%m.%Y %H:%M:%S')}\nОсталось ⏳:   {days_remaining} дней\n\n", parse_mode="HTML")
            else:
                await callback.message.answer("<b>• VPN пользователя 🛡️: </b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново /add ИЗМЕНИТТТЬЬЬЬ ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await callback.message.answer("<b>• Данные о пользователе 🗃</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново: ", parse_mode="HTML", reply_markup=back_keyboard)
        
            await callback.message.answer("<b>• VPN пользователя 🛡️: </b>\n\nПользователь с таким USERNAME не найдет ❌\nПопробуйте ввести USERNAME или ID заново:", parse_mode="HTML", reply_markup=back_keyboard)

# пополнение баланса
@dp.message_handler(state=AdmCommandState.WAITING_ID_OF_USER_FOR_ADD)
@block_check
async def handling_user_name(message: types.Message):
    global user_id_for_add
    global user_name_for_add
    try:
        user_id_for_add = int(message.text)
        user_name_for_add = None
    except Exception as e:
        user_name_for_add = message.text
        user_id_for_add = None
    await message.answer("• <b>Пополнение баланса: </b>\n\nВведите сумму для пополнения баланса:", reply_markup=back_keyboard, parse_mode="HTML")
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:
        await save_temp_message(message.from_user.id, message.text, None)
    await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD.set()

@dp.message_handler(state=AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD)
@block_check
async def handle_for_adm_add_sum(message: types.Message, state):
    try:
        adm_sum_for_add = int(message.text)
    except Exception as e:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток ❌\n Попробуйте заново /add ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("Введите корректную сумму (число) ❌")
    if user_id_for_add != None:
        await pay_operation(int(adm_sum_for_add), user_id=user_id_for_add)
    elif user_name_for_add != None:
        await pay_operation(int(adm_sum_for_add), user_name=user_name_for_add)
    await message.answer(f"• <b>Пополнение баланса: </b>\n\nБаланс указанного пользователя пополнен на: {adm_sum_for_add} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
    await edit_operations_history(user_id=user_id_for_add, user_name=user_name_for_add, operations=(+(int(adm_sum_for_add))), description_of_operation="Модератор")
    

# удаление баланса
@dp.message_handler(state=AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE)
@block_check
async def handling_user_name_for_delete(message: types.Message):
    global user_id_for_delete
    global user_name_for_delete
    try:
        user_id_for_delete = int(message.text)
        user_name_for_delete = None
    except Exception as e:
        user_name_for_delete = message.text
        user_id_for_delete = None
    await message.answer("• <b>Удаление баланса: </b>\n\nВведите сумму для удаления баланса:", reply_markup=back_keyboard, parse_mode="HTML")
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:
        await save_temp_message(message.from_user.id, message.text, None)
    await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE.set()

@dp.message_handler(state=AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE)
@block_check
async def handle_for_adm_delete_sum(message: types.Message, state):
    try:
        adm_sum_for_delete = int(message.text)
    except Exception as e:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток ❌\n Попробуйте заново /delete ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("Введите корректную сумму (число) ❌")
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:
        await save_temp_message(message.from_user.id, message.text, None)

    if user_id_for_delete != None:
        balance = await get_balance(user_id=user_id_for_delete)
        if balance >= int(adm_sum_for_delete):
            await delete_sum_operation(int(adm_sum_for_delete), user_id=user_id_for_delete)
            await edit_operations_history(user_id=user_id_for_delete, user_name=user_name_for_delete, operations=(-(int(adm_sum_for_delete))), description_of_operation="Модератор")
            await message.answer(f"• <b>Удаление баланса: </b>\n\nБаланс указанного пользователя удален на: {adm_sum_for_delete} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
            await state.finish()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /delete ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer('• <b>Удаление баланса: </b>\n\nУ данного пользователя баланс меньше, чем выше указанное число ❌\n\nПопробуйте заново:', parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
    elif user_name_for_delete != None:
        balance = await get_balance(user_name=user_name_for_delete)
        if balance >= int(adm_sum_for_delete):
            await delete_sum_operation(int(adm_sum_for_delete), user_name=user_name_for_delete)
            await message.answer(f"• <b>Удаление баланса: </b>\n\nБаланс указанного пользователя удален на: {adm_sum_for_delete} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
            await edit_operations_history(user_id=user_id_for_delete, user_name=user_name_for_delete, operations=(-(int(adm_sum_for_delete))), description_of_operation="Модератор")
            await state.finish()
        else: 
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n Попробуйте заново /delete ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer('• <b>Удаление баланса: </b>\n\nУ данного пользователя баланс меньше, чем выше указанное число ❌\n\nПопробуйте заново:', parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)

"""********************************************** СИСТЕМА ВОЗВРАЩЕНИЯ К ПРЕДЫДУЩИМ СООБЩЕНИЯМ ****************************************"""

@dp.callback_query_handler(lambda c: c.data == "back", state="*")
@block_check
async def back_handle(callback: types.CallbackQuery, state):
    await state.finish()
    user_id = callback.from_user.id
    message_id = await find_message_id(user_id)
    message_text, message_markup = await get_temp_message(user_id, message_id)
    start_kb = await start_kb_handle(user_id) 
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
    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
