#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from itsm.models import Event


@receiver(post_save, sender="api.DeployInstance")
def deploy_to_event(sender, instance, created, *args, **kwargs):
    """
    部署任务创建事件
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    event_name = "{}申请部署{}".format(instance.chanel, instance.app_name)
    Event.objects.create(
        name=event_name,
        state="draft",
        initiator="portal_sys",
        event_type="request",
        service_level="100",
        emergency_degree="common"
    )
    return None


@receiver(post_save, sender="api.Alert")
def alert_to_event(sender, instance, created, *args, **kwargs):
    """
    报警自动生成事件
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """

    event_name = "{}-{}-{}".format(instance.alertId, instance.alertGrade, instance.alertName)
    Event.objects.create(
        name=event_name,
        state="draft",
        event_type="incident",
        initiator="fit2cloud_sys",
        emergency_degree="importance",
    )
    return None
