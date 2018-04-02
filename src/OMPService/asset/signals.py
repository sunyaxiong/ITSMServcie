import time
import json

from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from OMPService import settings
from .models import Asset, Cpu, Mem
from lib.fit2cloud import Fit2CloudClient


@receiver(post_save, sender="asset.Asset")
def asset_sync(sender, instance, created, *args, **kwargs):
    """
    触发CMDB创建
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:
        data = instance.__dict__.copy()
        data.pop("dt_created")
        data.pop("dt_updated")
        data.pop("_state")
        data.pop("id")
        print(data)
        param = {
            "time_stamp": int(round(time.time() * 1000)),
        }

        post = {
            "devices": [
                data
            ]
        }

        res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).ph_device_add(
            param, json.dumps(post)
        )
        print(res)
        return None


@receiver(post_delete, sender="asset.Asset")
def asset_del_sync(sender, instance, *args, **kwargs):
    """
    触发CMDB删除
    :param sender:
    :param instance:
    :param args:
    :param kwargs:
    :return:
    """

    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }

    post = {
        "deviceName": "ser01",
    }

    res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).ph_device_delete(
        param, json.dumps(post)
    )
    print(res)
    return None


@receiver(post_save, sender="asset.Cpu")
def cpu_sync(sender, instance, created, *args, **kwargs):
    """
    触发CMDB创建
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:
        data = instance.__dict__.copy()
        asset = instance.device
        data["deviceName"] = asset.deviceName
        data.pop("dt_created")
        data.pop("dt_updated")
        data.pop("_state")
        data.pop("_device_cache")
        data.pop("id")
        param = {
            "time_stamp": int(round(time.time() * 1000)),
        }

        post = {
            "cpus": [
                data
            ]
        }

        res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).ph_cpu_add(
            param, json.dumps(post)
        )
        print(res)
        return None


@receiver(post_save, sender="asset.Disk")
def disk_sync(sender, instance, created, *args, **kwargs):
    """
    触发CMDB创建
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:
        data = instance.__dict__.copy()
        asset = instance.device
        data["deviceName"] = asset.deviceName
        data.pop("dt_created")
        data.pop("dt_updated")
        data.pop("_state")
        data.pop("_device_cache")
        data.pop("id")
        param = {
            "time_stamp": int(round(time.time() * 1000)),
        }

        post = {
            "disks": [
                data
            ]
        }

        res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).ph_disk_add(
            param, json.dumps(post)
        )
        print(res)
        return None



