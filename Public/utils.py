import datetime
import os

from Chat.exceptions import ClientError


def public_room_image_file_path(instance, filename):
    """Generates file path for uploading public room images"""
    extension = filename.split('.')[-1]
    file_name = f'{instance.pk}_{instance.uid}.{extension}'
    date = datetime.date.today()
    initial_path = f'pictures/uploads/room/{date.year}/{date.month}/{date.day}/'
    full_path = os.path.join(initial_path, file_name)
    return full_path


def default_public_room_image():
    image = "public/room/Black_image.jpg"
    return image


def find_or_create_public_chat(user,owner,title,uid):
    from .models import PublicChatRoom
    try:
        chat = PublicChatRoom.objects.get(title=title)

    except PublicChatRoom.DoesNotExist:
        try:
            chat = PublicChatRoom.objects.get(title=title)

        except PublicChatRoom.DoesNotExist:
            chat = PublicChatRoom(uid=uid,title=title,owner=owner)
            chat.save()
            chat.users.add(user)

    return chat


def find_public_room(uid):
    from .models import PublicChatRoom
    exception = None
    try:
        room = PublicChatRoom.objects.get(uid=uid)

    except PublicChatRoom.DoesNotExist:

        exception = ClientError(code='ROOM_INVALID',message='Invalid room')
        raise exception
    return room



