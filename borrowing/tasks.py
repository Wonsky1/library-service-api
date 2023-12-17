import os

import requests

from borrowing.models import Borrowing
from celery import shared_task
from django.utils import timezone

from payment.stripe_helper import count_fine_price


@shared_task
def borrowing_books():
    borrowings = Borrowing.objects.all()
    for borrowing in borrowings:
        if (
            borrowing.expected_return_date < timezone.localdate()
            and borrowing.user.telegram_notifications_enabled
            and borrowing.user.telegram_id
        ):
            additional_price = count_fine_price(borrowing) * 100
            url = (f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
                   f"/sendMessage?chat_id={borrowing.user.telegram_id}"
                   f"&text=You have an outdated borrowing: {borrowing.book.title}. "
                   f"You have to pay additional {additional_price}$, please return the book")
            requests.get(url)
    return "Send borrowing notifications"
