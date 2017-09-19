# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from fileupload.models import UploadFile, RobotID


class UploadFileAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class RobotIDAdmin(admin.ModelAdmin):
    list_display = ('robotid', 'type')
    search_fields = ('robotid', 'type')


admin.site.register(RobotID, RobotIDAdmin)
admin.site.register(UploadFile, UploadFileAdmin)