import base64
import datetime
import os
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.serializers.python import Serializer


TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


def user_image_upload_file_path(instance, filename):
    """Generates file path for uploading user images"""
    extension = filename.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{extension}'
    date = datetime.date.today()
    initial_path = f'pictures/uploads/user/{date.year}/{date.month}/{date.day}/'
    full_path = os.path.join(initial_path, file_name)
    return full_path


def get_default_profile_image():
    image = "profiles/default_user_image.png"
    return image


class LazyUserEncoder(Serializer):

    def get_dump_object(self,obj):
        dump_object = {}
        dump_object.update({'id':str(obj.id)})
        dump_object.update({'phone':str(obj.phone)})
        dump_object.update({'username':str(obj.username)})
        dump_object.update({'first_name': str(obj.profile.first_name)})
        dump_object.update({'last_name': str(obj.profile.last_name)})
        dump_object.update({'image': str(obj.profile.get_profile_image())})
        dump_object.update({'full_name': str(obj.profile.full_name())})
        return dump_object


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get("next"))
    return redirect


def save_temp_profile_image(image_str,user):
    INCORRECT_PADDING_EXCEPTION = 'Incorrect padding'

    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)

        if not os.path.exists(settings.TEMP + '/' + str(user.pk)):
            os.mkdir(settings.TEMP + '/' + str(user.pk))

        url = os.path.join(settings.TEMP + '/' + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(image_str)
        with storage.open('','wb+') as destination:
            destination.write(image)
            destination.close()

        return url
    except Exception as e:
        print('exception : '+ str(e))
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            image_str += '=' * ((4-len(image_str) %4) %4)
            return save_temp_profile_image(image_str,user)

    return None

def form_widget(self,field:str,attr:str,content):
    try:
        self.fields[str(field)].widget.attrs[str(attr)] = content
    except Exception as e:
        raise e
    return












