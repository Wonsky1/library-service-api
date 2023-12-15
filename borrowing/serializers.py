from django.contrib.auth import get_user_model
from django.db import transaction
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
            "book",
            "days_from_borrow",
            "is_active",
        )

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_book_return_time(
            attrs["expected_return_date"],
            attrs["book"],
            ValidationError
        )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        return borrowing

    @transaction.atomic()
    def update(self, instance, validated_data):
        returned = instance.actual_return_date
        instance.expected_return_date = validated_data.get(
            "expected_return_date",
            instance.expected_return_date
        )
        instance.actual_return_date = validated_data.get(
            "actual_return_date", instance.actual_return_date
        )
        book = validated_data["book"]
        if instance.actual_return_date and returned is None:
            book.inventory += 1
        instance.save()
        book.save()

        return instance


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="title"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "days_from_borrow",
        )


class BorrowingAdminListSerializer(BorrowingListSerializer):
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "days_from_borrow",
            "is_active",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)


class BorrowingDetailUserSerializer(UserSerializer):

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name")


class BorrowingAdminDetailSerializer(BorrowingDetailSerializer):
    user = BorrowingDetailUserSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "days_from_borrow",
            "is_active",
        )


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )


class BorrowingUpdateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )