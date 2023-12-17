# Create your tasks here

from borrowing.models import Borrowing
from user.models import User

from celery import shared_task

from django.utils import timezone


@shared_task
def count():
    return User.objects.count()
