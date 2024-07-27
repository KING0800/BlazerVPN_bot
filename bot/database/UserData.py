import sqlite3 as sq
import uuid
import os 

from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env')
VPN_PRICE_TOKEN = os.getenv("VPN_PRICE_TOKEN") 

# Создание таблицы UserInfo
async def UserInfo_db_start():
    with sq.connect('database.db') as db:
        cur = db.cursor()
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
        db.commit()

# добавление основных данных о пользователе 
async def edit_profile(user_name, user_id, referrer_id=None):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM UserINFO WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        if row is None:
            registration_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S") 
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
    with sq.connect('database.db') as db:
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
        with sq.connect('database.db') as db:
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
            return payment_key
    else:
        raise ValueError("Insufficient funds")
    
# операция по пополнению баланса
async def pay_operation(price, user_id=None, user_name=None):
    with sq.connect('database.db') as db:
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

# нахождение рефералов по user_id
async def get_referrer_username(user_id):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("SELECT user_name FROM UserINFO WHERE referrer_id = ?", (user_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return None
        
# поиск использования промокодов пользователями
async def check_promocode_used(user_id, promocode):
    with sq.connect('database.db') as db:
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
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("SELECT used_promocodes FROM UserINFO WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
        used_promocodes = result[0] if result else ""

        if used_promocodes:
            used_promocodes += f",{promocode}"
        else:
            used_promocodes = promocode

        # Обновляем запись
        cur.execute("UPDATE UserINFO SET used_promocodes = ? WHERE user_id = ?", (used_promocodes, user_id))
        db.commit()

"""****************************************************************** АДМИН ФУНКЦИИ *****************************************************************"""

# операция по удалению денег с баланса 
async def delete_sum_operation(price, user_id=None, user_name=None):
    db = sq.connect('database.db')
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
        
# нахождение данных о пользователе
async def find_user_data(user_id=None, user_name=None):
    with sq.connect('database.db') as db:
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

# система блокировки пользователей
async def ban_users_handle(user_id=None, user_name=None):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        if user_id != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_id = ?", (user_id,))
            result = cur.fetchone()
            if result[0] == 0:
                cur.execute("UPDATE UserINFO SET is_ban = 1 WHERE user_id = ?", (user_id,))
                return
            else:
                return "banned"
        elif user_name != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_name = ?", (user_name,))
            result = cur.fetchone()
            if result[0] == 0:
                cur.execute("UPDATE UserINFO SET is_ban = 1 WHERE user_name = ?", (user_name,))
            else:
                return "banned"
            
# система разблокировки пользователей
async def unban_users_handle(user_id=None, user_name=None):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        if user_id != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_id = ?", (user_id,))
            result = cur.fetchone()
            if result[0] == 1:
                cur.execute("UPDATE UserINFO SET is_ban = 0 WHERE user_id = ?", (user_id,))
                return
            else:
                return "unbanned"
        elif user_name != None:
            cur.execute("SELECT is_ban FROM UserINFO WHERE user_name = ?", (user_name,))
            result = cur.fetchone()
            if result[0] == 1:
                cur.execute("UPDATE UserINFO SET is_ban = 0 WHERE user_name = ?", (user_name,))
            else:
                return "unbanned"
            
# проверка на блокировку пользователя
async def is_user_ban_check(user_id):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        result = cur.execute("SELECT is_ban FROM UserINFO WHERE user_id = ?", (user_id,)).fetchone()
        if result[0] == 0:
            return False
        elif result[0] == 1:
            return True
