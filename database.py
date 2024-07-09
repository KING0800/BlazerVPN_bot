import sqlite3 as sq
import uuid
import os 
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
VPN_price_token = os.getenv("VPN_price_token") 

# создание всех БД для работы(1.UserINFO(общие данные о пользователях), 2.TempData(временные данные), 3.vpn_data(данные о vpn))
async def db_start():
    db = sq.connect('UserINFO.db')
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS UserINFO("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "user_id INTEGER, " 
        "user_name TEXT, "
        "balance INTEGER DEFAULT 0,"
        "time_of_registration TEXT,"
        "referrer_id INTEGER, "
        "used_promocodes TEXT"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS TempData("
        "user_id INTEGER, "
        "message_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "message_text TEXT, "
        "message_markup TEXT, "
        "payment_key TEXT UNIQUE"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS vpn_data("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "user_id INTEGER, "
        "user_name TEXT, "
        "location TEXT, "
        "active BOOLEAN, "
        "expiration_date DATETIME "
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
            registration_time = datetime.now().strftime("%Y.%m.%d %H:%M:%S")  # Получаем время в нужном формате
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
async def get_balance(user_name):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT balance FROM UserINFO WHERE user_name = ?",
            (user_name,)
        )
        row = cur.fetchone()
        if row is not None:
            return row[0]
    
# операция по покупке (снятие денег)
async def buy_operation(user_id, user_name):
    balance = await get_balance(user_name=user_name)
    if int(balance) >= float(VPN_price_token):
        db = sq.connect('UserINFO.db')
        cur = db.cursor()
        payment_key = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO TempData (user_id, payment_key) VALUES (?, ?)",
            (user_id, payment_key)
        )
        cur.execute(
            "UPDATE UserINFO SET balance = balance - ? WHERE user_name = ?",
            (VPN_price_token, user_name,)
        )
        db.commit()
        db.close()
        return payment_key
    else:
        raise ValueError("Insufficient funds")
    
# операция по пополнению баланса
async def pay_operation(price, user_id):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "UPDATE UserINFO SET balance = balance + ? WHERE user_id = ?",
        (price, user_id,)
    )
    db.commit()
    db.close()

# операция по удалению денег с баланса (ВРЕМЕННАЯ АДМИН КОМАНДА)
async def delete_sum_operation(price, user_id):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "UPDATE UserINFO SET balance = balance - ? WHERE user_id = ?",
        (price, user_id,)
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

"""*************************************************** РЕДАКТИРОВАНИЕ vpn_data *********************************************"""
# обновление данных о vpn
async def update_vpn_state(user_id, user_name, location, active, expiration_days):
    with sq.connect('UserINFO.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        now = datetime.now()
        expiration_date = now + timedelta(days=int(expiration_days)) 
        expiration_date_str = expiration_date.strftime("%Y.%m.%d %H:%M:%S")
        cur.execute(
            "INSERT INTO vpn_data (user_id, user_name, location, active, expiration_date) VALUES (?, ?, ?, ?, ?)",
            (user_id, user_name, location, active, expiration_date_str)
        )
        db.commit()

# обновление данных после продления VPN
async def extend_vpn_state(user_id, location, active, expiration_date, id):
    with sq.connect('UserINFO.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        expiration_date_str = expiration_date.strftime("%Y.%m.%d %H:%M:%S")
        cur.execute(
            "UPDATE vpn_data SET active=?, expiration_date=?, location=? WHERE user_id=? AND id=?",
            (active, expiration_date_str, location, user_id, id)
        )
        db.commit()

# удаляет записи старых vpn, когда у них кончается срок
def check_expired_vpns():
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        current_time = datetime.now()  # Получаем текущее время в Python
        current_time_str = current_time.strftime("%Y.%m.%d %H:%M:%S")  # Преобразуем в строку с форматом 
        cur.execute(f"SELECT * FROM vpn_data WHERE expiration_date < '{current_time_str}'")  # Используем строку в запросе
        vpn_data = cur.fetchall()
        for vpn in vpn_data:
            user_id = vpn[0]
            expiration_date_str = vpn[3]
            expiration_date = datetime.strptime(expiration_date_str, "%Y.%m.%d %H:%M:%S")
            cur.execute("DELETE FROM vpn_data WHERE user_id = ? AND expiration_date = ?", (user_id, expiration_date_str))
            db.commit()
            print(f"VPN для пользователя {user_id} с датой окончания {expiration_date} удален.")

# получение данных общих данных о vpn
async def get_vpn_data(user_id):
    with sq.connect('UserINFO.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        cur.execute("SELECT * FROM vpn_data WHERE user_id = ?", (user_id,))
        vpn_data = cur.fetchall()
        if vpn_data == None:
            return None
        else:
            return vpn_data
    
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
