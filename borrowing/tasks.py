from borrowing.models import Borrowing
from celery import shared_task
from django.utils import timezone

@shared_task
def count():
    borrowings = Borrowing.objects.all()
    total = 0
    today = timezone.localdate()
    for borrowing in borrowings:
        if borrowing.expected_return_date.today() < today:
            total += 1
    return total

