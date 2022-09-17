from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from Chat.utils import find_or_create_private_chat
from Notification.models import Notification


class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='user')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL,blank=True,related_name='friends')
    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.user.username


    def add_friend(self,account):
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

            content_type = ContentType.objects.get_for_model(self)
            self.notifications.create(
                target=self.user,
                from_user=account,
                redirect_url=f'{settings.BASE_URL}/account/{account.pk}',
                verb=f'You are now friends with {account.username}',
                content_type=content_type
            )
            self.save()

            chat = find_or_create_private_chat(self.user,account)
            if not chat.is_active:
                chat.is_active = True
                chat.save()

    def remove_friend(self,account):
        if account in self.friends.all():
            self.friends.remove(account)
            chat = find_or_create_private_chat(self.user,account)
            if chat.is_active:
                chat.is_active = False
                chat.save()

    def unfriend(self,remove):

        remover_friends_list = self
        remover_friends_list.remove_friend(remove)

        friend_list = FriendList.objects.get(user=remove)
        friend_list.remove_friend(remover_friends_list.user)

        content_type = ContentType.objects.get_for_model(self)

        friend_list.notifications.create(
            target=remove,
            from_user=self.user,
            redirect_url=f'{settings.BASE_URL}/account/{self.user.pk}/',
            verb=f'You are no longer friends with {self.user.username}.',
            content_type=content_type
        )

        self.notifications.create(
            target=self.user,
            from_user=remove,
            redirect_url=f"{settings.BASE_URL}/account/{remove.pk}/",
            verb=f"You are no longer friends with {remove.username}.",
            content_type=content_type,
        )

    @property
    def get_cname(self):
        return "FriendList"

    def is_mutual_friend(self,friend):
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=False, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.sender.username

    def accept(self):
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:
            content_type = ContentType.objects.get_for_model(self)

            receiver_notification = Notification.objects.get(target=self.receiver,content_type=content_type,object_id=self.id)
            receiver_notification.is_active = False
            receiver_notification.redirect_url = f'{settings.BASE_URL}/account/{self.sender.pk}/'
            receiver_notification.verb = f"You accepted {self.sender.username}'s friend request."
            receiver_notification.timestamp = timezone.now()
            receiver_notification.save()

            receiver_friend_list.add_friend(self.sender)

            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:
                self.notifications.create(
                    target=self.sender,
                    from_user=self.receiver,
                    redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
                    verb=f"{self.receiver.username} accepted your friend request.",
                    content_type=content_type,
                )
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()
            return receiver_notification

    def decline(self):
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)

        notification = Notification.objects.get(target=self.receiver,content_type=content_type,object_id=self.id)
        notification.is_active = False
        notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
        notification.verb = f"You declined {self.sender}'s friend request."
        notification.from_user = self.sender
        notification.timestamp = timezone.now()
        notification.save()

        self.notifications.create(
            target=self.sender,
            verb=f"{self.receiver.username} declined your friend request.",
            from_user=self.receiver,
            redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
            content_type=content_type,
        )

        return notification



    def cancel(self):
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)

        self.notifications.create(
            target=self.sender,
            verb=f"You cancelled the friend request to {self.receiver.username}.",
            from_user=self.receiver,
            redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
            content_type=content_type,
        )

        notification = Notification.objects.get(target=self.receiver,content_type=content_type,object_id=self.id)
        notification.verb = f'{self.sender.username} cancelled the friend request sent to you.'
        notification.read = False
        notification.save()

    @property
    def get_cname(self):
        return "FriendRequest"