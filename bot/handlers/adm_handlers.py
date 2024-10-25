import os
import datetime
import asyncio

from dotenv import load_dotenv
from typing import NamedTuple

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from bot.database.OperationsData import edit_operations_history, getting_operation_history
from bot.database.UserData import addind_vpn_count, get_balance, add_operation, pay_operation, get_referrer_info, find_user_data, ban_users_handle, unban_users_handle, delete_sum_operation
from bot.database.VpnData import delete_vpn, update_vpn_half_info, update_vpn_other_info, get_expiration_date, get_order_id, get_vpn_data, check_vpn_expiration_for_days, check_expired_vpns

from bot.keyboards.user_keyboards import insturtion_keyboard, back_keyboard
from bot.keyboards.adm_keyboards import pay_finland_keyboard, pay_germany_keyboard, pay_netherlands_keyboard, pay_sweden_keyboard, vpn_connection_type_keyboard, adm_panel_keyboard, location_kb, buy_info_keyboard, user_find_data, about_yourself_to_add_keyboard, about_yourself_to_delete_keyboard, finish_buy_vpn, extension_keyboard

from bot.utils.outline import create_new_key, find_keys_info

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

class AddVpnForUsers(StatesGroup):
    WAITING_FOR_USER_ID = State()
    
class DeleteVpnForUsers(StatesGroup):
    WAITING_FOR_USER_ID = State()
    WAITING_FOR_USER_ID_FOR_DELETE = State()

class FindUserHistory(StatesGroup):
    WAITING_FOR_USER_ID = State()

class SupportRequest(NamedTuple):
    user_id: int
    user_name: str
    question: str
    answer: str = None


support_requests = []



# # обработка кнопки для пересылания конфига для активации VPN пользователя   
# async def send_message(callback: CallbackQuery, state: FSMContext):
#     order_id = int(callback.data.split(".")[1])
#     location = callback.data.split(".")[2]
#     user_buy_id = int(callback.data.split(".")[3])
#     expiration_date = await get_expiration_date(ID=order_id)
#     if expiration_date == None:
#         await state.update_data(order_id=order_id, location=location)
#         await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/nZg0n9I", caption="• 🛒 <b>Покупка VPN</b>:\n\nПредоставьте ключ активации VPN для пользователя:", parse_mode="HTML"), reply_markup=back_keyboard)
#         await BuyVPNStates.WAITING_FOR_MESSAGE_TEXT.set()
#     else:
#         await callback.message.answer_photo(photo="https://imgur.com/43en7Eh", caption="• 🛒 <b>Покупка VPN</b>:\n\nДругой модератор уже обработал этот VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
#         await state.finish()
#         return 

# async def handling_moder_file(message: Message, state: FSMContext):
#     if message.text:
#         moder_vpn_key = message.text
#         order_id_data = await state.get_data()
#         order_id = order_id_data.get('order_id')
#         location = order_id_data.get('location')
#         if not int(order_id):
#             await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 🛒 <b>Покупка VPN</b>:\n\nID заказа не найден ❌", parse_mode="HTML")
#             await state.finish()
#             return
        
#         order_data = await get_order_id(int(order_id))
#         if not order_data:
#             await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка</b>:\n\nЗаказа с таким ID не существует.", parse_mode="HTML")
#             await state.finish()
#             return
            
#         try:
#             expiration_date = datetime.datetime.now() + timedelta(days=28)
#             await update_vpn_state(order_id=int(order_id), expiration_days=expiration_date.strftime("%d.%m.%Y %H:%M:%S"), vpn_key=moder_vpn_key)
#             await addind_vpn_count(user_id=order_data[1])
#             await message.answer_photo(photo="https://imgur.com/nZg0n9I", caption=f"• 🛒 <b>Покупка VPN</b>:\n\nVPN для пользователя @{order_data[2]} (ID: <code>{order_data[1]}</code>) активирован и добавлен в базу данных ✅", parse_mode="HTML")
#             await bot.send_photo(photo="https://imgur.com/VEYMRY2", chat_id=order_data[1], caption=f"• 🛒 <b>Покупка VPN</b>:\n\nVPN успешно активирован ✅\n\nПодключитесь к VPN по нашей <code>инструкции</code>, с которой можно ознакомиться нажав на кнопку снизу.\n\n<i>Срок действия:</i> <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n<i>Локация: </i>{location}\n\n<b>Ключ активации:</b>\n<pre>{moder_vpn_key}</pre>", parse_mode="HTML", reply_markup=finish_buy_vpn)
#             await state.finish()
            
#         except Exception as e:
#             await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 🛒 <b>Покупка VPN</b>:\n\nПроизошла ошибка во время записи данных ❌", parse_mode="HTML")
#             await state.finish()

