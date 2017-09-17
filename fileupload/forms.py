# /usr/bin/env python
# -*- coding:utf-8 -*-
from django.forms import ModelForm

from fileupload.models import UploadFile


class UploadFileForm(ModelForm):

    class Meta:
        model = UploadFile
        fields = '__all__'