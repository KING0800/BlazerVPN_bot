import sqlite3 as sq
import os
import datetime
import json
import re

from aiogram import types, Dispatcher, Bot
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext 
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound
from dotenv import load_dotenv, find_dotenv
from typing import NamedTuple
from keyboards import addind_count_for_extend, own_vpn_keyboard, numbers_for_replenishment, location_keyboard, reply_buy_keyboard, pay_sweden_keyboard, replenishment_balance, start_keyboard, back_keyboard, reply_keyboard, insturtion_keyboard, pay_finland_keyboard, pay_germany_keyboard, buy_keyboard, extend_keyboard, payment_type, promocode_keyboard
from database import db_start, edit_profile, extend_vpn_state, get_balance, buy_operation, pay_operation, get_vpn_data, update_vpn_state, get_temp_message, delete_temp_message, save_temp_message, find_message_id, find_user, get_referrer_username, save_promocode, check_promocode_used, delete_sum_operation
from payment import create_payment, check

load_dotenv(find_dotenv())
bot_token = os.getenv("bot_token") 
Blazer_chat_token = os.getenv("Blazer_chat_token") 
Anush_chat_token = os.getenv("Anush_chat_token")
paymaster_token = os.getenv("paymaster_token") 
VPN_price_token = os.getenv("VPN_price_token") 
Account_payment_id_token = os.getenv("Account_payment_id_token") 
Secret_payment_key_token = os.getenv("Secret_payment_key_token")
Promocode = os.getenv("Promocode")

TOKEN_API = bot_token
bot = Bot(TOKEN_API)

async def on_startup(dp):
    await db_start()

dp = Dispatcher(bot, storage=MemoryStorage())
previous_states = {}
support_requests = []

class BuyVPNStates(StatesGroup):
    WAITING_FOR_MESSAGE_TEXT = State()

class PaymentStates(StatesGroup):
    WAITING_FOR_AMOUNT = State()
    WAINING_FOR_PAYMENT_TYPE = State()
    WAITING_FOR_MESSAGE_TEXT = State()

class SupportStates(StatesGroup):
    WAITING_FOR_QUESTION = State()
    WAITING_FOR_MODERATOR_ANSWER = State()

class PromocodeStates(StatesGroup):
    WAITING_FOR_USER_PROMOCODE = State()

class AdmCommandState(StatesGroup):
    WAITING_FOR_SUM_MONEY = State()
    WAITING_FOR_DELETE_SUM_MONEY = State()

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

"""************************************************* БАЗОВЫЕ КОМАНДЫ (/start, /help, /balance) *****************************************************"""
# обработчик команды /start
@dp.message_handler(commands=['start'], state="*")
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
    await message.answer("""Добро пожаловать в BlazerVPN – ваш надежный партнер в обеспечении безопасной и анонимной связи в сети.
 
Наш сервис предлагает доступ к трем локациям:
• Швеция 🇸🇪
• Финляндия 🇫🇮
• Германия 🇩🇪

Обеспечивая быструю и защищенную передачу данных. Независимо от того, где вы находитесь, BlazerVPN гарантирует конфиденциальность и безопасность вашей онлайн активности. Обеспечьте себе свободу и защиту в интернете с BlazerVPN!""", reply_markup=start_keyboard)
 
    await save_temp_message(user_id, None, None)