#     else:
#         attempts = await state.get_data()
#         if attempts.get("attempts", 0) >= 3:
#             await message.answer_photo(photo="https://imgur.com/weO3juR", caption="Слишком много попыток ❌\n Попробуйте заново")
#             await state.finish()
#         else:
#             await state.update_data(attempts=attempts.get("attempts", 0) + 1)
#             await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 🛒 <b>Покупка VPN</b>:\n\nВы скинули неверный тип ключа VPN!\n\n<i>Попробуйте заново:</i>", parse_mode="HTML")


# обработка кнокпи для пересылания ответа модератора пользователю
# async def process_answer(callback: CallbackQuery, state: FSMContext):
#     global questions_user_id
#     questions_user_id = callback.data.split('_')[2]
#     await callback.message.answer("• 🆘 <b>Система поддержки</b>:\n\nНапишите свой ответ:", reply_markup=back_keyboard, parse_mode="HTML")
#     await save_temp_message(callback.from_user.id, callback.message.text, callback.message.reply_markup.as_json())
#     await callback.answer("")
#     await SupportStates.WAITING_FOR_MODERATOR_ANSWER.set()

# # обработка отправки ответа пользователю
# async def replying_for_moder(message: Message, state):
#     user_info = await getting_question(questions_user_id)
#     if user_info != None:
#         for info in user_info:
#             id = info[0]
#             user_id = info[1]
#             user_name = info[2]
#             question = info[3]

#         answer = message.text
#         try:
#             await bot.send_message(questions_user_id, f"• 🆘 <b>Ответ от модератора:</b>\n\n{answer}", reply_markup=back_keyboard, parse_mode="HTML")
#             await bot.send_message(ANUSH_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nВопрос пользователя @{user_name} (ID: <code>{user_id})</code>:\n\n{question}\n\n<b>Ответ модератора:</b>\n\n{answer}", parse_mode='HTML')
#             await bot.send_message(BLAZER_CHAT_TOKEN, f"• 🆘 <b>Система поддержки</b>:\n\nВопрос пользователя @{user_name} (ID: <code>{user_id})</code>:\n\n{question}\n\n<b>Ответ модератора:</b>\n\n{answer}", parse_mode="HTML")
#             await deleting_answered_reports(user_id=user_id)
#         except Exception as e:
#             await message.answer("Пользователь не найден!")
#     else: 
#         await message.answer("Данный пользователь не найден ❌")
#     if message.reply_markup:
#         await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
#     else:  
#         await save_temp_message(message.from_user.id, message.text, None)
#     await state.finish()

"""************************************************* АДМИН ПАНЕЛЬ **************************************************"""

# обработка сообщения админ панели
async def adm_panel_handle(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 🤖 <b>Админ панель:</b>\n\nВыберите нужно действие: ", parse_mode="HTML"), reply_markup=adm_panel_keyboard)
    await callback.answer('')

# обработка всех кнопок в админ панели
async def adm_panel_buttons_handler(callback: CallbackQuery):
    # удаление и Пополнение баланса
    if callback.data == "addind_balance_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 💵 <b>Пополнение баланса:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя:", parse_mode="HTML"), reply_markup=about_yourself_to_add_keyboard)
        await AdmCommandState.WAITING_ID_OF_USER_FOR_ADD.set()

    elif callback.data == "deleting_balance_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 💵 <b>Удаление баланса:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя:", parse_mode="HTML"), reply_markup=about_yourself_to_delete_keyboard)
        await AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE.set()

    elif callback.data == "user_data_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 🗃 <b>Данные о пользователе:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, информацию про которого хотите узнать: ", parse_mode="HTML"), reply_markup=back_keyboard)
        await AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO.set()

    elif callback.data == "vpn_user_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 🛡️ <b>VPN пользователя:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, информацию о VPN которого хотите узнать: ", parse_mode="HTML"), reply_markup=back_keyboard)
        await UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO.set()

    elif callback.data == "ban_user_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• ❌ <b>Блокировка пользователя:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, которого хотите заблокировать:", parse_mode="HTML"), reply_markup=back_keyboard)
        await BanUserState.WAITING_FOR_USER_ID.set()

    elif callback.data == "unban_user_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• ✅ <b>Разблокировка пользователя:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, которого хотите разблокировать:", parse_mode="HTML"), reply_markup=back_keyboard)
        await UnbanUserState.WAITING_FOR_USER_ID.set()

    elif callback.data == "add_vpn_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 🛡️ <b>Добавление VPN:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, которому хотите добавить VPN:", parse_mode="HTML"), reply_markup=back_keyboard)
        await AddVpnForUsers.WAITING_FOR_USER_ID.set()

    elif callback.data == "delete_vpn_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 🛡️ <b>Удаление VPN:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, которому хотите удалить VPN:", parse_mode="HTML"), reply_markup=back_keyboard)
        await DeleteVpnForUsers.WAITING_FOR_USER_ID.set()

    elif callback.data == "user_history_callback":
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 📋 <b>История операций пользователя:</b>\n\nВведите <code>ID</code> или <code>USERNAME</code> пользователя, историю операций которого хотите узнать:", parse_mode="HTML"), reply_markup=back_keyboard)
        await FindUserHistory.WAITING_FOR_USER_ID.set()

    await callback.answer('')

