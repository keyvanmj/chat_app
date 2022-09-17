from .views import create_or_return_private_chat, private_chatroom_view
from django.urls import path

urlpatterns = [
    path('private_chatroom/',private_chatroom_view,name='private_chatroom_view'),
    path('create_or_return_private_chat/', create_or_return_private_chat, name='create_or_return_private_chat'),
]