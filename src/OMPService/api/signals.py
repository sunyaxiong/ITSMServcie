#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from itsm.models import Event


@receiver(post_save, sender="api.DeployInstance")
def deploy_to_event(sender, instance, created, *args, **kwargs):
    """

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
    )
    return None


@receiver(post_save, sender="api.Alert")
def alert_to_event(sender, instance, created, *args, **kwargs):
    """

    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    event_name = "{}-{}-{}".format(instance.grade, instance.alert_type, instance.name)
    Event.objects.create(
        name=event_name,
        state="draft",
    )
    print("alert signals......")
    return None
