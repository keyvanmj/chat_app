from django.shortcuts import render
from django.conf import settings
DEBUG = False

def home_screen_view(request):
    context = {
        'debug_mode':settings.DEBUG,
        'debug':DEBUG,
        'room_id':'1'
    }
    return render(request,'personal/home.html',context)