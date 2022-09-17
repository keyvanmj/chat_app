from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from .models import PublicChatRoom


class PublicChatRoomListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        assert self.child.is_valid()
        validated_data = self.child.validated_data
        raise_errors_on_nested_writes('update', self.child, validated_data)
        info = model_meta.get_field_info(instance)
        m2m_fields = []
        for value in validated_data:
            if value in info.relations and info.relations[value].to_many:
                m2m_fields.append(value)
            else:
                pass

        instance.save()
        return instance


class PublicChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicChatRoom
        fields = ['id', 'title', 'users', ]
        list_serializer_class = PublicChatRoomListSerializer

    def __init__(self, *args, **kwargs):
        super(PublicChatRoomSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        self.fields['users'].style['template'] = 'forms/select_multiple.html'
        if request.path_info == reverse('public_room_list'):
            self.fields.pop('title')
        else:
            self.fields.pop('id')
