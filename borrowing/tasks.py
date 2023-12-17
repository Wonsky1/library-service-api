import os

import requests

from borrowing.models import Borrowing
from celery import shared_task
from django.utils import timezone

from payment.stripe_helper import count_fine_price


@shared_task
def borrowing_books():
    borrowings = Borrowing.objects.all()
    anyone_has_borrowed = False
    for borrowing in borrowings:
        if (
            borrowing.expected_return_date < timezone.localdate()
            and borrowing.user.telegram_notifications_enabled
            and borrowing.user.telegram_id
        ):
            additional_price = count_fine_price(borrowing) * 100
            url_for_user = (f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
                   f"/sendMessage?chat_id={borrowing.user.telegram_id}"
                   f"&text=You have an outdated borrowing: {borrowing.book.title}. "
                   f"You have to pay additional {additional_price}$, please return the book")
            requests.get(url_for_user)
            url_for_admin_group = (f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
                   f"/sendMessage?chat_id={os.getenv('ADMIN_GROUP')}"
                   f"&text=User {borrowing.user.email} has borrowing for book: {borrowing.book.title}. "
                   f"He has to pay additional {additional_price}$")
            requests.get(url_for_admin_group)
            anyone_has_borrowed = True
    if anyone_has_borrowed:
        url_for_admin_group = (f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
                               f"/sendMessage?chat_id={os.getenv('ADMIN_GROUP')}"
                               f"&text=Nobody has overdue borrowings")
        requests.get(url_for_admin_group)

    return "Send borrowing notifications"
