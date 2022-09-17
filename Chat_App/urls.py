from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from Personal.views import home_screen_view
urlpatterns = [
    path('',home_screen_view,name='home'),
    path('admin/', admin.site.urls),
    path('chat/', include('Chat.urls')),
    path('account/', include('Accounts.urls')),
    path('friend/', include('Friend.urls')),
    path('public/', include('Public.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

