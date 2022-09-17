from . import views
from django.urls import path

urlpatterns = [
    path('auth/register/',views.register_view,name='register_view'),
    path('auth/login/',views.login_view,name='login_view'),
    path('auth/logout/',views.logout_view,name='logout_view'),
    path('search/', views.account_search_view, name="search"),
    path('<pk>/',views.account_view,name='account_view'),
    path('<int:pk>/edit/',views.edit_account_view,name='edit_account_view'),
    path('<int:pk>/edit/crop_image/',views.crop_image,name='crop_image'),
]