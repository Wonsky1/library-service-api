import os
from dotenv import load_dotenv

from notifications.bot_utils import asyncio_run
from notifications.management.commands.start_bot import send_message


load_dotenv()


ADMIN_GROUP = (
    int(os.getenv("ADMIN_GROUP")) if os.getenv("ADMIN_GROUP") else None
)


async def _send_payment_notification(
    telegram_id: int, payment_info: dict
) -> None:
    await send_message(telegram_id, "payment")


async def _send_overdue_notification(
    telegram_id: int, overdue_info: dict
) -> None:
    await send_message(telegram_id, "overdue")
    await send_message(ADMIN_GROUP, "overdue")


async def _send_borrowing_notification(
    telegram_id: int, borrowing_info: dict
) -> None:
    await send_message(telegram_id, "borrowing")


def send_borrowing_notification(user: dict, borrowing_info: dict) -> None:
    asyncio_run(
        _send_borrowing_notification(user["telegram_id"], borrowing_info)
    )


def send_overdue_notification(
    users: dict,
) -> None:
    for user in users.values():
        asyncio_run(
            _send_overdue_notification(user["telegram_id"], user["overdues"])
        )


def send_payment_notification(user: dict, payment_info: dict) -> None:
    asyncio_run(_send_payment_notification(user["telegram_id"], payment_info))
