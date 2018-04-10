import time
import json

from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from OMPService import settings
from lib.fit2cloud import Fit2CloudClient
from .models import Profile


@receiver(post_save, sender="accounts.Profile")
def user_sync(sender, instance, created, *args, **kwargs):
    """
    Portal提交用户 --> itsm --> 云管
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:

        # 用户同步创建到itsm
        User.objects.create(
            username=instance.username,
            email=instance.email,
            is_staff=1,
            is_active=1,
        )

        # 组织同步创建到itsm
        Profile.objects.get_or_create(
            name=instance.channel_name,
        )

        post = {
            "accessToken": "vstecs.c0m",
            "email": instance.email,
            "name": instance.username,
            "status": "active",
            "userType": 3
        }

        _param = {
            "time_stamp": int(round(time.time() * 1000)),
        }
        _conf = settings.CLOUD_CONF.copy()
        _conf.pop("user")
        res = Fit2CloudClient(_conf, settings.cloud_secret_key).user_add(_param, json.dumps(post))


@receiver(post_save, sender="accounts.Channel")
def channel_sync(sender, instance, created, *args, **kwargs):
    """
    渠道-工作空间同步, itsm --> 云管
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:
        post = {
            "name": instance.name,
            "description": "sync",
        }

        _param = {
            "time_stamp": int(round(time.time() * 1000)),
        }
        _conf = settings.CLOUD_CONF.copy()
        # _conf.pop("user")
        res = Fit2CloudClient(_conf, settings.cloud_secret_key).workspace_add(
            _param, json.dumps(post)
        )
        print("res: ", res)
