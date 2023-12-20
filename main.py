
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiohttp import web


API_TOKEN = '6646889634:AAEU7beduw2Lzrpk_-sQdJ0iPIDyCk5Ag4E'  # Replace with your Telegram bot token
WEBHOOK_URL_PATH = '/advertise/create'
YOUR_CHAT_ID = 5564404963  # Replace with your Telegram chat ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Directory to save uploaded files
UPLOADS_DIR = 'images'
os.makedirs(UPLOADS_DIR, exist_ok=True)


async def handle_post(request):
    data = await request.post()

    # Extract data from the form-data
    photos = data.getall('photos')
    description = data.get('description', '')
    title = data.get('title', '')

    # Extract links from the form-data
    links = []
    i = 0
    while f'links[{i}][title]' in data:
        link_title = data.get(f'links[{i}][title]', '')
        link_url = data.get(f'links[{i}][link]', '')
        links.append({'title': link_title, 'link': link_url})
        i += 1

    # Process photos (upload and get links)
    uploaded_photo_links = []
    for photo in photos:
        # Save photo locally and get the link
        uploaded_photo_link = await save_photo(photo)
        uploaded_photo_links.append(uploaded_photo_link)

    # Combine all data
    result_data = {
        'photos': uploaded_photo_links,
        'description': description,
        'title': title,
        'links': links
    }

    # Generate Markdown message
    message_text = generate_html_message(result_data)

    # Send the result to the Telegram bot
    # await bot.send_message(chat_id=YOUR_CHAT_ID, text=message_text, parse_mode=ParseMode.MARKDOWN)
    # Send the result to the Telegram bot with ParseMode.HTML
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=message_text, parse_mode=ParseMode.HTML)

    return web.json_response({'status': 'success'})


async def save_photo(photo):
    # Save photo locally and return the link
    file_path = os.path.join(UPLOADS_DIR, photo.filename)
    with open(file_path, 'wb') as file:
        file.write(photo.file.read())
    uploaded_photo_link = f'file://{file_path}'  # Local file link
    return uploaded_photo_link


def generate_html_message(data):
    # Generate HTML-formatted message
    message = "<b>Photos:</b>\n"
    for photo_link in data['photos']:
        message += f"  - <a href='{photo_link}'>Photo</a>\n"

    message += f"<b> {data['title']}</b>\n\n" \
               f"<i>{data['description']}</i> \n\n"

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
