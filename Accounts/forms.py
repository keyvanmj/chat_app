from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from phonenumber_field.formfields import PhoneNumberField
from .models import User,Profile
from .utils import form_widget


class RegistrationForm(UserCreationForm):
    phone = PhoneNumberField()
    class Meta:
        model = User
        fields = ('phone','username','password1','password2')

    def __init__(self,*args,**kwargs):
        super(RegistrationForm, self).__init__(*args,**kwargs)
        self.fields['phone'].label = ''
        self.fields['phone'].widget.attrs['placeholder'] = 'Phone'
        self.fields['phone'].error_messages = {'invalid':'Enter a valid phone number (e.g. +989112234445).'}

        self.fields['username'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username'

        self.fields['password1'].label = ''
        form_widget(self=self,field='password1',attr='placeholder',content='Password')
        form_widget(self=self,field='password1',attr='tabindex',content='0')
        form_widget(self=self,field='password1',attr='role',content='button')
        form_widget(self=self,field='password1',attr='data-bs-toggle',content='popover')
        form_widget(self=self,field='password1',attr='title',content='Help Text')
        form_widget(self=self,field='password1',attr='data-bs-trigger',content='focus')
        form_widget(self=self,field='password1',attr='data-bs-placement',content='right')
        form_widget(self=self,field='password1',attr='data-bs-html',content='true')
        form_widget(self=self,field='password1',attr='data-bs-content',content=self.fields['password1'].help_text)

        self.fields['password2'].label = ''
        self.fields['password2'].widget.attrs['placeholder'] = 'Password Confirmation'
        form_widget(self=self, field='password2', attr='placeholder', content='Password Confirmation')
        form_widget(self=self, field='password2', attr='tabindex', content='0')
        form_widget(self=self, field='password2', attr='role', content='button')
        form_widget(self=self, field='password2', attr='data-bs-toggle', content='popover')
        form_widget(self=self, field='password2', attr='title', content='Help Text')
        form_widget(self=self, field='password2', attr='data-bs-trigger', content='focus')
        form_widget(self=self, field='password2', attr='data-bs-placement', content='right')
        form_widget(self=self, field='password2', attr='data-bs-html', content='true')
        form_widget(self=self, field='password2', attr='data-bs-content', content=self.fields['password2'].help_text)


        if self.errors:
            for err in self.errors:
                form_widget(self=self, field=err, attr='class', content='invalid')
        else:
            pass

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(phone=phone)
        except User.DoesNotExist:
            return phone
        raise forms.ValidationError('Phone "%s" is already in use.' % phone)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Username "%s" is already in use.' % username)


class UserAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='',widget=forms.PasswordInput(attrs={'placeholder':'Password'}))

    class Meta:
        model = User
        fields = ('phone','password')

    def __init__(self,*args,**kwargs):
        super(UserAuthenticationForm, self).__init__(*args,**kwargs)
        self.fields['phone'].label = ''
        self.fields['phone'].widget.attrs['placeholder'] = 'Phone'
        if self.errors:
            for err in self.errors:
                form_widget(self=self, field=err, attr='class', content='invalid')
        else:
            pass


    def clean(self):
        if self.is_valid():
            phone = self.cleaned_data.get('phone')
            password = self.cleaned_data.get('password')
            if not authenticate(phone=phone,password=password):
                raise forms.ValidationError({'password':'Invalid login'})



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name','last_name','image')

    def save(self, commit=True):
        profile = super(ProfileUpdateForm, self).save(commit=False)
        profile.first_name = self.cleaned_data.get('first_name')
        profile.last_name = self.cleaned_data.get('last_name')
        profile.image = self.cleaned_data.get('image')
        if commit:
            profile.save()
        return profile

class UserUpdateForm(ProfileUpdateForm):
    first_name = forms.CharField(max_length=255,required=False)
    last_name = forms.CharField(max_length=255,required=False)

    class Meta:
        model = User
        fields = ('username','phone','hide_phone','first_name','last_name')


    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(phone=phone)
        except User.DoesNotExist:
            return phone
        raise forms.ValidationError('Phone "%s" is already in use.' % phone)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Username "%s" is already in use.' % username)

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.username = self.cleaned_data.get('username')
        user.phone = self.cleaned_data.get('phone')
        user.hide_phone = self.cleaned_data.get('hide_phone')

        user.profile.first_name = self.cleaned_data.get('first_name')
        user.profile.last_name = self.cleaned_data.get('last_name')

        if commit:
            user.save()
        return user
