import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiohttp import web
import json
import asyncio

API_TOKEN = '6646889634:AAEU7beduw2Lzrpk_-sQdJ0iPIDyCk5Ag4E'  # Replace with your Telegram bot token
WEBHOOK_URL_PATH = '/advertise/create'
YOUR_CHAT_ID = 5564404963  # Replace with your Telegram chat ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def handle_post(request):
    try:
        # Read and parse the JSON data from the request body
        data = await request.json()
        print("Received data:", data)

        # Extract data from the JSON
        media = data.get('media', []) or []
        description = data.get('description', '')
        title = data.get('title', '')
        links = data.get('links', []) or []

        # Generate and send messages with media
        await generate_and_send_messages(media, description, title, links, YOUR_CHAT_ID)

        return web.json_response({'status': 'success'})
    except Exception as e:
        print("Error handling the request:", e)
        return web.json_response({'status': 'error'})

async def generate_and_send_messages(photos, videos, description, title, links, chat_id):
    try:
        # Generate HTML-formatted message
        message_text = f"<b>{title}</b>\n\n" \
                       f"<i>{description}</i>\n\n"

        # Create a list to store media objects
        media_group = []

        # Ensure photos and videos are lists
        if not isinstance(photos, list):
            photos = [photos]
        if not isinstance(videos, list):
            videos = [videos]

        # Create a caption for all photos and videos
        media_caption = f"<b>{title}</b>\n\n" \
                        f"<i>{description}</i>\n\n"

        # Add each photo to the media group with the common caption
        for index, photo_link in enumerate(photos):
            for link in links:
                media_caption += f"<a href='{link['link']}'><b>{link['title']}</b></a>   "

            media_group.append(types.InputMediaPhoto(media=photo_link, caption=media_caption, parse_mode=ParseMode.HTML))

        # Add each video to the media group
        for video_link in videos:
            media_group.append(types.InputMediaVideo(media=video_link, caption=media_caption, parse_mode=ParseMode.HTML))

        if media_group:  # Check if there are any media objects
            # Send the message with the photo album or video
            await bot.send_media_group(chat_id=chat_id, media=media_group)
        else:
            # Send a text message if there are no photos or videos
            await bot.send_message(chat_id=chat_id, text=message_text, parse_mode=ParseMode.HTML)

    except Exception as e:
        print("Error in generate_and_send_messages:", e)


async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_CHAT_ID, text='Bot has been started and is ready to receive requests.')

if __name__ == '__main__':
    app = web.Application()
    app.router.add_post(WEBHOOK_URL_PATH, handle_post)

    # Start the web application in a separate task
    asyncio.create_task(web.run_app(app, port=3000))

    # Start polling separately
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
