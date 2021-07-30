from aiogram import Bot

from db.my_selectors.users import list_users
from db.tables import User


async def notify_users(*, bot: Bot, author: User, notification_text: str):
    users = list_users()
    for user in users:
        if user.telegram_id != author.telegram_id:
            await bot.send_message(user.telegram_id, notification_text)
