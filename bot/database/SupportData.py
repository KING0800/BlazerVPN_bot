import sqlite3 as sq

# создание базы данных для системы поддержки 
async def SupportData_db_start():
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS SupportData("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, " 
            "user_name TEXT, "
            "question TEXT"
            ")"
        )

        db.commit()


async def edit_data(user_name, user_id, question):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportData WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row == None:
            cur.execute("INSERT INTO SupportData(user_name, user_id, question) VALUES (?, ?, ?)", (user_name, user_id, question))
        else:
            return
        
async def getting_question(user_id):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SupportData WHERE user_id = ?", (user_id,))
        info = cur.fetchall()
        if info != None:
            return info
        else:
            return None
        
async def deleting_answered_reports(user_id):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("DELETE FROM SupportData WHERE user_id = ?", (user_id,))
        return 