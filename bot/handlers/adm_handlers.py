import os
import datetime
import asyncio

from dotenv import load_dotenv
from typing import NamedTuple
from datetime import timedelta

from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound

from bot.database.OperationsData import edit_operations_history
from bot.database.TempData import save_temp_message, get_temp_message, delete_temp_message, find_message_id
from bot.database.UserData import get_balance, add_operation, pay_operation, get_referrer_username, find_user_data, ban_users_handle, unban_users_handle, is_user_ban_check, delete_sum_operation
from bot.database.VpnData import update_vpn_state, get_order_id, get_vpn_data, check_vpn_expiration_for_days, check_expired_vpns
from bot.database.SupportData import getting_question, deleting_answered_reports

from bot.keyboards.user_keyboards import support_keyboard, back_keyboard
from bot.keyboards.adm_keyboards import adm_panel_keyboard, buy_info_keyboard, user_find_data, about_yourself_to_add_keyboard, about_yourself_to_delete_keyboard, finish_buy_vpn, extension_keyboard

load_dotenv('.env')

BLAZER_CHAT_TOKEN = os.getenv('BLAZER_CHAT_TOKEN')
ANUSH_CHAT_TOKEN = os.getenv('ANUSH_CHAT_TOKEN')
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)

"""********************************************* СОСТОЯНИЯ ******************************************************"""

class BuyVPNStates(StatesGroup):
    WAITING_FOR_MESSAGE_TEXT = State()

class SupportStates(StatesGroup):
    WAITING_FOR_QUESTION = State()
    WAITING_FOR_MODERATOR_ANSWER = State()

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

support_requests = []


"""***************************************************************** """

