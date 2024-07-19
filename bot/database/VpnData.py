import sqlite3 as sq

from datetime import datetime, timedelta

# создание таблицы для данных о VPN пользователей
async def VpnData_db_start():
    with sq.connect('database.db') as db:
        cur = db.cursor()
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
        db.commit()

# обновление данных о vpn
async def update_vpn_state(user_id, user_name, location, active, expiration_days, name_of_vpn, vpn_config):
    with sq.connect('database.db') as db:
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
    with sq.connect('database.db') as db:
        check_expired_vpns()
        cur = db.cursor()
        expiration_date_str = expiration_date.strftime("%d.%m.%Y %H:%M:%S")
        cur.execute(
            "UPDATE VpnData SET active=?, expiration_date=?, location=? WHERE user_id=? AND id=?",
            (active, expiration_date_str, location, user_id, id)
        )
        db.commit()

# функция для проверки VPN на окончание срока
def check_expired_vpns():
    with sq.connect('database.db') as db:
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
        db.commit()

# получение данных общих данных о vpn
async def get_vpn_data(user_id=None, user_name=None):
    with sq.connect('database.db') as db:
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
        db.commit()