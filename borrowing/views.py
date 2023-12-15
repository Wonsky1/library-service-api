from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from borrowing.models import Borrowing
from user.permissions import IsAdminOrIfAuthenticatedReadAndCreateOnly
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminDetailSerializer,
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
                description="Filter by borrowing is active (ex. ?is_active=True)",
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
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        if self.request.method in ("PUT", "PATCH"):
            return BorrowingUpdateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
