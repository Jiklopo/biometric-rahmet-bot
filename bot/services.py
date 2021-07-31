from aiogram import Bot, types

from db.my_selectors.users import list_users
from db.states import UserStates
from db.tables import User


class WrongStateException(Exception):
    pass


async def notify_users(*, bot: Bot, author: User, notification_text: str):
    users = list_users()
    for user in users:
        if user.telegram_id != author.telegram_id:
            await bot.send_message(user.telegram_id, notification_text)


def check_registration(*, msg: types.Message, user: User):
    reply = None
    if not user:
        reply = 'Вы не зарегистрированы! Используйте команду /register'
    if reply:
        msg.reply(reply)
        raise WrongStateException


def check_kaspi(*, msg: types.Message, user: User):
    reply = None
    if user.state == UserStates.CREATED.value:
        reply = 'Вы не указали номер Каспи! Отправьте его сюда.'
    if reply:
        msg.reply(reply)
        raise WrongStateException


def check_ordering(*, msg: types.Message, user: User):
    reply = None
    if user.state == UserStates.ORDERING.value:
        reply = 'У вас есть активный заказ! Закройте его, используя /close.'
    if reply:
        msg.reply(reply)
        raise WrongStateException
