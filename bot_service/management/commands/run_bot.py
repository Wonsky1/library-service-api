import asyncio
import os

from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv


load_dotenv()


bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def send_message(telegram_ids: list, message: str):

    for telegram_id in telegram_ids:
        await bot.send_message(chat_id=telegram_id, text=message, parse_mode=ParseMode.MARKDOWN)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.first_name}!")


async def main() -> None:
    dp.message.register(my_books_cmd, Command("my_books"))

    # router = Router()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
