# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-18 03:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0003_uploadfile_create_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='RobotID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robotid', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'robotid',
            },
        ),
    ]
