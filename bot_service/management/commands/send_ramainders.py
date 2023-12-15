import asyncio

from bot_service.management.commands.run_bot import send_message

json = {
    "user1": {
        "username": "vlad",
        "first_name": "fdsf",
        "telegram_id": 562745779
    },
    "user2": {
        "username": "test",
        "first_name": "fsdf",
        "telegram_id": -4050199237
    }
}


def send_messages(users: dict, message: str):
    ids = [user.get("telegram_id", None)
           for user in users.values()
           if user.get("telegram_id", None)]

    asyncio.run(send_message(ids, message))


if __name__ == '__main__':
    send_messages(json, "Hello, world")
