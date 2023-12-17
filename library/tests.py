import os
import tempfile
import datetime
from decimal import Decimal

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db.utils import DataError

from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Book

BOOK_URL = reverse("library:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "cover": "H",
        "inventory": 10,
        "daily": Decimal("19.99"),
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
                    "daily": Decimal("19.99"),
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


class UnauthenticatedBookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.book = sample_book()

    def test_list_of_book_allowed_without_auth(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_auth_required(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "H",
            "inventory": 10,
            "daily": Decimal("19.99"),
        }

        response = self.client.post(BOOK_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_image_to_book_forbidden(self):
        url = image_upload_url(self.book.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "122334test_password",
        )
        self.client.force_authenticate(self.user)

        self.book = sample_book()

    def test_list_of_book_allowed_with_auth(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "H",
            "inventory": 10,
            "daily": Decimal("19.99"),
        }

        response = self.client.post(BOOK_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_to_book_forbidden(self):
        url = image_upload_url(self.book.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@admin.com",
            "122334test_password",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "cover": "H",
            "inventory": 10,
            "daily": Decimal("19.99"),
        }

        response = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_create_book_with_valid_cover(self):
        book = sample_book(cover="S")
        self.assertIsNotNone(book)
        self.assertEqual(book.title, "Sample book")
        self.assertEqual(book.author, "Sample author")
        self.assertEqual(book.cover, "S")
        self.assertEqual(book.inventory, 10)
        self.assertEqual(book.daily, Decimal("19.99"))

    def test_create_book_with_invalid_cover(self):
        with self.assertRaises(DataError):
            sample_book(cover="HZ")

        self.assertRaises(DataError)

    def test_retrieve_book_with_borrowings(self):
        book = sample_book()
        Borrowing.objects.create(
            expected_return_date=(
                datetime.date.today()
                + datetime.timedelta(days=13)
            ),
            book=book,
            user=self.user,
        )

        url = detail_url(book.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("borrowings", response.data)
        self.assertEqual(len(response.data["borrowings"]), 1)
        self.assertIn(str(self.user.email), response.data["borrowings"])
