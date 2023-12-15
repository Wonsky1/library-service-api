import os
import uuid

from django.db import models
from django.utils.text import slugify


def book_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}.{extension}"

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
    image = models.ImageField(null=True, upload_to=book_image_file_path)

    def __str__(self):
        return self.title
