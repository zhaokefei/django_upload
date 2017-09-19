# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import StringIO
import os
import time
from datetime import datetime

import xlrd
import xlwt
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

# Create your views here.

from fileupload.forms import UploadFileForm
from fileupload.models import UploadFile


# def index(request):
#     media = settings.MEDIA_ROOT
#     files = os.listdir(media)
#     if not files:
#         return HttpResponse('please contact administor!')
#     file = files[0]
#     path = os.path.join(media, file)
#     if os.path.isfile(path):
#         wb = xlrd.open_workbook(path)
#         table = wb.sheets()[0]
#         room_nums = table.nrows
#         member_nums = int(sum(table.col_values(2)[1:]))
#         create_time = file.split('.')[0]
#
#         return render(request, "home.html",
#                       {
#                           'file_path': path,
#                           'file_name': file,
#                           'room_nums': room_nums,
#                           'member_nums': member_nums,
#                           'create_time': create_time
#                       })
#     return HttpResponse('please contact administor!')

def index(request):
    media = settings.MEDIA_ROOT
    files = os.listdir(media)
    if not files:
        return HttpResponse('please contact administor!')

    excel_dict = {}
    proxy_room_nums = 0
    proxy_member_nums = 0
    room_nums = 0
    member_nums = 0
    for i, file in enumerate(files):
        path = os.path.join(media, file)
        if os.path.isfile(path):
            time_type = (file.split('.')[0]).split('_')
            create_time = time_type[0]
            type = time_type[-1]
            if type == 'proxymembers':
                wb = xlrd.open_workbook(path)
                tables = wb.sheets()
                for table in tables:
                    proxy_room_nums += (table.nrows - 1)
                    proxy_member_nums += int(sum(table.col_values(2)[1:]))

                excel_dict[type] = {'path': path, 'file': file,
                                    'room_nums': proxy_room_nums,
                                    'member_nums': proxy_member_nums,
                                    'create_time': create_time}

            elif type == 'allmembers':
                wb = xlrd.open_workbook(path)
                tables = wb.sheets()
                for table in tables:
                    room_nums += (table.nrows - 1)
                    member_nums += int(sum(table.col_values(2)[1:]))

                excel_dict[type] = {'path': path, 'file': file,
                                    'room_nums': room_nums,
                                    'member_nums': member_nums,
                                    'create_time': create_time}

            # time_type = (file.split('.')[0]).split('_')
            # create_time = time_type[0]
            # type = time_type[-1]

            # excel_dict[i] = {'path': path, 'file': file,
            #                  'room_nums': room_nums, 'member_nums': member_nums,
            #                  'create_time': create_time, 'type': type}

    return render(request, 'home.html',
                  {
                      'excel_dict': excel_dict
                  })


    # file = files[0]
    # path = os.path.join(media, file)
    # if os.path.isfile(path):
    #     wb = xlrd.open_workbook(path)
    #     table = wb.sheets()[0]
    #     room_nums = table.nrows
    #     member_nums = int(sum(table.col_values(2)[1:]))
    #     create_time = file.split('.')[0]
    #
    #     return render(request, "home.html",
    #                   {
    #                       'file_path': path,
    #                       'file_name': file,
    #                       'room_nums': room_nums,
    #                       'member_nums': member_nums,
    #                       'create_time': create_time
    #                   })
    # return HttpResponse('please contact administor!')

def handle_uploaded_file(f, path):
    #从路径中提取出 文件名 和 文件所在文件夹路径
    t = path.split("/")
    file_name = t[-1]
    file_title = file_name.split(".")[0]
    extension = file_name.split(".")[-1]
    t.remove(t[-1])
    t.remove(t[0])
    path = "/".join(t)
    try:
        if not os.path.exists(path):
           os.makedirs(path)
        file_name = path + "/" + file_title + "." + 'xls'
        print file_name
        destination = open(file_name, 'wb+')
        for chunk in f.chunks():
            modify_chunk = handle_write_excel(file_name, chunk)
            destination.write(modify_chunk)
            destination.close()
    except Exception, e:
        print e
    file_path = file_name.split("/")
    file_path.remove(file_path[0])
    excel_path = '/'.join(file_path)
    return excel_path


