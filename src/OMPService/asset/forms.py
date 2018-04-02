#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms import ValidationError


# class EventDetailForm(forms.Form):
#
#     emergency_degree = forms.ChoiceField(required=False, choices=Event.EMERGENCY_DEGREE)
#     solution = forms.CharField(required=False)
#     technician = forms.CharField(required=False)
#     attach_file = forms.FileField(required=False)
#
#     def clean_technician(self):
#         if self.data.get("technician") == "None":
#             raise ValidationError("请指派处理人")


class AssetForm(forms.Form):

    deviceName = forms.CharField(
        max_length=128, label="设备名"
    )
    deviceType = forms.CharField(
        max_length=128, label="设备类型"
    )
    computerRoomName = forms.CharField(
        max_length=128, label="机房名称"
    )
    positionAtRoom = forms.CharField(
        max_length=128, label="机柜位置"
    )
    sn = forms.CharField(
        max_length=128, label="SN号"
    )
    uPosition = forms.IntegerField(
        label="U位"
    )
    localIp = forms.GenericIPAddressField(
        max_length=128, label="私有IP"
    )
    manageIp = forms.GenericIPAddressField(
        max_length=128, label="管理IP"
    )
    publicIp = forms.GenericIPAddressField(
        max_length=128, label="互联网IP"
    )
    os = forms.CharField(
        max_length=128, label="操作系统"
    )
    RAID = forms.CharField(
        max_length=128, label="RAID配置"
    )
    assetTypeNumber = forms.CharField(
        max_length=128, label="设备型号"
    )
    manager = forms.CharField(
        max_length=128, label="管理员"
    )
    double_power = forms.IntegerField(
        label="是否双电源"
    )
    des = forms.CharField(
        max_length=128, label="设备描述"
    )


class CpuForm(forms.Form):

    deviceId = forms.CharField(
        max_length=128, label="设备ID"
    )
    deviceName = forms.CharField(
        max_length=128, label="设备名称"
    )
    cpuType = forms.CharField(
        max_length=128, label="cpu型号"
    )
    cpuCoreNum = forms.IntegerField(
        label="核心数"
    )
    rate = forms.CharField(
        max_length=128, label="主频"
    )
    remark = forms.CharField(
        max_length=128, label="备注"
    )
