from rest_framework import serializers

from library.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily")


class BookDetailSerializer(BookSerializer):
    borrowings = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="user.email"
    )

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily", "borrowings")
