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

    @staticmethod
    def validate_book_return_time(
            expected_date,
            actual_return_date,
            book,
            error_to_raise
    ):
        time_now = timezone.now().date()
        book_inventory = book.inventory
        if expected_date <= time_now:
            raise error_to_raise(
                f"Expected return date must be greater than {time_now}"
            )
        if actual_return_date:
            if actual_return_date <= time_now:
                raise error_to_raise(
                    f"Actual return date must be greater than {time_now}"
                )
        if book_inventory <= 0:
            raise error_to_raise(
                "You can't borrow the book, current book inventory must be "
                f"greater than. Current book inventory: {book_inventory}"
            )

    def clean(self):
        Borrowing.validate_book_return_time(
            self.expected_return_date,
            self.actual_return_date,
            self.book,
            ValidationError,
        )

    def __str__(self):
        return f"{self.book.title}, Taken {self.borrow_date}"
