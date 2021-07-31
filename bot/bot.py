import os
from dotenv import load_dotenv

from aiogram.types import ContentType
from aiogram import Bot, Dispatcher, types

from db.my_selectors.orders import get_active_user_order
from db.my_selectors.users import get_user

from bot.services import notify_users, check_registration, check_ordering, check_kaspi

from db.my_services.orders import create_order, append_text_to_order, finish_order
from db.my_services.users import create_user, update_user

from db.states import UserStates

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'register'])
async def register(msg: types.Message):
    user = get_user(telegram_id=msg.from_user.id)
    if user:
        reply = 'Вы уже зарегистрированы!'
    else:
        user = create_user(
            telegram_id=msg.from_user.id,
            username=msg.from_user.username,
            name=msg.from_user.full_name
        )
        reply = f'Здравствуйте, {user.name}!. ' \
                f'Отправьте мне свой номер каспи (можно номер карточки), чтобы другие могли отправлять вам деньги.'
    await msg.reply(reply)


@dp.message_handler(commands=['help'])
async def help(msg: types.Message):
    help_message = 'Haha'
    await msg.reply(help_message)


@dp.message_handler(commands=['order'])
async def new_order(msg: types.Message):
    user = get_user(telegram_id=msg.from_user.id)
    reply = 'Ничего не произошло...'
    check_registration(msg=msg, user=user)
    check_kaspi(msg=msg, user=user)
    check_ordering(msg=msg, user=user)
    if user.state == UserStates.REGISTERED.value:
        order = create_order(user_id=user.telegram_id)
        user = update_user(user=user, state=UserStates.ORDERING.value)
        reply = f'Заказ #{order.id} успешно создан. Отправьте мне то, что хотите заказать'
    await msg.reply(reply)


@dp.message_handler(commands=['close'])
async def close_order(msg: types.Message):
    user = get_user(telegram_id=msg.from_user.id)
    reply = 'Ничего не произошло...'
    check_registration(msg=msg, user=user)
    check_kaspi(msg=msg, user=user)
    if user.state == UserStates.ORDERING.value:
        order = get_active_user_order(user_id=user.telegram_id)
        order = finish_order(order=order)
        reply = f'Заказ #{order.id} успешно закрыт. Не забудьте забрать свои деньги.'
        await notify_users(bot=bot, author=user, notification_text=f'@{user.username} закрыл заказ.'
                                                                   f'Не забудьте перевести деньги.')
    elif user.state == UserStates.REGISTERED.value:
        reply = 'У вас нет активных заказов.'
    await msg.reply(reply)


@dp.message_handler(content_types=[ContentType.TEXT])
async def process_text(msg: types.Message):
    user = get_user(telegram_id=msg.from_user.id)
    reply = 'Ничего не произошло...'
    check_registration(msg=msg, user=user)
    if user.state == UserStates.CREATED.value:
        user = update_user(user=user, kaspi=msg.text, state=UserStates.REGISTERED.value)
        reply = f'Ваш номер каспи {user.kaspi}'
    if user.state == UserStates.ORDERING.value:
        order = get_active_user_order(user_id=user.telegram_id)
        order = append_text_to_order(order=order, text=f'\n{msg.text}')
        reply = f'Ваш заказ: {order.text}'
        await notify_users(bot=bot, author=user, notification_text=f'@{user.username} хочет заказать {order.text}')
    elif user.state == UserStates.REGISTERED.value:
        reply = 'У вас нет активных заказов. Создайте новый, используя /order'
    await msg.reply(reply)
