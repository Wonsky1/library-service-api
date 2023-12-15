from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from borrowing.models import Borrowing
from borrowing.permission import IsAdminOrIfAuthenticatedReadOnly
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
)


class BorrowingListPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = BorrowingListPagination

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("book", "user")
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        if self.request.method in ("PUT", "PATCH"):
            return BorrowingUpdateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
