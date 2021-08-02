import os
from dotenv import load_dotenv
from urllib.parse import urljoin
from aiogram.utils import executor
from aiohttp import web
from aiogram.dispatcher.webhook import get_new_configured_app

from bot.bot import bot, dp

load_dotenv()
ENV = os.getenv('ENV')
TOKEN = os.getenv('TOKEN')
APP_URL = os.getenv('APP_URL', '')

WEBHOOK_URL_PATH = '/webhook/' + TOKEN
WEBHOOK_URL = urljoin(APP_URL, WEBHOOK_URL_PATH)


def heroku_run():
    bot.delete_webhook()
    bot.set_webhook(WEBHOOK_URL)
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))


def local_run():
    bot.delete_webhook()
    print('Starting server...')
    executor.start_polling(
        dispatcher=dp,
        on_startup=print('Server Started.')
    )


if __name__ == '__main__':
    if ENV == 'HEROKU':
        heroku_run()
    elif ENV == 'DEV':
        local_run()
