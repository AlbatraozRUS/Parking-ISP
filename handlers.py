import logging
import os
from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from backend import get_photo, add_user, check_authorization, get_main_keyboard

#------------------------------------------------------------------------------

class AddUser(StatesGroup):
    waiting_for_username = State()

logger = logging.getLogger("Bot")

MAIN_MESSAGE = "*[Парковка на Солженицына 23А]*\n\n*Время:* %(time)s"

#------------------------------------------------------------------------------

async def handle_get_photo(update):
    logger.info(f"[{update['from']['username']}]({update['from']['id']})")

    roles = check_authorization(update)
    if "Member" not in roles:
        await update.answer("Вы не авторизованы")
        return

    message_text = MAIN_MESSAGE % {
        "time": datetime.now().strftime('%H:%M:%S %d %B')}
    
    keyboard = get_main_keyboard(roles)

    photo = get_photo()
    if photo is None:
        # Уведомление Дмитрия и Искандера о неработающей камере
        error_text = "*[Уведомление]*\n\n" \
                     "Камера недоступна, просьба перезапустить ее"
        await send_message_to(489419770, error_text)
        await send_message_to(381249598, error_text)
        
        await update.answer("Произошла ошибка")
        return

    if type(update) == types.CallbackQuery:
        photo_media = types.InputMediaPhoto(photo, caption=message_text)
        await update.message.edit_media(photo_media, reply_markup=keyboard)
    elif type(update) == types.Message:
        await update.answer_photo(photo=photo,
                                  caption=message_text,
                                  reply_markup=keyboard)
    else:
        await update.answer("Произошла какая-от ошибка :(\n\nОтправьте /start")
        return       

    photo.close()


async def handle_add_user(call: types.CallbackQuery, state: FSMContext):
    logger.info(f"[{call.from_user.username}]({call.from_user.id}) - "
                f"{call.data}")

    await call.message.delete()

    message = await call.message.answer("*Введите никнейм нового пользователя.* "
                                        "Например, @Dmitry285631\n\n"
                                        "_P.S. Для отмены отправьте_ /cancel")
    await state.update_data(message=message)

    await AddUser.waiting_for_username.set()
    await call.answer()


async def handle_confirm_add_user(message: types.Message, state: FSMContext):
    logger.info(f"[{message.from_user.username}]({message.from_user.id}) - "
                f"{message.text}")

    data = await state.get_data()
    await message.delete()

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🙋🏼‍♂️ Добавить пользователя", 
                                      callback_data="add_user"))
    keyboard.add(InlineKeyboardButton("📸 Фото парковки",
                                      callback_data="refresh"))

    if message.text == "/cancel":
        await data["message"].delete()
        await state.finish()
        await handle_get_photo(message)
        return

    if message.text[0] != "@":
        await state.finish()
        await data["message"].edit_text("*Никнейм должен начинаться с @*",
                                        reply_markup=keyboard)
        return

    if not add_user(message.text[1::]):
        await state.finish()
        await data["message"].edit_text("*Пользователь уже добавлен в базу*",
                                        reply_markup=keyboard)
        return

    await data["message"].edit_text("*Пользователь успешно добавлен*",
                                    reply_markup=keyboard)
    await state.finish()


async def handle_error(update, error: Exception):
    bot = Bot(token=os.getenv("TG_TOKEN"))
    update = dict(update)

    if update.get('callback_query') is not None:
        user_id = update['callback_query']['from']['id']
        user_username = update['callback_query']['from']['username']

        command = update['callback_query']['data']
        chat_id = update['callback_query']['message']['chat']['id']

        keyboard = get_main_keyboard(check_authorization(update['callback_query']))
    else:
        user_id = update['message']['from']['id']
        user_username = update['message']['from']['username']

        command = update['message']['text']
        chat_id = update['message']['chat']['id']

        keyboard = get_main_keyboard(check_authorization(update['message']))

    await bot.send_photo(chat_id, 
                         get_photo(), 
                         MAIN_MESSAGE % {'time': datetime.now().strftime('%H:%M:%S %d %B')},
                         parse_mode=types.ParseMode.MARKDOWN, 
                         reply_markup=keyboard)
    
    logger.error(f"{user_username}({user_id}) - {command}")
    logger.exception(error)

    exception_data = f"{error.__class__.__name__}: {str(error)}"
    message_text = f'''
    *[ADMIN]*
    В работе бота возникла ошибка:

    *User username:* {user_username}
    *User id:* {user_id}
    *Command:* {command}
    *Exception:* {exception_data}'''

    await bot.send_message(381249598, 
                           message_text, 
                           parse_mode=types.ParseMode.MARKDOWN)

    return True


async def send_message_to(tg_id, message):
    token = os.getenv('TG_TOKEN')

    bot = Bot(token=token)

    await bot.send_message(tg_id, message, parse_mode=types.ParseMode.MARKDOWN)


async def handle_unknown_message(message: types.Message):
    logger.info(f"[{message.from_user.username}]({message.from_user.id}) - "
                f"{message.text}")

    await message.answer(f"*Команда не распознана\n\n"
                         "Для получения фотографии парковки отправьте* /start")
