from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from library.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True, default=None)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    @property
    def days_from_borrow(self):
        if self.actual_return_date is not None:
            date = self.actual_return_date - self.borrow_date
            return date.days
        date = timezone.now().date() - self.borrow_date
        return date.days

    @property
    def is_active(self):
        if self.actual_return_date is None:
            return True
        return False

    @staticmethod
    def validate_book_return_time(
            expected_date,
            book,
            error_to_raise
    ):
        today = timezone.now().date()
        book_inventory = book.inventory
        if expected_date <= today:
            raise error_to_raise(
                f"Expected return date must be greater than {today}"
            )
        if expected_date > today + timedelta(days=14):
            raise error_to_raise(f"Expected return date must be less than {timedelta(days=14).days}")
        if book_inventory <= 0:
            raise error_to_raise(
                "You can't borrow the book, current book inventory must be "
                f"greater than. Current book inventory: {book_inventory}"
            )

    def clean(self):
        Borrowing.validate_book_return_time(
            self.expected_return_date,
            self.book,
            ValidationError,
        )

    def __str__(self):
        return f"{self.book.title}, Taken {self.borrow_date}"
