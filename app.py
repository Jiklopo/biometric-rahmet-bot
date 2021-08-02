import os

from dotenv import load_dotenv
from urllib.parse import urljoin
from aiogram.utils import executor

from bot.bot import bot, dp

load_dotenv()
ENV = os.getenv('ENV')
TOKEN = os.getenv('TOKEN')
APP_URL = os.getenv('APP_URL', '')

WEBHOOK_PATH = '/webhook/' + TOKEN
WEBHOOK_URL = urljoin(APP_URL, WEBHOOK_PATH)


async def heroku_on_startup(dp):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)


async def heroku_on_shutdown(dp):
    await bot.delete_webhook()


def heroku_run():
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=heroku_on_startup,
        on_shutdown=heroku_on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=os.getenv('PORT'),
    )


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
