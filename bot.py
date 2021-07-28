import os
from urllib.parse import urljoin

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

TOKEN = os.getenv('TOKEN', '')  # Press "Reveal Config Vars" in settings tab on Heroku and set TOKEN variable
PROJECT_NAME = os.getenv('PROJECT_NAME', 'aiogram-example')  # Set it as you've set TOKEN env var

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com/'  # Enter here your link from Heroku project settings
WEBHOOK_URL_PATH = '/webhook/' + TOKEN
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)

# Inline keyboard initialization with one refresh button
inline_keyboard = types.InlineKeyboardMarkup()
random_button = types.InlineKeyboardButton('Получить случайную цитату', callback_data='refresh')
inline_keyboard.add(random_button)

bot = Bot(TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(func=lambda cb: True)
async def start(message: types.Message):
    await message.reply(message.text)


async def on_startup(app):
    """Simple hook for aiohttp application which manages webhook"""
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == '__main__':
    # Create aiohttp.web.Application with configured route for webhook path
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))  # Heroku stores port you have to listen in your app