"""*********************************************** УДАЛЕНИЕ БАЛАНСА ***********************************************"""

# обрабатывает кнопку about_yourself_keyboard, чтобы указать, что удаление баланса должно быть модератору, который нажал на кнопку
async def deleting_balance_for_moder(callback: CallbackQuery, state: FSMContext):
    user_id_for_delete = callback.from_user.id
    user_name_for_delete = callback.from_user.username
    await state.update_data(user_id_for_delete=user_id_for_delete, user_name_for_delete=user_name_for_delete)
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 💵 <b>Удаление баланса:</b>\n\nВведите сумму для удаления баланса:", parse_mode="HTML"), reply_markup=back_keyboard)
    await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE.set()

# удаление баланса модераторами
async def handling_user_name_for_delete(message: Message, state: FSMContext):
    try:
        user_id_for_delete = int(message.text)
        user_name_for_delete = None
    except ValueError:
        user_name_for_delete = message.text
        user_id_for_delete = None

    user_info = await find_user_data(user_id=user_id_for_delete, user_name=user_name_for_delete)
    if user_info:
        await state.update_data(user_id_for_delete=user_id_for_delete, user_name_for_delete=user_name_for_delete)
        await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=f"• 💵 <b>Удаление баланса:</b>\n\nВведите сумму для удаления баланса:", reply_markup=back_keyboard, parse_mode="HTML")
        await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_DELETE.set()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /delete")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 💵 <b>Удаление баланса:</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)

# обработка числа для удаления баланса модераторами
async def handle_for_adm_delete_sum(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id_for_delete = data.get("user_id_for_delete")
    user_name_for_delete = data.get("user_name_for_delete")

    try:
        adm_sum_for_delete = int(message.text)
        if adm_sum_for_delete <= 0:
            raise ValueError
    except (ValueError, Exception) as e:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /delete ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            error_message = "• 💵 <b>Удаление баланса:</b>\n\n"
            if isinstance(e, ValueError):
                error_message += "Сумма для удаления должна быть больше нуля ❌\n\n<i>Попробуйте ввести сумму заново:</i>"
            else:
                error_message += "Введите корректную сумму (число) ❌"
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption=error_message, parse_mode="HTML")
        return
    user_info = await find_user_data(user_id=user_id_for_delete, user_name=user_name_for_delete)
    if user_info:
        user_id_for_reply = user_info[0][1]
        balance = await get_balance(user_id=user_id_for_delete, user_name=user_name_for_delete)
        if balance >= adm_sum_for_delete:
            await delete_sum_operation(adm_sum_for_delete, user_id=user_id_for_delete, user_name=user_name_for_delete)
            await edit_operations_history(user_id=user_id_for_delete, user_name=user_name_for_delete, operations=(-adm_sum_for_delete), description_of_operation="🤖 Модератор")
            await bot.send_photo(photo="https://imgur.com/i4sEHgp", chat_id=user_id_for_reply, caption=f"• 💵 <b>Удаление баланса</b>:\n\nМодератор удалил ваш баланс на сумму: <code>{adm_sum_for_delete}</code> ₽ ", parse_mode="HTML")
            await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=f"• 💵 <b>Удаление баланса:</b>\n\nБаланс указанного пользователя удален на: <code>{adm_sum_for_delete}</code> ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
            await state.finish()
        else:
            attempts = await state.get_data()
            attempts_count = attempts.get("attempts", 0)
            if attempts_count >= 3:
                await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /delete ")
                await state.finish()
            else:
                await state.update_data(attempts=attempts_count + 1)
                await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption='• 💵 <b>Удаление баланса:</b>\n\nУ данного пользователя баланс меньше, чем выше указанное число ❌\n\nПопробуйте заново:', parse_mode="HTML")

"""************************************************* ПОПОЛНЕНИЕ БАЛАНСА **************************************************"""

# обрабатывает кнопку about_yourself_keyboard, чтобы указать, что Пополнение баланса должно быть модератору, который нажал на кнопку
async def adding_balance_for_moder(callback: CallbackQuery, state: FSMContext):
    user_id_for_add = callback.from_user.id
    user_name_for_add = callback.from_user.username
    await state.update_data(user_id_for_add=user_id_for_add, user_name_for_add=user_name_for_add)
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/i4sEHgp", caption="• 💵 <b>Пополнение баланса:</b>\n\nВведите сумму для пополнения баланса:", parse_mode="HTML"), reply_markup=back_keyboard)
    await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD.set()

