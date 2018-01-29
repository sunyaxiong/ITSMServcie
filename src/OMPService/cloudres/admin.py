# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import VMInstance


class VMInstanceAdmin(admin.ModelAdmin):

    list_display = (
        "name", "instance_id", "instance_type", "platform", "monitoring", "public_ip", "security_groups",
        "zone", "Launch_time"
    )


admin.site.register(VMInstance, VMInstanceAdmin)