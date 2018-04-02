import time
import json

from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from OMPService import settings
from .forms import AssetForm
from .forms import CpuForm
from lib.fit2cloud import Fit2CloudClient


def asset_list(request):
    # 收敛前端提交参数
    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }

    # 获取vm接口数据
    res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).query_ph_device(param)
    data = res["data"]["items"] if res["code"] == "0000" else {}
    return render(request, "asset/asset_list.html", locals())


@csrf_exempt
def asset_add(request):

    url = request.META.get('HTTP_REFERER')
    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }
    # # test 数据
    # post = {
    #     "devices": [
    #         {
    #             "deviceName": "server-id-001",
    #             "deviceType": "web",
    #             "computerRoomName": "北京机房",
    #             "sn": "sn123456",
    #             "cupPosition": 8,
    #             "remoteIp": "192.168.1.1",
    #             "localIp": "47.24.16.88",
    #             "manageIp": "47.24.16.88",
    #             "des": "",
    #             "os": "linux",
    #             "raid": "",
    #             "type": "",
    #             "doublePower": 1,
    #             "manager": "张三",
    #             "dataState": 1
    #         }
    #     ]
    # }

    if request.method == "POST":

        form = AssetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # 根据运管数据格式打包
            post = {
                "devices": [
                    data
                ]
            }
            res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).ph_device_add(
                param, json.dumps(post)
            )

            return JsonResponse(res)
        messages.warning(request, form.errors)
        return HttpResponseRedirect(url)


def asset(request):

    url = request.META.get('HTTP_REFERER')

    if request.method == "POST":

        asset_form = AssetForm(request.POST)
        cpu_form = CpuForm(request.POST)
        # mem_form = CpuForm(request.POST)
        # disk_form = CpuForm(request.POST)
        if asset_form.is_valid():

            return HttpResponseRedirect(url)
    else:
        asset_form = AssetForm()
        cpu_form = CpuForm()

    return render_to_response('asset/asset.html', locals())
