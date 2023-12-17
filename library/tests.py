from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from library.models import Book


def sample_book(**params):
    # Create a sample book with optional parameters
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "H",  # Assuming "HARD" as the default cover choice
        "inventory": 10,
        "daily": 19.99,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class BookTests(TestCase):

    def test_create_book(self):
        book = sample_book()

        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Sample book")
        self.assertEqual(book.author, "Sample author")
        self.assertEqual(book.cover, "H")
        self.assertEqual(book.inventory, 10)
        self.assertEqual(book.daily, 19.99)


