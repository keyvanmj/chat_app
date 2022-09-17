from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.python import Serializer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
import asyncio

from django.db.models import F
from django.utils import timezone

from Accounts.models import Profile
from Chat.models import UnreadChatMessages
from Notification.models import Notification, NOTIFICATION_TYPE
from .constants import *
from .models import PublicChatRoom, PublicRoomChatMessage
from Chat.exceptions import ClientError
from Chat.utils import calculate_timestamp, LazyRoomChatMessageEncoder


class PublicChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        profile_obj = await sync_to_async(Profile.objects.get)(user=self.scope['user'])
        self.profile_image = profile_obj.get_profile_image()

        await self.accept()
        self.room_id = None

    async def disconnect(self, code):
        try:
            if self.room_id != None:
                await self.leave_room(self.room_id)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        command = content.get('command',None)
        try:
            if command == 'send':
                if len(content['message'].lstrip()) != 0:
                    await self.send_room(content['room_id'],content['message'])

            elif command == 'join':
                await self.join_room(content['room'])

            elif command == 'leave':
                await self.leave_room(content['room'])

            elif command == 'get_room_chat_messages':
                await self.display_progress_bar(True)
                room = await get_room_or_error(content['room_id'])
                payload = await get_room_chat_messages(room,content['page_number'])
                if payload != None:
                    payload = json.loads(payload)
                    await self.send_messages_payload(payload['messages'],payload['new_page_number'])

                else:
                    raise ClientError(204,"Something went wrong retrieving the chatroom messages.")

                await self.display_progress_bar(False)

        except ClientError as e:
            await self.display_progress_bar(False)
            await self.handle_client_error(e)


    async def send_room(self,room_id,message):
        if self.room_id != None:
            if str(room_id) != str(self.room_id):
                raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
            if not is_authenticated(self.scope["user"]):
                raise ClientError("AUTH_ERROR", "You must be authenticated to chat.")
        else:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

        room = await get_room_or_error(room_id)

        connected_users = room.connect_users.all().order_by('-created_date')
        users = room.users.all().exclude(pk=self.scope['user'].pk).order_by('-created_date')
        await asyncio.gather(*[
            append_unread_msg_if_not_connected(room, users, connected_users, message,self.scope['user']),
            create_public_room_chat_message(room,self.scope['user'],message)
        ])

        await self.channel_layer.group_send(
            room.group_name,
            {
                'type':'chat.message',
                'image':self.profile_image,
                'username':self.scope['user'].username,
                'user_id':self.scope['user'].id,
                'message':message,
                'room_id':room_id,
            }
        )

    async def chat_message(self,event):
        print(event)
        timestamp = calculate_timestamp(timezone.now())
        await self.send_json(
            {
                'msg_type':MSG_TYPE_MESSAGE,
                'image':event['image'],
                'username':event['username'],
                'user_id':event['user_id'],
                'message':event['message'],
                'natural_timestamp':timestamp,
                'room_id': event['room_id'],
            }
        )

    async def join_room(self,room_id):
        is_auth = is_authenticated(self.scope['user'])
        try:
            room = await get_room_or_error(room_id)
        except ClientError as e:
            await self.handle_client_error(e)

        if is_auth:
            await connect_user(room,self.scope['user'])

        self.room_id = room.id

        await on_user_connected(room, self.scope['user'])


        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name
        )
        await self.send_json(
            {
                'join':str(room.id),
                'room_title': room.title
            }
        )
        num_connected_users = await get_num_connected_users(room)
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type':'connected.user.count',
                'connected_user_count':num_connected_users
            }
        )

    async def leave_room(self,room_id):
        is_auth = is_authenticated(self.scope['user'])
        room = await get_room_or_error(room_id)
        if is_auth:
            await disconnect_user(room,self.scope['user'])

        self.room_id = None

        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name
        )
        num_connected_users = await get_num_connected_users(room)
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type':'connected.user.count',
                'connected_user_count':num_connected_users
            }
        )

    async def handle_client_error(self,e):
        error_data = {}
        error_data['error'] = e.code
        if e.message:
            error_data['message'] = e.message
            await self.send_json(error_data)

        return

    async def send_messages_payload(self,messages,new_page_number):
        await self.send_json(
            {
                'messages_payload':'messages_payload',
                'messages':messages,
                'new_page_number':new_page_number,
            }
        )

    async def connected_user_count(self,event):
        await self.send_json(
            {
                'msg_type':MSG_TYPE_CONNECTED_USER_COUNT,
                'connected_user_count':event['connected_user_count'],
            }
        )

    async def display_progress_bar(self,is_displayed):
        await self.send_json(
            {
                'display_progress_bar':is_displayed
            }
        )


def is_authenticated(user):
    if user.is_authenticated:
        return True
    return False

@database_sync_to_async
def get_num_connected_users(room):

    if room.connect_users:
        return len(room.connect_users.all())
    return 0



@database_sync_to_async
def create_public_room_chat_message(room,user,message):
    public_room_chat_message = PublicRoomChatMessage.objects.create(user=user,room=room,content=message)
    return public_room_chat_message


@database_sync_to_async
def connect_user(room,user):
    return room.connect_user(user)


@database_sync_to_async
def disconnect_user(room,user):
    return room.disconnect_user(user)


@database_sync_to_async
def get_room_or_error(room_id):
    try:
        room = PublicChatRoom.objects.get(pk=room_id)
    except PublicChatRoom.DoesNotExist:
        raise ClientError('ROOM_INVALID','Invalid room.')
    return room


@database_sync_to_async
def get_room_chat_messages(room,page_number):
    try:
        qs = PublicRoomChatMessage.objects.by_room(room)
        p = Paginator(qs,DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

        payload = {}

        new_page_number = int(page_number)
        if new_page_number <= p.num_pages:
            new_page_number = new_page_number + 1
            s = LazyRoomChatMessageEncoder()
            payload['messages'] = s.serialize(p.page(page_number).object_list)

        else:
            payload['messages'] = 'None'

        payload['new_page_number'] = new_page_number
        return json.dumps(payload)

    except Exception as e:
        pass
    return None


@database_sync_to_async
def append_unread_msg_if_not_connected(room, other_users, connected_users, message,user):
    other_disconnect_users = [x for x in other_users if x not in connected_users]
    if other_disconnect_users:
        try:
            unread_msgs = UnreadChatMessages.objects.filter(public_room=room, user__in=other_disconnect_users)
            for un_msg in unread_msgs:
                un_msg.most_recent_message = message
                un_msg.count += 1
                un_msg.save()
            else:
                content_type = ContentType.objects.get_for_model(unread_msgs[0])
                notification = Notification.objects.filter(
                    target__in=other_disconnect_users,
                    content_type=content_type,
                    notification_type=NOTIFICATION_TYPE[1]
                )
                notification.update(from_user=user)

        except UnreadChatMessages.DoesNotExist:
            for user in other_disconnect_users:
                unread_msgs = UnreadChatMessages(public_room=room, user=user, count=1)
                unread_msgs.save()
    return


@database_sync_to_async
def on_user_connected(room, user):
    connected_users = room.connect_users.all()
    if user in connected_users:
        try:
            unread_msgs = UnreadChatMessages.objects.get(public_room=room, user=user)
            unread_msgs.count = 0
            unread_msgs.save()

        except UnreadChatMessages.DoesNotExist:
            UnreadChatMessages(public_room=room, user=user).save()

    return

