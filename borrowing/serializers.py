from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowing.models import Borrowing
from library.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
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
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)


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
