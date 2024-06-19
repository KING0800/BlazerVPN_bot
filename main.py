import logging
import sqlite3 as sq
import os
import datetime

from aiogram import types, Dispatcher, Bot, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound
from dotenv import load_dotenv, find_dotenv
from typing import NamedTuple
from keyboards import location_keyboard, pay_sweden_keyboard, replenishment_balance, start_keyboard, back_keyboard, reply_keyboard, insturtion_keyboard, pay_finland_keyboard, pay_germany_keyboard, buy_keyboard, extend_keyboard
from database import db_start, edit_profile, get_balance, buy_operation, pay_operation, checking_balance, get_vpn_state, update_vpn_state
from payment import create_payment, check

load_dotenv(find_dotenv())
bot_token = os.getenv("bot_token") 
Blazer_chat_token = os.getenv("Blazer_chat_token") 
Anush_chat_token = os.getenv("Anush_chat_token")
paymaster_token = os.getenv("paymaster_token") 
VPN_price_token = os.getenv("VPN_price_token") 
Account_payment_id_token = os.getenv("Account_payment_id_token") 
Secret_payment_key_token = os.getenv("Secret_payment_key_token")

TOKEN_API = bot_token
bot = Bot(TOKEN_API)

async def on_startup(dp):
    await db_start()

dp = Dispatcher(bot, storage=MemoryStorage())
previous_states = {}
support_requests = []

class SendMessageStates(StatesGroup):
    WAITING_FOR_MESSAGE_TEXT = State()
    WAITING_FOR_AMOUNT = State()

class SupportStates(StatesGroup):
    WAITING_FOR_QUESTION = State()
    WAITING_FOR_ANSWER = State()
    WAITING_FOR_MODERATOR_ANSWER = State()
    WAITING_FOR_MODERATOR_TEXT = State()

class SupportRequest(NamedTuple):
    user_id: int
    user_name: str
    question: str
    answer: str = None

previous_markup = None