# обработка кнопки для пересылания конфига для активации VPN пользователя   
async def send_message(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    order_id = int(callback.data.split(".")[1])
    location = callback.data.split(".")[2]
    user_id = int(callback.data.split(".")[3])

    await state.update_data(order_id=order_id)

    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("• 🛒 <b>Покупка VPN</b>:\n\nСкиньте конфиг активации VPN для пользователя: ", parse_mode="HTML", reply_markup=back_keyboard)
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        await BuyVPNStates.WAITING_FOR_MESSAGE_TEXT.set()

async def handling_moder_file(message: types.Message, state: FSMContext):
    if message.document:
        moder_file = message.document.file_id
        moder_file_name = message.document.file_name

        order_id_data = await state.get_data()
        order_id = order_id_data.get('order_id')
        if not int(order_id):
            await message.answer("• 🛒 <b>Покупка VPN</b>:\n\nID заказа не найден ❌", parse_mode="HTML")
            await state.finish()
        
        order_data = await get_order_id(int(order_id))
        if not order_data:
            await message.answer("• ❌ <b>Ошибка</b>:\n\nЗаказа с таким ID не существует.", parse_mode="HTML")
            await state.finish()
            
        try:
            expiration_date = datetime.datetime.now() + timedelta(days=28)
            await update_vpn_state(order_id=int(order_id), active=True, expiration_days=expiration_date.strftime("%d.%m.%Y %H:%M:%S"), name_of_vpn=moder_file_name, vpn_config=moder_file)
        except Exception as e:
            await message.answer("• 🛒 <b>Покупка VPN</b>:\n\nПроизошла ошибка по время записи данных в базу данных ❌", parse_mode="HTML")
            await state.finish()

        await message.answer(f"• 🛒 <b>Покупка VPN</b>:\n\nVPN для пользователя @{order_data[2]} (ID: <code>{order_data[1]}</code>) активирован и добавлен в базу данных ✅", parse_mode="HTML")
        await bot.send_document(order_data[1], moder_file, caption=f"• 🛒 <b>Покупка VPN</b>:\n\nVPN успешно активирован ✅\n\nПодключитесь к VPN по нашей <code>инструкции</code>, с которой можно ознакомиться нажав на кнопку снизу.\n\n<i>Срок действия:</i> <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n\nПродлить VPN можно в любое время через нашего бота.", parse_mode="HTML", reply_markup=finish_buy_vpn)
        await state.finish()
    else:
        attempts = await state.get_data()
        if attempts.get("attempts", 0) >= 3:
            await message.answer("Слишком много попыток ❌\n Попробуйте заново")
            await state.finish()
        else:
            await state.update_data(attempts=attempts.get("attempts", 0) + 1)
            await message.answer("• 🛒 <b>Покупка VPN</b>:\n\nВы скинули неверный тип конфига!\n\n<i>Попробуйте заново:</i>", parse_mode="HTML")


# обработка кнокпи для пересылания ответа модератора пользователю
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    global questions_user_id
    questions_user_id = callback.data.split('_')[2]
    await callback.message.answer("• 🆘 <b>Система поддержки</b>:\n\nНапишите свой ответ:", reply_markup=back_keyboard, parse_mode="HTML")
    await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    await callback.answer("")
    await SupportStates.WAITING_FOR_MODERATOR_ANSWER.set()

# обработка отправки ответа пользователю
async def replying_for_moder(message: types.Message, state):
    user_info = await getting_question(questions_user_id)
    if user_info != None:
        for info in user_info:
            id = info[0]
            user_id = info[1]
            user_name = info[2]
            question = info[3]

        answer = message.text
        try:
            await bot.send_message(questions_user_id, f"• 🆘 <b>Ответ от модератора:</b>\n\n{answer}", reply_markup=back_keyboard, parse_mode="HTML")
            await bot.send_message(ANUSH_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nВопрос пользователя @{user_name} (ID: <code>{user_id})</code>:\n\n{question}\n\n<b>Ответ модератора:</b>\n\n{answer}", parse_mode='HTML')
            await bot.send_message(BLAZER_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nВопрос пользователя @{user_name} (ID: <code>{user_id})</code>:\n\n{question}\n\n<b>Ответ модератора:</b>\n\n{answer}", parse_mode="HTML")
            await deleting_answered_reports(user_id=user_id)
        except ChatNotFound:
            await message.answer("Пользователь не найден!")
    else: 
        await message.answer("Данный пользователь не найден ❌")
    if message.reply_markup:
        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
    else:  
        await save_temp_message(message.from_user.id, message.text, None)
    await state.finish()

# обработка сообщения админ панели
async def adm_panel_handle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        await callback.message.edit_text("• 🤖 <b>Админ панель:</b>\n\nВыберите нужно действие: ", reply_markup=adm_panel_keyboard, parse_mode="HTML")
        if callback.message.reply_markup:
            await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
        else:
            await save_temp_message(callback.from_user.id, callback.message.text, None)
        await callback.answer('')

# обработка всех кнопок в админ панели
async def adm_panel_buttons_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        # удаление и Пополнение баланса
        if callback.data == "addind_balance_callback":
            await callback.message.edit_text("• 💵 <b>Пополнение баланса:</b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=about_yourself_to_add_keyboard, parse_mode="HTML")
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            await AdmCommandState.WAITING_ID_OF_USER_FOR_ADD.set()
        elif callback.data == "deleting_balance_callback":
            await callback.message.edit_text("• 💵 <b>Удаление баланса:</b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=about_yourself_to_delete_keyboard, parse_mode="HTML")
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            await AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE.set()

        elif callback.data == "user_data_callback":
            await callback.message.edit_text("• 🗃 <b>Данные о пользователе:</b>\n\nВведите ID или USERNAME пользователя, информацию про которого хотите узнать: ", reply_markup=back_keyboard, parse_mode="HTML")
            await callback.answer('')
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            await AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO.set()

        elif callback.data == "vpn_user_callback":
            await callback.message.edit_text("• 🛡️ <b>VPN пользователя:</b>\n\nВведите ID или USERNAME пользователя, информацию о VPN которого хотите узнать: ", reply_markup=back_keyboard, parse_mode="HTML")
            await callback.answer('')
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            await UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO.set()
        elif callback.data == "ban_user_callback":
            await callback.message.edit_text("• ❌ <b>Блокировка пользователя:</b>\n\nВведите ID или USERNAME пользователя, которого хотите заблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
            await callback.answer('')
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            await BanUserState.WAITING_FOR_USER_ID.set()
        elif callback.data == "unban_user_callback":
            await callback.message.edit_text("• ✅ <b>Разблокировка пользователя:</b>\n\nВведите ID или USERNAME пользователя, которого хотите разблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
            await callback.answer('')
            if callback.message.reply_markup:
                await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
            else:
                await save_temp_message(callback.from_user.id, callback.message.text, None)
            await UnbanUserState.WAITING_FOR_USER_ID.set()

# обрабатывает кнопку about_yourself_keyboard, чтобы указать, что удаление баланса должно быть модератору, который нажал на кнопку
async def deleting_balance_for_moder(callback: types.CallbackQuery, state):
    global user_id_for_delete
    global user_name_for_delete
    user_id_for_delete = callback.from_user.id
    user_name_for_delete = callback.from_user.username
    await callback.message.edit_text("• 💵 <b>Удаление баланса:</b>\n\nВведите сумму для удаления баланса:", reply_markup=back_keyboard, parse_mode="HTML")
    if callback.message.reply_markup:
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        await save_temp_message(callback.from_user.id, callback.message.text, None)
    await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE.set()

# обрабатывает кнопку about_yourself_keyboard, чтобы указать, что Пополнение баланса должно быть модератору, который нажал на кнопку
async def adding_balance_for_moder(callback: types.CallbackQuery, state):
    global user_id_for_add
    global user_name_for_add
    user_id_for_add = callback.from_user.id
    user_name_for_add = callback.from_user.username
    await callback.message.edit_text("• 💵 <b>Пополнение баланса:</b>\n\nВведите сумму для пополнения баланса:", reply_markup=back_keyboard, parse_mode="HTML")
    if callback.message.reply_markup:
        await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
    else:
        await save_temp_message(callback.from_user.id, callback.message.text, None)
    await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD.set()


# обработка разблокировки пользователя через информацию о пользователе
async def unban_user2_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        data = await state.get_data()
        try:
            user_id = int(data.get("user_id"))
            user_name = None
            is_registrated_user = await find_user_data(user_id=user_id)
            if is_registrated_user:
                result = await unban_users_handle(user_id=user_id)
                if result != "unbanned":
                    await callback.message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                else:
                    await callback.message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново - /unban ")
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
                    await callback.message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                else:
                    await callback.message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново - /unban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)

# обработка разблокировки пользователя 
async def unban_user_handle(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        try:
            user_id = int(message.text)
            user_name = None
            is_registrated_user = await find_user_data(user_id=user_id)
            if is_registrated_user:
                result = await unban_users_handle(user_id=user_id)
                if result != "unbanned":
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                else:
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("Слишком много попыток ❌\nПопробуйте заново - /unban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
        except Exception as e:
            user_name = message.text
            user_id = None
            is_registrated_user = await find_user_data(user_name=user_name)
            if is_registrated_user:
                result = await unban_users_handle(user_name=user_name)
                if result != "unbanned":
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                else:
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)

                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("Слишком много попыток ❌\nПопробуйте заново - /unban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)

# обработка блокировки пользователя через меню информации о пользователе
async def ban_user2_handle(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        data = await state.get_data()
        try:
            user_id = int(data.get("user_id"))
            user_name = None
            is_registrated_user = await find_user_data(user_id=user_id)
            if is_registrated_user:
                result = await ban_users_handle(user_id=user_id)
                if result != "banned":
                    await callback.message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                else:
                    await callback.message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nЭтот пользователь уже находится в бане ❌", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\nПопробуйте заново - /ban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')

        except Exception as e:
            user_name = data.get("user_name")
            user_id = None
            is_registrated_user = await find_user_data(user_name=user_name)
            if is_registrated_user:
                result = await ban_users_handle(user_name=user_name)
                if result != "banned":
                    await callback.message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                else:
                    await callback.message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nЭтот пользователь уже находится в бане ❌", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n Попробуйте заново - /ban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)

# обработка блокировки пользователей 
async def ban_user_handle(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        try:
            user_id = int(message.text)
            user_name = None
            is_registrated_user = await find_user_data(user_id=user_id)
            if is_registrated_user:
                result = await ban_users_handle(user_id=user_id)
                if result != "banned":
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                else:
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nЭтот пользователь уже находится в бане ❌", parse_mode="HTML", reply_markup=back_keyboard)
                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("Слишком много попыток ❌\nПопробуйте заново - /ban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь с таким <b>ID</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
        except Exception as e:
            user_name = message.text
            user_id = None
            is_registrated_user = await find_user_data(user_name=user_name)
            if is_registrated_user:
                result = await ban_users_handle(user_name=user_name)
                if result != "banned":
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
                else:
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nЭтот пользователь уже находится в бане ❌", parse_mode="HTML", reply_markup=back_keyboard)

                await state.finish()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("Слишком много попыток ❌\nПопробуйте заново - /ban ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)

# обработка поиска информации о VPN пользователей
async def find_info_about_users_vpn(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
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
                    expiration_date = vpn[5]
                    if expiration_date is not None:
                        expiration_date = str(expiration_date)
                        expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                        days_remaining = (expiration_date_new - datetime.datetime.now()).days
                        name_of_vpn = vpn[6]
                        vpn_config = vpn[7]
                        await bot.send_document(message.from_user.id, vpn_config, caption=f"• 🛡️ <b>VPN пользователя:</b>\n\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date_new.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n", parse_mode="HTML")
                    else:
                        await message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nУ пользователя имеется приобретенный VPN, который не обработан модераторами.", parse_mode="HTML")
            else:
                await message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
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
                        if expiration_date is not None:
                            expiration_date = str(expiration_date)
                            expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                            days_remaining = (expiration_date_new - datetime.datetime.now()).days
                            name_of_vpn = vpn[6]
                            vpn_config = vpn[7]
                            await bot.send_document(message.from_user.id, vpn_config, caption=f"• 🛡️ <b>VPN пользователя:</b>\n\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date_new.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n", parse_mode="HTML")
                        else:
                            await message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nУ пользователя имеется приобретенный VPN, который не обработан модераторами.", parse_mode="HTML")
                else:
                    await message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await message.answer("Слишком много попыток ❌\nПопробуйте заново - /user_vpn ")
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await message.answer("• 🗃 <b>Данные о пользователе</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново: ", parse_mode="HTML", reply_markup=back_keyboard)
            
                await message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nПользователь с таким USERNAME не найдет ❌\n\nПопробуйте ввести USERNAME или ID заново:", parse_mode="HTML", reply_markup=back_keyboard)

# обработка информации о пользователе
async def find_user_info_for_adm_panel(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
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

            if is_banned == 0:
                is_banned = "-"
            else:
                is_banned = "+"

            if referrer_id == None:
                referrer_id = "-"
                user_info_text = f"• 🗃 <b>Данные о пользователе</b>:\n\nID в базе данных: <code>{id}</code>\nTelegram ID: <code>{user_id}</code>\nUsername пользователя: <code>{user_name}</code>\nБаланс: <code>{balance}</code> ₽\nВремя регистрации: <code>{time_of_registration}</code>\nРеферер: <code>-</code>\nИспользованные промокоды: <code>{used_promocodes_text}</code>\nЗабанен ли пользователь: <code>{is_banned}</code>"
            else:
                referrer_username = await get_referrer_username(user_id=referrer_id)
                user_info_text = f"• 🗃 <b>Данные о пользователе</b>:\n\nID в базе данных: <code>{id}</code>\nTelegram ID: <code>{user_id}</code>\nUsername пользователя: <code>{user_name}</code>\nБаланс: <code>{balance}</code> ₽\nВремя регистрации: <code>{time_of_registration}</code>\nРеферер: {referrer_username}({referrer_id})\nИспользованные промокоды: <code>{used_promocodes_text}</code>\nЗабанен ли пользователь: <code>{is_banned}</code>"
            await message.answer(user_info_text, reply_markup=user_find_data, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
            await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()

        elif user_id_for_find_info == None and user_info == []:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\nПопробуйте заново - /user_info ")
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 🗃 <b>Данные о пользователе</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново: ", parse_mode="HTML", reply_markup=back_keyboard)
        elif user_name_for_find_info == None and user_info == []:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /user_info ", reply_markup=back_keyboard)
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 🗃 <b>Данные о пользователе</b>:\n\nПользователь с таким <b>ID</b> не найден ❌", parse_mode="HTML", reply_markup=back_keyboard)

# обработка информации о VPN пользователей через меню управления пользователем
async def vpn_info_handle(callback: types.CallbackQuery, state: FSMContext):   
    user_id = callback.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await callback.message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        data = await state.get_data()
        try:
            user_id1 = int(data.get("user_id"))
            user_name = None
            vpn_data = await get_vpn_data(user_id=user_id1)
            user_info = await find_user_data(user_id=user_id1)
            if user_info != None:
                if vpn_data != None:
                    for vpn in vpn_data:
                        id = vpn[0]
                        user_id = vpn[1]
                        user_name = vpn[2]
                        location = vpn[3]
                        active = vpn[4]
                        expiration_date = vpn[5]
                        if expiration_date is not None:
                            expiration_date = str(expiration_date)
                            expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                            days_remaining = (expiration_date_new - datetime.datetime.now()).days
                            name_of_vpn = vpn[6]
                            vpn_config = vpn[7]
                            await bot.send_document(callback.from_user.id, vpn_config, caption=f"• 🛡️ <b>VPN пользователя:</b>\n\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n", parse_mode="HTML")
                        else:
                            await callback.message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nУ пользователя имеется приобретенный VPN, который не обработан модераторами.", parse_mode="HTML")
                        await callback.answer('')
                        await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()

                else:
                    await callback.message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                    await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /user_vpn")
                    await callback.answer('')
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("• 🛡️ <b>VPN пользователя:</b>:\n\nПользователь с таким <b>ID</b> не найден ❌\n\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)
        except Exception:
            user_name = data.get("user_name")
            user_id = None
            vpn_data = await get_vpn_data(user_name=user_name)
            user_info = await find_user_data(user_name=user_name)
            if user_info != [] or user_info != None:
                if vpn_data != []:
                    for vpn in vpn_data:
                        id = vpn[0]
                        user_id = vpn[1]
                        user_name = vpn[2]
                        location = vpn[3]
                        active = vpn[4]
                        expiration_date = vpn[5]
                        if expiration_date is not None:
                            expiration_date = str(expiration_date)
                            expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                            days_remaining = (expiration_date_new - datetime.datetime.now()).days
                            name_of_vpn = vpn[6]
                            vpn_config = vpn[7]
                            await bot.send_document(callback.from_user.id, vpn_config, caption=f"• 🛡️ <b>VPN пользователя:</b>\n\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date_new.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n", parse_mode="HTML")
                        else:
                            await callback.message.answer("• 🛡️ <b>VPN пользователя:</b>:\n\nУ пользователя имеется приобретенный VPN, который не обработан модераторами.", parse_mode="HTML")
                        await callback.answer('')
                        await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
                else:
                    await callback.message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
                    await callback.answer('')
                    await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
            else:
                attempts = await state.get_data()
                if attempts.get("attempts", 0) >= 3:
                    await callback.message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /user_vpn")
                    await callback.answer('')
                    await state.finish()
                else:
                    await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                    await callback.message.answer("• 🛡️ <b>VPN пользователя:</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)

# Пополнение баланса администратором
async def handling_user_name(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        global user_id_for_add
        global user_name_for_add
        try:
            user_id_for_add = int(message.text)
            user_name_for_add = None
        except Exception as e:
            user_name_for_add = message.text
            user_id_for_add = None
        await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nВведите сумму для пополнения баланса:", reply_markup=back_keyboard, parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD.set()

# ожидание суммы пополнения баланса модератором
async def handle_for_adm_add_sum(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        try:
            global adm_sum_for_add
            adm_sum_for_add = int(message.text)
        except Exception as e:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /add")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nВведите корректную сумму (число) ❌", parse_mode="HTML")
        if adm_sum_for_add > 0:
            if user_id_for_add != None:
                await add_operation(int(adm_sum_for_add), user_id=user_id_for_add)
                await bot.send_message(user_id_for_add, f"• 💵 <b>Пополнение баланса</b>:\n\nМодератор пополнил ваш баланс на сумму: {adm_sum_for_add} ₽ ✅", parse_mode="HTML")
            elif user_name_for_add != None:
                user_info = await find_user_data(user_name=user_name_for_add)
                for info in user_info:
                    user_id_for_reply = info[1]
                await add_operation(int(adm_sum_for_add), user_name=user_name_for_add)
                await bot.send_message(user_id_for_reply, f"• 💵 <b>Пополнение баланса</b>:\n\nМодератор пополнил ваш баланс на сумму: {adm_sum_for_add} ₽ ✅", parse_mode="HTML")
        else:
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /add")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nСумма для пополнения должна быть больше нуля ❌\n\n<i>Попробуйте ввести сумму заново:</i>", parse_mode="HTML")
        await message.answer(f"• 💵 <b>Пополнение баланса</b>:\n\nБаланс указанного пользователя пополнен на: {adm_sum_for_add} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
        await state.finish()
        await edit_operations_history(user_id=user_id_for_add, user_name=user_name_for_add, operations=(+(int(adm_sum_for_add))), description_of_operation="🤖 Модератор")

# удаление баланса модераторами
async def handling_user_name_for_delete(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        global user_id_for_delete
        global user_name_for_delete
        try:
            user_id_for_delete = int(message.text)
            user_name_for_delete = None
        except Exception as e:
            user_name_for_delete = message.text
            user_id_for_delete = None
        await message.answer("• 💵 <b>Удаление баланса:</b>\n\nВведите сумму для удаления баланса:", reply_markup=back_keyboard, parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)
        await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE.set()

# обработка числа для удаления баланса модераторами
async def handle_for_adm_delete_sum(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("• ❌ <b>Вы заблокированы:</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        await state.finish()
        return
    else:
        try:
            adm_sum_for_delete = int(message.text)
        except Exception as e:
            attempts = await state.get_data()
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /delete ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 💵 <b>Удаление баланса:</b>\n\nВведите корректную сумму (число) ❌", parse_mode="HTML")
        if message.reply_markup:
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
        else:
            await save_temp_message(message.from_user.id, message.text, None)

        if adm_sum_for_delete > 0:
            if user_id_for_delete != None:
                balance = await get_balance(user_id=user_id_for_delete)
                if balance >= int(adm_sum_for_delete):
                    await delete_sum_operation(int(adm_sum_for_delete), user_id=user_id_for_delete)
                    await edit_operations_history(user_id=user_id_for_delete, user_name=user_name_for_delete, operations=(-(int(adm_sum_for_delete))), description_of_operation="🤖 Модератор")
                    await bot.send_message(user_id_for_delete, f"• 💵 <b>Удаление баланса</b>:\n\nМодератор удалил ваш баланс на сумму: {adm_sum_for_delete} ₽ ", parse_mode="HTML")
                    await message.answer(f"• 💵 <b>Удаление баланса:</b>\n\nБаланс указанного пользователя удален на: {adm_sum_for_delete} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
                    await state.finish()
                else:
                    attempts = await state.get_data()
                    if attempts.get("attempts", 0) >= 3:
                        await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /delete ")
                        await state.finish()
                    else:
                        await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                        await message.answer('• 💵 <b>Удаление баланса:</b>\n\nУ данного пользователя баланс меньше, чем выше указанное число ❌\n\nПопробуйте заново:', parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
            elif user_name_for_delete != None:
                balance = await get_balance(user_name=user_name_for_delete)
                if balance >= int(adm_sum_for_delete):
                    user_info = await find_user_data(user_name=user_name_for_delete)
                    for info in user_info:
                        user_id__for_send_message = info[1]
                    await delete_sum_operation(int(adm_sum_for_delete), user_name=user_name_for_delete)
                    await bot.send_message(user_id__for_send_message, f"• 💵 <b>Удаление баланса</b>:\n\nМодератор удалил ваш баланс на сумму: {adm_sum_for_delete} ₽", parse_mode="HTML")
                    await message.answer(f"• 💵 <b>Удаление баланса:</b>\n\nБаланс указанного пользователя удален на: {adm_sum_for_delete} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
                    await edit_operations_history(user_id=user_id_for_delete, user_name=user_name_for_delete, operations=(-(int(adm_sum_for_delete))), description_of_operation="🤖 Модератор")
                    await state.finish()
                else: 
                    attempts = await state.get_data()
                    if attempts.get("attempts", 0) >= 3:
                        await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /delete ")
                        await state.finish()
                    else:
                        await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                        await message.answer('• 💵 <b>Удаление баланса:</b>\n\nУ данного пользователя баланс меньше, чем выше указанное число ❌\n\nПопробуйте заново:', parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
        else:
            if attempts.get("attempts", 0) >= 3:
                await message.answer("Слишком много попыток ❌\n\nПопробуйте заново - /delete")
                await state.finish()
            else:
                await state.update_data(attempts=attempts.get("attempts", 0) + 1)
                await message.answer("• 💵 <b>Удаление баланса</b>:\n\nСумма для пополнения должна быть больше нуля ❌\n\n<i>Попробуйте ввести сумму заново:</i>", parse_mode="HTML")

async def notification_moders_for_vpns_soon(days: int):
    while True:
        information_about_vpns = await check_vpn_expiration_for_days(days=days)
        if information_about_vpns != []:
            for info in information_about_vpns:
                user_id = info[0]
                user_name = info[1]
                expiration_date = info[2]
                file = info[3]
                
                notification_sent = await check_notification_sent(user_id, user_name, expiration_date)
                if not notification_sent:
                    await bot.send_document(document=file, chat_id=BLAZER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> осталось меньше <code>{days}</code> дней до окончания.", parse_mode="HTML")
                    await bot.send_document(document=file, chat_id=ANUSH_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> осталось меньше <code>{days}</code> дней до окончания.", parse_mode="HTML")
                    await bot.send_document(document=file, chat_id=user_id, caption=f"• 🛡 <b>Ваш VPN</b>:\n\nДо окончания срока действия вашего VPN осталось <code>{days}</code> дней. \nСрок окончания действия VPN: <code>{expiration_date}</code>\n\n<i>Чтобы продлить свой VPN, используйте кнопку ниже, либо используйте команду -</i> /extend_vpn", parse_mode="HTML", reply_markup=extension_keyboard)
                    
                    await mark_notification_sent(user_id, user_name, expiration_date)
        await asyncio.sleep(1800)

notification_status = {}

async def check_notification_sent(user_id, user_name, expiration_date):
    return notification_status.get((user_id, user_name, expiration_date), False)

async def mark_notification_sent(user_id, user_name, expiration_date):
    notification_status[(user_id, user_name, expiration_date)] = True

async def notification_moders_for_vpns_end():
    while True:
        information_about_vpns = await check_expired_vpns()
        if information_about_vpns != []:
            for info in information_about_vpns:
                user_id = info[0]
                user_name = info[1]
                expiration_date = info[2]
                file = info[3]
                await bot.send_document(document=file, chat_id=BLAZER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> был удален c связи с окончанием срока действия. ✅", parse_mode="HTML")
                await bot.send_document(document=file, chat_id=ANUSH_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> был удален c связи с окончанием срока действия. ✅", parse_mode="HTML")
                await bot.send_document(document=file, chat_id=user_id, caption=f"• 🛡 <b>Ваш VPN</b>:\n\nВаш VPN был успешно удален ✅\nСрок окончания действия VPN: <code>{expiration_date}</code>\n\n<i>Чтобы купить VPN, используйте кнопку ниже, либо используйте команду -</i> /buy", parse_mode="HTML", reply_markup=buy_info_keyboard)
        await asyncio.sleep(60)

def register_adm_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(send_message, lambda c: "reply_buy_keyboard" in c.data)
    dp.register_message_handler(handling_moder_file, state=BuyVPNStates.WAITING_FOR_MESSAGE_TEXT, content_types=['text', 'document'])
    dp.register_callback_query_handler(process_answer, lambda c: "reply_keyboard" in c.data)
    dp.register_message_handler(replying_for_moder, state=SupportStates.WAITING_FOR_MODERATOR_ANSWER, content_types=['text', 'document'])
    dp.register_callback_query_handler(adm_panel_handle, lambda c: c.data == "adm_panel_callback")
    dp.register_callback_query_handler(adm_panel_buttons_handler, lambda c: c.data == "addind_balance_callback" or c.data == "deleting_balance_callback" or c.data == "user_data_callback" or c.data == "vpn_user_callback" or c.data == "ban_user_callback" or c.data == "unban_user_callback")
    dp.register_callback_query_handler(unban_user2_handle, lambda c: c.data == "unban_user2_callback", state=AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS)
    dp.register_message_handler(unban_user_handle, state=UnbanUserState.WAITING_FOR_USER_ID)
    dp.register_callback_query_handler(ban_user2_handle, lambda c: c.data == "ban_user2_callback", state=AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS)
    dp.register_message_handler(ban_user_handle, state=BanUserState.WAITING_FOR_USER_ID)
    dp.register_message_handler(find_info_about_users_vpn, state=UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO)
    dp.register_message_handler(find_user_info_for_adm_panel, state=AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO)
    dp.register_callback_query_handler(vpn_info_handle, lambda c: c.data == "vpn_user2_callback", state=AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS)
    dp.register_message_handler(handling_user_name, state=AdmCommandState.WAITING_ID_OF_USER_FOR_ADD)
    dp.register_message_handler(handle_for_adm_add_sum, state=AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD)
    dp.register_message_handler(handling_user_name_for_delete, state=AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE)
    dp.register_message_handler(handle_for_adm_delete_sum, state=AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE)
    dp.register_callback_query_handler(adding_balance_for_moder, lambda c: c.data == "about_yourself_callback", state=AdmCommandState.WAITING_ID_OF_USER_FOR_ADD)
    dp.register_callback_query_handler(deleting_balance_for_moder, lambda c: c.data == "about_yourself_to_delete_callback", state=AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE)
    


