import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowing.models import Borrowing
from library.serializers import BookSerializer
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.stripe_helper import create_stripe_session
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
            attrs["expected_return_date"], attrs["book"], ValidationError
        )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        book = validated_data["book"]
        book.save()

        request = self.context.get("request")
        create_stripe_session(borrowing, request)
        return borrowing

    @transaction.atomic()
    def update(self, instance, validated_data):
        returned = instance.actual_return_date
        instance.expected_return_date = validated_data.get(
            "expected_return_date", instance.expected_return_date
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


class BorrowingListPaymentSerializer(PaymentSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status")


class BorrowingAdminListSerializer(BorrowingListSerializer):
    user = serializers.CharField(source="user.email", read_only=True)
    payments = BorrowingListPaymentSerializer(many=True, read_only=True)

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
            "payments",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)


class BorrowingDetailUserSerializer(UserSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name")


class BorrowingDetailPaymentSerializer(PaymentSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "session_id",
            "session_url",
            "money_to_pay",
        )


class BorrowingAdminDetailSerializer(BorrowingDetailSerializer):
    user = BorrowingDetailUserSerializer(many=False, read_only=True)
    payments = BorrowingDetailPaymentSerializer(many=True, read_only=True)

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
            "payments",
        )


class BorrowingCreateSerializer(BorrowingSerializer):
    message = serializers.CharField(
        max_length=63,
        default="To initiate the borrowing process of the book, "
                "please make an initial payment.",
        read_only=True
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "message",
            "payments",
        )
        read_only_fields = (
            "message",
            "payments",
        )


class BorrowingUpdateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    message = serializers.CharField(
        max_length=63,
        default="To successfully complete the return of the borrowed book, "
        "please make a payment first.",
        read_only=True,
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "message",
            "payments",
        )
        read_only_fields = (
            "message",
            "payments",
        )

    def validate(self, attrs):
        borrowing = self.instance

        if borrowing.actual_return_date:
            raise serializers.ValidationError(
                "The borrowed book has already been returned."
            )

        return attrs

    def update(self, instance, validated_data):
        instance.actual_return_date = datetime.date.today()
        instance.book.inventory += 1
        instance.book.save()
        instance.save()

        request = self.context.get("request")
        create_stripe_session(instance, request)

        return instance


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"
