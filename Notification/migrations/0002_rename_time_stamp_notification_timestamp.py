# Generated by Django 4.0.4 on 2022-05-24 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Notification', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='time_stamp',
            new_name='timestamp',
        ),
    ]
