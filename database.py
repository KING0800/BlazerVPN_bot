import sqlite3 as sq
import uuid
import os 
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
VPN_price_token = os.getenv("VPN_price_token") 

async def db_start():
    db = sq.connect('UserINFO.db')
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS UserINFO("
        "user_id INTEGER PRIMARY KEY, " 
        "user_name TEXT, "
        "balance INTEGER DEFAULT 0,"
        "payment_key TEXT UNIQUE,"
        "vpn_active BOOLEAN DEFAULT FALSE,"
        "vpn_location TEXT,"
        "vpn_expiration_date DATETIME, "
        "referrer_id INTEGER"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS TempData("
        "user_id TEXT, "
        "message_id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "message_text TEXT, "
        "message_markup TEXT "
        ")"
    )
    db.commit()

async def edit_profile(user_name, user_id, referrer_id=None):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM UserINFO WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        if referrer_id != None:
            cur.execute(
                "INSERT INTO UserINFO(user_id, user_name, referrer_id) VALUES (?, ?, ?)",
                (user_id, user_name, referrer_id, )
            )
        else:
            cur.execute(
                "INSERT INTO UserINFO(user_id, user_name) VALUES (?, ?)",
                (user_id, user_name,)
                )
    db.commit()
    db.close()


async def checking_balance(amount, user_name):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM UserINFO WHERE user_name = ?",
        (user_name,)
    )
    row = cur.fetchone()
    if row is None:
        cur.execute(
            "INSERT INTO UserINFO(user_name) VALUES (?)",
            (user_name,))
        db.commit()
    cur.execute(
        "UPDATE UserINFO SET balance = balance + ? WHERE user_name = ?",
        (amount, user_name)
    )
    db.commit()
    db.close()

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
    
async def buy_operation(user_name):
    balance = await get_balance(user_name)
    if int(balance) >= float(VPN_price_token):
        db = sq.connect('UserINFO.db')
        cur = db.cursor()
        cur.execute(
            "SELECT payment_key FROM UserINFO WHERE user_name = ?",
            (user_name,)
        )
        existing_order_id = cur.fetchone()

        if existing_order_id:
            payment_key = str(uuid.uuid4())
        else:
            payment_key = str(uuid.uuid4())

        cur.execute(
            "UPDATE UserINFO SET balance = balance - ?, payment_key = ? WHERE user_name = ?",
            (VPN_price_token, payment_key, user_name,)
        )
        db.commit()
        db.close()
        return payment_key
    else:
        raise ValueError("Insufficient funds")
    
async def pay_operation(price, user_id):
    balance = await get_balance(user_id)
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "UPDATE UserINFO SET balance = balance + ? WHERE user_id = ?",
        (price, user_id,)
    )
    db.commit()
    db.close()

async def changing_payment_key(payment_key):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "SELECT user_id FROM UserINFO WHERE payment_key = ?",
        (payment_key,)
    )
    row = cur.fetchone()
    db.close()
    return row

async def update_vpn_state(user_id, active, expiration_date):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute(
            "UPDATE UserINFO SET vpn_active = ?, vpn_expiration_date = ? WHERE user_id = ?",
            (active, expiration_date, user_id)
        )
        db.commit()

async def get_vpn_state(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT vpn_active, vpn_expiration_date FROM UserINFO WHERE user_id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        if row:
            active, expiration_date = row
            if expiration_date:
                days_remaining = (int(expiration_date) - int((datetime.now()).day))
                return active, days_remaining
            else:
                return active, None 
        return None, None 
    
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
        

async def find_user(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        result = cur.execute(
            "SELECT * FROM UserINFO WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        return bool(len(result))
        db.commit()

async def count_refs(user_id):
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        return cur.execute("SELECT COUNT('id') as count FROM UserINFO WHERE 'referrer_id' = ?", (user_id,)).fetchone()[0]