# Пополнение баланса администратором
async def handling_user_name(message: Message, state: FSMContext):
    try:
        user_id_for_add = int(message.text)
        user_name_for_add = None
    except Exception as e:
        user_name_for_add = message.text
        user_id_for_add = None
    
    user_info = await find_user_data(user_id=user_id_for_add, user_name=user_name_for_add)
    if user_info:
        await state.update_data(user_id_for_add=user_id_for_add, user_name_for_add=user_name_for_add)
        await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=f"• 💵 <b>Пополнение баланса</b>:\n\nВведите сумму для пополнения баланса:", reply_markup=back_keyboard, parse_mode="HTML")
        await AdmCommandState.WAITING_FOR_SUM_HANDLE_FOR_ADD.set()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /add")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 💵 <b>Пополнение баланса:</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)

async def handle_for_adm_add_sum(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id_for_add = data.get("user_id_for_add")
    user_name_for_add = data.get("user_name_for_add")  
    try:
        adm_sum_for_add = int(message.text)
        if adm_sum_for_add <= 0:
            raise ValueError
    except (ValueError, Exception) as e:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /add")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            error_message = "• 💵 <b>Пополнение баланса</b>:\n\n"
            if isinstance(e, ValueError):
                error_message += "Сумма для пополнения должна быть больше нуля ❌\n\n<i>Попробуйте ввести сумму заново:</i>"
            else:
                error_message += "Введите корректную сумму (число) ❌"
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption=error_message, parse_mode="HTML")
        return
    user_info = await find_user_data(user_id=user_id_for_add, user_name=user_name_for_add)
    if user_info:
        user_id_for_reply = user_info[0][1]
        await add_operation(price=adm_sum_for_add, user_id=user_id_for_add, user_name=user_name_for_add)
        await bot.send_photo(photo="https://imgur.com/i4sEHgp", chat_id=user_id_for_reply, caption=f"• 💵 <b>Пополнение баланса</b>:\n\nМодератор пополнил ваш баланс на сумму: {adm_sum_for_add} ₽ ✅", parse_mode="HTML")

    await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=f"• 💵 <b>Пополнение баланса</b>:\n\nБаланс указанного пользователя пополнен на: {adm_sum_for_add} ₽ ✅", reply_markup=back_keyboard, parse_mode="HTML")
    await state.finish()
    await edit_operations_history(user_id=user_id_for_add, user_name=user_name_for_add, operations=(+(int(adm_sum_for_add))), description_of_operation="🤖 Модератор")

"""********************************************************* РАЗБЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ ************************************************"""

# обработка разблокировки пользователя через информацию о пользователе
async def unban_user2_handle(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    user_id = int(data.get("user_id")) if data.get("user_id") else None
    user_name = data.get("user_name")
    is_registrated_user = await find_user_data(user_id=user_id, user_name=user_name)
    if is_registrated_user:
        result = await unban_users_handle(user_id=user_id, user_name=user_name)
        if result != "unbanned":
            await callback.message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=f"• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• ✅ <b>Разблокировка пользователя:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
        await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n Попробуйте заново - /unban ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь с таким <b>USERNAME</b> не найден ❌\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
    await callback.answer("")
        
# обработка разблокировки пользователя 
async def unban_user_handle(message: Message, state):
    user_id = message.from_user.id
    try:
        user_id = int(message.text)
        user_name = None
    except ValueError:
        user_name = message.text
        user_id = None

    is_registrated_user = await find_user_data(user_id=user_id, user_name=user_name)
    if is_registrated_user:
        result = await unban_users_handle(user_id=user_id, user_name=user_name)
        if result != "unbanned":
            await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=f"• ✅ <b>Разблокировка пользователя:</b>\n\nПользователь успешно разблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• ✅ <b>Разблокировка пользователя:</b>\n\nЭтот пользователь уже разблокирован ❌", parse_mode="HTML", reply_markup=back_keyboard)
        await state.finish()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\nПопробуйте заново - /unban ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• ✅ <b>Разблокировка пользователя:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)

"""*********************************************************** БЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ ***********************************************************"""

# обработка блокировки пользователя через меню информации о пользователе
async def ban_user2_handle(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    user_id = int(data.get("user_id")) if data.get("user_id") else None
    user_name = data.get("user_name")

    is_registrated_user = await find_user_data(user_id=user_id, user_name=user_name)
    if is_registrated_user:
        result = await ban_users_handle(user_id=user_id, user_name=user_name)
        if result != "banned":
            await callback.message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• ❌ <b>Блокировка пользователя:</b>\n\nПользователь успешно заблокирован ✅", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• ❌ <b>Блокировка пользователя:</b>\n\nЭтот пользователь уже находится в бане ❌", parse_mode="HTML", reply_markup=back_keyboard)
        await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\nПопробуйте заново - /ban ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• ❌ <b>Блокировка пользователя:</b>\n\nnПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново:", parse_mode="HTML", reply_markup=back_keyboard)
    await callback.answer("")

# обработка блокировки пользователей 
async def ban_user_handle(message: Message, state):
    user_id = message.from_user.id
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

"""************************************************************** ПОИСК ИНФОРМАЦИИ О ПОЛЬЗОВАТЕЛЕ *************************************"""

