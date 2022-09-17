from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from Notification.models import Notification, NOTIFICATION_TYPE
from .models import PrivateChatRoom,UnreadChatMessages
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(post_save,sender=PrivateChatRoom)
def create_unread_chatroom_messages_obj(sender,instance,created,**kwargs):
    if created:
        unread_msgs1 = UnreadChatMessages(room=instance,user=instance.user1)
        unread_msgs1.save()

        unread_msgs2 = UnreadChatMessages(room=instance,user=instance.user2)
        unread_msgs2.save()


@receiver(pre_save,sender=UnreadChatMessages)
def add_unread_msg_count(sender,instance,**kwargs):
    if instance.room:
        if instance.id is None:
            pass
        else:
            previous = UnreadChatMessages.objects.get(id=instance.id)
            if previous.count < instance.count:
                content_type = ContentType.objects.get_for_model(instance)
                if instance.user == instance.room.user1:
                    other_user = instance.room.user2
                else:
                    other_user = instance.room.user1
                try:
                    notification = Notification.objects.get(
                        target=instance.user,
                        content_type=content_type,
                        object_id=instance.id
                    )
                    notification.verb = instance.most_recent_message
                    notification.timestamp = timezone.now()
                    notification.save()
                except Notification.DoesNotExist:
                    instance.notification.create(
                        target=instance.user,
                        from_user=other_user,
                        redirect_url="{}/chat/private_chatroom/?room_id={}".format(settings.BASE_URL, instance.room.id),
                        verb=instance.most_recent_message,
                        content_type=content_type,
                        # private chat room notification
                        notification_type=NOTIFICATION_TYPE[0]
                    ).save()



@receiver(pre_save,sender=UnreadChatMessages)
def remove_unread_msg_count_notification(sender,instance,**kwargs):
    if instance.room:
        if instance.id is None:
            pass
        else:
            previous = UnreadChatMessages.objects.get(id=instance.id)
            if previous.count > instance.count:
                content_type = ContentType.objects.get_for_model(instance)
                try:
                    notification = Notification.objects.get(
                        target=instance.user,
                        content_type=content_type,
                        object_id=instance.id
                    )
                    notification.delete()
                except Notification.DoesNotExist:
                    pass

