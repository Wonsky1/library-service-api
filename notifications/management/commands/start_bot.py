import asyncio
import os

from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from django.core.management import BaseCommand
from dotenv import load_dotenv

from notifications.bot_helper import obtain_token, check_user, connected_user_with_telegram

load_dotenv()


bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def send_message(telegram_ids: list, message: str):

    for telegram_id in telegram_ids:
        await bot.send_message(chat_id=telegram_id, text=message, parse_mode=ParseMode.MARKDOWN)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    parameter = obtain_token(message.text)
    if parameter:
        user = await check_user(parameter)
        if user:
            await message.answer(f"Hello, {user}!")
            result_message = await connected_user_with_telegram(user, message.from_user.id)

            await message.answer(result_message)


    else:
        await message.answer(f"Not found user")


async def main() -> None:
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        asyncio.run(main())