"""************************************************* БАЗОВЫЕ КОМАНДЫ (/start, /help, /balance) *****************************************************"""
# обработчик команды /start
@dp.message_handler(commands=['start'], state="*")
async def start_cmd(message: types.Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await edit_profile(user_name, user_id)
    await message.answer("""Добро пожаловать в BlazerVPN – ваш надежный партнер в обеспечении безопасной и анонимной связи в сети.
 
Наш сервис предлагает доступ к трем локациям:
• Швеция 🇸🇪
• Финляндия 🇫🇮
• Германия 🇩🇪

Обеспечивая быструю и защищенную передачу данных. Независимо от того, где вы находитесь, BlazerVPN гарантирует конфиденциальность и безопасность вашей онлайн активности. Обеспечьте себе свободу и защиту в интернете с BlazerVPN!""", reply_markup=start_keyboard)

# обработчик всех входящий сообщений
@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    if message.text == "/help":
        await message.answer("Доступные команды:\n"
                           "/start - Начать работу с ботом\n"
                           "/balance - Проверить баланс\n"
                           "/help - Список команд", reply_markup=start_keyboard)
    elif message.text == "/balance":
        user_name = message.from_user.username
        balance = await get_balance(user_name)
        await message.answer(f"Ваш баланс: {balance} ₽", reply_markup=start_keyboard)
    else:
        await message.answer("Неверная команда. Пожалуйста, используйте одну из доступных команд.", reply_markup=start_keyboard)

# обработчик кнопки balance(balance)
@dp.callback_query_handler(lambda c: c.data == "balance")
async def balance_def(callback: types.CallbackQuery):
    user_name = callback.from_user.username
    balance = await get_balance(user_name)
    await callback.message.edit_text(f"Ваш баланс: {balance} ₽", reply_markup=replenishment_balance)

# обработчик кнопки help(help_callback)
@dp.callback_query_handler(lambda c: c.data == "help_callback")
async def help_kb_handle(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Для связи с разработчиком бота перейдите по ссылке: \nhttps://t.me/KING_08001", reply_markup=back_keyboard)
    async with state.proxy() as data:
        data['previous_text'] = callback.message.text
        data['previous_markup'] = callback.message.reply_markup

"""*********************************************** ВЫБОР ЛОКАЦИИ И ПОКУПКА ВПН ************************************************************************"""
# обработка кнопки выбора локации (buy_vpn)
@dp.callback_query_handler(lambda c: c.data == "buy_vpn")
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите локацию:", reply_markup=location_keyboard)
    async with state.proxy() as data:
        data['previous_text'] = callback.message.text
        data['previous_markup'] = callback.message.reply_markup

# обработка кнопок локаций (Sweden_callback, Finland_callback, Germany_callback)
@dp.callback_query_handler(lambda c: c.data == "Sweden_callback" or c.data == "Finland_callback" or c.data == "Germany_callback")
async def location_choose_def(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "Sweden_callback":
        await callback.message.edit_text(f"Вы выбрали локацию: Швеция 🇸🇪\nСтоимость данного товара {VPN_price_token} ₽", reply_markup=pay_sweden_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup
        await callback.answer("")

    elif callback.data == "Finland_callback":
        await callback.message.edit_text(f"Вы выбрали локацию: Финляндия 🇫🇮\nСтоимость данного товара {VPN_price_token} ₽", reply_markup=pay_finland_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup
        await callback.answer("")

    elif callback.data == "Germany_callback":
        await callback.message.edit_text(f"Вы выбрали локацию: Германия 🇩🇪\nСтоимость данного товара {VPN_price_token} ₽", reply_markup=pay_germany_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup
        await callback.answer("")

# функция, которая обрабатывает покупку VPN.
async def buying_VPN_def(callback, country,  state):
    """Обработчик покупки VPN для заданной страны"""
    user_name = callback.from_user.username
    balance = await get_balance(user_name)
    if float(balance) < float(VPN_price_token):
        await callback.answer("У вас недостаточно средств ❌")
        await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup
    else:
        payment_key = await buy_operation(user_name)
        await callback.message.edit_text("Вы купили товар ✅! Ожидайте подготовки товара модераторами. Ключ активации VPN будет отправлен в этом чате.")
        user_id = callback.from_user.id
        async with state.proxy() as data:
            data['payment_key'] = payment_key
        await bot.send_message(Blazer_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
        await bot.send_message(Anush_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗаказал VPN на локации: {country}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
        await update_vpn_state(user_id=user_id, location=country, active=True, expiration_date=30)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

# хендлер, который вызывает функцию, для обработки покупки VPN. Обрабатывает кнопки (Buying_sweden_VPN, Buying_finland_VPN, Buying_germany_VPN)
@dp.callback_query_handler(lambda c: c.data == "Buying_sweden_VPN" or c.data == "Buying_finland_VPN" or c.data == "Buying_germany_VPN")
async def buying_VPN_handle(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "Buying_sweden_VPN":
        await buying_VPN_def(callback, "Швеция 🇸🇪", state)

    elif callback.data == "Buying_finland_VPN":
        await buying_VPN_def(callback, "Финляндия 🇫🇮", state) 

    elif callback.data == "Buying_germany_VPN":
        await buying_VPN_def(callback, "Германия 🇩🇪", state)

# обработка кнопки ответа пользователю после покупки (payment_callback)
@dp.callback_query_handler(lambda c: c.data == "payment_callback")
async def payment_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Введите сообщение:", reply_markup=back_keyboard)
    await SendMessageStates.WAITING_FOR_MESSAGE_TEXT.set()
    await callback.answer("")

# обработка ответа пользователю от модератора.
@dp.message_handler(state=SendMessageStates.WAITING_FOR_MESSAGE_TEXT)
async def send_message(message: types.Message, state: FSMContext):
    message_text = message.text
    async with state.proxy() as data:
        payment_key = str(data.get('payment_key'))
    if payment_key:
        try:
            db = sq.connect('UserINFO.db')
            cur = db.cursor()
            cur.execute(
                "SELECT user_id FROM UserINFO WHERE payment_key = ?",
                (payment_key,)
            )
            row = cur.fetchone()
            db.close()
            if row:
                user_id = row[0]
                await bot.send_message(
                    user_id,
                    text=f"Спасибо за покупку\nВаш код активации: <pre>{message.text}</pre>\nСледуйте инструкции для активации VPN",
                    reply_markup=insturtion_keyboard,
                    parse_mode="HTML"
                )
                await message.answer(
                    f"Сообщение для @{user_id} отправлено ✅: {message_text}",
                    reply_markup=back_keyboard
                )
            else:
                await message.answer("Не удалось отправить сообщение покупателю. Неверный ID заказа. ❌")
        except ChatNotFound:
            print("Не удалось отправить сообщение покупателю. Неверный ID пользователя ❌")
            await message.answer("Не удалось отправить сообщение покупателю. Неверный ID пользователя ❌")
    else:
        await message.answer(f"Пользователь не найден ❌", reply_markup=back_keyboard)
    await state.finish()


"""***************************************************** ПРОДЛЕНИЕ VPN *************************************************************************"""
# хендлер для обработки кнопок для продления VPN(extension_vpn, extend_callback)
@dp.callback_query_handler(lambda c: c.data == "extension_vpn" or c.data == "extend_callback")
async def example_name_def(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "extension_vpn":
        user_id = callback.from_user.id
        active, days_remaining = await get_vpn_state(user_id)
        if active is None:
            await callback.message.edit_text("У вас нету действующего VPN! Вам его необходимо приобрести ", reply_markup=buy_keyboard)
        else:
            await callback.message.edit_text(f"Продление VPN на месяц стоит {VPN_price_token} ₽\nНажмите на кнопку, если готовы продлить VPN", reply_markup=extend_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "extend_callback":
        user_name = callback.from_user.username
        user_id = callback.from_user.id
        balance = await get_balance(user_name)
        if float(balance) >= float(VPN_price_token):
            await pay_operation(user_name)
            active, days_remaining = await get_vpn_state(user_id)
            if days_remaining is not None:
                expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
                await update_vpn_state(user_id, True, expiration_date)
                await callback.message.edit_text(f"VPN продлен на 1 месяц. До окончания действия VPN осталось {days_remaining + 30} дней")
            else:
                await callback.message.edit_text("VPN уже был продлен на максимальный срок.")
        else:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup

"""************************************************** ПОПОЛНЕНИЕ БАЛАНСА*************************************************"""
# обработка кнопки для оплаты(replenishment)
@dp.callback_query_handler(lambda c: c.data == "replenishment")
async def replenishment_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Введите сумму пополнения:", reply_markup=back_keyboard)
    await SendMessageStates.WAITING_FOR_AMOUNT.set()
    await callback.answer("")

# обработка пополнения баланса
@dp.message_handler(state=SendMessageStates.WAITING_FOR_AMOUNT)
async def handle_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount > 0:
            try:
                payment_url, payment_id = create_payment(amount, message.from_user.id)
            except Exception as e:
                logging.error(f"Ошибка при создании платежа: {e} ❌")
                await message.answer("Произошла ошибка. Попробуйте позже. ❌")
                return

            payment_button = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Оплатить", url=payment_url),
                        InlineKeyboardButton(text="Проверить оплату", callback_data=f"checking_payment_{payment_id}")
                    ]
                ]
            )
            await message.answer(f"Счет на оплату сформирован. ✅", reply_markup=payment_button)
            async with state.proxy() as data:
                data['previous_text'] = message.text
                data['previous_markup'] = message.reply_markup
        else:
            await message.answer("Сумма пополнения должна быть больше 0.")
    except ValueError:
        await message.answer("Введите корректную сумму (число).")
    
# обработка кнопки, для проверки успешного пополнения(checking_payment_)
@dp.callback_query_handler(lambda c: "checking_payment_" in c.data)
async def succesfull_payment(callback: types.CallbackQuery):
    result = check(callback.data.split('_')[-1])
    if result:
        await callback.message.answer('Оплата еще не прошла. ')
        return
    else:
        await callback.message.answer('Оплата прошла успешно. ')

"""****************************************************** СИСТЕМА ПОДДЕРЖКИ *******************************************************"""
# обработка кнопка поддержки (help_command_callback)
@dp.callback_query_handler(lambda c: c.data == "help_command_callback")
async def support_handle(callback: types.CallbackQuery):
    await callback.message.edit_text("Задайте вопрос:", reply_markup=back_keyboard)
    await SupportStates.WAITING_FOR_QUESTION.set()
    await callback.answer("")

# обработка отправления сообщения от пользователя модераторам
@dp.message_handler(state=SupportStates.WAITING_FOR_QUESTION)
async def process_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    question = message.text

    support_request = SupportRequest(user_id=user_id, user_name=user_name, question=question)
    support_requests.append(support_request)

    await message.answer("Вопрос отправлен модератору! Ожидайте ответ в этом чате.", reply_markup=start_keyboard)
    await bot.send_message(Blazer_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n{question}", reply_markup=reply_keyboard)
    await bot.send_message(Anush_chat_token, f"Пользователь @{user_name} (ID: {user_id})\nЗадал вопрос:\n{question}", reply_markup=reply_keyboard)
    await SupportStates.WAITING_FOR_MODERATOR_TEXT.set()

# обработка кнопки, для пересылания ответа модератора пользователю (reply_keyboard)
@dp.callback_query_handler(lambda c: c.data == "reply_keyboard", state=SupportStates.WAITING_FOR_MODERATOR_TEXT)
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите свой ответ:")
    await SupportStates.WAITING_FOR_MODERATOR_ANSWER.set()

# обработка пересылания сообщения от модератора пользователю.
@dp.message_handler(state=SupportStates.WAITING_FOR_MODERATOR_ANSWER)
async def replying_for_moder(message: types.Message):
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
                await bot.send_message(support_request.user_id, f"Ответ от модератора:\n{answer}", reply_markup=start_keyboard)
                await message.answer(f"Ответ отправлен пользователю @{user_name} (ID: {user_id})")
            except ChatNotFound:
                await message.answer("Пользователь не найден!")
            break

"""********************************************** СИСТЕМА ВОЗВРАЩЕНИЯ К ПРЕДЫДУЩИМ СООБЩЕНИЯМ ****************************************"""

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_handle(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if 'previous_text' in data and 'previous_markup' in data:
            await callback.message.edit_text(data['previous_text'], reply_markup=data['previous_markup'])
            await callback.answer("")
            data.pop('previous_text', None)
            data.pop('previous_markup', None)
        else:
            await callback.message.edit_text("Вы возвращены на начальное меню.", reply_markup=start_keyboard)
            await callback.answer("")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
