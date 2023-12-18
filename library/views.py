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
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
