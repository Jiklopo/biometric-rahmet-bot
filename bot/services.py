from aiogram import Bot, types
from aiogram.utils.exceptions import MessageNotModified
from sqlalchemy.orm import Session

from db.my_selectors.users import get_all_users_from_orders
from db.states import UserStates
from db.tables import User, Order


class WrongStateException(Exception):
    pass


class WrongChatException(Exception):
    pass


async def update_order_message(*,
                               session: Session,
                               bot: Bot,
                               order: Order,
                               text: str = None,
                               inline_markup: types.InlineKeyboardMarkup = None):
    if text is None:
        users = get_all_users_from_orders(session=session, order=order)
        author = users.pop(0)
        text = f'Инициатор заказа @{author.username}\n'
        if users:
            text += 'Кто заказывает с ним:\n'
            for user in users:
                text += f'@{user.username}\n'
        text += '\nЧто в заказе:'
        text += order.text
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=order.chat_id,
            message_id=int(order.message_id),
            reply_markup=inline_markup
        )
    except MessageNotModified:
        print(f'Message of {order} has not been modified.')


def get_order_markup(*, order: Order) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton('Заказать вместе', callback_data=f'join_order#{order.id}')
    markup.add(join_button)
    return markup


# These checkers must be async so that bot can reply to messages
async def check_private(*, msg: types.Message):
    if msg.chat.type != 'private':
        await msg.reply('Эту команду можно использовать только в личном чате!')
        raise WrongChatException


async def check_group(*, msg: types.Message):
    if msg.chat.type not in ['group', 'supergroup']:
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
