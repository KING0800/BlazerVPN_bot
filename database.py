import sqlite3 as sq
import uuid
import os 
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
VPN_PRICE_TOKEN = os.getenv("VPN_price_token") 

# создание всех БД для работы(1.UserINFO(общие данные о пользователях), 2.TempData(временные данные), 3.VpnData(данные о vpn))
async def db_start():
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    # данные о пользователе
    cur.execute(
        "CREATE TABLE IF NOT EXISTS UserINFO("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "user_id INTEGER, " 
        "user_name TEXT, "
        "balance INTEGER DEFAULT 0,"
        "time_of_registration TEXT,"
        "referrer_id INTEGER, "
        "used_promocodes TEXT,"
        "is_ban BOOLEAN DEFAULT False"
        ")"
    )
    # временные данные
    cur.execute(
        "CREATE TABLE IF NOT EXISTS TempData("
        "user_id INTEGER, "
        "message_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "message_text TEXT, "
        "message_markup TEXT, "
        "payment_key TEXT UNIQUE"
        ")"
    )
    # данные о VPN
    cur.execute(
        "CREATE TABLE IF NOT EXISTS VpnData("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "user_id INTEGER, "
        "user_name TEXT, "
        "location TEXT, "
        "active BOOLEAN, "
        "expiration_date DATETIME, "
        "name_of_vpn TEXT, "
        "vpn_config TEXT"
        ")"
    )
    # таблица для отслеживания истории операций пользователя 
    cur.execute(
        "CREATE TABLE IF NOT EXISTS OperationsHistory("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id INTEGER UNIQUE, "
        "user_name TEXT, "
        "operations TEXT, "
        "time_of_operation TEXT, " 
        "description_of_operation TEXT" 
        ")"
    )

    db.commit()

