# Generated by Django 4.0.4 on 2022-08-21 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Chat', '0011_remove_unreadchatmessages_users_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unreadchatmessages',
            options={'verbose_name_plural': 'UnreadChatMessages'},
        ),
    ]
