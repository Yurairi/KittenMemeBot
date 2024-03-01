import requests
from config import *
import asyncio
from typing import List, Tuple, Any
import random
import io
import os
from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession, ClientError
from aiogram import Dispatcher
from handlers import router, bot


async def get_cat_images(count: int = 10) -> Any:
    params: dict = {
        'limit': count
    }

    try:
        async with ClientSession() as session:
            async with session.get(API_URL, params=params) as response:
                response.raise_for_status()
                data: list = await response.json()
                image_urls: List[str] = [cat['url'] for cat in data]
                return image_urls
    except ClientError as e:
        print(f"Error fetching cat images: {e}")
        return []


async def create_meme(image_url: str, text0: str, text1: str) -> Any:
    try:
        response: Any = requests.get(image_url)
        image_data = io.BytesIO(response.content)
        image = Image.open(image_data)

        draw: ImageDraw = ImageDraw.Draw(image)

        font_path: str = os.path.join(os.getcwd(), "arial.ttf")

        font: ImageFont = ImageFont.truetype(font_path, size=40)

        text0_bbox = draw.textbbox((0, 0), text0, font=font)
        text0_width, text0_height = text0_bbox[2] - text0_bbox[0], text0_bbox[3] - text0_bbox[1]

        text1_bbox = draw.textbbox((0, 0), text1, font=font)
        text1_width, text1_height = text1_bbox[2] - text1_bbox[0], text1_bbox[3] - text1_bbox[1]

        text0_position: Tuple[int, int] = ((image.width - text0_width) // 3, 0)
        text1_position: Tuple[int, int] = ((image.width - text1_width) // 3, image.height - text1_height - 16)

        draw.text(text0_position, text0, font=font, fill='white')
        draw.text(text1_position, text1, font=font, fill='white')

        image = image.convert("RGB")
        random_filename: str = str(random.randint(1, 10000))
        image.save(os.path.join(os.getcwd(),  f"{random_filename}.jpeg"), format='JPEG', encoding='utf-8')

        return f"{random_filename}.jpeg"

    except Exception as e:
        print(f"Error creating custom meme: {e}")
        return None


async def download_image(url: str) -> bytes:
    try:
        async with ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Error')
