from datetime import datetime

import pytz
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.conf import settings
from django.utils import timezone

from Notification.models import Notification
from Public.models import PublicChatRoom


class PrivateChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='user2')
    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="connected_users")
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user1.username} , {self.user2.username}'

    def connect_user(self,user):
        is_user_added = False
        if not user in self.connected_users.all():
            self.connected_users.add(user)
            is_user_added = True
        return is_user_added


    def disconnect_user(self,user):
        is_user_removed = False
        if user in self.connected_users.all():
            self.connected_users.remove(user)
            is_user_removed = True
        return is_user_removed


    @property
    def group_name(self):
        return f'PrivateChatRoom-{self.id}'


class RoomChatMessageManager(models.Manager):
    def by_room(self,room):
        qs = RoomChatMessage.objects.filter(room=room).order_by('-timestamp')
        return qs

    def room_messages(self,room,user):
        from Chat.utils import get_today
        try:
            qs = self.get_queryset().filter(room=room)
        except RoomChatMessage.DoesNotExist:
            qs = self.get_queryset()(
                user=user,
                room=room,
                timestamp=get_today(),
                content='',)
        return qs

class RoomChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    objects = RoomChatMessageManager()

    def __str__(self):
        return self.content

class UnreadChatMessages(models.Model):
    room = models.ForeignKey(PrivateChatRoom,on_delete=models.CASCADE,related_name='room',blank=True,null=True)
    public_room = models.ForeignKey(PublicChatRoom,on_delete=models.CASCADE,related_name='public_room',blank=True,null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    most_recent_message = models.CharField(max_length=1000,blank=True,null=True)
    reset_timestamp = models.DateTimeField()
    notification = GenericRelation(Notification)

    class Meta:
        verbose_name_plural = 'UnreadChatMessages'

    def __str__(self):
        return f'Messages that {str(self.user.username)} has not read yet.'


    def save(self,*args,**kwargs):
        if not self.id:
            self.reset_timestamp = timezone.now()

        return super(UnreadChatMessages, self).save(*args,**kwargs)

    @property
    def get_cname(self):
        if self.room:
            return "UnreadChatMessages"
        elif self.public_room:
            return "UnreadPublicMessages"

    @property
    def get_room(self):
        if self.room:
            return self.room
        elif self.public_room:
            return self.public_room
    
    @property
    def get_other_user(self):
        if self.room:
            if self.user == self.room.user1:
                return self.room.user2
            else:
                return self.room.user1








