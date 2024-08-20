import sqlite3 as sq

from datetime import datetime, timedelta, timezone

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
async def update_vpn_state(order_id, active, expiration_days, name_of_vpn, vpn_config):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(
            "UPDATE VpnData SET active = ?, expiration_date = ?, name_of_vpn = ?, vpn_config = ? WHERE id = ?",
            (active, expiration_days, name_of_vpn, vpn_config, order_id)
        )
        db.commit()
# обновление данных после продления VPN
async def extend_vpn_state(user_id, location, active, expiration_date, id):
    with sq.connect('database.db') as db:
        await check_expired_vpns()
        cur = db.cursor()
        expiration_date_str = expiration_date.strftime("%d.%m.%Y %H:%M:%S")
        cur.execute(
            "UPDATE VpnData SET active=?, expiration_date=?, location=? WHERE user_id=? AND id=?",
            (active, expiration_date_str, location, user_id, id)
        )
        db.commit()

# функция для проверки VPN на окончание срока
async def check_expired_vpns():
    with sq.connect('database.db') as db:
        list = []
        cur = db.cursor()
        current_time = datetime.now()
        current_time_str = current_time.strftime("%d.%m.%Y %H:%M:%S")
        cur.execute("SELECT * FROM VpnData WHERE expiration_date < ?", (current_time_str,)) 
        vpn_data = cur.fetchall()
        if vpn_data: 
            for vpn in vpn_data:
                user_id = vpn[1]
                user_name = vpn[2]
                expiration_date_str = vpn[5]
                file = vpn[7]
                expiration_date = datetime.strptime(expiration_date_str, "%d.%m.%Y %H:%M:%S")
                if current_time > expiration_date:
                    cur.execute("DELETE FROM VpnData WHERE user_id = ? AND expiration_date = ?", (user_id, expiration_date_str))
                    db.commit()
                    info_list = [user_id, user_name, expiration_date, file]
                    list.append(info_list)
            return list
        return []
                   

# функция, которая проверяет VPN на срок действия и отправляет уведомление если осталось меньше 5 дней до окончания
async def check_vpn_expiration_for_days(days: int):
    with sq.connect('database.db') as db:
        result = []
        cur = db.cursor()
        current_date = datetime.now(timezone.utc).date()
        cur.execute("SELECT * FROM VpnData WHERE expiration_date IS NOT NULL")
        vpn_data = cur.fetchall()
        if vpn_data:
            for vpn in vpn_data:
                user_id = vpn[1]
                user_name = vpn[2]
                expiration_date_str = vpn[5]
                file = vpn[7]
                expiration_date = datetime.strptime(expiration_date_str, "%d.%m.%Y %H:%M:%S").date()
                days_remaining = (expiration_date - current_date).days

                if days_remaining == days:
                    info_list = [user_id, user_name, expiration_date, file] 
                    result.append(info_list)
            return result 
        return []


# получение данных общих данных о vpn
async def get_vpn_data(user_id=None, user_name=None):
    with sq.connect('database.db') as db:
        await check_expired_vpns()
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

async def save_order_id(user_id, user_name, location):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO VpnData (user_id, user_name, location) VALUES (?, ?, ?)",
            (user_id, user_name, location)
        )
        order_id = cur.lastrowid
        db.commit()
        return order_id
    
async def get_order_id(order_id):
    with sq.connect('database.db') as db:
        cur = db.cursor()        
        cur.execute("SELECT * FROM VpnData WHERE id = ?", (order_id,))
        order_data = cur.fetchone()
        return order_data
