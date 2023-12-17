from borrowing.models import Borrowing
from celery import shared_task
from django.utils import timezone
from borrowing.serializers import TaskSerializer
from notifications.bot_commands import send_overdue_notification


@shared_task
def borrowing_books():
    borrowings = Borrowing.objects.all()
    users = {}
    for borrowing in borrowings:
        if borrowing.expected_return_date < timezone.localdate() and borrowing.user.telegram_notifications_enabled:
            borrowing_serializer = TaskSerializer(borrowing)
            users[borrowing.user.telegram_id] = borrowing_serializer.data
    # return users
    send_overdue_notification(users)
