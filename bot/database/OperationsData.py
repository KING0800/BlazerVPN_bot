import sqlite3 as sq

from datetime import datetime

# создание таблицы для истории операций пользователя
async def OperationsData_db_start():
    with sq.connect('database.db') as db:
        cur = db.cursor()
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

# добавление данных о истории операций пользователя в бд
async def edit_operations_history(user_id, user_name, operations, description_of_operation):
    operation_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with sq.connect('database.db') as db:
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

# получение информации о истории операций с бд
async def getting_operation_history(user_id):
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM OperationsHistory WHERE user_id = ?", (user_id,))
        operation_history = cur.fetchall()
        if operation_history is None:
            return None
        else:
            return operation_history