from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from library.models import Book
from library.permissions import IsAdminOrReadOnly
from library.serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookImageSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        if self.action == "upload_image":
            return BookImageSerializer
        return BookSerializer

    @extend_schema(
        description="Add a new book (For admin)",
        examples=[
            OpenApiExample(
                "Book create",
                value={
                    "title": "Sample Book",
                    "author": "John Doe",
                    "cover": "HARD",
                    "inventory": 10,
                    "daily": "10.99",
                    "image": "null",
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(
                {
                    "cover": f"Cover must be one of the following: "
                    f"{Book.COVER_CHOICES[0][0]} "
                    f"or {Book.COVER_CHOICES[1][0]}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific book"""
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Get all books in our library (For all)",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Get book by id (For all)",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Fully update book by id (For admin)",
        examples=[
            OpenApiExample(
                "Book update",
                value={
                    "title": "Sample Book",
                    "author": "John Doe",
                    "cover": "HARD",
                    "inventory": 10,
                    "daily": "10.99",
                    "image": "null",
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Partial update book by id (For admin)",
        examples=[
            OpenApiExample(
                "Update title",
                value={
                    "title": "Sample Book",
                },
            ),
            OpenApiExample(
                "Update author",
                value={
                    "author": "John Doe",
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
