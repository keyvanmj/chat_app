from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from .forms import PublicChatRoomForm
from rest_framework.decorators import api_view,parser_classes,renderer_classes,permission_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.parsers import FormParser,MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .generics import ListUpdateAPIView
from .models import PublicChatRoom, PublicRoomChatMessage
from .serializers import PublicChatRoomSerializer
from .utils import find_or_create_public_chat, find_public_room

User = get_user_model()


DEBUG = False


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([TemplateHTMLRenderer])
@parser_classes([FormParser,MultiPartParser])
def public_chat_view(request,uid):
    context = {}
    room = None
    user = request.user
    if uid:
        room = find_public_room(uid)
    public_serializer = PublicChatRoomSerializer(instance=room,context={'request':request})

    if request.method == 'POST':
        serializer = PublicChatRoomSerializer(data=request.data,instance=room,context={'request':request})
        if serializer.is_valid():
            validate_user = serializer.validated_data.get('users')
            if user not in validate_user:
                context['error'] = {"users":["You can't remove your self from room"]}
            else:
                serializer.update(request.user,serializer.validated_data)
                serializer.save()
                context['redirect_url'] = reverse('public_chat', kwargs={'uid': uid})
                context['response'] = 'The room was successfully updated.'
        else:
            context['error'] = serializer.errors
        return JsonResponse(context)
    context['debug_mode'] = settings.DEBUG
    context['debug'] = DEBUG
    context['room_id'] = room.pk
    context['public_serializer'] = public_serializer
    context['room_uid'] = uid
    context['members'] = room.users.all()
    context['all_users'] = User.objects.all()
    context['room_owner'] = room.owner
    context['msg_and_friend'] = get_recent_public_room_messages(user)
    return Response(data=context,template_name='public/public_chat_room.html')

def create_or_return_public_chat(request,*args,**kwargs):
    payload = {}
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.pk)
        if request.method == 'POST':
            uid_token = get_random_string(8)
            forms = PublicChatRoomForm(request.POST)
            if forms.is_valid():
                title = forms.cleaned_data.get('title',None)
                owner = request.user
                try:
                    public_chat_room = find_or_create_public_chat(user=user,owner=owner,title=title, uid=uid_token)

                    payload['redirect_url'] = reverse('public_chat', kwargs={'uid': public_chat_room.uid})

                except User.DoesNotExist:
                    payload['response'] = 'Unable to start a chat with that user.'
                payload['response'] = 'The room was successfully created.'

            else:

                payload['error'] = forms.errors

    else:
        payload['response'] = "You can't start a chat if you are not authenticated."

    return JsonResponse(payload)



def get_recent_public_room_messages(user):

    rooms = PublicChatRoom.objects.filter(users=user)
    msg_and_friend = []
    for room in rooms:
        members = room.users.exclude(pk=user.pk)

        try:

            message = PublicRoomChatMessage.objects.filter(
                Q(room=room)&
                ~Q(user=user)
            ).latest('timestamp')
        except PublicRoomChatMessage.DoesNotExist:
            message = PublicRoomChatMessage(
                user=user,
                room=room,
                timestamp=timezone.now(),
                content='',
            )
        msg_and_friend.append({
            'message':message,
            'friend':members,
            'rooms':rooms
        })
    return sorted(msg_and_friend,key=lambda x:x['message'].timestamp,reverse=True)


class PublicRoomList(ListUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PublicChatRoomSerializer
    renderer_classes = [TemplateHTMLRenderer]
    parser_classes = [FormParser,MultiPartParser]
    template_name = 'public/public_room_list.html'

    def get_queryset(self):
        qs = PublicChatRoom.objects.all()
        return qs

    def get(self,*args,**kwargs):
        qs = self.get_queryset().all()
        return Response({'public_rooms':qs})

    def put(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_queryset().get(id=data.get('id'))
        instance.users.add(data.get('users', None))
        instance.save()

        serializer = self.serializer_class(instance,data=data,context={'request':request},many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        payload = {
            'redirect_url':reverse('public_chat',kwargs={'uid':instance.uid})
        }
        return JsonResponse(payload)


