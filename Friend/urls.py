from django.urls import path
from .views import (
    send_friend_request, friend_requests, friends_list_view,
    accept_friend_request,cancel_friend_request,decline_friend_request,
    remove_friend,
)


urlpatterns = [
    path('list/<int:pk>/', friends_list_view, name='friends_list'),
    path('friend_remove/',remove_friend,name='remove_friend'),
    path('friend_request/',send_friend_request,name='send_friend_request'),
    path('friend_requests/<int:pk>/', friend_requests, name='friend_requests'),
    path('friend_request_cancel/',cancel_friend_request,name='cancel_friend_request'),
    path('friend_request_accept/<friend_request_id>/',accept_friend_request,name='accept_friend_request'),
    path('friend_request_decline/<friend_request_id>/',decline_friend_request,name='decline_friend_request')

]