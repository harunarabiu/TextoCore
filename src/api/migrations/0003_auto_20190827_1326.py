# Generated by Django 2.2.4 on 2019-08-27 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_message_msg_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='msg_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]