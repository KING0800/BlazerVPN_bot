import logging
import sqlite3 as sq

from aiogram import types, Dispatcher, Bot, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound
from typing import NamedTuple
from keyboards import location_keyboard, pay_sweden_keyboard, replenishment_balance, start_keyboard, back_keyboard, reply_keyboard, insturtion_keyboard, pay_finland_keyboard, pay_germany_keyboard
from tokens import bot_token, Blazer_chat_token, Anush_chat_token, paymaster_token, VPN_price_token, Account_id, Secret_key
from database import db_start, edit_profile, get_balance, buy_operation, pay_operation, changing_payment_key
from payment import create_payment, check


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

class SupportRequest(NamedTuple):
    user_id: int
    user_name: str
    question: str
    answer: str = None


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

@dp.callback_query_handler()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "buy_vpn":
        await callback.message.edit_text("Выберите локацию:", reply_markup=location_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "help_callback":
        await callback.message.edit_text("Для связи с разработчиком бота перейдите по ссылке: \nhttps://t.me/KING_08001", reply_markup=back_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup
        
    elif callback.data == "extension_vpn":
        await callback.message.edit_text("Недоделано", reply_markup=back_keyboard)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "Sweden_callback":
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


    elif callback.data == "Buying_sweden_VPN":
        user_name = callback.from_user.username
        balance = await get_balance(user_name)
        if balance < 100:
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
            await bot.send_message(Blazer_chat_token, f"Пользователь {user_name}\nЗаказал VPN на локации: Швеция 🇸🇪\nID пользователя: {user_id}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
            await bot.send_message(Anush_chat_token, f"Пользователь {user_name}\nЗаказал VPN на локации: Швеция 🇸🇪\nID пользователя: {user_id}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "Buying_finland_VPN":
        user_name = callback.from_user.username
        balance = await get_balance(user_name)
        if balance < 100:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup 
        else:
            payment_key = await buy_operation(user_name)
            await callback.message.answer("Вы купили товар ✅! Ожидайте подготовки товара модераторами. Ключ активации VPN будет отправлен в этом чате.")
            user_id = callback.from_user.id

            async with state.proxy() as data:
                data['payment_key'] = payment_key
            await bot.send_message(Blazer_chat_token, f"Пользователь {user_name}\nЗаказал VPN на локации: Финляндия 🇫🇮\nID пользователя: {user_id}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
            await bot.send_message(Anush_chat_token, f"Пользователь {user_name}\nЗаказал VPN на локации: Финляндия 🇫🇮\nID пользователя: {user_id}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "Buying_germany_VPN":
        user_name = callback.from_user.username
        balance = await get_balance(user_name)
        if balance < 100:
            await callback.answer("У вас недостаточно средств ❌")
            await callback.message.edit_text("Чтобы пополнить свой баланс, нажмите на кнопку.", reply_markup=replenishment_balance)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup 
        else:
            payment_key = await buy_operation(user_name)
            await callback.message.answer("Вы купили товар ✅! Ожидайте подготовки товара модераторами. Ключ активации VPN будет отправлен в этом чате.")
            user_id = callback.from_user.id

            async with state.proxy() as data:
                data['payment_key'] = payment_key
            await bot.send_message(Blazer_chat_token, f"Пользователь {user_name}\nЗаказал VPN на локации: Германия 🇩🇪\nID пользователя: {user_id}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
            await bot.send_message(Anush_chat_token, f"Пользователь {user_name}\nЗаказал VPN на локации: Германия 🇩🇪\nID пользователя: {user_id}\nПредоставьте ключ активации.", reply_markup=reply_keyboard)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup

    elif "checking_payment_" in callback.data:
        payment_id = callback.data.split("_")[-1]
        try:
            payment_successful = check(payment_id)
        except Exception as e:
            logging.error(f"Ошибка при проверке платежа: {e} ❌")
            await callback.message.edit_text('Произошла ошибка при проверке оплаты. ❌')
            return

        if payment_successful:
            user_name = callback.message.from_user.username
            await callback.message.edit_text('Оплата прошла успешно. ✅')
            await callback.answer("")
            pay_operation(user_name)
            async with state.proxy() as data:
                data['previous_text'] = callback.message.text
                data['previous_markup'] = callback.message.reply_markup
        else:
            await callback.message.edit_text('Оплата еще не прошла. ❌')   
            await callback.answer("")
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "balance":
        user_name = callback.from_user.username
        await callback.message.edit_text(f'Ваш баланс: {await get_balance(user_name=user_name)} ₽', reply_markup=replenishment_balance)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "reply_keyboard":
        await callback.message.answer("Введите текст сообщения:")
        await SendMessageStates.WAITING_FOR_MESSAGE_TEXT.set()
        await callback.answer("")
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup

    elif callback.data == "replenishment":
        text = "Введите сумму пополнения баланса:"
        await callback.message.edit_text(text)
        async with state.proxy() as data:
            data['previous_text'] = callback.message.text
            data['previous_markup'] = callback.message.reply_markup
        await SendMessageStates.WAITING_FOR_AMOUNT.set()
        
    elif callback.data == "help_command_callback":
        await callback.message.answer("Введите текст своего вопроса:")
        await state.set_state(SupportStates.WAITING_FOR_QUESTION)
   
    elif callback.data == "instruction_keyboard":
        await callback.message.answer("Инструкция не доделана.")
        await callback.answer("")
        previous_data = previous_states.get(callback.message.chat.id, [])
        previous_data.append({
            'text': callback.message.text,
            'reply_markup': callback.message.reply_markup
        })
        previous_states[callback.message.chat.id] = previous_data
    
    elif callback.data == "back":
        async with state.proxy() as data:
            previous_text = data.get('previous_text')
            previous_markup = data.get('previous_markup')

        if previous_text and previous_markup:
            await callback.message.edit_text(previous_text, reply_markup=previous_markup)
            await state.finish()  # Или переход в другое состояние
        else:
            await callback.message.edit_text("Нет предыдущего состояния ❌. Используйте /start")
            await state.finish()  # Или переход в другое состояние

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
            await state.finish()
            # Сохраняем предыдущие данные
            async with state.proxy() as data:
                data['previous_text'] = message.text
                data['previous_markup'] = message.reply_markup
        else:
            await message.answer("Сумма пополнения должна быть больше 0.")
    except ValueError:
        await message.answer("Введите корректную сумму (число).")

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

    async with state.proxy() as data:
        data['previous_text'] = message.text
        data['previous_markup'] = message.reply_markup

@dp.message_handler(state=SupportStates.WAITING_FOR_QUESTION)
async def report_answer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    question = message.text
    answer_id = len(support_requests) - 1

    request = SupportRequest(user_id, user_name, question)
    support_requests.append(request)

    report_keyboard = InlineKeyboardMarkup()
    report_keyboard.add(
            InlineKeyboardButton(text="Отправить ответ", callback_data=f"answer_{answer_id}")
    )
    await bot.send_message(Blazer_chat_token, 
                f"Новый запрос от @{user_name} (ID: {user_id}):\n{question}", reply_markup=report_keyboard)
    await bot.send_message(Anush_chat_token, 
                f"Новый запрос от @{user_name} (ID: {user_id}):\n{question}", reply_markup=report_keyboard)
    await message.answer(f"Ваш запрос принят ✅. Ожидайте ответа модератора.")
    await state.set_state(SupportStates.WAITING_FOR_ANSWER)

@dp.callback_query_handler(text_startswith="answer_", state=SupportStates.WAITING_FOR_ANSWER)
async def handle_moderator_answer(callback: types.CallbackQuery, state: FSMContext):
    answer_id = int(callback.data.split("_")[1])
    await state.update_data(answer_id=answer_id)
    await callback.message.answer("Введите свой ответ:")
    await callback.answer("")
    await state.set_state(SupportStates.WAITING_FOR_MODERATOR_ANSWER)

@dp.message_handler(state=SupportStates.WAITING_FOR_MODERATOR_ANSWER)
async def repling_maneger(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer_id = data.get("answer_id")
    request = support_requests[answer_id]
    request_answer = message.text
    await bot.send_message(request.user_id, f"Ответ модератора:\n{request_answer}")
    await bot.send_message(Blazer_chat_token, f"Запрос от @{request.user_name} закрыт. ✅")
    await bot.send_message(Anush_chat_token, f"Запрос от @{request.user_name} закрыт. ✅")
    await state.finish()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        executor.start_polling(dp, on_startup=on_startup)
    except KeyboardInterrupt:
        print('Exit')
