import asyncio
import os
from urllib.parse import urljoin

from aiogram.utils import executor
from dotenv import load_dotenv
from aiogram.types import ContentType
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

load_dotenv()
ENV = os.getenv('ENV')
TOKEN = os.getenv('TOKEN')
APP_URL = os.getenv('APP_URL', '')

WEBHOOK_URL_PATH = 'webhook/' + TOKEN
WEBHOOK_URL = urljoin(APP_URL, WEBHOOK_URL_PATH)

bot = Bot(TOKEN)
dp = Dispatcher(bot)


def heroku_run():
    bot.delete_webhook()
    bot.set_webhook(WEBHOOK_URL)
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))


def local_run():
    bot.delete_webhook()
    executor.start_polling(dispatcher=dp)


if __name__ == '__main__':
    if ENV == 'HEROKU':
        heroku_run()
    else:
        local_run()
