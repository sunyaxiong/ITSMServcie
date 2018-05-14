from django.db import models

from lib.models import BaseModel


class Alert(BaseModel):

    alertId = models.CharField("告警ID", max_length=128)
    alertName = models.CharField("告警名称", max_length=128)
    alertGrade = models.CharField("告警等级", max_length=128, default="1")
    f2cServerId = models.CharField("服务器在云管平台的ID", max_length=128)
    instanceId = models.CharField("实例ID", max_length=128, null=True, blank=True)
    instanceName = models.CharField("实例名称", max_length=128, null=True, blank=True)
    privateIp = models.GenericIPAddressField("私有IP", null=True, blank=True)
    publicIp = models.GenericIPAddressField("公有IP", null=True, blank=True)
    cloudAccountId = models.CharField("云账户ID", max_length=128)
    userId = models.CharField("用户ID", max_length=128)
    userName = models.CharField("用户名", max_length=128)
    alertMsg = models.TextField("告警信息")
    created = models.CharField("告警时间", max_length=128)

    def __str__(self):
        return self.name


class DeployInstance(BaseModel):

    chanel = models.CharField(verbose_name="渠道名称", max_length=128)
    consumer_number = models.CharField(verbose_name="客户电话", max_length=128)
    consumer_name = models.CharField(verbose_name="客户姓名", max_length=128)
    consumer_email = models.EmailField(verbose_name="客户邮箱")
    app_name = models.CharField(verbose_name="应用名称", max_length=128)
    cloud_env = models.CharField(verbose_name="云环境", max_length=128)
    cpu = models.IntegerField(verbose_name="CPU", null=True, blank=True)
    mem = models.IntegerField(verbose_name="内存", null=True, blank=True)
    is_vm_instance = models.BooleanField(verbose_name="是否创建虚拟机", default=0)
    order_number = models.CharField("订单号", max_length=128, default=0, null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(self.chanel, self.app_name)

    class Meta:
        app_label = "api"
        verbose_name = "deploy"
        verbose_name_plural = "deploy"


from .signals import deploy_to_event
from .signals import alert_to_event
