from django.db import models

# Create your models here.


class TestDb(models.Model):

    name = models.CharField("名称", max_length=128)
    desc = models.CharField("描述", max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "cas_sync"


class app_user(models.Model):

    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    desc = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = "cas_sync"
        db_table = "app_user"
