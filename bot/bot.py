import os
from dotenv import load_dotenv

from aiogram.types import ContentType
from aiogram import Bot, Dispatcher, types

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=[ContentType.TEXT])
async def echo(message: types.Message):
    await message.reply(message.text)
