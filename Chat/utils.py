from datetime import datetime
import pytz
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.python import Serializer
from .exceptions import ClientError
from .models import PrivateChatRoom
from . import constants

def find_or_create_private_chat(user1,user2):
    try:
        chat = PrivateChatRoom.objects.get(user1=user1,user2=user2)

    except PrivateChatRoom.DoesNotExist:
        try:
            chat = PrivateChatRoom.objects.get(user1=user2,user2=user1)

        except PrivateChatRoom.DoesNotExist:
            chat = PrivateChatRoom(user1=user1,user2=user2)
            chat.save()

    return chat


def find_room(room_id,user):
    from Friend.models import FriendList
    exception = None
    try:
        room = PrivateChatRoom.objects.get(pk=room_id)

    except PrivateChatRoom.DoesNotExist:

        exception = ClientError(code='ROOM_INVALID',message='Invalid room')
        return exception
    if user != room.user1 and user != room.user2:

        exception = ClientError(code='ROOM_ACCESS_DENIED',message='You do not have permission to join this room.')
        return exception
    friend_list = FriendList.objects.get(user=user).friends.all()
    if not room.user1 in friend_list:
        if not room.user2 in friend_list:
            exception = ClientError(code='ROOM_ACCESS_DENIED',message='You must be friends to chat.')
            return exception
    return room



def calculate_timestamp(timestamp):
    ts = ""

    if(naturalday(timestamp) == 'today') or (naturalday(timestamp) == 'yesterday'):
        str_time = datetime.strftime(timestamp, "%I:%M %p")
        str_time.strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"

    else:
        str_time = datetime.strftime(timestamp,"%m/%d/%Y")
        ts = f"{str_time}"

    return str(ts)


class LazyRoomChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'msg_type': constants.MSG_TYPE_MESSAGE})
        dump_object.update({'msg_id': str(obj.id)})
        dump_object.update({'user_id': str(obj.user.pk)})
        dump_object.update({'username': str(obj.user.username)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'image':str(obj.user.profile.get_profile_image())})
        dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
        return dump_object


def get_today():
    today = datetime(
        year=1950,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        tzinfo=pytz.UTC
    )
    return today
