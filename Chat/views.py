from datetime import datetime
from itertools import chain
from urllib.parse import urlencode
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from Accounts.models import User
from Friend.models import FriendList
from .models import PrivateChatRoom, RoomChatMessage
from .utils import find_or_create_private_chat, find_room

DEBUG = False
@login_required(login_url='login_view')
@api_view(['GET'])
@parser_classes([JSONParser])
def private_chatroom_view(request,*args,**kwargs):
    context = {}
    room_id = request.GET.get('room_id')
    user = request.user
    msg_and_friend = get_recent_chatroom_messages(user)
    context['msg_and_friend'] = msg_and_friend
    context['BASE_URL'] = settings.BASE_URL
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG
    if room_id:
        room = find_room(room_id, user)
        context['room_id'] = room_id
        context['room'] = room
        try:
            if room.user1 == user:
                friend = room.user2
            else:
                friend = room.user1
            context['room_messages'] = RoomChatMessage.objects.room_messages(room=room,user=user)
            context['other_user'] = friend
        except AttributeError as e:
            context['exceptions'] = e
            return redirect(reverse('private_chatroom_view',))

    if room_id is None and not msg_and_friend:
        return redirect(reverse('account_view',kwargs={'pk':user.pk}))
    return render(request,'chat/room.html',context)


def create_or_return_private_chat(request,*args,**kwargs):
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == 'POST':
            user2_id = request.POST.get('user2_id')
            try:
                user2 = User.objects.get(pk=user2_id)
                chat = find_or_create_private_chat(user1,user2)
                payload['response'] = 'Successfully got the chat.'
                payload['chatroom_id'] = chat.id

            except User.DoesNotExist:
                payload['response'] = 'Unable to start a chat with that user.'

    else:
        payload['response'] = "You can't start a chat if you are not authenticated."

    return JsonResponse(payload)


def get_recent_chatroom_messages(user):
    rooms1 = PrivateChatRoom.objects.filter(user1=user)
    rooms2 = PrivateChatRoom.objects.filter(user2=user)

    rooms = list(chain(rooms1,rooms2))
    msg_and_friend = []
    for room in rooms:
        if room.user1 == user:
            friend = room.user2
        else:
            friend = room.user1

        friend_list = FriendList.objects.get(user=user)
        if not friend_list.is_mutual_friend(friend):
            chat = find_or_create_private_chat(user,friend)
            chat.is_active = False
            chat.save()
        else:
            try:
                message = RoomChatMessage.objects.filter(room=room,user=friend).latest('timestamp')

            except RoomChatMessage.DoesNotExist:
                message = RoomChatMessage(
                    user=friend,
                    room=room,
                    timestamp=datetime.now(),
                    content='',
                )
            msg_and_friend.append({
                'message':message,
                'friend':friend,
            })
    return sorted(msg_and_friend,key=lambda x:x['message'].timestamp,reverse=True)