# обработка поиска информации о VPN пользователей
async def find_info_about_users_vpn(message: Message, state):
    try:
        user_id = int(message.text)
        user_name = None
    except Exception as e:
        user_name = message.text
        user_id = None
    vpn_data = await get_vpn_data(user_id=user_id, user_name=user_name)
    user_info = await find_user_data(user_name=user_name, user_id=user_id)
    if user_info:
        if vpn_data:
            for vpn in vpn_data:
                id = vpn[0]
                user_id = vpn[1]
                user_name = vpn[2]
                location = vpn[3]
                expiration_date = vpn[4]
                vpn_key = vpn[5]
                if expiration_date:
                    expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date_new - datetime.datetime.now()).days
                    await bot.send_photo(photo="https://imgur.com/i4sEHgp",
                                        chat_id=message.from_user.id, 
                                        caption=f"• 🛡 <b>VPN пользователя:</b>\n\nID:  <code>{id}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n", 
                                        parse_mode="HTML")
                else:
                    await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 🛡 <b>VPN пользователя:</b>\n\nУ пользователя имеется приобретенный VPN, который не обработан модераторами.", parse_mode="HTML")
        else:
            await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 🛡 <b>VPN пользователя:</b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
        await state.finish()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\nПопробуйте заново - /user_vpn ")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡 <b>VPN пользователя:</b>\n\nПользователь с таким <code>USERNAME</code> не найдет ❌\n\nПопробуйте ввести <code>USERNAME</code> или <code>ID</code> заново:", parse_mode="HTML", reply_markup=back_keyboard)

# обработка информации о пользователе
async def find_user_info_for_adm_panel(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        user_id_for_find_info = int(message.text)
        user_name_for_find_info = None
    except ValueError:
        user_name_for_find_info = message.text
        user_id_for_find_info = None
    user_info = await find_user_data(user_id=user_id_for_find_info, user_name=user_name_for_find_info)
    await state.update_data(user_name=user_name_for_find_info, user_id=user_id_for_find_info)

    if user_info:
        id, user_id, user_name, balance, time_of_registration, referrer_id, used_promocodes, is_banned, vpns_count = user_info[0]
        used_promocodes_text = "-" if not used_promocodes else ", ".join(used_promocodes.split(","))
        is_banned = "-" if is_banned == 0 else "+"
        if referrer_id:
            ref_user_name = await get_referrer_info(user_id=referrer_id)
            for ref_id, ref_name in ref_user_name:
                referrer_username = "Пользователь без <b>USERNAME</b>" if ref_name is None else "@" + (ref_user_name[0][1]) + " (ID: <code>" + str(ref_id) + "</code>)"
        else:
            referrer_username = "<code>-</code>"
        user_info_text = f"• 🗃 <b>Данные о пользователе</b>:\n\nID в базе данных: <code>{id}</code>\nTelegram ID: <code>{user_id}</code>\nUsername пользователя: <code>{user_name}</code>\nБаланс: <code>{balance}</code> ₽\nВремя регистрации: <code>{time_of_registration}</code>\nРеферер: {referrer_username}\nИспользованные промокоды: <code>{used_promocodes_text}</code>\nЗабанен ли пользователь: <code>{is_banned}</code>\nКол-во VPN за все время: <code>{vpns_count}</code>"
        await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption=user_info_text, reply_markup=user_find_data, parse_mode="HTML")
        await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()

    elif user_id_for_find_info is None and user_info == []:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\nПопробуйте заново - /user_info ")
            await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🗃 <b>Данные о пользователе</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести ID или USERNAME заново: ", parse_mode="HTML", reply_markup=back_keyboard)
    elif user_name_for_find_info is None and user_info == []:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /user_info ", reply_markup=back_keyboard)
            await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🗃 <b>Данные о пользователе</b>:\n\nПользователь с таким <b>ID</b> не найден ❌", parse_mode="HTML", reply_markup=back_keyboard)


"""********************************************************* ПОИСК ИНФОРМАЦИИ О VPN ПОЛЬЗОВАТЕЛЕЙ ****************************************************"""

