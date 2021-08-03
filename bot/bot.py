import os
from dotenv import load_dotenv

from aiogram.types import ContentType
from aiogram import Bot, Dispatcher, types
from sqlalchemy.orm import Session

from db import engine
from db.my_selectors.orders import get_active_user_order, get_order, get_group_order
from db.my_selectors.users import get_user
from db.states import UserStates

from db.my_services.orders import create_order, append_text_to_order, finish_order, add_joined_user
from db.my_services.users import create_user, update_user, delete_user
from db.validators import validate_kaspi
from bot.services import (
    update_order_message,
    check_registration,
    check_ordering,
    check_kaspi,
    check_group,
    check_private,
    get_order_markup,
    WrongChatException,
    WrongStateException
)

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'register'])
async def register(msg: types.Message):
    try:
        await check_private(msg=msg)
    except WrongChatException:
        return

    with Session(engine) as session:
        user = get_user(session=session, telegram_id=msg.from_user.id)
        if user:
            reply = 'Вы уже зарегистрированы!'

        else:
            user = create_user(
                session=session,
                telegram_id=msg.from_user.id,
                username=msg.from_user.username,
                name=msg.from_user.full_name
            )
            reply = f'Здравствуйте, {user.name}! ' \
                    f'Отправьте мне свой номер каспи (можно номер карточки), чтобы другие могли отправлять вам деньги.'

    await msg.reply(reply)


@dp.message_handler(commands=['help'])
async def help(msg: types.Message):
    help_message = 'Здравствуйте! Чтобы мной пользоваться, /register, ' \
                   'а затем введите свой номер каспи. Добавьте меня в групповой чат, ' \
                   'создайте новый /order. Отвечайте на мои сообщения, чтобы добавить что-то в заказ. ' \
                   'Если вы не являетесь инициатором, то сначала нужно будет присоединиться к заказу.' \
                   'Используйте /close, чтобы никто не мог добавлять в заказ.'
    await msg.reply(help_message)


@dp.message_handler(commands=['unregister'])
async def unregister(msg: types.Message):
    try:
        await check_private(msg=msg)
    except WrongChatException:
        return

    with Session(engine) as session:
        user = get_user(session=session, telegram_id=msg.from_user.id)
        if not user:
            reply = 'Вы не зарегистрированы!'

        else:
            delete_user(session=session, user=user)
            reply = 'Ваш аккаунт удален.'

    await msg.reply(reply)


@dp.message_handler(commands=['order'])
async def new_order(msg: types.Message):
    try:
        await check_group(msg=msg)
    except WrongChatException:
        return

    with Session(engine) as session:
        user = get_user(session=session, telegram_id=msg.from_user.id)

        try:
            await check_registration(msg=msg, user=user)
            await check_kaspi(msg=msg, user=user)
            await check_ordering(msg=msg, user=user)
        except WrongStateException:
            return

        order = get_group_order(session=session, group_id=msg.chat.id)

        if order:
            await msg.reply('В этой группе уже есть заказ! Сначала закройте его.')
            return

        if user.state == UserStates.REGISTERED.value:
            bot_msg: types.Message = await bot.send_message(msg.chat.id, f'@{user.username} хочет создать новый заказ!')
            order = create_order(
                session=session,
                user_id=user.telegram_id,
                chat_id=bot_msg.chat.id,
                message_id=bot_msg.message_id
            )
            user = update_user(session=session, user=user, state=UserStates.ORDERING.value)
            markup = get_order_markup(order=order)
            text = f'@{user.username} создал новый заказ!'
            await update_order_message(session=session, bot=bot, order=order, text=text, inline_markup=markup)
            return

    await msg.reply('Ничего не произошло...')


@dp.message_handler(commands=['close'])
async def close_order(msg: types.Message):
    try:
        await check_group(msg=msg)
    except WrongChatException:
        return

    with Session(engine) as session:
        user = get_user(session=session, telegram_id=msg.from_user.id)
        reply = 'Ничего не произошло...'

        try:
            await check_registration(msg=msg, user=user)
            await check_kaspi(msg=msg, user=user)
        except WrongStateException:
            return

        order = get_active_user_order(session=session, user_id=user.telegram_id)

        if user.state == UserStates.ORDERING.value:
            order = finish_order(session=session, order=order)
            await update_order_message(session=session, bot=bot, order=order)
            return

        elif user.state == UserStates.JOINED.value:
            reply = 'Закрыть заказ может только инициатор.'

        elif user.state == UserStates.REGISTERED.value:
            reply = 'У вас нет активных заказов.'

    await msg.reply(reply)


@dp.message_handler(content_types=[ContentType.TEXT])
async def process_text(msg: types.Message):
    with Session(engine) as session:
        user = get_user(session=session, telegram_id=msg.from_user.id)
        reply = 'Ничего не произошло...'

        try:
            await check_registration(msg=msg, user=user)
        except WrongStateException:
            return

        if user.state == UserStates.CREATED.value:
            kaspi = msg.text
            if validate_kaspi(kaspi):
                user = update_user(session=session, user=user, kaspi=kaspi, state=UserStates.REGISTERED.value)
                reply = f'Ваш номер каспи {user.kaspi}'
            else:
                reply = 'Введите номер телефона в международном формате или номер карточки без пробелов.'

        elif user.state in [UserStates.ORDERING.value, UserStates.JOINED.value]:
            await check_group(msg=msg)
            order = get_group_order(session=session, group_id=msg.chat.id)
            order = append_text_to_order(session=session, order=order, updated_by=user, text=f'\n{msg.text}')
            markup = get_order_markup(order=order)
            await update_order_message(session=session, bot=bot, order=order, inline_markup=markup)
            return

        elif user.state == UserStates.REGISTERED.value:
            reply = 'У вас нет активных заказов. Создайте новый, используя /order'

    await msg.reply(reply)


@dp.callback_query_handler(lambda c: c.data.startswith('join_order'))
async def join_order_callback(callback: types.CallbackQuery):
    with Session(engine) as session:
        user = get_user(session=session, telegram_id=callback.from_user.id)
        if not user or user.state == UserStates.CREATED.value:
            await callback.answer('Сначала зарегистрируйтесь!')
            return

        order_id = int(callback.data.split('#')[1])
        order = get_order(session=session, order_id=order_id)

        if order.user_id == user.telegram_id:
            await callback.answer('Вы не можете присоединиться к своему заказу!')
            return

        order = add_joined_user(session=session, order=order, user=user)
        markup = get_order_markup(order=order)
        update_user(session=session, user=user, state=UserStates.JOINED.value)

    await update_order_message(session=session, bot=bot, order=order, inline_markup=markup)
    await callback.answer('Вы успешно добавлены.')
