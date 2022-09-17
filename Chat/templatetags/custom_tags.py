from django import template
from Accounts.models import Profile, User
from Chat.views import get_recent_chatroom_messages

register = template.Library()

@register.inclusion_tag(takes_context=True,filename='../templates/chat/message_box.html')
def message_box(context,*args,**kwargs):
    request = context['request']
    profiles = Profile.objects.all()
    try:
        room_name = context['room_name']
    except:
        pass

    return {
        'profile':profiles,
        'request':request,
    }

@register.inclusion_tag(takes_context=True,filename='../templates/shared/sidebar.html')
def side_bar(context,*args,**kwargs):
    users = None
    request = context['request']

    msg_and_friend = kwargs.get('msg_and_friend',None)
    profiles = Profile.objects.all()
    try:
        users = context['users']
    except:
        pass

    return {
        'request':request,
        'profile':profiles,
        'msg_and_friend':msg_and_friend,
        'users':users
    }