import os

from dotenv import load_dotenv

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from datetime import datetime

from bot.handlers.user_handlers import taking_vpn_price

from bot.keyboards.user_keyboards import help_kb, balance_handle_keyboard, start_kb_handle, device_keyboard, support_to_moders, replenishment_balance, back_keyboard, support_keyboard, location_keyboard, buy_keyboard, addind_count_for_extend, extend_keyboard, numbers_for_replenishment
from bot.keyboards.adm_keyboards import about_yourself_to_add_keyboard, about_yourself_to_delete_keyboard

from bot.database.UserData import is_user_ban_check, get_balance, get_referrer_info
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
ANUSH_CHAT_TOKEN = os.getenv("ANUSH_CHAT_TOKEN")
BLAZER_CHAT_TOKEN = os.getenv("BLAZER_CHAT_TOKEN")
HELPER_CHAT_TOKEN = os.getenv("HELPER_CHAT_TOKEN")

"""******************************************************************* ФУНКЦИЯ ДЛЯ ОБРАБОТКИ ВСЕХ КОМАНД *******************************************************"""

async def handle_text(message: Message, state):
    user_id = message.from_user.id
    if await is_user_ban_check(user_id=user_id):
        await message.answer_photo(photo="https://imgur.com/zhPS0ja", caption="<b>• Вы заблокированы ❌</b>\n\n<i>Вы можете узнать причину блокировки, спросив у модераторов: </i>", reply_markup=support_keyboard, parse_mode="HTML")
        return
    else:
        if message.text == "/help":
            if user_id == int(ANUSH_CHAT_TOKEN) or user_id == int(BLAZER_CHAT_TOKEN) or user_id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/aQbOPS0",
                                           caption="<b>• Доступные команды:</b>\n\n"
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
                                "************** <code>АДМИН КОМАНДЫ</code> **************\n"
                                "/user_info - 🗃 Данные о пользователях\n"
                                "/user_vpn - 🛡️ VPN пользователей\n"
                                "/add - 💵 Пополнение баланса\n"
                                "/delete - 💵 Удаление баланса\n"
                                "/ban - ❌ Заблокировать пользователя\n"
                                "/unban - ✅ Разблокировать пользователя\n", reply_markup=start_kb_handle(user_id), parse_mode="HTML")
                
            else:
                await message.answer_photo(photo="https://imgur.com/aQbOPS0",
                                           caption="<b>• Доступные команды:</b>\n\n"
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
            user_id = message.from_user.id
            balance = await get_balance(user_id=user_id)
            await message.answer_photo(photo="https://imgur.com/ATlnyXR", caption=f"• 💵 <b>Баланс</b>:\n\nВаш баланс: <code>{balance}</code> ₽\n\n<i>Чтобы пополнить свой баланс, вы можете использовать кнопку ниже, либо использовать команду - /replenishment</i>", reply_markup=balance_handle_keyboard, parse_mode="HTML")

        elif message.text == "/connect_with_dev":
            await message.answer_photo(photo="https://imgur.com/wz2wvor", caption="• 🧑‍💻 <b>Связь с разработчиком</b>:\n\nДля связи с разработчиком бота перейдите по <b><a href = 'https://t.me/KING_08001'>ссылке</a></b>", reply_markup=help_kb, parse_mode="HTML")
  
        elif message.text == "/buy":
            await message.answer_photo(photo="https://imgur.com/7Qhm4tw", caption="• 📍 <b>Локация:</b>\n\nДоступные локации:", reply_markup=location_keyboard, parse_mode="HTML")

        elif message.text == "/extend_vpn":
            user_id = message.from_user.id
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
                    await message.answer_photo(photo="https://imgur.com/Fv2UUEl", caption=f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}<b>Продление VPN на 28 дней стоит <code>{price}</code> ₽ 💵\nНажмите на кнопку, если готовы продлить VPN </b>🛡", parse_mode="HTML", reply_markup=extend_keyboard)
                else:
                    await message.answer_photo(photo="https://imgur.com/Fv2UUEl", caption=f"• 🛡 <b>Продление VPN:</b>\n\n{vpn_info_text}<b>Продление VPN на 28 дней стоит <code>{price}</code> ₽ 💵. \nВыберите VPN </b>🛡<b>, который хотите продлить:</b>", reply_markup=kb_for_count, parse_mode="HTML") 
            else: 
                await message.answer_photo(photo="https://imgur.com/2RUdfMp", caption="• 🛡 <b>Продление VPN:</b>\n\nУ вас нету действующего VPN ❌! \n\n<i>Вам его необходимо приобрести, нажав на кнопку ниже, либо использовав команду -</i> /buy", parse_mode="HTML", reply_markup=buy_keyboard)

        elif message.text == "/replenishment":
            await message.answer_photo(photo="https://imgur.com/GedgOxd", caption="• 💵 <b>Пополнение баланса</b>:\n\nВыберите сумму пополнения 💵, либо введите нужную самостоятельно: ", parse_mode="HTML", reply_markup=numbers_for_replenishment)
            await PaymentStates.WAITING_FOR_AMOUNT.set()

        elif message.text == "/support":
            await message.answer_photo(photo="https://imgur.com/K4hLFUD", caption="• 🆘 <b>Система поддержки</b>:\n\nЧтобы связаться с модераторами, нажмите на кнопку ниже.", parse_mode="HTML", reply_markup=support_to_moders)

        elif message.text == "/ref_system":
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
                text += "• 🤝 <b>Реферальная система</b>:\n\nУ вас еще нет рефералов."
            await message.answer_photo(photo="https://imgur.com/UcKZLFn", caption=text, parse_mode="HTML", reply_markup=back_keyboard)

        elif message.text == "/promocode":
            await message.answer_photo(photo="https://imgur.com/CwQn7Qv", caption="• 🎟 <b>Система промокодов</b>:\n\nВведите действующий промокод:", parse_mode="HTML", reply_markup=back_keyboard)
            await PromocodeStates.WAITING_FOR_USER_PROMOCODE.set()

        elif message.text == "/instruction":
            await message.answer_photo(photo="https://imgur.com/undefined", caption="• 📖 <b>Инструкция:</b>\n\nВыберите платформу, по которой хотите получить инструкцию по использованию VPN 🛡:", parse_mode="HTML", reply_markup=device_keyboard)            

        elif message.text == "/my_vpn":
            vpn_data = await get_vpn_data(user_id=user_id)
            if vpn_data != None:
                vpn_info_text = "• 🛡 <b>Ваши VPN</b>:\n\n"
                numbers = 0
                for vpn in vpn_data:
                    numbers += 1
                    location = vpn[3]
                    expiration_date = vpn[4]
                    vpn_key = vpn[5]
                    if expiration_date is not None:
                        expiration_date_new = datetime.datetime.strptime(str(expiration_date), "%d.%m.%Y %H:%M:%S")
                        days_remaining = (expiration_date_new - datetime.datetime.now()).days
                        vpn_info_text += f"{numbers}. ID: <code>{vpn[0]}</code>\n📍 Локация:  <code> {location}</code>\n🕘 Дата окончания:   <code>{expiration_date}</code>\n⏳ Осталось:   <code>{days_remaining}</code> дней\n🔑 Ключ активации: <pre>{vpn_key}</pre>\n\n"
                    else:
                        vpn_info_text += f"{numbers}. У вас имеется приобретенный VPN 🛡, который еще не обработан модераторами.\nОжидайте ответа модерации.\n\n"
                        numbers -= 1

                await message.answer_photo(photo="https://imgur.com/4NwMie5", caption=vpn_info_text, parse_mode="HTML", reply_markup=buy_keyboard)
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption=f"• 🛡 <b>Ваши VPN</b>:\n\nВы не имеете действующего VPN ❌\n\n<i>Чтобы купить VPN, воспользуйтесь кнопкой ниже, либо используйте команду</i> - /buy", parse_mode="HTML", reply_markup=buy_keyboard)
        
        elif message.text == "/history_of_operations":
            user_name = message.from_user.username
            user_id = message.from_user.id
            operation_history = await getting_operation_history(user_id=user_id)
            if operation_history is None or operation_history == []:
                await message.answer_photo("https://imgur.com/weO3juR", caption="• 📋 <b>История операций</b>:\n\nУ вас нет истории операций ❌", parse_mode="HTML", reply_markup=replenishment_balance)
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
            await message.answer_photo(photo="https://imgur.com/QnZumh4", caption=message_text, parse_mode="HTML", reply_markup=back_keyboard)

            await message.answer(message_text, reply_markup=back_keyboard, parse_mode="HTML")

        ##### ADM COMMANDS
        elif message.text == "/add":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN) or message.from_user.id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 💵 <b>Пополнение баланса:</b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", parse_mode="HTML", reply_markup=about_yourself_to_add_keyboard)
                await AdmCommandState.WAITING_ID_OF_USER_FOR_ADD.set()
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)
                
        elif message.text == "/delete":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN) or message.from_user.id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 💵 <b>Удаление баланса:</b>\n\nВведите <b>ID</b> или <b>USERNAME</b> пользователя:", parse_mode="HTML", reply_markup=about_yourself_to_delete_keyboard)
                await AdmCommandState.WAITING_ID_OF_USER_HANDLE_FOR_DELETE.set()
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)
                
        elif message.text == "/ban":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN) or message.from_user.id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• ❌ <b>Блокировка пользователя:</b>\n\nВведите ID или USERNAME пользователя, которого хотите заблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
                await BanUserState.WAITING_FOR_USER_ID.set()
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)

        elif message.text == "/unban":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN) or message.from_user.id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• ✅ <b>Разблокировка пользователя:</b>\n\nВведите ID или USERNAME пользователя, которого хотите разблокировать:", parse_mode="HTML", reply_markup=back_keyboard)
                await UnbanUserState.WAITING_FOR_USER_ID.set()
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)

        elif message.text == "/user_info":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN) or message.from_user.id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 🗃 <b>Данные о пользователе:</b>\n\nВведите ID или USERNAME пользователя, информацию про которого хотите узнать: ", parse_mode="HTML", reply_markup=back_keyboard)
                await AdmButtonState.WAITING_FOR_USER_ID_FOR_USER_INFO.set()
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)

        elif message.text == "/user_vpn":
            if message.from_user.id == int(ANUSH_CHAT_TOKEN) or message.from_user.id == int(BLAZER_CHAT_TOKEN) or message.from_user.id == int(HELPER_CHAT_TOKEN):
                await message.answer_photo(photo="https://imgur.com/i4sEHgp", caption="• 🛡️ <b>VPN пользователя:</b>\n\nВведите ID или USERNAME пользователя, информацию о VPN которого хотите узнать: ", parse_mode="HTML", reply_markup=back_keyboard)
                await UserVPNInfo.WAITING_FOR_USER_ID_FOR_USER_VPN_INFO.set()
            else:
                await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nВы не имеете доступа к этой команде! ❌\n\n<i>Чтобы узнать доступные вам команды, используйте</i> - /help", parse_mode="HTML", reply_markup=back_keyboard)
        else:
            await message.answer_photo(photo="https://imgur.com/weO3juR", caption="• ❌ <b>Ошибка:</b>\n\nНеверная команда. Пожалуйста, используйте одну из доступных команд (/help)", reply_markup=start_kb_handle(user_id), parse_mode="HTML")


def register_command_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(handle_text, content_types=['text'])