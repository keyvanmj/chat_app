from django.urls import path

from Public.views import public_chat_view, create_or_return_public_chat,PublicRoomList

urlpatterns = [
    path('<str:uid>',public_chat_view,name='public_chat'),
    path('list/',PublicRoomList.as_view(),name='public_room_list'),
    path('create_or_return_public_chat/', create_or_return_public_chat, name='create_or_return_public_chat'),
]