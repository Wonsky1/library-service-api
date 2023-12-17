import os

import requests

from borrowing.models import Borrowing
from celery import shared_task
from django.utils import timezone


@shared_task
def borrowing_books():
    borrowings = Borrowing.objects.all()
    for borrowing in borrowings:
        if borrowing.expected_return_date < timezone.localdate() and borrowing.user.telegram_notifications_enabled:
            url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage?chat_id={borrowing.user.telegram_id}&text=You have an outdated borrowing: {borrowing.book.title}, please return the book"
            requests.get(url)
    return "Send borrowing notifications"
