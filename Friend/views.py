from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from Accounts.models import User
from Friend.models import FriendRequest, FriendList


def friends_list_view(request,*args,**kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get('pk')
        if user_id:
            try:
                current_user = User.objects.get(pk=user_id)
                context['current_user'] = current_user

            except User.DoesNotExist:
                return HttpResponse('That user does not exist.')

            try:
                friend_list = FriendList.objects.get(user=current_user)
            except FriendList.DoesNotExist:
                return HttpResponse(f'Could not find a friend list for {current_user.username}.')

            if user != current_user:
                if user not in friend_list.friends.all():
                    return HttpResponse('You must be friends to view their friends list.')
            friends = []
            auth_user_friends_list = FriendList.objects.get(user=user)
            for friend in friend_list.friends.all():
                friends.append((friend,auth_user_friends_list.is_mutual_friend(friend)))
            context['friends'] = friends
    else:
        return HttpResponse('You must be friends to view their friends list.')

    return render(request, "friend/friend_list.html", context)



def friend_requests(request,*args,**kwargs):
    user = request.user
    context = {}
    if user.is_authenticated:
        user_id = kwargs.get('pk')
        user_model = User.objects.get(pk=user_id)
        if user_model == user:
            friend_request = FriendRequest.objects.filter(receiver=user_model,is_active=True)
            context['friend_requests'] = friend_request
        else:
            return HttpResponse("You can't view another users friend requests.")

    else:
        redirect('login_view')
    return render(request,'friend/friend_requests.html',context)


def send_friend_request(request,*args,**kwargs):
    user = request.user
    payload = {}
    if request.method == 'POST' and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')
        print(request.POST)
        if user_id:
            receiver = User.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user,receiver=receiver)
                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise Exception('You already sent them a friend request.')

                    friend_request = FriendRequest(sender=user,receiver=receiver)
                    friend_request.save()
                    payload['response'] = 'Friend request sent'
                except Exception as e:
                    payload['response'] = str(e)

            except FriendRequest.DoesNotExist:
                friend_request = FriendRequest(sender=user,receiver=receiver)
                friend_request.save()
                payload['response'] = 'Friend request sent.'

            if payload['response'] == None:
                payload['response'] = 'Something went wrong.'
        else:
            payload['response'] = 'Unable to sent a friend request.'

    else:
        payload['response'] = 'You must be authenticated to send a friend request.'

    return JsonResponse(payload)



def accept_friend_request(request,*args,**kwargs):
    user = request.user
    payload = {}
    if request.method == 'GET' and user.is_authenticated:
        friend_request_id = kwargs.get('friend_request_id')
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver == user:
                if friend_request:
                    update_notification = friend_request.accept()
                    payload['response'] = 'Friend request accepted.'

                else:
                    payload['response'] = 'Something went wrong.'

            else:
                payload['response'] = 'That is not your request to accept.'

        else:
            payload['response'] = 'Unable to accept that friend request.'

    else:
        payload['response'] = 'You must be authenticate to accept a friend request.'

    return JsonResponse(payload)


def remove_friend(request,*args,**kwargs):
    user = request.user
    payload = {}
    if request.method == 'POST' and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')
        if user_id:
            try:
                user_model = User.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(user_model)
                payload['response'] = 'Successfully removed that friend.'

            except Exception as e:
                payload['response'] = f'Something went wrong : {str(e)}'

        else:
            payload['response'] = 'There was an error. Unable to remove that friend.'
    else:
        payload['response'] = 'You must be authenticate to remove a friend.'

    return JsonResponse(payload)

def decline_friend_request(request,*args,**kwargs):
    user = request.user
    payload = {}
    if request.method == 'GET' and user.is_authenticated:
        friend_request_id = kwargs.get('friend_request_id')
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver == user:
                if friend_request:
                    update_notification = friend_request.decline()
                    payload['response'] = 'Friend request declined.'

                else:
                    payload['response'] = 'Something went wrong.'

            else:
                payload['response'] = 'That is not your friend request to decline.'

        else:
            payload['response'] = 'Unable to decline that friend request.'

    else:
        payload['response'] = 'You must be authenticated to decline a friend request.'

    return JsonResponse(payload)


def cancel_friend_request(request,*args,**kwargs):
    user = request.user
    payload = {}

    if request.method == 'POST' and user.is_authenticated:
        print(request.POST)
        user_id = request.POST.get('receiver_user_id')
        if user_id:
            receiver = User.objects.get(pk=user_id)
            try:
                friend_request = FriendRequest.objects.filter(sender=user,receiver=receiver,is_active=True)

            except FriendRequest.DoesNotExist:
                payload['response'] = 'Nothing to cancel. Friend request does not exist.'

            if len(friend_request) > 1:
                for req in friend_request:
                    req.cancel()
                payload['response'] = 'Friend request canceled.'

            else:
                friend_request.first().cancel()
                payload['response'] = 'Friend request canceled.'

        else:
            payload['response'] = 'Unable to cancel that friend request.'

    else:
        payload['response'] = 'You must be authenticated to cancel a friend request.'

    return JsonResponse(payload)
















