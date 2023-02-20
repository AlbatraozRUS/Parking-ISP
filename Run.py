import asyncio
import locale
import logging
import os


from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from handlers import (AddUser,
                      handle_get_photo,
                      handle_add_user, 
                      handle_confirm_add_user, 
                      handle_error,
                      handle_unknown_message)
                      
#------------------------------------------------------------------------------

logger = logging.getLogger("Bot")

#------------------------------------------------------------------------------


def main():
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    format = "%(asctime)s - [%(module)s]:%(funcName)s() - %(message)s"

    logging.basicConfig(level=logging.INFO, format=format,
                        datefmt='%d-%m-%Y %H:%M:%S')

    try:
        logger.info("Starting bot...")
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        return


async def run_bot():
    token = os.getenv('TG_TOKEN')

    bot = Bot(token=token, parse_mode=types.ParseMode.MARKDOWN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_all_handlers(dp)

    await dp.skip_updates()
    await dp.start_polling()


def register_all_handlers(dp: Dispatcher):
    dp.register_message_handler(
        handle_get_photo, 
        commands="start")

    dp.register_callback_query_handler(
        handle_get_photo, 
        Text(equals="refresh"))

    dp.register_callback_query_handler(
        handle_add_user, 
        Text(equals="add_user"))

    dp.register_message_handler(
        handle_confirm_add_user,
        state=AddUser.waiting_for_username)
    
    dp.register_errors_handler(
        handle_error,
        exception=BaseException)

    dp.register_message_handler(handle_unknown_message)

if __name__ == "__main__":
    main()
