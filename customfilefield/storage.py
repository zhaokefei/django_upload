# /usr/bin/env python
# -*- coding:utf-8 -*-

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os, time


class FileStorage(FileSystemStorage):
    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        #初始化
        super(FileStorage, self).__init__(location, base_url)

    #重写 _save方法
    def _save(self, name, content):
        #文件扩展名
        ext = os.path.splitext(name)[1]
        #文件目录
        d = os.path.dirname(name)
        #定义文件名，以上传时间命名，像这样的一串数字144557245952
        fn = str(time.time())
        fn = ("").join(fn.split("."))
        #重写合成文件名
        name = os.path.join(d, fn + ext)
        #调用父类方法
        return super(FileStorage, self)._save(name, content)