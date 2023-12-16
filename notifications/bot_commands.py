import asyncio

from notifications.management.commands.start_bot import send_message


def send_notification(
    telegram_id: int,
    payment: dict = None,
    overdue: dict = None,
    borrowing: dict = None,
):
    text_message = ""
    if payment:
        text_message = "payment"
    if overdue:
        text_message = "overdue"
    if borrowing:
        text_message = "borrowing"

    asyncio.run(send_message(telegram_id, text_message))
