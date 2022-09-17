from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from Chat.models import UnreadChatMessages
from Notification.models import Notification, NOTIFICATION_TYPE
from .models import PublicChatRoom
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(post_save,sender=PublicChatRoom)
def create_unread_public_messages_obj(sender,instance,created,**kwargs):
    if created:
        try:
            unread_msgs = UnreadChatMessages(public_room=instance, user=instance.users)
            unread_msgs.save()
        except ValueError:
            unread_msgs = UnreadChatMessages(public_room=instance, user=instance.owner)
            unread_msgs.save()


@receiver(pre_save,sender=UnreadChatMessages)
def add_unread_msg_count(sender,instance,**kwargs):
    if instance.public_room:
        if instance.id is None:
            pass
        else:
            previous = UnreadChatMessages.objects.get(id=instance.id)
            if previous.count < instance.count:
                content_type = ContentType.objects.get_for_model(instance)
                try:
                    notification = Notification.objects.get(
                        target=instance.user,
                        content_type=content_type,
                        object_id=instance.id
                    )
                    notification.verb = instance.most_recent_message
                    notification.notification_type = NOTIFICATION_TYPE[1]
                    notification.timestamp = timezone.now()
                    notification.save()
                except Notification.DoesNotExist:
                    instance_notif = instance.notification.create(
                        target=instance.user,
                        redirect_url="{}/public/{}".format(settings.BASE_URL, instance.public_room.uid),
                        verb=instance.most_recent_message,
                        content_type=content_type,
                        # public chat room notification type
                        notification_type=NOTIFICATION_TYPE[1]
                    )
                    instance_notif.save()


@receiver(pre_save,sender=UnreadChatMessages)
def remove_unread_msg_count_notification(sender,instance,**kwargs):
    if instance.public_room:
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
                        object_id=instance.id,
                    )
                    notification.delete()
                except Notification.DoesNotExist:
                    pass

                except Notification.MultipleObjectsReturned:
                    notification = Notification.objects.filter(
                        target=instance.user,
                        content_type=content_type,
                        object_id=instance.id,
                    )
                    notification.delete()
