from django.contrib import admin

from .models import Event
from .models import Issue
from .models import Change
from .models import Config
from .models import TimeTree


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "technician")


class IssueAdmin(admin.ModelAdmin):
    pass


class ChangeAdmin(admin.ModelAdmin):
    list_display = ("name", "state")


class ConfigAdmin(admin.ModelAdmin):
    pass


class TimeTreeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event, EventAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Change, ChangeAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(TimeTree, TimeTreeAdmin)
