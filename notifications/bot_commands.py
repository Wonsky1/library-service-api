import asyncio
import os
from typing import List
from dotenv import load_dotenv

from notifications.management.commands.start_bot import send_message


load_dotenv()


ADMIN_GROUP = int(os.getenv("ADMIN_GROUP")) if os.getenv("ADMIN_GROUP") else None


def perform_create_async(serializer):
    asyncio.create_task(send_borrowing_notification_async(-4050199237, {}))
    asyncio.create_task(send_payment_notification_async(-4050199237, {}))
    asyncio.create_task(send_overdue_notification_async({
        "user1": {
            "telegram_id": -4050199237,
            "overdues": {}
        }
    }))


async def _send_payment_notification(
    telegram_id: int,
    payment_info: dict
) -> None:
    await send_message(telegram_id, "payment")


async def _send_overdue_notification(
    telegram_id: int,
    overdue_info: dict
) -> None:
    await send_message(telegram_id, "overdue")
    await send_message(ADMIN_GROUP, "overdue")




async def _send_borrowing_notification(
    telegram_id: int,
    borrowing_info: dict
) -> None:
    await send_message(telegram_id, "borrowing")


def send_borrowing_notification(
    user: dict,
    borrowing_info: dict
) -> None:
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    asyncio.create_task(_send_borrowing_notification(user["telegram_id"], borrowing_info))
    # loop.close()


def send_overdue_notification(
    users: dict,
) -> None:
    loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    for user in users.values():
        asyncio.create_task(_send_overdue_notification(user["telegram_id"], user["overdues"]))


def send_payment_notification(
    user: dict,
    payment_info: dict
) -> None:
    # asyncio.set_event_loop(loop)
    loop = asyncio.new_event_loop()

    # Установіть цей цикл як поточний
    asyncio.set_event_loop(loop)

    try:
        # Додайте ваші завдання в цикл подій
        task1 = loop.create_task(_send_overdue_notification(user["telegram_id"], payment_info))

        loop.run_until_complete(asyncio.gather(task1))
    finally:
        # Закрийте цикл подій
        loop.close()
    # asyncio.create_task(_send_overdue_notification(user["telegram_id"], payment_info))
