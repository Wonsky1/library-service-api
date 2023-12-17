import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from library.models import Book

BOOK_URL = reverse("library:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "H",
        "inventory": 10,
        "daily": 19.99,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def image_upload_url(book_id):
    return reverse("library:book-upload-image", args=[book_id])


def detail_url(book_id):
    return reverse("library:book-detail", args=[book_id])


class BookImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)

        self.book = sample_book()

    def tearDown(self):
        self.book.image.delete()

    def test_create_book(self):
        self.assertIsNotNone(self.book)
        self.assertEqual(self.book.title, "Sample book")
        self.assertEqual(self.book.author, "Sample author")
        self.assertEqual(self.book.cover, "H")
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.daily, 19.99)

    def test_upload_image_to_book(self):
        url = image_upload_url(self.book.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.book.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.book.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_book_list(self):
        url = BOOK_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Test book",
                    "author": "Test author",
                    "cover": "H",
                    "inventory": 10,
                    "daily": 19.99,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(title="Test book")
        self.assertIsNotNone(book.image)

    def test_image_url_is_shown_on_book_detail(self):
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.book.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_book_list(self):
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(BOOK_URL)

        self.assertIn("image", res.data[0].keys())
