from django.db import models

from lib.models import BaseModel


class Alert(BaseModel):

    alert_id = models.CharField(verbose_name="告警ID", max_length=128)
    name = models.CharField(verbose_name="告警名称", max_length=128)
    grade = models.CharField(verbose_name="告警等级", max_length=128, default="common")
    alert_type = models.CharField(verbose_name="告警类型", max_length=128)
    state = models.CharField(verbose_name="告警状态", max_length=128)
    timestamp = models.CharField(verbose_name="时间戳", max_length=128)
    resource_id = models.CharField(verbose_name="资源ID", max_length=128)
    resource_name = models.CharField(verbose_name="资源名称", max_length=128, null=True, blank=True)
    resource_ip = models.CharField(verbose_name="资源IP", max_length=128, null=True, blank=True)
    technician = models.CharField(verbose_name="技术员", max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name


class DeployInstance(BaseModel):

    chanel = models.CharField(verbose_name="渠道名称", max_length=128)
    consumer_number = models.CharField(verbose_name="客户电话", max_length=11)
    consumer_name = models.CharField(verbose_name="客户姓名", max_length=128)
    consumer_email = models.EmailField(verbose_name="客户邮箱")
    app_name = models.CharField(verbose_name="应用名称", max_length=128)
    cloud_env = models.CharField(verbose_name="云环境", max_length=128)
    cpu = models.IntegerField(verbose_name="CPU", null=True, blank=True)
    mem = models.IntegerField(verbose_name="内存", null=True, blank=True)
    is_vm_instance = models.BooleanField(verbose_name="是否创建虚拟机", default=0)

    def __str__(self):
        return "{}-{}".format(self.chanel, self.app_name)

    class Meta:
        app_label = "api"
        verbose_name = "deploy"
        verbose_name_plural = "deploy"


from .signals import deploy_to_event
from .signals import alert_to_event
