# /usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import os
import pandas as pd
from datetime import datetime

from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger

from django.conf import settings

from fileupload.models import RobotID

logger = get_task_logger(__name__)


# @periodic_task(run_every=(crontab(hour=10, minute=20)), name='room_members')
@periodic_task(run_every=(crontab(minute='*/5')), name='room_members')
def get_room_members():
    logger.info('enter get_room_members method')
    media = settings.MEDIA_ROOT
    delete_file_floder(media, type='A')

    m = pd.read_sql('''
    select ci.vcName as NowRoomName, vcChatRoomSerialNo as U_RoomID, count(*) as MemberCounts from chatroom_info ci
    join chatroom_info_member cim on ci.id=cim.chatroommodel_id
    join member_info mi on mi.id=cim.memberinfo_id group by ci.vcChatRoomSerialNo
    ''', settings.CONN_URI_NEW)

    n = pd.read_sql('''
    select RoomID, owner, U_RoomID from WeChatRoomInfo;
    ''', settings.WYETH_URI)

    g = pd.read_sql('''
    select RoomID, owner, U_RoomID from WeChatRoomInfo;
    ''', settings.GEMII_B_URI)

    h = pd.concat([n, g])

    # a = m.merge(h, how='left', on=['NowRoomName', 'U_RoomID'])
    a = m.merge(h, how='left', on=['U_RoomID'])

    a.to_excel(os.path.join(settings.BASE_DIR, 'media/{}_allmembers.xlsx'.format(datetime.now().strftime("%Y-%m-%d %H:%M"))), index=False)

    logger.info('end get_room_members method')


@periodic_task(run_every=(crontab(minute='*/4')), name='proxy_members')
def get_proxy_members():
    logger.info('enter get_proxy_members method')
    media = settings.MEDIA_ROOT
    delete_file_floder(media, type='B')

    path = os.path.join(settings.BASE_DIR, 'media/{}_proxymembers.xlsx'.format(datetime.now().strftime("%Y-%m-%d %H:%M")))

    ew = pd.ExcelWriter(path)

    proxy_types = ["1", "2", "3"]
    sheet_names = ["代理群1", "代理群2", "代理群3"]

    for type, sheet in zip(proxy_types, sheet_names):
        generate_proxy_excel(ew, type, sheet)

    ew.save()


def generate_proxy_excel(ew, type, sheet):

    robot_lists = (RobotID.objects.filter(type=type).values_list('robotid', flat=True))
    robot_ids = tuple([str(robotid) for robotid in robot_lists])

    m = pd.read_sql('''
    select ci.vcName as NowRoomName, vcChatRoomSerialNo as U_RoomID, count(*) as MemberCounts from chatroom_info ci
    join chatroom_info_member cim on ci.id=cim.chatroommodel_id
    join member_info mi on mi.id=cim.memberinfo_id where ci.vcRobotSerialNo in {} group by ci.vcChatRoomSerialNo
    '''.format(robot_ids), settings.CONN_URI_NEW)

    n = pd.read_sql('''
    select RoomID, owner, U_RoomID from WeChatRoomInfo;
    ''', settings.WYETH_URI)

    g = pd.read_sql('''
    select RoomID, owner, U_RoomID from WeChatRoomInfo;
    ''', settings.GEMII_B_URI)

    h = pd.concat([n, g])

    # a = m.merge(h, how='left', on=['NowRoomName', 'U_RoomID'])
    a = m.merge(h, how='left', on=['U_RoomID'])

    # a.to_excel(os.path.join(settings.BASE_DIR, 'media/{}_proxymembers.xlsx'.format(datetime.now().strftime("%Y-%m-%d %H:%M"))), index=False)
    a.to_excel(ew, sheet_name=sheet, index=False)

    logger.info('end get_proxy_members method')


def delete_file_floder(media, type):
    logger.info('enter delete_file_floder method')
    if os.path.isfile(media):
        try:
            file_name = os.path.basename(media).split('.')[0]
            file_type = file_name.split('_')[-1]
            if type == 'A' and file_type == 'allmembers':
                logger.info('delete allmembers excel file')
                os.remove(media)
            elif type == 'B' and file_type == 'proxymembers':
                logger.info('delete proxymembers excel file')
                os.remove(media)
        except Exception, e:
            logger.info('raise error %s' % e.message)
            pass
    elif os.path.isdir(media):
        for item in os.listdir(media):
            itemsrc = os.path.join(media, item)
            delete_file_floder(itemsrc, type)