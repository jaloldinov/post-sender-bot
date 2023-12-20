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

    # Combine all data
    result_data = {
        'photos': photos,
        'description': description,
        'title': title,
        'links': links
    }

    # Generate HTML message
    message_text = generate_html_message(result_data)

    # Send the result to the Telegram bot
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=message_text, parse_mode=ParseMode.HTML)

    return web.json_response({'status': 'success'})

def generate_html_message(data):
    # Generate HTML-formatted message
    message = "<b>Photos:</b>\n"
    for photo_link in data['photos']:
        message += f"  - <a href='{photo_link}'>Photo</a>\n"

    message += f"<b>{data['title']}</b>\n\n" \
               f"<i>{data['description']}</i>\n\n"

    for link in data['links']:
        message += f"  <a href='{link['link']}'><b>{link['title']}</b></a>"

    return message

async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_CHAT_ID, text='Bot has been started and is ready to receive requests.')

if __name__ == '__main__':
    app = web.Application()
    app.router.add_post(WEBHOOK_URL_PATH, handle_post)

    # Start the web application
    web.run_app(app, port=3000)
    executor.start_polling(dp, skip_updates=True)