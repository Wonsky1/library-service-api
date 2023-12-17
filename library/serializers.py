from rest_framework import serializers

from library.models import Book


class BookSerializer(serializers.ModelSerializer):
    cover = serializers.ChoiceField(choices=Book.COVER_CHOICES)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily",
            "image"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        cover_value = instance.get_cover_display()
        representation["cover"] = cover_value
        return representation


class BookDetailSerializer(BookSerializer):
    borrowings = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily",
            "borrowings",
            "image"
        )

    def get_borrowings(self, obj):
        borrowing_objects = obj.borrowings.all()
        user_emails = borrowing_objects.values_list("user__email", flat=True)
        return user_emails


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "image")
