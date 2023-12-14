from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowing.models import Borrowing
from library.serializers import BookSerializer
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "books",
            "user"
        )

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_book_return_time(
            attrs["expected_return_date"],
            attrs["actual_return_date"],
            ValidationError
        )
        return data


class BorrowingListSerializer(BorrowingSerializer):
    books = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="title"
    )
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "books",
            "user"
        )


class UserShowsSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name")


class BorrowingDetailSerializer(BorrowingSerializer):
    books = BookSerializer(many=True, read_only=True)
    user = UserShowsSerializer(many=False, read_only=True)
