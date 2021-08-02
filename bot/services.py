from aiogram import Bot, types

from db.my_selectors.users import list_users
from db.states import UserStates
from db.tables import User, Order


class WrongStateException(Exception):
    pass


class WrongChatException(Exception):
    pass


def update_order_message(*, bot: Bot, order: Order, text: str, inline_markup: types.InlineKeyboardMarkup = None):
    return bot.edit_message_text(
        text=text,
        chat_id=order.chat_id,
        message_id=int(order.message_id),
        reply_markup=inline_markup
    )


async def check_private(*, msg: types.Message):
    if msg.chat.type != 'private':
        await msg.reply('Эту команду можно использовать только в личном чате!')
        raise WrongChatException


async def check_group(*, msg: types.Message):
    if msg.chat.type != 'group':
        await msg.reply('Эта команда работает только в групповых чатах!')
        raise WrongChatException


async def check_registration(*, msg: types.Message, user: User):
    reply = None
    if not user:
        reply = 'Вы не зарегистрированы! Используйте команду /register'
    if reply:
        await msg.reply(reply)
        raise WrongStateException


async def check_kaspi(*, msg: types.Message, user: User):
    reply = None
    if user.state == UserStates.CREATED.value:
        reply = 'Вы не указали номер Каспи! Отправьте его сюда.'
    if reply:
        await msg.reply(reply)
        raise WrongStateException


async def check_ordering(*, msg: types.Message, user: User):
    reply = None
    if user.state == UserStates.ORDERING.value:
        reply = 'У вас есть активный заказ! Закройте его, используя /close.'
    if reply:
        await msg.reply(reply)
        raise WrongStateException
