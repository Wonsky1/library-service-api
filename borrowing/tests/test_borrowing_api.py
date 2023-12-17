from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminDetailSerializer,
)
from library.models import Book

BORROWING_URL = reverse("borrowing:borrowing-list")
VALID_DATE = timezone.now().date() + timedelta(days=2)


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Steven King",
        "cover": "H",
        "inventory": 5,
        "daily": 3
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    book = sample_book()
    defaults = {
        "expected_return_date": VALID_DATE,
        "book": book,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


VALID_PAYLOAD = {
    "expected_return_date": VALID_DATE,
    "book": sample_book(),
}


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_borrowing_list_auth_required(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_create_auth_required(self):
        payload = VALID_PAYLOAD
        response = self.client.post(BORROWING_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_detail_auth_required(self):
        user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        borrowing = sample_borrowing(user=user)
        response = self.client.get(detail_url(borrowing.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_update_delete_auth_required(self):
        user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        payload = VALID_PAYLOAD
        borrowing = sample_borrowing(user=user)

        response = self.client.patch(detail_url(borrowing.id), payload)
        response2 = self.client.put(detail_url(borrowing.id), payload)
        response3 = self.client.delete(detail_url(borrowing.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response3.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_borrowing_list(self):
        sample_borrowing(user=self.user)

        response = self.client.get(BORROWING_URL)

        borrowing = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowing, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_borrowing_list_user_see_yourself_borrowings(self):
        borrowing1 = sample_borrowing(user=self.user)
        user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass1",
        )
        borrowing2 = sample_borrowing(user=user)

        response = self.client.get(BORROWING_URL)
        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        self.assertIn(serializer1.data, response.data["results"])
        self.assertNotIn(serializer2.data, response.data["results"])

    def test_filter_borrowing_by_is_active(self):
        borrowing1 = sample_borrowing(user=self.user)
        borrowing2 = sample_borrowing(
            actual_return_date=timezone.now().date(),
            user=self.user
        )
        borrowing3 = sample_borrowing(user=self.user)

        response = self.client.get(
            BORROWING_URL, {"is_active": "True"}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertIn(serializer1.data, response.data["results"])
        self.assertIn(serializer3.data, response.data["results"])
        self.assertNotIn(serializer2.data, response.data["results"])

    def test_filter_borrowing_by_user_id_not_working(self):
        user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass1",
        )

        borrowing1 = sample_borrowing(user=self.user)
        sample_borrowing(user=user)

        response = self.client.get(
            BORROWING_URL, {"user_id": user.id}
        )

        serializer1 = BorrowingListSerializer(borrowing1)

        self.assertIn(serializer1.data, response.data["results"])

    def test_borrowing_retrieve(self):
        borrowing = sample_borrowing(user=self.user)

        url = detail_url(borrowing.id)
        response = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_borrowing(self):
        book = sample_book()
        payload = {
            "expected_return_date": VALID_DATE,
            "book": book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        response2 = self.client.get(BORROWING_URL)

        borrowing = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowing, many=True)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data["results"], serializer.data)

    def test_create_borrowing_with_invalid_negative_expected_date(self):
        yesterday = timezone.now().date() - timedelta(days=1)
        book = sample_book()
        payload = {
            "expected_return_date": yesterday,
            "book": book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        borrowings = Borrowing.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(borrowings, 0)

    def test_create_borrowing_with_invalid_too_big_expected_date(self):
        book = sample_book()
        big_date = timezone.now().date() + timedelta(days=15)
        payload = {
            "expected_return_date": big_date,
            "book": book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        borrowings = Borrowing.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(borrowings, 0)

    def test_create_borrowing_with_invalid_zero_inventory_books(self):
        book = sample_book(inventory=0)
        payload = {
            "expected_return_date": VALID_DATE,
            "book": book.id,
        }
        response = self.client.post(BORROWING_URL, payload)
        borrowings = Borrowing.objects.count()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(borrowings, 0)

    def test_borrowing_update_delete_authorized_forbidden(self):
        payload = VALID_PAYLOAD
        borrowing = sample_borrowing(user=self.user)
        response = self.client.patch(detail_url(borrowing.id), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response2 = self.client.put(detail_url(borrowing.id), payload)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        response3 = self.client.delete(detail_url(borrowing.id))
        self.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_borrowing_admin_list(self):
        sample_borrowing(user=self.user)

        response = self.client.get(BORROWING_URL)

        borrowing = Borrowing.objects.all()
        serializer = BorrowingAdminListSerializer(borrowing, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_borrowing_list_admin_see_all_borrowings(self):
        borrowing_admin = sample_borrowing(user=self.user)
        user = get_user_model().objects.create_user(
            "test@test.com",
            "userpass",
        )
        borrowing_user = sample_borrowing(user=user)

        response = self.client.get(BORROWING_URL)
        serializer1 = BorrowingAdminListSerializer(borrowing_admin)
        serializer2 = BorrowingAdminListSerializer(borrowing_user)

        self.assertIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])

    def test_borrowing_admin_retrieve(self):
        borrowing = sample_borrowing(user=self.user)

        url = detail_url(borrowing.id)
        response = self.client.get(url)

        serializer = BorrowingAdminDetailSerializer(borrowing)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_borrowing_admin_update(self):
        book = sample_book(title="TEST")
        payload = {
            "expected_return_date": VALID_DATE,
            "book": book.id,
        }
        borrowing = sample_borrowing(user=self.user)
        url = detail_url(borrowing.id)
        response1 = self.client.put(url, payload)
        response11 = self.client.patch(url, payload)
        response2 = self.client.get(BORROWING_URL)

        borrowing = Borrowing.objects.all()
        serializer = BorrowingAdminListSerializer(borrowing, many=True)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response11.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["results"], serializer.data)

    def test_borrowing_admin_delete(self):
        borrowing = sample_borrowing(user=self.user)
        url = detail_url(borrowing.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        borrowings = Borrowing.objects.count()
        self.assertEqual(borrowings, 0)
