import sqlite3 as sq

# создание таблицы для временных сообщений и данных
async def TempData_db_start():
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS TempData("
            "user_id INTEGER, "
            "message_id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "message_text TEXT, "
            "message_markup TEXT, "
            "payment_key TEXT UNIQUE,"
            "photo_url TEXT"
            ")"
        )

        db.commit()

# сохранение сообщений и inline кнопок, для последующего использования кнопки "Назад"
async def save_temp_message(user_id, message_text, message_markup, photo_url):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM TempData WHERE user_id = ?", (user_id,))
            count = cur.fetchone()[0]
            if count >= 15:
                cur.execute("SELECT message_id FROM TempData WHERE user_id = ? ORDER BY message_id ASC LIMIT 1", (user_id,))
                message_id = cur.fetchone()[0] 
                await delete_temp_message(user_id, message_id)
            cur.execute(
                "INSERT INTO TempData (user_id, message_text, message_markup, photo_url) VALUES (?, ?, ?, ?)",
                (user_id, message_text, message_markup, photo_url)
            )
            db.commit()
        except Exception as e:
            print(f"Ошибка при сохранении сообщения в базу данных: {e}")


# получение сообщений и inline кнопок, для последующего использования кнопки "Назад"
async def get_temp_message(user_id, message_id=None):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        if message_id:
            cur.execute(
                "SELECT message_text, message_markup, photo_url FROM TempData WHERE user_id = ? AND message_id = ?",
                (user_id, message_id)
            )
        else:
            cur.execute(
                "SELECT message_text, message_markup, photo_url FROM TempData WHERE user_id = ?",
                (user_id,)
            )
        row = cur.fetchone()
        if row:
            await delete_temp_message(user_id=user_id, message_id=message_id)
            return row[0], row[1], row[2]
        db.commit()
        return None, None, None
        

# удаление сообщений и inline кнопок, используемых для кнопки "Назад"
async def delete_temp_message(user_id, message_id):
    with sq.connect('database.db') as db:
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
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(
            "SELECT MAX(message_id) FROM TempData WHERE user_id = ?", 
            (user_id,)
        )
        message_id = cur.fetchone()[0] 
        db.commit()
        return message_id