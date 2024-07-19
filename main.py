import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.handlers.user_handlers import register_user_handlers
from bot.handlers.adm_handlers import register_adm_handlers
from bot.handlers.commands_handlers import register_command_handlers

from bot.database.OperationsData import OperationsData_db_start
from bot.database.TempData import TempData_db_start
from bot.database.UserData import UserInfo_db_start
from bot.database.VpnData import VpnData_db_start
from bot.database.SupportData import SupportData_db_start

def register_handler(dp: Dispatcher) -> None:
    register_user_handlers(dp=dp)
    register_adm_handlers(dp=dp)
    register_command_handlers(dp=dp)

token = os.getenv("BOT_TOKEN")
bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())


async def main(dp: Dispatcher) -> None:
    load_dotenv('.env')
    try:
        await OperationsData_db_start()
        await TempData_db_start()
        await UserInfo_db_start()
        await VpnData_db_start()
        await SupportData_db_start()
        
    except Exception as ex:
        print(f"Ошибка при инициализации базы данных: {ex}")

    register_handler(dp=dp)

if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=main)