# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from lib.models import BaseModel


class VMInstance(BaseModel):
    name = models.CharField(max_length=256, blank=True, null=True, verbose_name="实例名称")
    instance_id = models.CharField(max_length=256, blank=True, null=True, verbose_name="实例ID")
    instance_type = models.CharField(max_length=256, blank=True, null=True, verbose_name="实例类型")
    Launch_time = models.DateTimeField(null=True, blank=True)
    zone = models.CharField(max_length=256, blank=True, null=True)
    monitoring = models.CharField(max_length=256, blank=True, null=True)
    platform = models.CharField(max_length=128, blank=True, null=True)
    vpcid = models.CharField(max_length=128, blank=True, null=True)
    public_ip = models.CharField(max_length=256, blank=True, null=True)
    public_dns = models.CharField(max_length=256, blank=True, null=True)
    private_ip = models.CharField(max_length=256, blank=True, null=True)
    private_dns = models.CharField(max_length=256, blank=True, null=True)
    security_groups = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        app_label = "cloudres"
        verbose_name = "虚拟机"
        verbose_name_plural = "虚拟机"

    def __str__(self):
        return str(self.name)


class ResourceInfo(BaseModel):
    resource_id = models.CharField(verbose_name="资源ID", max_length=128)
    hostname = models.CharField(verbose_name="资源名称", max_length=128)
    ip = models.CharField(verbose_name="IP地址", max_length=128, null=True, blank=True)
    cloud_name = models.CharField(verbose_name="云环境名称", max_length=128)
    channel_name = models.CharField(verbose_name="渠道名称", max_length=128)

    def __str__(self):
        return str(self.resource_id)
