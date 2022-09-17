from django.contrib import admin
from .models import PrivateChatRoom,RoomChatMessage,UnreadChatMessages
from django.core.paginator import Paginator
from django.core.cache import cache


@admin.action(description='Reset selected unread messages (count and message)')
def reset_message_and_count(model_admin, request, queryset):
    try:
        queryset.update(count=0)
        queryset.update(most_recent_message='')
    except:
        pass


class CachePaginator(Paginator):
    def _get_count(self):
        if not hasattr(self,"_count"):
            self._count = None
        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key,-1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key,self._count,3600)

            except:
                self._count = len(self.object_list)

            return self._count

    count = property(_get_count)


class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id','user1','user2']
    search_fields = ['id','user1__username','user2__username','user1__phone','user2__phone']
    readonly_fields = ['id']


class RoomChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room','user','timestamp']
    list_display = ['room','user','content','timestamp']
    search_fields = ['user__username','content']
    readonly_fields = ['id','user','room','timestamp']

    show_full_result_count = False
    paginator = CachePaginator


class UnreadChatRoomMessagesAdmin(admin.ModelAdmin):
    list_display = ['room','public_room','user', 'count']
    search_fields = ['room__user1__username', 'room__user2__username', ]
    readonly_fields = ['id',]
    actions = [reset_message_and_count]

admin.site.register(PrivateChatRoom,PrivateChatRoomAdmin)
admin.site.register(RoomChatMessage,RoomChatMessageAdmin)
admin.site.register(UnreadChatMessages,UnreadChatRoomMessagesAdmin)