from os import getenv
import sys
import logging
import asyncio
from dotenv import load_dotenv

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


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! \n Welcome to the bot. This bot is designed to help you with your questions and provide you with the information you need. \n If you have any questions, please contact the developer: https://github.com/sadhiin.")

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    This handler receives messages with `/help` command
    """
    text = """
    '/start' - Start the bot \n'/help' - Get help\n'/chat' - Chat with the bot\n'/image' - Generate an image\n'/video' - Generate a video\n'/audio' - Generate an audio\n'/document' - Generate a document\n'/clear' - Clear the memory
    """
    await message.answer(text)

@dp.message(Command("clear"))
async def command_clear_handler(message: Message) -> None:
    pass

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



@dp.message(Command("chat"))
async def command_chat_handler(message: Message) -> None:
    """
    This handler receives messages with `/chat` command
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": [{"type": "text", "text": message.text}]}
            ]
        )

        response_text = escape_markdown_v2(str(response.choices[0].message.content))
        await message.answer(f"{response_text}", parse_mode=ParseMode.MARKDOWN_V2,)
    except Exception as e:
        await message.answer(f"Error: {e}")



async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