"""****************************************************** РЕДАКТИРОВАНИЕ UserINFO *********************************************"""
# добавление основных данных о пользователе 
async def edit_profile(user_name, user_id, referrer_id=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM UserINFO WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        if row is None:
            registration_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")  # Получаем время в нужном формате
            if referrer_id is not None:
                cur.execute(
                    "INSERT INTO UserINFO(user_id, user_name, time_of_registration, referrer_id) VALUES (?, ?, ?, ?)",
                    (user_id, user_name, registration_time, referrer_id)
                )
            else:
                cur.execute(
                    "INSERT INTO UserINFO(user_id, user_name, time_of_registration) VALUES (?, ?, ?)",
                    (user_id, user_name, registration_time)
                )
        db.commit()

# получение данных о балансе пользователя
async def get_balance(user_name=None, user_id=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        if user_name != None:
            cur.execute(
                "SELECT balance FROM UserINFO WHERE user_name = ?",
                (user_name,)
            )
            row = cur.fetchone()
            if row is not None:
                return row[0]
            else:
                return None
        elif user_id != None:
            cur.execute(
                "SELECT balance FROM UserINFO WHERE user_id = ?",
                (user_id,)
            )
            row = cur.fetchone()
            if row is not None:
                return row[0]
            else:
                return None
    
# операция по покупке (снятие денег)
async def buy_operation(user_id, user_name):
    balance = await get_balance(user_name=user_name)
    if int(balance) >= float(VPN_PRICE_TOKEN):
        db = sq.connect('UserINFO.db')
        cur = db.cursor()
        payment_key = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO TempData (user_id, payment_key) VALUES (?, ?)",
            (user_id, payment_key)
        )
        cur.execute(
            "UPDATE UserINFO SET balance = balance - ? WHERE user_name = ?",
            (VPN_PRICE_TOKEN, user_name,)
        )
        db.commit()
        db.close()
        return payment_key
    else:
        raise ValueError("Insufficient funds")
    
# операция по пополнению баланса
async def pay_operation(price, user_id=None, user_name=None):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    if user_name == None:
        cur.execute(
            "UPDATE UserINFO SET balance = balance + ? WHERE user_id = ?",
            (price, user_id,)
        )
    elif user_id == None:
        cur.execute(
            "UPDATE UserINFO SET balance = balance + ? WHERE user_name = ?",
            (price, user_name,)
        )
    db.commit()
    db.close()

# операция по удалению денег с баланса (ВРЕМЕННАЯ АДМИН КОМАНДА)
async def delete_sum_operation(price, user_id=None, user_name=None):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    if user_name == None:
        cur.execute(
            "UPDATE UserINFO SET balance = balance - ? WHERE user_id = ?",
            (price, user_id,)
        )
    elif user_id == None:
        cur.execute(
            "UPDATE UserINFO SET balance = balance - ? WHERE user_name = ?",
            (price, user_name,)
        )
    db.commit()
    db.close()

# нахождение данных о пользователе
async def find_user(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        result = cur.execute(
            "SELECT * FROM UserINFO WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        return bool(len(result))
        db.commit()

async def find_user_data(user_id=None, user_name=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        if user_id != None:
            result = cur.execute("SELECT * FROM UserINFO WHERE user_id = ?", (user_id,)).fetchall()
            if result != None:
                return result
            else:
                return None
        elif user_name != None:
            result = cur.execute("SELECT * FROM UserINFO WHERE user_name = ?", (user_name,)).fetchall()
            if result != None:
                return result
            else:
                return None

# нахождение рефералов по user_id
async def get_referrer_username(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute("SELECT user_name FROM UserINFO WHERE referrer_id = ?", (user_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return None
        
# поиск использования промокодов пользователями
async def check_promocode_used(user_id, promocode):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute("SELECT used_promocodes FROM UserINFO WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        if result:
            used_promocodes = result[0]
            if used_promocodes is not None and promocode in used_promocodes.split(','):
                return True
        return False

# сохранение данных о использованных промокодах пользователями
async def save_promocode(user_id, promocode):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute("UPDATE UserINFO SET used_promocodes = ? WHERE user_id = ?", (f"{promocode},", user_id))
        db.commit()

# система блокировки пользователей
async def ban_users_handle(user_id=None, user_name=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        if user_id != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_id = ?", (user_id,))
            result = cur.fetchone()
            if result[0] == 'False':
                cur.execute("UPDATE UserINFO SET is_ban = 'True' WHERE user_id = ?", (user_id,))
                return
            else:
                return "banned"
        elif user_name != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_name = ?", (user_name,))
            result = cur.fetchone()
            if result[0] == "False":
                cur.execute("UPDATE UserINFO SET is_ban = 'True' WHERE user_name = ?", (user_name,))
            else:
                return "banned"
            
# система разблокировки пользователей
async def unban_users_handle(user_id=None, user_name=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        if user_id != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_id = ?", (user_id,))
            result = cur.fetchone()
            if result[0] == 'True':
                cur.execute("UPDATE UserINFO SET is_ban = 'False' WHERE user_id = ?", (user_id,))
                return
            else:
                return "unbanned"
        elif user_name != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_name = ?", (user_name,))
            result = cur.fetchone()
            if result[0] == "True":
                cur.execute("UPDATE UserINFO SET is_ban = 'False' WHERE user_name = ?", (user_name,))
            else:
                return "unbanned"
            
async def is_user_ban_check(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        result = cur.execute("SELECT is_ban FROM UserINFO WHERE user_id = ?", (user_id,)).fetchone()
        if result[0] == 'False':
            return False
        elif result[0] == 'True':
            return True


"""*************************************************** РЕДАКТИРОВАНИЕ VpnData *********************************************"""
# обновление данных о vpn
async def update_vpn_state(user_id, user_name, location, active, expiration_days, name_of_vpn, vpn_config):
    with sq.connect('UserINFO.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        now = datetime.now()
        expiration_date = now + timedelta(days=int(expiration_days)) 
        expiration_date_str = expiration_date.strftime("%d.%m.%Y %H:%M:%S")
        cur.execute(
            "INSERT INTO VpnData (user_id, user_name, location, active, expiration_date, name_of_vpn, vpn_config) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, user_name, location, active, expiration_date_str, name_of_vpn, vpn_config)
        )
        db.commit()

# обновление данных после продления VPN
async def extend_vpn_state(user_id, location, active, expiration_date, id):
    with sq.connect('UserINFO.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        expiration_date_str = expiration_date.strftime("%d.%m.%Y %H:%M:%S")
        cur.execute(
            "UPDATE VpnData SET active=?, expiration_date=?, location=? WHERE user_id=? AND id=?",
            (active, expiration_date_str, location, user_id, id)
        )
        db.commit()


def check_expired_vpns():
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        current_time = datetime.now()
        current_time_str = current_time.strftime("%d.%m.%Y %H:%M:%S")
        cur.execute("SELECT * FROM VpnData WHERE expiration_date < ?", (current_time_str,)) 
        vpn_data = cur.fetchall()
        if vpn_data: 
            for vpn in vpn_data:
                user_id = vpn[1]
                expiration_date_str = vpn[5]
                expiration_date = datetime.strptime(expiration_date_str, "%d.%m.%Y %H:%M:%S")
                if current_time > expiration_date:
                    cur.execute("DELETE FROM VpnData WHERE user_id = ? AND expiration_date = ?", (user_id, expiration_date_str))
                    db.commit()
                    print(f"VPN для пользователя {user_id} с датой окончания {expiration_date} удален.")

# получение данных общих данных о vpn
async def get_vpn_data(user_id=None, user_name=None):
    with sq.connect('UserINFO.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        if user_id != None:
            cur.execute("SELECT * FROM VpnData WHERE user_id = ?", (user_id,))
            vpn_data = cur.fetchall()
            if vpn_data == None:
                return None
            else:
                return vpn_data
        elif user_name != None:
            cur.execute("SELECT * FROM VpnData WHERE user_name = ?", (user_name,))
            vpn_data = cur.fetchall()
            if vpn_data == None:
                return None
            else:
                return vpn_data
    
"""************************************************** РЕДАКТИРОВАНИЕ OperationsHistory ************************************************"""

async def edit_operations_history(user_id, user_name, operations, description_of_operation):
    operation_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute("SELECT operations, time_of_operation, description_of_operation FROM OperationsHistory WHERE user_id = ?", (user_id,))
        existing_data = cur.fetchone()
        
        if existing_data:
            existing_operations, existing_time, existing_description = existing_data
            operations = str(existing_operations) + "," + str(operations) if str(existing_operations) else str(operations)
            time_of_operation = existing_time + "," + operation_time if existing_time else operation_time
            description_of_operation = existing_description + "," + description_of_operation if existing_description else description_of_operation
            cur.execute("UPDATE OperationsHistory SET operations = ?, time_of_operation = ?, description_of_operation = ? WHERE user_id = ?", 
                        (operations, time_of_operation, description_of_operation, user_id))
        else:
            cur.execute("INSERT INTO OperationsHistory(user_id, user_name, operations, time_of_operation, description_of_operation) VALUES (?, ?, ?, ?, ?)",
                        (user_id, user_name, operations, operation_time, description_of_operation))

        db.commit()


async def getting_operation_history(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM OperationsHistory WHERE user_id = ?", (user_id,))
        operation_history = cur.fetchall()
        if operation_history is None:
            return None
        else:
            return operation_history

"""************************************************** РЕДАКТИРОВАНИЕ TempData *********************************************************"""
# сохранение сообщений и inline кнопок, для последующего использования кнопки "Назад"
async def save_temp_message(user_id, message_text, message_markup):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute("SELECT COUNT() FROM TempData WHERE user_id = ?", (user_id,))
        count = cur.fetchone()[0]
        
        if count >= 5: 
            cur.execute(
                "DELETE FROM TempData WHERE user_id = ? AND message_id = (SELECT MIN(message_id) FROM TempData WHERE user_id = ?)", 
                (user_id, user_id)
            ) 
        cur.execute(
            "INSERT INTO TempData (user_id, message_text, message_markup) VALUES (?, ?, ?)",
            (user_id, message_text, message_markup)
        )
        db.commit()

# получение сообщений и inline кнопок, для последующего использования кнопки "Назад"
async def get_temp_message(user_id, message_id=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        if message_id:
            cur.execute(
                "SELECT message_text, message_markup FROM TempData WHERE user_id = ? AND message_id = ?",
                (user_id, message_id)
            )
        else:
            cur.execute(
                "SELECT message_text, message_markup FROM TempData WHERE user_id = ?",
                (user_id,)
            )
        row = cur.fetchone()
        if row:
            return row[0], row[1]
        return None, None

# удаление сообщений и inline кнопок, используемых для кнопки "Назад"
async def delete_temp_message(user_id, message_id=None):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        if message_id:
            cur.execute(
                "DELETE FROM TempData WHERE user_id = ? AND message_id = ?",
                (user_id, message_id)
            )
        else:
            cur.execute(
                "DELETE FROM TempData WHERE user_id = ?",
                (user_id,)
            )
        db.commit()

# нахождение временных сообщений и inline кнопок по user_id 
async def find_message_id(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT MAX(message_id) FROM TempData WHERE user_id = ?", 
            (user_id,)
        )
        message_id = cur.fetchone()[0]
        db.commit()
        return message_id


