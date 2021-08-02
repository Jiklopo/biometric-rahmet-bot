import dataclasses
import os
from dotenv import load_dotenv

from aiogram.types import ContentType
from aiogram import Bot, Dispatcher, types

from db.my_selectors.orders import get_active_user_order, get_order
from db.my_selectors.users import get_user

from bot.services import update_order_message, check_registration, check_ordering, check_kaspi, check_group, \
    check_private

from db.my_services.orders import create_order, append_text_to_order, finish_order, add_joined_user
from db.my_services.users import create_user, update_user

from db.states import UserStates

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'register'])
async def register(msg: types.Message):
    await check_private(msg=msg)

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
    await check_group(msg=msg)

    user = get_user(telegram_id=msg.from_user.id)
    reply = 'Ничего не произошло...'
    markup = None

    await check_registration(msg=msg, user=user)
    await check_kaspi(msg=msg, user=user)
    await check_ordering(msg=msg, user=user)

    if user.state == UserStates.REGISTERED.value:
        bot_msg: types.Message = await bot.send_message(msg.chat.id, f'@{user.username} хочет создать новый заказ!')
        order = create_order(user_id=user.telegram_id, chat_id=bot_msg.chat.id, message_id=bot_msg.message_id)
        user = update_user(user=user, state=UserStates.ORDERING.value)
        markup = types.InlineKeyboardMarkup()
        join_button = types.InlineKeyboardButton('Заказать вместе', callback_data=f'join_order#{order.id}')
        markup.add(join_button)
        text = f'@{user.username} создал новый заказ!'
        await update_order_message(bot=bot, order=order, text=text, inline_markup=markup)

    await msg.reply(reply, reply_markup=markup)


@dp.message_handler(commands=['close'])
async def close_order(msg: types.Message):
    await check_group(msg=msg)

    user = get_user(telegram_id=msg.from_user.id)
    reply = 'Ничего не произошло...'

    await check_registration(msg=msg, user=user)
    await check_kaspi(msg=msg, user=user)

    if user.state == UserStates.ORDERING.value:
        order = get_active_user_order(user_id=user.telegram_id)
        order = finish_order(order=order)
        reply = f'Заказ #{order.id} успешно закрыт. Не забудьте забрать свои деньги.'
        await update_order_message(bot=bot,
                                   author=user,
                                   text=f'@{user.username} закрыл заказ. Не забудьте перевести деньги.')

    elif user.state == UserStates.REGISTERED.value:
        reply = 'У вас нет активных заказов.'

    await msg.reply(reply)


@dp.message_handler(content_types=[ContentType.TEXT])
async def process_text(msg: types.Message):
    user = get_user(telegram_id=msg.from_user.id)
    reply = 'Ничего не произошло...'

    await check_registration(msg=msg, user=user)

    if user.state == UserStates.CREATED.value:
        user = update_user(user=user, kaspi=msg.text, state=UserStates.REGISTERED.value)
        reply = f'Ваш номер каспи {user.kaspi}'

    elif user.state == UserStates.ORDERING.value:
        order = get_active_user_order(user_id=user.telegram_id)
        order = append_text_to_order(order=order, text=f'\n{msg.text}')
        reply = f'Ваш заказ: {order.text}'
        await update_order_message(bot=bot, author=user, text=f'@{user.username} хочет заказать {order.text}')

    elif user.state == UserStates.REGISTERED.value:
        reply = 'У вас нет активных заказов. Создайте новый, используя /order'

    await msg.reply(reply)

    #
    # @dp.callback_query_handlers(func=lambda c: c.data.startswith('join_order'))
    # async def join_order_callback(callback: types.CallbackQuery):
    #     user = get_user(telegram_id=callback.from_user.id)
    #     order_id = callback.data.split('#')[1]
    #     order = get_order(order_id=order_id)
    #     order = add_joined_user(order=order, user=user)
