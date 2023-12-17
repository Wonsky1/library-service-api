from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
            "telegram_notifications_enabled",
            "telegram_id",
        )
        read_only_fields = ("is_staff", "telegram_id")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class DetailUserSerializer(UserSerializer):
    telegram_auth_link = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
            "telegram_notifications_enabled",
            "telegram_id",
            "telegram_auth_link"
        )
        read_only_fields = ("is_staff", "telegram_id", "telegram_auth_link")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_telegram_auth_link(self, obj):
        return f"https://t.me/LibraryRemainderBot?start={obj.id}"
