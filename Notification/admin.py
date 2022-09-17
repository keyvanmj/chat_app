from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_filter = ['content_type']
    list_display = ['target','content_type','timestamp','notification_type']
    search_fields = ['target__username','notification_type__icontains']
    readonly_fields = []


admin.site.register(Notification,NotificationAdmin)