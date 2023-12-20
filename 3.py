import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiohttp import web
import json


API_TOKEN = '6646889634:AAEU7beduw2Lzrpk_-sQdJ0iPIDyCk5Ag4E'  # Replace with your Telegram bot token
WEBHOOK_URL_PATH = '/advertise/create'
YOUR_CHAT_ID = 5564404963  # Replace with your Telegram chat ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def handle_post(request):
    # Read and parse the JSON data from the request body
    data = await request.json()

    # Extract data from the JSON
    photos = data.get('photos', [])
    description = data.get('description', '')
    title = data.get('title', '')
    links = data.get('links', [])

    # Generate and send messages with photos
    await generate_and_send_messages(photos, description, title, links, YOUR_CHAT_ID)

    return web.json_response({'status': 'success'})

async def generate_and_send_messages(photos, description, title, links, chat_id):
    # Generate HTML-formatted message
    for photo_link in photos:
        message_text = f"<a href='{photo_link}'>&#8205;</a>\n" \
                       f"<b>{title}</b>\n\n" \
                       f"<i>{description}</i>\n\n"

        for link in links:
            message_text += f"  <a href='{link['link']}'><b>{link['title']}</b></a>"

        # Send each message with a photo
        await bot.send_message(chat_id=chat_id, text=message_text, parse_mode=ParseMode.HTML)

async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_CHAT_ID, text='Bot has been started and is ready to receive requests.')

if __name__ == '__main__':
    app = web.Application()
    app.router.add_post(WEBHOOK_URL_PATH, handle_post)

    # Start the web application
    web.run_app(app, port=3000)
    # Note: The line below starts polling, it might interfere with the web application. Consider removing it or running it separately.
    executor.start_polling(dp, skip_updates=True)
