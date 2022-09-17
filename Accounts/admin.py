from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


class UserAdmin(BaseUserAdmin):
    list_display = ('phone','email', 'username', 'created_date', 'last_login', 'is_superuser', 'is_staff')
    search_fields = ('phone','email', 'username',)
    readonly_fields = ('id', 'created_date', 'last_login','password')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Profile)
admin.site.register(User,UserAdmin)