def uploads(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
           upload_file = UploadFile.objects.create(name=request.FILES['file'].name, file=request.FILES['file']) #写入数据库
           path = upload_file.file.url
           file_name = handle_uploaded_file(request.FILES['file'], path)  # 上传处理
           upload_file.file = file_name
           upload_file.save()  # 保存
           return HttpResponseRedirect("/")
    else:
        form = UploadFileForm()
    return render(request, 'home.html', {'form': form})


def handle_write_excel(file_name, file_contents):
    wb = xlrd.open_workbook(
        filename=file_name, file_contents=file_contents)  # 关键点在于这里
    table = wb.sheets()[0]

    robot_ids = table.col_values(0)

    f = StringIO.StringIO()
    # 创建一个 excel
    file = xlwt.Workbook()
    write_table = file.add_sheet(u'机器人被封')

    for i, robot_id in enumerate(robot_ids):
        write_table.write(i, 0, robot_id)

    file.save(f)
    return f.getvalue()


def download(request, f):
    t = f.split("/")
    file_name = t[-1]
    t.remove(t[-1])
    # t.remove(t[0])
    file_path = "/".join(t)
    def file_iterator(file_name, file_path, chunk_size=512):
        path = file_path +"/" + file_name
        with open(path) as f:
           while True:
              c = f.read(chunk_size)
              if c:
                 yield c
              else:
                 break
    try:
        response = StreamingHttpResponse(file_iterator(file_name, file_path))
        response['Content-Type'] = 'application/octet-stream'
        # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
    except:
        return HttpResponse("Sorry but Not Found the File")
    return response

# def download(request):
#
#     def get_room_members():
#         media = settings.MEDIA_ROOT
#         delete_file_floder(media)
#
#         import pandas as pd
#
#         wyeth_uri = 'mysql://root:t721si74@wechat4bot2wyeth.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn/wechat?charset=utf8mb4'
#         gemii_uri = 'mysql://root:t721si74@wechat4bot.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn/wechat?charset=utf8mb4'
#         gemii_b_uri = 'mysql://root:t721si74@wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn/wechat_group?charset=utf8mb4'
#         uconn_uri_new = 'mysql://root:t721si74@wechatbot4jbb.chnh6yhldzwc.rds.cn-north-1.amazonaws.com.cn/u_connector?charset=utf8mb4'
#
#         m = pd.read_sql('''
#         select ci.vcName as NowRoomName, vcChatRoomSerialNo as U_RoomID, count(*) from chatroom_info ci
#         join chatroom_info_member cim on ci.id=cim.chatroommodel_id
#         join member_info mi on mi.id=cim.memberinfo_id group by ci.vcChatRoomSerialNo
#         ''', uconn_uri_new)
#
#         n = pd.read_sql('''
#         select RoomID, NowRoomName, owner, U_RoomID from WeChatRoomInfo;
#         ''', wyeth_uri)
#
#         g = pd.read_sql('''
#         select RoomID, NowRoomName, owner, U_RoomID from WeChatRoomInfo;
#         ''', gemii_b_uri)
#
#         h = pd.concat([n, g])
#
#         a = m.merge(h, how='left', on=['NowRoomName', 'U_RoomID'])
#
#         a.to_excel(os.path.join(settings.BASE_DIR, 'media/{}_member.xlsx'.format(datetime.now().strftime("%Y-%m-%d"))), index=False)
#
#         path = os.path.join(media, os.listdir(media)[0])
#         with open(path) as f:
#            while True:
#               c = f.read()
#               if c:
#                  yield c
#               else:
#                  break
#
#     def delete_file_floder(media):
#         if os.path.isfile(media):
#             try:
#                 os.remove(media)
#             except:
#                 pass
#         elif os.path.isdir(media):
#             for item in os.listdir(media):
#                 itemsrc = os.path.join(media, item)
#                 delete_file_floder(itemsrc)
#
#
#     try:
#         # response = StreamingHttpResponse(file_iterator(file_name, file_path))
#         response = StreamingHttpResponse(get_room_members())
#         # response = StreamingHttpResponse(get_member())
#         response['Content-Type'] = 'application/octet-stream'
#         # response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
#         response['Content-Disposition'] = 'attachment;filename="{0}_member.xlsx"'.format(datetime.now().strftime("%Y-%m-%d"))
#     except:
#         return HttpResponse("Sorry but Not Found the File")
#     return response

