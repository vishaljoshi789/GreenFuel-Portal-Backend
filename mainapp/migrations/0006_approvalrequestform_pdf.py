# Generated by Django 5.1.6 on 2025-07-29 19:18

import mainapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_remove_approvalrequestform_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvalrequestform',
            name='pdf',
            field=models.FileField(blank=True, default=None, null=True, upload_to=mainapp.models.approval_pdf_upload_path),
        ),
    ]