# обработка информации о VPN пользователей через меню управления пользователем
async def vpn_info_handle(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id1 = int(data.get("user_id")) if data.get("user_id") else None
    user_name = data.get("user_name")

    user_info = await find_user_data(user_id=user_id1, user_name=user_name)
    if user_info:
        vpn_data = await get_vpn_data(user_id=user_id1, user_name=user_name)
        if vpn_data:
            for vpn in vpn_data:
                id, user_id, user_name, location, expiration_date, vpn_key, asd = vpn
                if expiration_date:
                    expiration_date_new = datetime.datetime.strptime(expiration_date, "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date_new - datetime.datetime.now()).days
                    await bot.send_photo(photo="https://imgur.com/i4sEHgp",
                                        chat_id=callback.from_user.id, 
                                        caption=f"• 🛡 <b>VPN пользователя:</b>\n\nID: <code>{id}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n", 
                                        parse_mode="HTML")
                else:
                    await callback.message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 🛡 <b>VPN пользователя:</b>\n\nУ пользователя имеется приобретенный VPN, который не обработан модераторами.", parse_mode="HTML")
                await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
        else:
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡 <b>VPN пользователя:</b>\n\nПользователь пока не имеет ни одного VPN ❌", parse_mode="HTML", reply_markup=back_keyboard)
            await AdmButtonState.WAITING_FOR_CALLBACK_BUTTONS.set()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /user_vpn")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await callback.message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡 <b>VPN пользователя:</b>:\n\nПользователь с таким <b>USERNAME</b> не найден ❌\n\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)
    await callback.answer("")

"""************************************************ СООБЩЕНИЕ О СРОКАХ ОКОНЧАНИЯ VPN ****************************************************"""

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
                    await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=BLAZER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> осталось меньше <code>{days}</code> дней до окончания.", parse_mode="HTML")
                    await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=ANUSH_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> осталось меньше <code>{days}</code> дней до окончания.", parse_mode="HTML")
                    
                    await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=user_id, caption=f"• 🛡 <b>Ваш VPN</b>:\n\nДо окончания срока действия вашего VPN осталось <code>{days}</code> дней. \nСрок окончания действия VPN: <code>{expiration_date}</code>\n\n<i>Чтобы продлить свой VPN, используйте кнопку ниже", parse_mode="HTML", reply_markup=extension_keyboard)
                    
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
                await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=BLAZER_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> был удален c связи с окончанием срока действия. ✅", parse_mode="HTML")
                await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=ANUSH_CHAT_TOKEN, caption=f"❗️ <b>Важно!</b>\n\nVPN для пользователя @{user_name} (ID: <code>{user_id}</code>) с датой окончания <code>{expiration_date}</code> был удален c связи с окончанием срока действия. ✅", parse_mode="HTML")
                
                await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=user_id, caption=f"• 🛡 <b>Ваш VPN</b>:\n\nВаш VPN был успешно удален ✅\nСрок окончания действия VPN: <code>{expiration_date}</code>\n\n<i>Чтобы купить VPN, используйте кнопку ниже", parse_mode="HTML", reply_markup=buy_info_keyboard)
        await asyncio.sleep(60)

"""************************************************ ДОБАВЛЕНИЕ VPN ****************************************************"""

async def add_user_vpn(message: Message, state):
    try:
        user_id_for_add = int(message.text)
        user_name_for_add = None
    except Exception as e:
        user_name_for_add = message.text
        user_id_for_add = None
    
    user_info = await find_user_data(user_id=user_id_for_add, user_name=user_name_for_add)
    if user_info != []:
        user_id_for_add = user_info[0][1]
        user_name_for_add = user_info[0][2]
        await message.answer_photo(photo="https://imgur.com/hW9OgnB", caption="• 🛡️ <b>Добавление VPN:</b>\n\nВыберите локацию: ", parse_mode="HTML", reply_markup=location_kb(user_name=user_name_for_add, user_id=user_id_for_add))
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /add_vpn")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡️ <b>Добавление VPN:</b>\n\nПользователь с таким <b>USERNAME</b> или <b>ID</b> не найден ❌\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)


async def location_choose_def(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("Sweden_callback"):
        user_id = callback.data.split("_")[2]
        user_name = await find_user_data(user_id=user_id)
        user_name = user_name[0][2]
        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: <code>Швеция</code> 🇸🇪\nВыберите протокол подключения вашего VPN:", parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Швеция 🇸🇪", user_id=user_id))
    
    elif callback.data.startswith("Netherlands_callback"):
        user_id = callback.data.split("_")[2]
        user_name = await find_user_data(user_id=user_id)[2]

        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: <code>Нидерланды</code> 🇳🇱\nВыберите протокол подключения вашего VPN:", parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Нидерланды 🇳🇱", user_id=user_id))

    elif callback.data.startswith("Finland_callback"):
        user_id = callback.data.split("_")[2]
        user_name = await find_user_data(user_id=user_id)[2]

        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: <code>Финляндия</code> 🇫🇮\nВыберите протокол подключения вашего VPN:",  parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Финляндия 🇫🇮", user_id=user_id))

    elif callback.data.startswith("Germany_callback"):
        user_id = callback.data.split("_")[2]
        user_name = await find_user_data(user_id=user_id)[2]

        await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/Lf6OlGm", caption=f"• 🛡 <b>Выбор протокола подключения:</b>\n\nВы выбрали локацию: <code>Германия</code> 🇩🇪\nВыберите протокол подключения вашего VPN:",  parse_mode="HTML"), reply_markup=await vpn_connection_type_keyboard(location="Германия 🇩🇪", user_id=user_id))
    await callback.answer("")


