import datetime
import os
import requests
from borrowing.models import Borrowing
from celery import shared_task
from django.utils import timezone
from payment.stripe_helper import FINE_MULTIPLIER


OVERDUE_IMAGE_URL = "https://i.imgur.com/258kR4X.jpg"


def get_fine_price(borrowing):
    overdue_days = (
        timezone.localdate()
        - borrowing.expected_return_date
    ).days

    fine_price_in_cents = int(
        overdue_days
        * float(borrowing.book.daily)
        * FINE_MULTIPLIER
        * 100
    ) if overdue_days > 0 else 0

    return fine_price_in_cents / 100


@shared_task
def borrowing_books():
    borrowings = Borrowing.objects.all()
    nobody_borrowed = True
    for borrowing in borrowings:
        if borrowing.expected_return_date < timezone.localdate():
            additional_price = get_fine_price(borrowing)
            overdued_days = (
                datetime.date.today().day - borrowing.days_from_borrow
            )

            if (
                borrowing.user.telegram_notifications_enabled
                and borrowing.user.telegram_id
            ):
                url_for_user = (
                    f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
                    f"/sendPhoto?chat_id={borrowing.user.telegram_id}"
                    f"&photo={OVERDUE_IMAGE_URL}"
                    f"&caption=📕 You have an outdated borrowing: "
                    f"{borrowing.book.title} for {overdued_days}"
                    f" days. 💰You have to pay additional "
                    f"{additional_price}USD 🔗, please return the book"
                )
                requests.get(url_for_user)

            url_for_admin_group = (
                f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
                f"/sendPhoto?chat_id={os.getenv('ADMIN_GROUP')}"
                f"&photo={OVERDUE_IMAGE_URL}"
                f"&caption=📕 User {borrowing.user.email} "
                f"has borrowing overdue for book: {borrowing.book.title} "
                f"for {overdued_days}"
                f" days. He has to pay additional {additional_price}USD 🔗"
            )
            requests.get(url_for_admin_group)
            nobody_borrowed = False
    if nobody_borrowed:
        url_for_admin_group = (
            f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}"
            f"/sendMessage?chat_id={os.getenv('ADMIN_GROUP')}"
            f"&text=Nobody has overdue borrowings today"
        )
        requests.get(url_for_admin_group)

    return "Sent borrowing notifications"
