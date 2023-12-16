from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


@sync_to_async
def check_user(parameter: int):
    try:
        user = get_user_model().objects.get(pk=parameter)
    except get_user_model().DoesNotExist:
        return None

    return user



def obtain_token(command: str):
    if len(command.split()) == 2:

        try:
            id = int(command.split()[1])
        except ValueError:
            return None

        if id <= 0:
            return None

        return id
    return None


@sync_to_async
def connected_user_with_telegram(user: get_user_model(), telegram_id: int) -> str:
    if not user.telegram_id is None:
        return "You need to reset your telegram id, to connect to this telegram account"

    if not user.telegram_notifications_enabled:
        return "You need to enable notifications in your profile"
    try:
        user.telegram_id = telegram_id
        user.save()
        return "Successfully connected"
    except IntegrityError:
        return "This telegram account is already registered for another account"


