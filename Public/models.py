import secrets

from django.db import models
from django.conf import settings

from Public.utils import default_public_room_image, public_room_image_file_path


class PublicChatRoom(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        blank=False
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text="chat room members.", blank=True,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    connect_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text="users who are connected to chat room.", blank=True,
        related_name="connect_users",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='room_owner'
    )

    uid = models.CharField(
        max_length=8,
        unique=True
    )
    image = models.ImageField(
        upload_to=public_room_image_file_path,
        default=default_public_room_image, null=True,
        blank=True, max_length=1024,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    def connect_user(self, user):
        is_user_added = False
        if not user in self.connect_users.all():
            self.connect_users.add(user)
            self.save()
            is_user_added = True

        elif user in self.connect_users.all():
            is_user_added = True

        return is_user_added

    def disconnect_user(self, user):
        is_user_removed = False
        if user in self.connect_users.all():
            self.connect_users.remove(user)
            self.save()
            is_user_removed = True

        return is_user_removed

    @property
    def group_name(self):
        return "PublicChatRoom-%s" % self.id

    def get_users_count(self):
        return len(self.users.all())



class PublicRoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by('-timestamp')
        return qs


class PublicRoomChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False)

    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content
