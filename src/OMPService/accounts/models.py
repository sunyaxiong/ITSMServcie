from django.db import models
from django.contrib.auth.models import User


class Channel(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, max_length=30, null=True, blank=True, verbose_name="渠道")

