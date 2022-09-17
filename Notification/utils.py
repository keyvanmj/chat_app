from django.core.serializers.python import Serializer
from django.contrib.humanize.templatetags.humanize import naturaltime


class LazyNotificationEncoder(Serializer):
    """
        Serialize a Notification into JSON.
        There are 3 types
            1. FriendRequest
            2. FriendList
            3. UnreadChatRoomMessage
    """

    def get_dump_object(self, obj):
        dump_object = {}
        if obj.get_content_object_type() == 'FriendRequest':
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'is_active': str(obj.content_object.is_active)})
            dump_object.update({'is_read': str(obj.read)})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "image_url": str(obj.from_user.get_profile_image()),
                }
            })

        if obj.get_content_object_type() == "FriendList":
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'is_read': str(obj.read)})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "image_url": str(obj.from_user.get_profile_image()),
                }
            })
        if obj.get_content_object_type() == "UnreadChatMessages":
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "title": str(obj.content_object.get_other_user.username),
                    "image_url": str(obj.content_object.get_other_user.get_profile_image()),
                    "room_id":obj.content_object.room.pk
                }
            })
        if obj.get_content_object_type() == "UnreadPublicMessages":
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "title": str(obj.from_user.username),
                    "image_url": str(obj.from_user.get_profile_image()),
                    "room_id":obj.content_object.public_room.pk,
                    "room_title":obj.content_object.public_room.title,
                }
            })
        return dump_object
