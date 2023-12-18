import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def book_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/book/", filename)


class Book(models.Model):
    COVER_CHOICES = [
        ("H", "HARD"),
        ("S", "SOFT"),
    ]
    title = models.CharField(max_length=128)
    author = models.CharField(max_length=150)
    cover = models.CharField(max_length=1, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=book_image_file_path
    )

    @staticmethod
    def validate_cover_choice(cover, error_to_raise):
        valid_cover_choices = [choice[0] for choice in Book.COVER_CHOICES]
        if cover not in valid_cover_choices:
            raise error_to_raise(
                {
                    "cover": f"Cover must be one of the following: "
                    f"{valid_cover_choices[0]} "
                    f"or {valid_cover_choices[1]}"
                }
            )

    def clean(self):
        Book.validate_cover_choice(self.cover, ValidationError)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()

        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title
