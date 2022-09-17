import json
import os
import cv2
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core import files
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from Friend.models import FriendList, FriendRequest
from Friend.status import FriendRequestStatus
from Friend.utils import get_friend_request_or_false
from Public.forms import PublicChatRoomForm
from .forms import RegistrationForm, UserAuthenticationForm, UserUpdateForm
from Accounts.models import User, Profile
from .utils import get_redirect_if_exists, save_temp_profile_image

def account_search_view(request):
    context = {}
    if request.method == 'GET':
        search_query = request.GET.get('q')
        if len(search_query) > 0:
            user = request.user
            search_results = User.objects.filter(
                Q(username=search_query) |
                Q(profile__first_name=search_query) |
                Q(profile__last_name=search_query)
            ).distinct()

            accounts = []
            if user.is_authenticated:
                auth_user_friend_list = FriendList.objects.get(user=user)
                for account in search_results:
                    accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
                    context['accounts'] = accounts
            else:
                for account in search_results:
                    accounts.append((account, False))
                context['accounts'] = accounts
    return render(request, 'accounts/search_results.html', context)


def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse('You are already authenticated as ' + str(user.phone))

    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            phone = form.cleaned_data.get('phone')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(phone=phone, password=raw_password)
            login(request, account)
            destination = kwargs.get('next')
            if destination:
                return redirect(destination)
            return redirect('home')
    else:
        form = RegistrationForm()

    context = {
        'registration_form': form
    }

    return render(request, 'accounts/register.html', context)


def login_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return redirect('home')

    destination = get_redirect_if_exists(request)

    if request.POST:
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            user = authenticate(phone=phone, password=password)
            if user:
                login(request, user)
                if destination:
                    return redirect(destination)
                return redirect('home')
    else:
        form = UserAuthenticationForm()

    context = {
        'login_form': form
    }

    return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    return redirect("home")


def account_view(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get('pk')

    try:
        user = User.objects.get(pk=user_id)
    except:
        return HttpResponse('Something went wrong.')

    if user:
        context['pk'] = user.pk
        context['username'] = user.username
        context['first_name'] = user.profile.first_name
        context['last_name'] = user.profile.last_name
        context['phone'] = user.phone
        context['hide_phone'] = user.hide_phone

        context['image'] = user.get_profile_image()

        try:
            friend_list = FriendList.objects.get(user=user)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=user)
            friend_list.save()

        friends = friend_list.friends.all()
        context['friends'] = friends

        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        friend_requests = None
        if request.user.is_authenticated and request.user != user:
            is_self = False
            if friends.filter(pk=request.user.pk):
                is_friend = True
            else:
                if get_friend_request_or_false(sender=user, receiver=request.user) != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=user,
                                                                                       receiver=request.user).pk

                elif get_friend_request_or_false(sender=request.user, receiver=user) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        elif not request.user.is_authenticated:
            is_self = False

        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True)
            except:
                pass

        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests
        context['BASE_URL'] = settings.BASE_URL
        context['public_form'] = PublicChatRoomForm()
    return render(request, "accounts/account.html", context)


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            image_str = request.POST.get('image')
            url = save_temp_profile_image(image_str, user)
            img = cv2.imread(url)

            crop_x = int(float(str(request.POST.get('cropX'))))
            crop_y = int(float(str(request.POST.get('cropY'))))
            crop_width = int(float(str(request.POST.get('cropWidth'))))
            crop_height = int(float(str(request.POST.get('cropHeight'))))

            if crop_x < 0:
                crop_x = 0
            if crop_y < 0:
                crop_y = 0
            crop_img = img[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]
            cv2.imwrite(url, crop_img)
            user.profile.image.delete()

            user.profile.image.save('profiles/profile_image.png', files.File(open(url, 'rb')))
            user.save()

            payload['result'] = 'success'
            payload['cropped_profile_image'] = user.profile.get_profile_image()

            os.remove(url)

        except Exception as e:
            print('exception : ' + str(e))
            payload['error'] = 'error'
            payload['exception'] = str(e)

    return HttpResponse(json.dumps(payload), content_type='application/json')


def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect('login_view')
    user_id = kwargs.get('pk')
    user = User.objects.get(pk=user_id)
    if user.pk != request.user.pk:
        return HttpResponse('You cannot edit someone else profile.')

    if request.POST:
        form = UserUpdateForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account_view', pk=user.pk)
        else:
            form = UserUpdateForm(
                data=request.POST, instance=request.user, initial={
                    'id': user.pk,
                    'phone': user.phone,
                    'username': user.username,
                    'hide_phone': user.hide_phone,
                    'first_name': user.profile.first_name,
                    'last_name': user.profile.last_name,
                    'image': user.profile.get_profile_image(),
                }
            )
    else:
        form = UserUpdateForm(
            initial={
                "id": user.pk,
                "phone": user.phone,
                "username": user.username,
                "hide_phone": user.hide_phone,
                'first_name': user.profile.first_name,
                'last_name': user.profile.last_name,
                'image': user.profile.get_profile_image(),
            }
        )
    context = {
        'form': form,
        'DATA_UPLOAD_MAX_MEMORY_SIZE': settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
    }
    return render(request, 'accounts/edit_account.html', context)
