from django import forms
from .models import PublicChatRoom


class PublicChatRoomForm(forms.ModelForm):
    class Meta:
        model = PublicChatRoom
        fields = ['title','users']

    def __init__(self, *args, **kwargs):
        super(PublicChatRoomForm, self).__init__(*args, **kwargs)
        # add a "form-control" class to each form input
        # for enabling bootstrap
        self.fields['title'].widget.attrs.update({'placeholder':'Enter Room Name'})
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })