# Generated by Django 4.0.4 on 2022-08-20 12:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Chat', '0008_unreadchatmessages_public_room_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='unreadchatmessages',
            name='users',
            field=models.ManyToManyField(help_text='users for public chat room', related_name='public_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='unreadchatmessages',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='private_user', to=settings.AUTH_USER_MODEL),
        ),
    ]