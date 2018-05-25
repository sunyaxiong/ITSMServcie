#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from itsm.models import Event
from accounts import models as accounts_model


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

    # TODO org_admin处理订单审批流程
    try:
        org_admin = accounts_model.Profile.objects.filter(
            channel_name=instance.chanel,
            org_admin=1
        ).first()

        technician = User.objects.filter(username=org_admin.username).filter()

    except Exception as e:
        print(e)
        technician = User.objects.filter(username="admin").first()

    if instance.order_number:
        Event.objects.create(
            name=event_name,
            state="draft",
            initiator=instance.consumer_name,
            initiator_phone=instance.consumer_number,
            initiator_email=instance.consumer_email,
            initiator_channel=instance.chanel,
            event_type="request",
            service_level="100",
            emergency_degree="common",
            technician=technician,
            cloud_order=instance.order_number,
            auto_deploy=1,
        )
    else:
        Event.objects.create(
            name=event_name,
            state="draft",
            initiator=instance.consumer_name,
            initiator_phone=instance.consumer_number,
            initiator_email=instance.consumer_email,
            initiator_channel=instance.chanel,
            event_type="request",
            service_level="100",
            emergency_degree="common",
            technician=default_user,
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

    default_user = User.objects.filter(username=instance.username)[0]
    event_name = "{}-{}-{}".format(instance.alertId, instance.alertGrade, instance.alertName)
    Event.objects.create(
        name=event_name,
        state="draft",
        event_type="incident",
        initiator="fit2cloud_sys",
        emergency_degree="importance",
        technician=default_user,
    )
    return None
