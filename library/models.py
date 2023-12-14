from django.conf import settings
from django.db import models


class Book(models.Model):
    COVER_CHOICES = {
        "H": "HARD",
        "S": "SOFT"
    }
    title = models.CharField(max_length=128)
    author = models.CharField(max_length=150)
    cover = models.CharField(max_length=1, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily = models.DecimalField()


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    books = models.ManyToManyField(Book, blank=True, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
