# Generated by Django 5.1.6 on 2025-03-22 06:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_remove_approvalrequestform_initiate_dept_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvalrequestform',
            name='form_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.approvalrequestcategory'),
        ),
    ]