async def choosing_vpn_connection_def(callback: CallbackQuery, state: FSMContext):
    location = callback.data.split(".")[1]
    user_id = callback.data.split('.')[2]
    if location == "Швеция 🇸🇪":
        kb = pay_sweden_keyboard(user_id)
    elif location == "Нидерланды 🇳🇱":
        kb = pay_netherlands_keyboard(user_id)
    elif location == "Финляндия 🇫🇮":
        kb = pay_finland_keyboard(user_id)
    elif location == "Германия 🇩🇪":
        kb = pay_germany_keyboard(user_id)

    location = f"<code>{location.split(" ")[0]}</code> {location.split(" ")[1]}"
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/cXpphjT", caption=f"• 🛡 <b>Покупка VPN:</b>\n\nВы выбрали VPN на локации: {location}\nПротокол подключения: <code>Shadowsocks</code> 🧦", parse_mode="HTML"), reply_markup=kb)
    await callback.answer('')

async def choosing_location_for_buying_VPN(callback: CallbackQuery, state: FSMContext):
    if "Buying_sweden" in callback.data:
        await buying_VPN_def(callback=callback, country="Швеция 🇸🇪", user_id=callback.data.split(".")[1])
    elif "Buying_finland" in callback.data:
        await buying_VPN_def(callback=callback, country="Финляндия 🇫🇮", user_id=callback.data.split(".")[1])
    elif "Buying_germany" in callback.data:
        await buying_VPN_def(callback=callback, country="Германия 🇩🇪", user_id=callback.data.split(".")[1])
    elif "Buying_netherlands" in callback.data:
        await buying_VPN_def(callback=callback, country="Нидерланды 🇳🇱", user_id=callback.data.split(".")[1])
    await callback.answer("")

async def buying_VPN_def(callback, country, user_id):
    user_name = await find_user_data(user_id=user_id)
    user_name = user_name[0][2]

    expiration_date = datetime.datetime.now() + datetime.timedelta(days=28) # срок действия VPN 28 дней
    vpn_id = await update_vpn_half_info(user_id=user_id, user_name=user_name, location=country, expiration_days=expiration_date.strftime("%d.%m.%Y %H:%M:%S")) # сохранение данных пользователей и половину информации о впн в бд
    create_new_key(key_id=vpn_id, name=f"ID: {user_id}", data_limit_gb=200.0, location=country) # создание нового ключа для VPN
    vpn_key = find_keys_info(key_id=vpn_id, location=country) # получение ключа
    await update_vpn_other_info(vpn_key=vpn_key, vpn_id=vpn_id) # сохранение ключа в бд
    await addind_vpn_count(user_id=user_id)
    await bot.send_photo(photo="https://imgur.com/hW9OgnB", chat_id=user_id, caption=f"• 🛒 <b>Покупка VPN</b>:\n\nМодератор предоставил вам VPN на <code>28</code> дней. ✅\n\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\nОзнакомьтесь с нашей инструкцией по использованию VPN ниже по кнопке.", parse_mode="HTML", reply_markup=insturtion_keyboard)
    await callback.message.edit_media(media=InputMediaPhoto(media="https://imgur.com/hW9OgnB", caption=f"• 🛒 <b>Покупка VPN</b>:\n\nVPN был успешно предоставлен пользователю @{user_name} (ID: <code>{user_id}</code>) ✅", parse_mode="HTML"), reply_markup=back_keyboard)
    await edit_operations_history(user_id=user_id, user_name=user_name, operations=(float(0)), description_of_operation="🛒 Покупка VPN")
    await callback.answer("")


"""*********************************************************************** УДАЛЕНИЕ VPN ***********************************************************************"""

async def deleting_user_vpn(message: Message, state):
    try:
        user_id_for_add = int(message.text)
        user_name_for_add = None
    except Exception as e:
        user_name_for_add = message.text
        user_id_for_add = None
    
    user_info = await find_user_data(user_id=user_id_for_add, user_name=user_name_for_add)
    if user_info != []:
        await message.answer_photo(photo="https://imgur.com/hW9OgnB", caption="• 🛒 <b>Удаление VPN</b>:\n\nВведите <code>ID</code> VPN, которое хотите удалить: ", parse_mode="HTML", reply_markup=back_keyboard)
        await DeleteVpnForUsers.WAITING_FOR_USER_ID_FOR_DELETE.set()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /user_vpn")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡️ <b>Удаление VPN:</b>\n\nПользователь с таким <b>USERNAME</b> или <b>ID</b> не найден ❌\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)

async def handle_vpn_id(message: Message, state):
    try:
        vpn_id = int(message.text)
    except Exception as e:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /delete_vpn")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡️ <b>Удаление VPN:</b>\n\nВы ввели неправильный <b>ID</b> ❌\nПопробуйте ввести <b>ID</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)
    if await delete_vpn(vpn_id=vpn_id) == None:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /delete_vpn")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 🛡️ <b>Удаление VPN:</b>\n\nВы ввели <b>ID</b>, которого нету в базе данных ❌\nПопробуйте ввести <b>ID</b> заново:", parse_mode="HTML", reply_markup=back_keyboard)
    else:
        await message.answer_photo(photo="https://imgur.com/hW9OgnB", caption="• 🛡️ <b>Удаление VPN:</b>\n\nVPN пользователя успешно удален ✅", parse_mode="HTML", reply_markup=back_keyboard)
        await state.finish()

