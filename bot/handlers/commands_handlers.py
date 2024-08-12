import os

from dotenv import load_dotenv

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime

from bot.keyboards.user_keyboards import help_kb, balance_handle_keyboard, start_kb_handle, device_keyboard, replenishment_balance, back_keyboard, support_keyboard, location_keyboard, buy_keyboard, addind_count_for_extend, extend_keyboard, numbers_for_replenishment
from bot.keyboards.adm_keyboards import about_yourself_to_add_keyboard, about_yourself_to_delete_keyboard

from bot.database.UserData import is_user_ban_check, get_balance, get_referrer_username
from bot.database.VpnData import get_vpn_data
from bot.database.TempData import save_temp_message
from bot.database.OperationsData import getting_operation_history
from bot.database.SupportData import getting_question


"""********************************************************************** СОСТОЯНИЯ ******************************************************************"""

class PromocodeStates(StatesGroup):
    WAITING_FOR_USER_PROMOCODE = State()

class PaymentStates(StatesGroup):
    WAITING_FOR_AMOUNT = State()
    WAITING_FOR_USER_EMAIL_HANDLE = State()
    WAINING_FOR_PAYMENT_TYPE = State()
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

# импорт токенов из файла .env
load_dotenv('.env')
VPN_PRICE_TOKEN = os.getenv("VPN_PRICE_TOKEN")
ANUSH_CHAT_TOKEN = os.getenv("ANUSH_CHAT_TOKEN")
BLAZER_CHAT_TOKEN = os.getenv("BLAZER_CHAT_TOKEN")

"""******************************************************************* ФУНКЦИЯ ДЛЯ ОБРАБОТКИ ВСЕХ КОМАНД *******************************************************"""

