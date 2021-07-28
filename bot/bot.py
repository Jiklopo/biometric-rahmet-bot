import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher(bot)
