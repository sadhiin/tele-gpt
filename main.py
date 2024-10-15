from os import getenv
import sys
import json
import requests
import logging
import asyncio
from dotenv import load_dotenv
import aiohttp
from cachetools import TTLCache
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from storage import SimpleStorage
import openai

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
MODEL = getenv("MODEL")

client = openai.OpenAI(api_key=getenv("OPENAI_API_KEY"))

dp = Dispatcher()
db = SimpleStorage()

# Create a shared session and cache
session = None
cache = TTLCache(maxsize=100, ttl=3600)  # Cache with 100 items, 1 hour TTL

def escape_markdown_v2(text: str) -> str:
    # List of characters that need to be escaped in MarkdownV2
    reserved_characters = [
        '.', '!', '(', ')', '*', '_', '[', ']', '~',
        '>', '#', '+', '-', '=', '|', '{', '}', '`'
    ]

    # Escape the special characters by replacing them with their escaped version
    for char in reserved_characters:
        text = text.replace(char, f'\\{char}')

    return text

async def make_request_through_openai(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant as a telegram bot. Your main goal is to help the user with their questions and provide them with the information they need."
        }
    ]
    messages.append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model=str(MODEL),
        messages=messages,
        response_format={ "type": "text" }
    )

    response_text = escape_markdown_v2(str(response.choices[0].message.content))
    return response_text

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session

async def make_request_through_rapid_api(text: str, assistant_message: str) -> str:
    url = "https://chatgpt-42.p.rapidapi.com/conversationllama3"

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant as a telegram bot. Your main goal is to help the user with their questions and provide them with the information they need."
            },
            {
                "role": "user",
                "content": f"{text}"
            }
        ],
        "web_access": True
    }

    headers = {
        "x-rapidapi-key": getenv("RAPID_API_KEY"),
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    session = await get_session()
    async with session.post(url=url, json=payload, headers=headers) as response:
        result = await response.json()

    return escape_markdown_v2(str(result['result']))

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! \nWelcome to the bot. This bot is designed to help you with your questions and provide you with the information you need. \n If you have any questions, please contact the developer: https://github.com/sadhiin.")


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    This handler receives messages with `/help` command
    """
    text = """
    '/start' - Start the bot \n'/help' - Get help\n'/chat' - Chat with the bot\n'/online' - Get information from the internet\n'/clear' - Clear the memory
    """
    await message.answer(text)


@dp.message(Command("chat"))
async def command_chat_handler(message: Message) -> None:
    """
    This handler receives messages with `/chat` command
    """
    try:
        user_text = str(message.text).strip("/chat")
        if user_text:
            logging.info(f"Message: {user_text}")

            # Check cache first
            cached_response = cache.get(user_text)
            if cached_response:
                response_text = cached_response
            else:
                response_text = await make_request_through_openai(user_text)
                cache[user_text] = response_text

            logging.info(f"Response: received from api, Saving the data")
            await db.add_message(message.from_user.id, user_text, response_text)
            await message.answer(f"{response_text}", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await message.answer("Oh 🙄, you didn't write anything. Please write your question.")
    except Exception as e:
        await message.answer(f"🥴 Error: {e}")

@dp.message(Command("online"))
async def command_online_handler(message: Message) -> None:
    """
    This handler receives messages with `/online` command
    """
    try:
        user_text = str(message.text).strip("/online")
        if user_text is not None and user_text != "":
            logging.info(f"Message: {user_text}")

            response_text = await make_request_through_openai(user_text)
            logging.info(f"Response: resived from api, Saving the data")

            await db.add_message(message.from_user.id, user_text, response_text)
            await message.answer(f"{response_text}", parse_mode=ParseMode.MARKDOWN_V2,)
        else:
            await message.answer(f"Oh 🙄, you didn't write anything. Please write your question.")
    except Exception as e:
        await message.answer(f"Error: {e}")

@dp.message(Command("clear"))
async def command_clear_handler(message: Message) -> None:
    """
    This handler receives messages with `/clear` command
    """
    try:
        logging.info(f"Clearing memory")
        await db.clear_messages(message.from_user.id)
        await message.answer(f"Memory cleared")
    except Exception as e:
        await message.answer(f"🥴Error: {e}")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Start the bot
    try:
        await dp.start_polling(bot)
    finally:
        # Close the aiohttp session when the bot stops
        if session:
            await session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