async def handle_text(message: types.Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer("<b>• Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if message.text == "/help":
            if user_id == int(ANUSH_CHAT_TOKEN) or user_id == int(BLAZER_CHAT_TOKEN):
                await message.answer("<b>• Доступные команды:</b>\n\n"
                                "/start - Обновить бота\n"
                                "/help - Узнать список команд\n"
                                "/balance - 💵 Узнать свой баланс\n"
                                "/connect_with_dev - 🧑‍💻 Связаться с разработчиком бота\n"
                                "/buy - 🛒 Купить VPN\n"
                                "/extend_vpn - ⌛️ Продлить VPN\n"
                                "/replenishment - 💵 Пополнить баланс\n"
                                "/support - 🆘 Задать вопрос\n"
                                "/my_vpn - 🛡️ Мои VPN\n"
                                "/ref_system - 🤝 Реферальная система\n"
                                "/promocode - 🎟 Промокоды\n"
                                "/history_of_operations - 📋 История операций\n"
                                "/instruction - 📄 Инструкция по использованию VPN\n"
                                "/user_info - 🗃 Данные о пользователях\n"
                                "/user_vpn - 🛡️ VPN пользователей\n"
                                "/add - 💵 Пополнение баланса\n"
                                "/delete - 💵 Удаление баланса", reply_markup=start_kb_handle(user_id), parse_mode="HTML")
            else:
                await message.answer("<b>• Доступные команды:</b>\n\n"
                                "/start - Обновить бота\n"
                                "/help - Узнать список команд\n"
                                "/balance - 💵 Узнать свой баланс\n"
                                "/connect_with_dev - 🧑‍💻 Связаться с разработчиком бота\n"
                                "/buy - 🛒 Купить VPN\n"
                                "/extend_vpn - ⌛️ Продлить VPN\n"
                                "/replenishment - 💵 Пополнить баланс\n"
                                "/support - 🆘 Задать вопрос\n"
                                "/my_vpn - 🛡️ Мои VPN\n"
                                "/ref_system - 🤝 Реферальная система\n"
                                "/promocode - 🎟 Промокоды\n"
                                "/history_of_operations - 📋 История операций\n"
                                "/instruction - 📄 Инструкция по использованию VPN", reply_markup=start_kb_handle(user_id), parse_mode="HTML")
    
            
        elif message.text == "/balance":
            user_name = message.from_user.username
            balance = await get_balance(user_name)
            await message.answer(f"• 💵 <b>Баланс</b>:\n\nВаш баланс: <code>{balance}</code> ₽\n\n<i>Чтобы пополнить свой баланс, вы можете использовать кнопку ниже, либо использовать команду - /replenishment</i>", reply_markup=balance_handle_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

        elif message.text == "/connect_with_dev":
            await message.answer("• 🧑‍💻 <b>Связь с разработчиком</b>:\n\nДля связи с разработчиком бота перейдите по ссылке: \n\nhttps://t.me/KING_08001", reply_markup=help_kb, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

        elif message.text == "/buy":
            await message.answer("• 📍 <b>Выбор локации</b>:\n\nВыберите подходящую для вас локацию:\n\n<tg-spoiler><i>В скором времени будут добавлены дополнительные локации</i></tg-spoiler>", reply_markup=location_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

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
                    vpn_info_text += f"{numbers}. 📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n"
                kb_for_count = addind_count_for_extend(count=numbers)
                if numbers == 1:
                    await message.answer(f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}\n\n<b>Продление VPN на 30 дней стоит <code>{VPN_PRICE_TOKEN}</code> ₽ 💵\nНажмите на кнопку, если готовы продлить VPN </b>🛡", reply_markup=extend_keyboard, parse_mode="HTML")
                else:
                    await message.answer(f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}\n\n<b>Продление VPN на 30 дней стоит <code>{VPN_PRICE_TOKEN}</code> ₽ 💵. \nВыберите VPN </b>🛡<b>, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
            else: 
                await message.answer("• 🛡 <b>Продление VPN:</b>\n\nУ вас нету действующего VPN ❌! \n\n<i>Вам его необходимо приобрести, нажав на кнопку ниже, либо использовав команду -</i> /buy", reply_markup=buy_keyboard, parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)

        elif message.text == "/replenishment":
            await message.answer("• 💵 <b>Пополнение баланса</b>:\n\nВыберите сумму пополнения 💵, либо введите нужную самостоятельно: ", reply_markup=numbers_for_replenishment, parse_mode="HTML")
            await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            await PaymentStates.WAITING_FOR_AMOUNT.set()
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)


        elif message.text == "/support":
            user_id = message.from_user.id 
            info_question = await getting_question(user_id=user_id)
            if info_question != []:
                await message.answer("• 🆘 <b>Система поддержки</b>:\n\nВы уже задавали вопрос ❌\n<i>Дождитесь пока модераторы ответят на ваш предыдущий вопрос</i>", reply_markup=back_keyboard, parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
                return
            else:
                await message.answer("• 🆘 <b>Система поддержки</b>:\n\nЗдравствуйте. Чем можем помочь?", reply_markup=back_keyboard, parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
                await SupportStates.WAITING_FOR_QUESTION.set()

        elif message.text == "/ref_system":
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
            await message.answer(text, reply_markup=back_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

        elif message.text == "/promocode":
            await message.answer("• 🎟 <b>Система промокодов</b>:\n\nВведите действующий промокод:", reply_markup=back_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)
            await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()

        elif message.text == "/instruction":
            await message.answer("• 📖 <b>Инструкция:</b>\n\nВыберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", reply_markup=device_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

        elif message.text == "/my_vpn":
            vpn_data = await get_vpn_data(user_id)
            if vpn_data:
                vpn_info_text = "• 🛡 <b>Ваши VPN</b>:\n\n"
                for vpn in vpn_data:
                    location = vpn[3]
                    active = vpn[4]
                    expiration_date = datetime.strptime(vpn[5], "%d.%m.%Y %H:%M:%S")
                    days_remaining = (expiration_date - datetime.now()).days
                    vpn_info_text += f"📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date.strftime('%d.%m.%Y %H:%M:%S')}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n\n"
                await message.answer(vpn_info_text, reply_markup=buy_keyboard, parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
            else:
                await message.answer(f"• 🛡 <b>Ваши VPN</b>:\n\nВы не имеете действующего VPN ❌\n\n<i>Чтобы купить VPN, воспользуйтесь кнопкой ниже, либо используйте команду</i> - /buy", reply_markup=buy_keyboard, parse_mode="HTML")
                if message.reply_markup:
                    await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                else:
                    await save_temp_message(message.from_user.id, message.text, None)
        
        elif message.text == "/history_of_operations":
            user_id = message.from_user.id
            user_name = message.from_user.username
            operation_history = await getting_operation_history(user_id=user_id)
            if operation_history is None or operation_history == []:
                await message.answer("• 📋 <b>История операций</b>:\n\nУ вас нет истории операций ❌", reply_markup=replenishment_balance, parse_mode="HTML")
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

            await message.answer(message_text, reply_markup=back_keyboard, parse_mode="HTML")
            if message.reply_markup:
                await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
            else:
                await save_temp_message(message.from_user.id, message.text, None)

        ##### ADM COMMANDS
        if message.text == "/add" or message.text == "/delete" or message.text == "/ban" or message.text == "/unban" or message.text == "/user_info" or message.text ==  "/user_vpn":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN):
                if message.text == "/add":
                    await message.answer("• 💵 <b>Пополнение баланса:</b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=about_yourself_to_add_keyboard, parse_mode="HTML")
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                    await AdmCommandState.WAITING_ID_OF_USER_FOR_ADD.set()
                
                elif message.text == "/delete":
                    await message.answer("• 💵 <b>Удаление баланса:</b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", reply_markup=about_yourself_to_delete_keyboard, parse_mode="HTML")
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                    await AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE.set()

                elif message.text == "/ban":
                    await message.answer("• ❌ <b>Блокировка пользователя:</b>\n\nВведите ID или USERNAME пользователя, которого хотите заблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                    await BanUserState.WAITING_FOR_USER_ID.set()
                
                elif message.text == "/unban":
                    await message.answer("• ✅ <b>Разблокировка пользователя:</b>\n\nВведите ID или USERNAME пользователя, которого хотите разблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                    await UnbanUserState.WAITING_FOR_USER_ID.set()

                elif message.text == "/user_info":
                    await message.answer("• 🗃 <b>Данные о пользователе:</b>\n\nВведите ID или USERNAME пользователя, информацию про которого хотите узнать: ", reply_markup=back_keyboard, parse_mode="HTML")
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                    await AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO.set()

                elif message.text == "/user_vpn":
                    await message.answer("• 🛡️ <b>VPN пользователя:</b>\n\nВведите ID или USERNAME пользователя, информацию о VPN которого хотите узнать: ", reply_markup=back_keyboard, parse_mode="HTML")
                    if message.reply_markup:
                        await save_temp_message(message.from_user.id, message.text, message.reply_markup.as_json())
                    else:
                        await save_temp_message(message.from_user.id, message.text, None)
                    await UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO.set()
            else:
                await message.answer("• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            await message.answer("• ❌ <b>Ошибка:</b>\n\nНеверная команда. Пожалуйста, используйте одну из доступных команд (/help)", reply_markup=start_kb_handle(user_id), parse_mode="HTML")   


def register_command_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(handle_text, content_types=['text'])