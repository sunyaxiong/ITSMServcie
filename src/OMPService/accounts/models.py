import jsonfield

from django.db import models
from django.contrib.auth.models import User

from lib.models import BaseModel


class Channel(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")
    event_module = jsonfield.JSONField(verbose_name="事件模板", null=True, blank=True)
    issue_module = jsonfield.JSONField(verbose_name="问题模板", null=True, blank=True)
    change_module = jsonfield.JSONField(verbose_name="变更模板", null=True, blank=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, max_length=30, null=True, blank=True, verbose_name="渠道")
    phone = models.BigIntegerField("手机号", null=True, blank=True)
    email = models.EmailField("邮箱", null=True, blank=True)
    position = models.CharField("岗位", max_length=128, null=True, blank=True)

    def __str__(self):
        return self.user.username


class MessageAlert(BaseModel):
    """
    """
    user = models.ForeignKey(User)
    content = models.TextField("提醒内容", null=True, blank=True)
    ins = models.CharField("流程类型", max_length=128, null=True, blank=True)
    ins_id = models.CharField("流程id", max_length=128, null=True, blank=True)
    action_type = models.CharField("动作类型", max_length=128, null=True, blank=True)