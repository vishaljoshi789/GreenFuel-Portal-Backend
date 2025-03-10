# Generated by Django 5.1.6 on 2025-03-10 09:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_approvalrequestform_approvalprocess_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='designation',
            name='business_unit',
        ),
        migrations.RemoveField(
            model_name='user',
            name='business_unit',
        ),
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
        migrations.AddField(
            model_name='approvalrequestform',
            name='business_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.businessunit'),
        ),
        migrations.AddField(
            model_name='approvalrequestform',
            name='designation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.designation'),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('business_unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.businessunit')),
            ],
        ),
        migrations.AddField(
            model_name='approvalrequestform',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.department'),
        ),
        migrations.AddField(
            model_name='designation',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.department'),
        ),
    ]
