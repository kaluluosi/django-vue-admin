#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/14 15:49
# @Author  : harry
import datetime
import json
import time

from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from dvadmin.system.models import Users, LoginLog, FileList
from dvadmin.system.views.login_log import LoginLogSerializer
from dvadmin.utils.json_response import DetailResponse


def jx_timestamp():
    cur_time = datetime.datetime.now()
    a = datetime.datetime.strftime(cur_time, '%Y-%m-%d %H:%M:%S')
    timeStamp = int(time.mktime(time.strptime(a, "%Y-%m-%d %H:%M:%S")))
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


class DataVViewSet(GenericViewSet):
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    extra_filter_backends = []
    ordering_fields = ['create_datetime']

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def homepage_statistics(self, request):
        # Users  新增
        # LoginLog  # 最后登录
        timestr = jx_timestamp().split(" ")
        min_time = datetime.datetime.strptime(timestr[0] + " " + "00:00:00", "%Y-%m-%d %H:%M:%S")
        max_time = datetime.datetime.strptime(timestr[0] + " " + "23:59:59", "%Y-%m-%d %H:%M:%S")
        # 今日注册
        today_register = Users.objects.filter(create_datetime__gte=min_time, is_superuser=0).count()
        # 今日登录
        today_login = len(set(LoginLog.objects.filter(create_datetime__gte=min_time).values_list('username')))
        # 三日新增
        Three_days_register = Users.objects.filter(
            create_datetime__gte=min_time - datetime.timedelta(days=3), is_superuser=0).count()
        # 七日新增
        Seven_days_register = Users.objects.filter(
            create_datetime__gte=min_time - datetime.timedelta(days=7), is_superuser=0).count()
        # 七日活跃
        Seven_days_login = len(set(LoginLog.objects.filter(
            create_datetime__gte=min_time - datetime.timedelta(days=7)).values_list('username')))
        # 月活跃
        month_login = len(set(LoginLog.objects.filter(
            create_datetime__gte=min_time - datetime.timedelta(days=30)).values_list('username')))
        # 七日用户登录数
        sum_days_login_list = []
        for i in range(7):
            sum_days_login_list.append({"time": (min_time + datetime.timedelta(days=-i)).strftime("%Y-%m-%d"),
                                        "count": len(set(LoginLog.objects.filter(
                                            create_datetime__lte=max_time - datetime.timedelta(days=i),
                                            create_datetime__gte=min_time - datetime.timedelta(days=i)).values_list(
                                            'username')))})

        # 七日注册用户数
        sum_days_register_list = []
        for i in range(7):
            sum_days_register_list.append(
                {"time": (min_time + datetime.timedelta(days=-i)).strftime("%Y-%m-%d"), "count": Users.objects.filter(
                    create_datetime__lte=max_time - datetime.timedelta(days=i),
                    create_datetime__gte=min_time - datetime.timedelta(days=i), is_superuser=0).count()})
        # 用户总数
        sum_register = Users.objects.filter(is_superuser=0).count()
        # FileList  附件
        today_f_l = FileList.objects.filter(create_datetime__gte=min_time).count()
        sum_f_l = FileList.objects.all().count()
        # 今日附件
        today_file = {'count': today_f_l, "occupy_space": 0}
        # 总附件
        sum_file = {'count': sum_f_l, "occupy_space": 0}
        data = {
            "today_register": today_register,
            "today_login": today_login,
            "Three_days_register": Three_days_register,
            "Seven_days_register": Seven_days_register,
            "Seven_days_login": Seven_days_login,
            "month_login": month_login,
            "sum_days_login_list": sum_days_login_list,
            "sum_days_register_list": sum_days_register_list,
            "sum_register": sum_register,
            "today_file": today_file,
            "sum_file": sum_file,
        }
        return DetailResponse(data=data, msg="获取成功")
