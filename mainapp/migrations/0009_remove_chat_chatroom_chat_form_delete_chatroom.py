# Generated by Django 5.1.6 on 2025-04-14 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_remove_approvalrequestform_category_max_level_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='chatroom',
        ),
        migrations.AddField(
            model_name='chat',
            name='form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.approvalrequestform'),
        ),
        migrations.DeleteModel(
            name='ChatRoom',
        ),
    ]
