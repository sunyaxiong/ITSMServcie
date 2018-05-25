from django.contrib import admin

from . import models


class AlertAdmin(admin.ModelAdmin):
    list_display = ("alertId", "alertName", "alertGrade", "f2cServerId", "instanceId")


class DeployAdmin(admin.ModelAdmin):
    list_display = ("chanel", "consumer_number", "consumer_name", "app_name", "order_number")

admin.site.register(models.Alert, AlertAdmin)
admin.site.register(models.DeployInstance, DeployAdmin)