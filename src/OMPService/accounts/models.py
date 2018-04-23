import jsonfield

from django.db import models
from django.contrib.auth.models import User

from lib.models import BaseModel


class Channel(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称", unique=True)
    event_module = jsonfield.JSONField(verbose_name="事件模板", null=True, blank=True)
    issue_module = jsonfield.JSONField(verbose_name="问题模板", null=True, blank=True)
    change_module = jsonfield.JSONField(verbose_name="变更模板", null=True, blank=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    username = models.CharField("用户名", max_length=128)
    channel_name = models.CharField("渠道名称", max_length=128)
    # user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # channel = models.ForeignKey(Channel, max_length=30, null=True, blank=True, verbose_name="渠道")
    phone = models.BigIntegerField("手机号", null=True, blank=True)
    email = models.EmailField("邮箱", null=True, blank=True)
    position = models.CharField("岗位", max_length=128, null=True, blank=True)
    department = models.CharField("部门", max_length=128, null=True, blank=True)

    def __str__(self):
        return self.username


class MessageAlert(BaseModel):
    """
    账户注册审核提醒;
    """
    ACTION_TYPE = (
        ("reg_info", "新用户审核提醒"),
    )

    user = models.ForeignKey(User)
    initiator = models.CharField("发起人", max_length=128, null=True, blank=True)
    content = models.TextField("提醒内容", null=True, blank=True)
    ins = models.CharField("流程类型", max_length=128, null=True, blank=True)
    ins_id = models.CharField("流程id", max_length=128, null=True, blank=True)
    action_type = models.CharField(
        "动作类型", max_length=128, null=True, blank=True, choices=ACTION_TYPE
    )
    checked = models.BooleanField("是否查看", default=0)


from .signals import user_sync
from .signals import channel_sync