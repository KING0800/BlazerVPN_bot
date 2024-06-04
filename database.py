import sqlite3 as sq
import uuid
from tokens import VPN_price

async def db_start():
    db = sq.connect('UserINFO.db')
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS UserINFO("
        "user_id INTEGER PRIMARY KEY, " 
        "user_name TEXT, "
        "balance INTEGER DEFAULT 0,"
        "payment_key TEXT UNIQUE"
        ")"
    )
    db.commit()

async def edit_profile(user_name, user_id):
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM UserINFO WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        cur.execute(
            "INSERT INTO UserINFO(user_id, user_name) VALUES (?, ?)",
            (user_id, user_name)
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
    print(user_name)
    with sq.connect('UserINFO.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT balance FROM UserINFO WHERE user_name = ?",
            (user_name,)
        )
        row = cur.fetchone()
        if row is not None:
            return row[0]
        else:
            return "Значение не найдено." 
    

    
async def buy_operation(user_name):
    balance = await get_balance(user_name)
    if int(balance) >= float(VPN_price):
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
            (VPN_price, payment_key, user_name,)
        )
        db.commit()
        db.close()
        return payment_key
    else:
        raise ValueError("Insufficient funds")
    

async def pay_operation(user_name):
    balance = await get_balance(user_name)
    db = sq.connect('UserINFO.db')
    cur = db.cursor()
    cur.execute(
        "UPDATE UserINFO SET balance = balance + ? WHERE user_name = ?",
        (VPN_price, user_name,)
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


    
