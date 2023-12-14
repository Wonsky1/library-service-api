from rest_framework import serializers

from library.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily")


class BookDetailSerializer(BookSerializer):
    borrowings = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily", "borrowings")

    def get_borrowings(self, obj):
        borrowing_objects = obj.borrowings.all()
        user_emails = borrowing_objects.values_list("user__email", flat=True)
        return user_emails