"""*********************************************************************** ИСТОРИЯ ОПЕРАЦИЙ ПОЛЬЗОВАТЕЛЯ ***********************************************************************"""

async def handle_user_id_for_history(message: Message, state):
    try:
        user_id = int(message.text)
        user_name = None
    except Exception as e:
        user_id = None
        user_name = message.text
    
    user_info = await find_user_data(user_id=user_id, user_name=user_name)
    user_operation = await getting_operation_history(user_id=user_id, user_name=user_name)
    if user_info != []:
        if user_operation != []:
            message_text = "• 📋 <b>История операций пользователя</b>:\n\n"
            for operation in user_operation:
                id, user_db_id, user_db_name, operations, time_of_operation, description_of_operation = operation
                operations = operations.split(",")
                time_of_operation = time_of_operation.split(",")
                description_of_operation = description_of_operation.split(",")

                for i in range(len(operations)):
                    operation_value = operations[i]
                    if "-" not in operation_value:
                        operation_value = "+" + operation_value

                    message_text += f"<i>{time_of_operation[i]}</i> - <b>{description_of_operation[i]}</b>:  <code>{operation_value}</code> ₽\n"
            await message.answer_photo(photo="https://imgur.com/QnZumh4", caption=message_text, parse_mode="HTML", reply_markup=back_keyboard)
            await state.finish()
        else:
            await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• 📋 <b>История операций пользователя</b>:\n\nУ пользователя нету истории операций ❌", parse_mode="HTML", reply_markup=back_keyboard)
            await state.finish()
    else:
        attempts = await state.get_data()
        attempts_count = attempts.get("attempts", 0)
        if attempts_count >= 3:
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="Слишком много попыток ❌\n\nПопробуйте заново - /user_history")
            await state.finish()
        else:
            await state.update_data(attempts=attempts_count + 1)
            await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="• 📋 <b>История операций пользователя</b>:\n\nПользователь с таким <b>USERNAME</b> или <b>ID</b> не найден ❌\nПопробуйте ввести <b>ID</b> или <b>USERNAME</b> заново: ", parse_mode="HTML", reply_markup=back_keyboard)

def register_adm_handlers(dp: Dispatcher) -> None:
    # dp.register_callback_query_handler(send_message, lambda c: "reply_buy_keyboard" in c.data)
    # dp.register_message_handler(handling_moder_file, state=BuyVPNStates.WAITING_FOR_MESSAGE_TEXT)
    # dp.register_callback_query_handler(process_answer, lambda c: "reply_keyboard" in c.data)
    # dp.register_message_handler(replying_for_moder, state=SupportStates.WAITING_FOR_MODERATOR_ANSWER, content_types=['text', 'document'])
    
    dp.register_callback_query_handler(adm_panel_handle, lambda c: c.data == "adm_panel_callback", state="*")
    dp.register_callback_query_handler(adm_panel_buttons_handler, lambda c: c.data == "addind_balance_callback" or c.data == "deleting_balance_callback" or c.data == "user_data_callback" or c.data == "vpn_user_callback" or c.data == "ban_user_callback" or c.data == "unban_user_callback" or c.data == "add_vpn_callback" or c.data == "delete_vpn_callback" or c.data == "user_history_callback", state="*")
    dp.register_callback_query_handler(unban_user2_handle, lambda c: c.data == "unban_user2_callback", state="*")
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
    dp.register_message_handler(add_user_vpn, state=AddVpnForUsers.WAITING_FOR_USER_ID)
    dp.register_callback_query_handler(location_choose_def, lambda c: c.data.startswith("Sweden_callback") or c.data.startswith("Finland_callback") or c.data.startswith("Germany_callback") or c.data.startswith("Netherlands_callback"), state="*")
    dp.register_callback_query_handler(choosing_location_for_buying_VPN, lambda c: "Buying_sweden_adm" in c.data or "Buying_finland" in c.data or "Buying_germany" in c.data or "Buying_netherlands" in c.data, state="*")
    dp.register_callback_query_handler(choosing_vpn_connection_def, lambda c: "vpn_connection_type_adm" in c.data, state="*")
    dp.register_message_handler(deleting_user_vpn, state=DeleteVpnForUsers.WAITING_FOR_USER_ID)
    dp.register_message_handler(handle_vpn_id, state=DeleteVpnForUsers.WAITING_FOR_USER_ID_FOR_DELETE)
    dp.register_message_handler(handle_user_id_for_history, state=FindUserHistory.WAITING_FOR_USER_ID)