from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from .models import FriendRequest
from Notification.models import NOTIFICATION_TYPE
from django.conf import settings


@receiver(post_save,sender=FriendRequest)
def create_notification(sender,instance,created,**kwargs):
    if created:
        instance.notifications.create(
            target=instance.receiver,
            from_user=instance.sender,
            redirect_url=f"{settings.BASE_URL}/account/{instance.sender.pk}",
            verb=f'{instance.sender.username} sent you a friend request.',
            content_type=instance,
            # general notification
            notification_type=NOTIFICATION_TYPE[2]
        )

