from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from library.models import Book


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

    @staticmethod
    def validate_book_return_time(
            expected_date,
            actual_return_date,
            error_to_raise
    ):
        time_now = timezone.now().date()
        if expected_date <= time_now:
            raise error_to_raise(
                f"Expected return date must be greater than {time_now}"
            )
        if actual_return_date <= time_now:
            raise error_to_raise(
                f"Actual return date must be greater than {time_now}"
            )

    def clean(self):
        Borrowing.validate_book_return_time(
            self.expected_return_date,
            self.actual_return_date,
            ValidationError,
        )
