import json
import logging
import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#------------------------------------------------------------------------------

logger = logging.getLogger("Bot")

#------------------------------------------------------------------------------

def get_photo():
    try:
        os.system(
            "wget http://parking.melnik.ru:43434/cgi-bin/test.jpg -O photo.jpg")

        if not os.stat('photo.jpg').st_size:
            raise FileNotFoundError
            
        return open('photo.jpg', 'rb')
    except FileNotFoundError:
        logger.error("Файл с фото не найден")
        return None


def check_authorization(update):
    user_id = update['from']['id']
    user_name = update['from']['username']

    users = load_users()


    for user in users:
        if user['TG_name'] == user_name:
            if user['TG_id'] is None:
                user['TG_id'] = user_id
                with open("users.json", "w") as f:
                    json.dump(users, f)
            return user['Roles']

    for user in users:
        if user['TG_id'] == user_id:
            return user['Roles']

    return []


def add_user(TG_name):
    users = load_users()

    for user in users:
        if user['TG_name'] == TG_name:
            return False

    users.append({"TG_id": None, "TG_name": TG_name, "Roles": ["Member"]})
    with open("users.json", "w") as f:
        json.dump(users, f)
    return True


def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def get_main_keyboard(roles):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Обновить", callback_data="refresh"))
    if "Admin" in roles:
        keyboard.add(InlineKeyboardButton("🙋🏼‍♂️ Добавить пользователя",
                                          callback_data="add_user"))

    return keyboard
