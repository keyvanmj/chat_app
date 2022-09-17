from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import user_image_upload_file_path,get_default_profile_image
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name=_("user"))
    first_name = models.CharField(_("first name"),max_length=255, blank=True, null=True)
    last_name = models.CharField(_("last name"),max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        _('Image'),upload_to=user_image_upload_file_path,
        default=get_default_profile_image,null=True,
        blank=True,max_length=1024,
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")


    def get_profile_image(self):
        if self.image:
            return self.image.url
        else:
            return None

    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return self.user.username

    def get_profile_image_filename(self):
        return str(self.image)[str(self.image).index('profile_images/' + str(self.pk) + "/"):]


class UserManager(BaseUserManager):

    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_("The Phone Number must be set"))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(**extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(unique=True)
    email = models.EmailField(_("email address"), unique=True,blank=True,null=True)
    username = models.CharField(_("username"),max_length=40,unique=True)
    is_staff = models.BooleanField(_("staff"),default=False)
    is_active = models.BooleanField(_("active"),default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    hide_phone = models.BooleanField(default=True)

    USERNAME_FIELD = "username"
    PHONE_FIELD = "phone"
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    def __str__(self):
        if self.username:
            return self.username
        else:
            return '-'

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


    def full_name(self):
        if self.profile.first_name and self.profile.last_name:
            return f'{self.profile.first_name} {self.profile.last_name} ({self.username})'
        else:
            return self.username

    def get_profile_image(self):
        if self.profile.image:
            return self.profile.image.url
        else:
            return None