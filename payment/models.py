from django.contrib.auth import get_user_model
from django.db import models

from borrowing.models import Borrowing
from user.models import User


class Payment(models.Model):
    # STATUS_CHOICES = {
    #     "PENDING": "Pending",
    #     "PAID": "Paid",
    # }
    #
    # TYPE_CHOICES = {
    #     "PAYMENT": "Payment",
    #     "FINE": "Fine"
    # }
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ]

    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine"),
    ]

    status = models.CharField(max_length=63, choices=STATUS_CHOICES)
    type = models.CharField(max_length=63, choices=TYPE_CHOICES)
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=127, unique=True)
    money_to_pay = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )
    user = models.ForeignKey(
        User,
        related_name="payments",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Payment #{self.id} - {self.status} by {self.user.email}"
