from django.db import transaction
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from borrowing.models import Borrowing
from notifications.bot_commands import send_borrowing_notification
from payment.models import Payment
from user.permissions import IsAdminOrIfAuthenticatedReadAndCreateOnly
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminDetailSerializer,
    BorrowingReturnSerializer,
)


class BorrowingListPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadAndCreateOnly,)
    pagination_class = BorrowingListPagination

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("book", "user")

        if is_active in ("True", "1"):
            queryset = queryset.filter(actual_return_date=None)

        if self.request.user.is_staff and user_id:
            queryset = queryset.filter(user_id=int(user_id))

        if self.request.user.is_staff is True:
            return queryset
        return queryset.filter(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=bool,
                description="Filter by borrowing is active "
                            "(ex. ?is_active=True)",
                required=False,
            ),
            OpenApiParameter(
                "user_id",
                type=int,
                description="Filter by user id (ex. ?user_id=2)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list" and self.request.user.is_staff is False:
            return BorrowingListSerializer
        if self.action == "list" and self.request.user.is_staff is True:
            return BorrowingAdminListSerializer
        if self.action == "retrieve" and self.request.user.is_staff is True:
            return BorrowingAdminDetailSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        if self.request.method in ("PUT", "PATCH"):
            return BorrowingUpdateSerializer
        return BorrowingSerializer

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    @transaction.atomic
    def return_borrowing(self, request, pk=None):
        user = self.request.user
        borrowing = self.get_object()
        serializer = self.get_serializer(instance=borrowing, data=request.data)

        if serializer.is_valid():
            payment_pending = Payment.objects.filter(
                user=user, borrowing=borrowing, status="PENDING"
            ).first()

            if payment_pending:
                raise serializers.ValidationError(
                    f"You have to pay before returning the book. "
                    f"Please pay via this link: {payment_pending.session_url}"
                )

            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        user = self.request.user

        has_pending_payments = Payment.objects.filter(
            user=user, status="PENDING"
        ).exists()
        if has_pending_payments:
            raise serializers.ValidationError(
                "You have pending payments. Please pay them before borrowing."
            )

        borrowing = serializer.save(user=user)

        send_borrowing_notification(user, borrowing)

        return borrowing
