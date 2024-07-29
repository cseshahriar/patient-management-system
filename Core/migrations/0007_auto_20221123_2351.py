# Generated by Django 3.2.15 on 2022-11-23 17:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0006_alter_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True, validators=[django.core.validators.RegexValidator('^[\\d]{10,12}$', message='Format (ex: 0123456789)')], verbose_name='Mobile Phone'),
        ),
    ]
