# Generated by Django 5.1.6 on 2025-03-10 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_alter_approvalrequestform_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvalrequestform',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='department', to='mainapp.department'),
        ),
        migrations.AlterField(
            model_name='approvalrequestform',
            name='initiate_dept',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='initiate_dept', to='mainapp.department'),
        ),
    ]
