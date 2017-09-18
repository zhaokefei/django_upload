# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class UploadFile(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to="uploads/%Y/%m")
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'uploadfile'


class RobotID(models.Model):
    robotid = models.CharField(max_length=50)

    class Meta:
        db_table = 'robotid'

