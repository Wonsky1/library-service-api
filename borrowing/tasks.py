# Create your tasks here

from borrowing.models import Borrowing
from user.models import User

from celery import shared_task

from django.utils import timezone

@shared_task
def count():
    return User.objects.count()

    # users = User.objects.all()
    # total = 0
    # for user in users:
    #     if user.plane_date_return < timezone.now():
    #         total += 1
    # return total







from celery import Celery

app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

@app.task
def add(x, y):
    return x + y