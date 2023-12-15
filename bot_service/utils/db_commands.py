from django.contrib.auth import get_user_model


def find_telegram_user_by_id(telegram_user_id):
    try:
        telegram_user = get_user_model().objects.get(telegram_id=telegram_user_id)
        return telegram_user
    except get_user_model().DoesNotExist:
        return None
