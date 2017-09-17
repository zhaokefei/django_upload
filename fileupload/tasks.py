# /usr/bin/env python
# -*- coding:utf-8 -*-
import os
from datetime import datetime

from celery.schedules import crontab
from celery.task import periodic_task

from django.conf import settings


@periodic_task(run_every=(crontab(hour=0, minute=20)), name='room_members')
def get_room_members():
    media = settings.MEDIA_ROOT
    delete_file_floder(media)

    import pandas as pd


    m = pd.read_sql('''
    select ci.vcName as NowRoomName, vcChatRoomSerialNo as U_RoomID, count(*) from chatroom_info ci
    join chatroom_info_member cim on ci.id=cim.chatroommodel_id
    join member_info mi on mi.id=cim.memberinfo_id group by ci.vcChatRoomSerialNo
    ''', settings.CONN_URI_NEW)

    n = pd.read_sql('''
    select RoomID, NowRoomName, owner, U_RoomID from WeChatRoomInfo;
    ''', settings.WYETH_URI)

    g = pd.read_sql('''
    select RoomID, NowRoomName, owner, U_RoomID from WeChatRoomInfo;
    ''', settings.GEMII_B_URI)

    h = pd.concat([n, g])

    a = m.merge(h, how='left', on=['NowRoomName', 'U_RoomID'])

    a.to_excel(os.path.join(settings.BASE_DIR, 'media/{}.xlsx'.format(datetime.now().strftime("%Y-%m-%d %H:%M"))), index=False)


def delete_file_floder(media):
    if os.path.isfile(media):
        try:
            os.remove(media)
        except:
            pass
    elif os.path.isdir(media):
        for item in os.listdir(media):
            itemsrc = os.path.join(media, item)
            delete_file_floder(itemsrc)