# обработчик всех входящий сообщений
@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message, state):
    if message.text == "/help":
        await message.answer("Доступные команды:\n"
                           "/start - Обновить бота\n"
                           "/help - Узнать список команд\n"
                           "/balance - Узнать свой баланс\n"
                           "/connect_with_dev - Связаться с разработчиком бота\n"
                           "/buy_vpn - Купить VPN\n"
                           "/extension_vpn - Продлить VPN\n"
                           "/replenishment - Пополнить баланс\n"
                           "/support - Задать вопрос\n"
                           "/my_vpn - Мои VPN\n"
                           "/ref_system - Реферальная система\n"
                           "/promocode - Промокоды\n"
                           "/instruction - Инструкция по использованию VPN", reply_markup=start_keyboard, parse_mode="HTML")
         
    elif message.text == "/balance":
        user_name = message.from_user.username
        balance = await get_balance(user_name)
        await message.answer(f"Ваш баланс: {balance} ₽", reply_markup=replenishment_balance)

    elif message.text == "/connect_with_dev":
        await message.answer("Для связи с разработчиком бота перейдите по ссылке: \n\nhttps://t.me/KING_08001", reply_markup=back_keyboard)

    elif message.text == "/buy_vpn":
        await message.answer("Выберите локацию:", reply_markup=location_keyboard)
        
    elif message.text == "/extension_vpn":
        user_id = message.from_user.id
        vpn_data = await get_vpn_data(user_id)
        if vpn_data:
            numbers = 0
            vpn_info_text = ""
            for vpn in vpn_data:
                numbers += 1
                location = vpn[2]
                active = vpn[3]
                expiration_date = datetime.datetime.strptime(str(vpn[4]), "%Y.%m.%d %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                vpn_info_text += f"{numbers}. Локация: {location}\nДата окончания: {expiration_date.strftime('%Y.%m.%d %H:%M:%S')}\nОсталось: {days_remaining} дней\n\n"
            kb_for_count = await addind_count_for_extend(count=numbers)
            if numbers == 1:
                await message.answer("<b>У вас один VPN:</b>\n\n" + vpn_info_text + f"<b>Продление VPN на 30 дней стоит {VPN_price_token} ₽ 💵\nНажмите на кнопку, если готовы продлить VPN</b>", reply_markup=extend_keyboard, parse_mode="HTML")
            else:
                await message.answer(f"<b>Ваши VPN 🛡:</b>\n\n{vpn_info_text}<b>Продление VPN на 30 дней стоит {VPN_price_token} ₽ 💵. Выберите VPN, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await message.answer("У вас нету действующего VPN ❌! Вам его необходимо приобрести ", reply_markup=buy_keyboard)
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())

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
        text = f"Ваша реферальная ссылка: <pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\nПоделитесь этой ссылкой со своими знакомыми, чтобы получить 15 ₽ себе на баланс.\n\n"
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
        await message.answer_photo(photo="https://i.imgur.com/0feN5h0.jpeg", caption="""
Настройка для Android:
1. Загрузите приложение WireGuard из Google Play.
2. Для добавления туннеля WireGuard нажмите на кнопку «плюс» в нижнем углу экрана и выберите опцию. Здесь можно загрузить конфигурацию из скачанного файла конфигурации (которую мы прикрепили к этой ниже) или ввести данные вручную.""")
        await message.answer_photo(photo="https://i.imgur.com/MvB2M5t.png", caption="""
3. Нажмите на переключатель рядом с появившимся именем туннеля. Система Android попросит выдать WireGuard разрешения для работы в качестве VPN. Дайте разрешение. После этого соединение будет установлено, в статус-баре будет отображаться знак в виде ключа""")
    
    elif message.text == "/my_vpn":
        user_id = message.from_user.id
        vpn_data = await get_vpn_data(user_id)
        if vpn_data:
            vpn_info_text = "Ваши VPN 🛡:\n\n"
            for vpn in vpn_data:
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%Y.%m.%d %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                vpn_info_text += f"Локация: {location}\nДата окончания: {expiration_date.strftime('%Y.%m.%d %H:%M:%S')}\nОсталось: {days_remaining} дней\n\n"
            await message.answer(vpn_info_text, reply_markup=back_keyboard)
        else:
            await message.answer(f"Вы не имеете действующего VPN ❌", reply_markup=own_vpn_keyboard)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
    ##### ADM COMMANDS
    elif message.text == "/add":
        await message.answer("введите сумму для пополнения: ")
        await AdmCommandState.WAITING_FOR_SUM_MONEY.set()
    elif message.text == "/delete":
        await message.answer("введите сумму для удаления: ")
        await AdmCommandState.WAITING_FOR_DELETE_SUM_MONEY.set()

    else:
        await message.answer("Неверная команда. Пожалуйста, используйте одну из доступных команд (/help)", reply_markup=start_keyboard)   
    
        
# обработчик кнопки balance(balance)
@dp.callback_query_handler(lambda c: c.data == "balance", state="*")
async def balance_def(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    balance = await get_balance(user_name)
    await callback.message.edit_text(f"Ваш баланс: {balance} ₽", reply_markup=replenishment_balance)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработчик кнопки help(help_callback)
@dp.callback_query_handler(lambda c: c.data == "help_callback", state="*")
async def help_kb_handle(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Для связи с разработчиком бота перейдите по ссылке: \n\nhttps://t.me/KING_08001", reply_markup=back_keyboard)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

"""*********************************************** ВЫБОР ЛОКАЦИИ И ПОКУПКА ВПН ************************************************************************"""
# обработка кнопки выбора локации (buy_vpn)
@dp.callback_query_handler(lambda c: c.data == "buy_vpn", state="*")
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите локацию:", reply_markup=location_keyboard)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

# обработка кнопок локаций (Sweden_callback, Finland_callback, Germany_callback)
@dp.callback_query_handler(lambda c: c.data == "Sweden_callback" or c.data == "Finland_callback" or c.data == "Germany_callback")
async def location_choose_def(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "Sweden_callback":
        await callback.message.edit_text(f"Вы выбрали локацию: Швеция 🇸🇪\nVPN на данной локации сейчас нету в наличии ❌", reply_markup=back_keyboard)
        #await callback.message.edit_text(f"Вы выбрали локацию: Швеция 🇸🇪\nСтоимость данного товара {VPN_price_token} ₽", reply_markup=pay_sweden_keyboard)
        #await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        #await callback.answer("")

    elif callback.data == "Finland_callback":
        await callback.message.edit_text(f"Вы выбрали локацию: Финляндия 🇫🇮\nСтоимость данного товара {VPN_price_token} ₽", reply_markup=pay_finland_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await callback.answer("")

    elif callback.data == "Germany_callback":
        await callback.message.edit_text(f"Вы выбрали локацию: Германия 🇩🇪\nVPN на данной локации сейчас нету в наличии ❌", reply_markup=back_keyboard)
        #await callback.message.edit_text(f"Вы выбрали локацию: Германия 🇩🇪\nСтоимость данного товара {VPN_price_token} ₽", reply_markup=pay_germany_keyboard)
        #await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        #await callback.answer("")

# функция, которая обрабатывает покупку VPN.
async def buying_VPN_def(callback, country,  state):
    """Обработчик покупки VPN для заданной страны"""
    user_name = callback.from_user.username
    user_id = callback.from_user.id
    balance = await get_balance(user_name)
    if float(balance) < float(VPN_price_token):
        await callback.answer("У вас недостаточно средств ❌")
        await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        payment_key = await buy_operation(user_id=user_id, user_name=user_name)
        await callback.message.edit_text("Вы купили товар ✅! Ожидайте подготовки товара модераторами. Ключ активации VPN будет отправлен в этом чате.")
        user_id = callback.from_user.id
        async with state.proxy() as data:
            data['payment_key'] = payment_key
        await bot.send_message(Blazer_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard)
        await bot.send_message(Anush_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_buy_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await BuyVPNStates.WAITING_FOR_MESSAGE_TEXT.set()

# хендлер, который вызывает функцию, для обработки покупки VPN. Обрабатывает кнопки (Buying_sweden_VPN, Buying_finland_VPN, Buying_germany_VPN)
@dp.callback_query_handler(lambda c: c.data == "Buying_sweden_VPN" or c.data == "Buying_finland_VPN" or c.data == "Buying_germany_VPN")
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

# обработка кнопки ответа пользователю после покупки (payment_callback)
@dp.callback_query_handler(lambda c: c.data == "payment_callback")
async def payment_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Введите сообщение:", reply_markup=back_keyboard)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    await BuyVPNStates.WAITING_FOR_MESSAGE_TEXT.set()
    await callback.answer("")

# обработка ответа пользователю от модератора.
@dp.callback_query_handler(lambda c: c.data == "reply_buy_keyboard", state=BuyVPNStates.WAITING_FOR_MESSAGE_TEXT)
async def send_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Скиньте конфиг активации VPN для пользователя: ")
    await BuyVPNStates.WAITING_FOR_MESSAGE_TEXT.set()

@dp.message_handler(content_types=['text', 'document'],  state=BuyVPNStates.WAITING_FOR_MESSAGE_TEXT)
async def send_message_handle(message: types.Message, state):
    user_name = message.from_user.username
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    else:
        answer = message.text
        file_id = None
        file_name = None    
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
                if file_id is not None and file_name is not None:
                    await bot.send_document(user_id, file_id, caption="Спасибо за покупку!\nСледуйте инструкции для активации VPN", reply_markup=insturtion_keyboard)
                    await update_vpn_state(user_id=user_id, user_name=user_name, location=country, active=True, expiration_days=30)
                    await bot.send_document(message.from_user.id, file_id, caption=f"Файл для @{user_name} отправлен ✅", reply_markup=start_keyboard)

                else:
                    await bot.send_message(user_id, text=f"Спасибо за покупку\nВаш код активации: <pre>{answer}</pre>\nСледуйте инструкции для активации VPN", reply_markup=insturtion_keyboard, parse_mode="HTML")
                    await update_vpn_state(user_id=user_id, user_name=user_name, location=country, active=True, expiration_days=30)
                    await message.answer(f"Сообщение для @{user_name} отправлено ✅: {answer}", reply_markup=start_keyboard)

                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
            else:
                await message.answer("Не удалось отправить сообщение покупателю. Неверный ID заказа. ❌")
        except ChatNotFound:
            print("Не удалось отправить сообщение покупателю. Неверный ID пользователя ❌")
            await message.answer("Не удалось отправить сообщение покупателю. Неверный ID пользователя ❌")
    else:
        await message.answer(f"Пользователь не найден ❌", reply_markup=back_keyboard)
    await state.finish()

# обработка кнопки (instruction_keyboard)
@dp.callback_query_handler(lambda c: c.data == "instruction_keyboard")
async def instruction_handle(callback: types.CallbackQuery):
    await callback.message.answer_photo(photo="https://i.imgur.com/0feN5h0.jpeg", caption="""
Настройка для Android:
1. Загрузите приложение WireGuard из Google Play.
2. Для добавления туннеля WireGuard нажмите на кнопку «плюс» в нижнем углу экрана и выберите опцию. Здесь можно загрузить конфигурацию из скачанного файла конфигурации (которую мы прикрепили к этой ниже) или ввести данные вручную.""")
    await callback.message.answer_photo(photo="https://i.imgur.com/MvB2M5t.png", caption="""
3. Нажмите на переключатель рядом с появившимся именем туннеля. Система Android попросит выдать WireGuard разрешения для работы в качестве VPN. Дайте разрешение. После этого соединение будет установлено, в статус-баре будет отображаться знак в виде ключа""")


"""****************************************************************** ПРОДЛЕНИЕ VPN *************************************************************************"""
# хендлер для обработки кнопок для продления VPN(extension_vpn, extend_callback)
@dp.callback_query_handler(lambda c: c.data == "extension_vpn" or c.data == "extend_callback" or "extend_vpn" in c.data, state="*")
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
                expiration_date = datetime.datetime.strptime(str(vpn[5]), "%Y.%m.%d %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
                vpn_info_text += f"{numbers}. Локация: {location}\nДата окончания: {expiration_date.strftime('%Y.%m.%d %H:%M:%S')}\nОсталось: {days_remaining} дней\n\n"
            kb_for_count = await addind_count_for_extend(count=numbers)
            if numbers == 1:
                await callback.message.edit_text("<b>У вас один VPN:</b>\n\n" + vpn_info_text + f"<b>Продление VPN на 30 дней стоит {VPN_price_token} ₽ 💵\nНажмите на кнопку, если готовы продлить VPN</b>", reply_markup=extend_keyboard, parse_mode="HTML")
            else:
                await callback.message.edit_text(f"<b>Ваши VPN 🛡:</b>\n\n{vpn_info_text}<b>Продление VPN на 30 дней стоит {VPN_price_token} ₽ 💵. Выберите VPN, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await callback.message.edit_text("У вас нету действующего VPN ❌! Вам его необходимо приобрести ", reply_markup=buy_keyboard)
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

    elif callback.data == "extend_callback":
        user_name = callback.from_user.username
        balance = await get_balance(user_name)
        user_id = callback.from_user.id
        if float(balance) >= float(VPN_price_token):
            await pay_operation(VPN_price_token, user_id)
            vpn_data = await get_vpn_data(user_id)
            days_remaining = ""
            for vpn in vpn_data:
                id = vpn[0]
                location = vpn[3]
                active = vpn[4]
                expiration_date = datetime.datetime.strptime(vpn[5], "%Y.%m.%d %H:%M:%S")
                days_remaining = (expiration_date - datetime.datetime.now()).days
            new_expiration_date = expiration_date + datetime.timedelta(days=30)
            await extend_vpn_state(user_id=user_id, location=location, active=True, expiration_date=new_expiration_date, id=id)    
            await callback.message.edit_text(f"VPN продлен на 30 дней ✅ \n\nДо окончания действия VPN осталось {days_remaining + 30} дней", reply_markup=back_keyboard)
            await bot.send_message(Blazer_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nПродлил VPN на 30 дней.")
            await bot.send_message(Anush_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nПродлил VPN на 30 дней.")
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        else:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    
    elif "extend_vpn" in callback.data:
        user_id = callback.from_user.id
        user_name = callback.from_user.username
        vpn_number = callback.data.split('_')[2]
        vpn_data = await get_vpn_data(user_id)
        vpn = vpn_data[int(vpn_number) - int(1)]
        balance = await get_balance(user_name)
        if float(balance) >= float(VPN_price_token):
            await pay_operation(VPN_price_token, user_id)
            id = vpn[0]
            location = vpn[3]
            expiration_date = datetime.datetime.strptime(vpn[5], "%Y.%m.%d %H:%M:%S")
            days_remaining = (expiration_date - datetime.datetime.now()).days
            new_expiration_date = expiration_date + datetime.timedelta(days=30)
            await extend_vpn_state(user_id=user_id, location=location, active=True, expiration_date=new_expiration_date, id=id)
            await callback.message.edit_text(f"VPN продлен на 1 месяц ✅ \n\nДо окончания действия VPN осталось {days_remaining + 30} дней", reply_markup=back_keyboard)
            await bot.send_message(Anush_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nПродлил VPN на 30 дней.")
            await bot.send_message(Blazer_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nПродлил VPN на 30 дней.")
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        else:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())

        
            
"""************************************************** ПОПОЛНЕНИЕ БАЛАНСА *************************************************"""

# обработка кнопки для оплаты(replenishment)
@dp.callback_query_handler(lambda c: c.data == "replenishment", state="*")
async def replenishment_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите сумму пополнения, либо введите нужную самостоятельно: ", reply_markup=numbers_for_replenishment)
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    await PaymentStates.WAITING_FOR_AMOUNT.set()
    await callback.answer("")

@dp.callback_query_handler(lambda c: c.data == "200_for_replenishment_callback" or c.data == "500_for_replenishment_callback" or c.data == "1000_for_replenishment_callback", state=PaymentStates.WAITING_FOR_AMOUNT)
async def rubls_200_for_replenishment(callback: types.CallbackQuery, state):
    await callback.message.edit_text("Выберите платежную систему: ", reply_markup=payment_type)
    global amount
    if callback.data == "200_for_replenishment_callback":
        amount = 200
    elif callback.data == "500_for_replenishment_callback":
        amount = 500
    elif callback.data == "1000_for_replenishment_callback":
        amount = 1000
    await PaymentStates.WAINING_FOR_PAYMENT_TYPE.set()           

# обработка пополнения баланса
@dp.message_handler(state=PaymentStates.WAITING_FOR_AMOUNT)
async def handle_amount(message: types.Message, state: FSMContext):
    try:
        global amount
        amount = int(message.text)
        if amount > 0:
            await message.answer("Выберите платежную систему:", reply_markup=payment_type)
            await PaymentStates.WAINING_FOR_PAYMENT_TYPE.set()
        else:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток. Попробуйте заново /replenishment")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("Сумма пополнения должна быть больше 0.")
    except ValueError:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток. Попробуйте заново /replenishment")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("Введите корректную сумму (число).")
       
@dp.callback_query_handler(lambda c: c.data == "bank_card_payment_callback" or c.data == "yoomoney_payment_callback" or c.data == "TinkoffPay_callback" or c.data == "SberPay_callback", state=PaymentStates.WAINING_FOR_PAYMENT_TYPE)
async def payment_type_handle(callback: types.CallbackQuery, state):
    if callback.data == "bank_card_payment_callback":
        try:
            payment_url, payment_id = create_payment(amount, callback.from_user.id, "bank_card")
        except Exception as e:
            await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌")
            return
    elif callback.data == "yoomoney_payment_callback":
        try:
            payment_url, payment_id = create_payment(amount, callback.from_user.id, "yoo_money")
        except Exception as e:
            await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌")
            return
    elif callback.data == "TinkoffPay_callback":
        try:
            payment_url, payment_id = create_payment(amount, callback.from_user.id, "tinkoff_bank")
        except Exception as e:
            await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌")
            return
    elif callback.data == "SberPay_callback":
        try:
            payment_url, payment_id = create_payment(amount, callback.from_user.id, "sberbank")
        except Exception as e:
            await callback.message.edit_text("Произошла ошибка. Попробуйте позже. ❌")
            return
        
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
async def succesfull_payment(callback: types.CallbackQuery):
    payment_id = check(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    if payment_id:
        await callback.message.answer('Оплата прошла успешно ✅ \nЧтобы узнать свой баланс /balance')
        await pay_operation(amount, user_id)
        await callback.answer("")
    else:
        await callback.answer('Оплата еще не прошла. ')

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

    await message.answer("Вопрос отправлен модератору! Ожидайте ответ в этом чате.", reply_markup=start_keyboard)
    await bot.send_message(Blazer_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n{question}", reply_markup=reply_keyboard)
    await bot.send_message(Anush_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n{question}", reply_markup=reply_keyboard)
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
                await bot.send_message(support_request.user_id, f"Ответ от модератора:\n\n{answer}", reply_markup=start_keyboard)
                await bot.send_message(Anush_chat_token, f"Ответ отправлен пользователю @{user_name} (ID: {user_id})")
                await bot.send_message(Blazer_chat_token, f"Ответ отправлен пользователю @{user_name} (ID: {user_id})")
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
async def ref_system(callback: types.CallbackQuery):
    user_id = callback.message.from_user.id
    referrals = await get_referrer_username(user_id)
    if referrals != None:
        referrals = referrals.split("\n")
    else:
        referrals = referrals
    text = f"Ваша реферальная ссылка: <pre>https://t.me/blazervpnbot?start={user_id}</pre>\n\nПоделитесь этой ссылкой со своими знакомыми, чтобы получить 5 ₽ себе на баланс.\n\n"
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
async def promo_handle(callback: types.CallbackQuery, state):
    await callback.message.edit_text("Введите действующий промокод:", reply_markup=back_keyboard)
    if callback.message.reply_markup:
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        await save_temp_message(callback.from_user.id, callback.message.text, None)
    await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()

@dp.message_handler(state=PromocodeStates.WAITING_FOR_USER_PROMOCODE)
async def handle_user_promo(message: types.Message, state):
    user_promo = message.text
    user_id = message.from_user.id
    check_used_promo = await check_promocode_used(user_id, Promocode)
    if str(user_promo) == str(Promocode) and check_used_promo == False:
        await message.answer("Вы ввели правильный промокод ✅ \nНа ваш баланс зачислено: 20 рублей!", reply_markup=back_keyboard)
        await pay_operation(20, user_id)
        await save_promocode(user_id, user_promo)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
    elif str(user_promo) == str(Promocode) and check_used_promo == True:
        await message.answer("Вы уже использовали данный промокод ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard)    
    else:
        await message.answer("Вы ввели неправильный промокод, либо он неактуален ❌\n\nСледите за новостями в нашем сообществе в вк", reply_markup=promocode_keyboard)
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
    await state.finish()

"""*********************************************** ОБРАБОТКА ИНФОРМАЦИИ О VPN ПОЛЬЗОВАТЕЛЕЙ ******************************************"""

@dp.callback_query_handler(lambda c: c.data == "myvpn_callback", state="*")
async def myvpn_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    vpn_data = await get_vpn_data(user_id)
    if vpn_data:
        vpn_info_text = "Ваши VPN 🛡:\n\n"
        for vpn in vpn_data:
            location = vpn[3]
            active = vpn[4]
            expiration_date = datetime.datetime.strptime(vpn[5], "%Y.%m.%d %H:%M:%S")
            days_remaining = (expiration_date - datetime.datetime.now()).days
            vpn_info_text += f"Локация: {location}\nДата окончания: {expiration_date.strftime('%Y.%m.%d %H:%M:%S')}\nОсталось: {days_remaining} дней\n\n"
        await callback.message.edit_text(vpn_info_text, reply_markup=buy_keyboard)
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


"""********************************************** СИСТЕМА ВОЗВРАЩЕНИЯ К ПРЕДЫДУЩИМ СООБЩЕНИЯМ ****************************************"""

@dp.callback_query_handler(lambda c: c.data == "back", state="*")
async def back_handle(callback: types.CallbackQuery, state):
    await state.finish()
    user_id = callback.from_user.id
    message_id = await find_message_id(user_id)
    message_text, message_markup = await get_temp_message(user_id, message_id) 

    if message_text and message_markup:
        message_markup = deserialize_keyboard(message_markup)
        await callback.message.edit_text(message_text, reply_markup=message_markup)
        await delete_temp_message(user_id, message_id)
    else:
        await callback.message.edit_text("Вы возвращены на начальное меню.", reply_markup=start_keyboard)

    await callback.answer("")

"""************************************************************* ВРЕМЕННЫЕ АДМИН КОМАНДЫ ******************************************************"""

@dp.message_handler(state=AdmCommandState.WAITING_FOR_SUM_MONEY)
async def user_add_sum_handle(message: types.Message, state):
    user_sum = message.text
    user_id = message.from_user.id
    await pay_operation(int(user_sum), user_id)
    await message.answer(f"вы пополнили баланс на {user_sum}")
    await state.finish()

@dp.message_handler(state=AdmCommandState.WAITING_FOR_DELETE_SUM_MONEY)
async def user_add_sum_handle(message: types.Message, state):
    user_sum = message.text
    user_id = message.from_user.id
    await delete_sum_operation(int(user_sum), user_id)
    await message.answer(f"вы удалили баланс на {user_sum}")
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
