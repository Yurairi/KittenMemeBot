from config import BOT_TOKEN, START_TEXT
from meme_creator import get_cat_images, create_meme
import requests
import os
from aiogram.filters import CommandStart, Command
from aiogram.types import URLInputFile, Message, FSInputFile
from aiogram import Bot, types, Router
from typing import List, Any


router: Router = Router()
bot = Bot(token=BOT_TOKEN)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer_sticker(
        sticker="CAACAgIAAxkBAAMZZeEEBA9hgV8nuK-zIT1xbwGsSgoAAs0rAALEkbBIcYhgxom4IKM0BA"
    )
    await message.answer(text=START_TEXT)


@router.message(Command("get_cat"))
async def send_cat_photos(message: types.Message):
    image_urls: Any = await get_cat_images(count=10)
    for url in image_urls:
        response = requests.get(url)
        if response:
            image: URLInputFile = URLInputFile(url)
            await bot.send_photo(message.chat.id, image)
        else:
            await message.reply("Ошибка при загрузке изображения.")


def split_text_by_words(input_string):
    words: List[str] = input_string.split()
    half_length: int = len(input_string) // 2

    current_length: int = 0
    split_index: int = 0

    for i, word in enumerate(words):
        current_length += len(word) + 1
        if current_length >= half_length:
            split_index = i
            break
    if len(words) == 2:
        first_part = words[0]
        second_part = words[1]
    else:
        first_part = " ".join(words[: split_index + 1])
        second_part = " ".join(words[split_index + 1 :])

    return first_part, second_part


@router.message(Command("meme"))
async def create_and_send_meme(message: Message) -> None:
    text_args: str = message.text[5:]
    text_input: str = text_args if len(text_args) > 0 else "Прикрепи текст"

    text0, text1 = split_text_by_words(text_input)

    image_url: str = await get_cat_images(1)

    name: str = await create_meme(image_url[0], text0, text1)
    photo: FSInputFile = FSInputFile(name, "rb")

    if os.path.getsize(name) != 0:
        await message.answer(text="Твое изображение готово")
        await bot.send_photo(message.chat.id, photo)
        os.remove(name)
    else:
        await message.reply("Ошибка при создании мема.")
