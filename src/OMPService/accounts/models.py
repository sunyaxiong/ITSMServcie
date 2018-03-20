import jsonfield

from django.db import models
from django.contrib.auth.models import User


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
    position = models.EmailField("岗位", null=True, blank=True)

    def __str__(self):
        return self.user.username
