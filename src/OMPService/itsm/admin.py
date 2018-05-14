from django.contrib import admin

from .models import Event
from .models import EventProcessLog
from .models import Issue
from .models import Change
from .models import ChangeProcessLog
from .models import Config
from .models import TimeTree
from .models import ProductInfo
from .models import SatisfactionLog
from .models import Knowledge
from .models import Release


class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "technician", "event_type", "app_name")
    list_filter = ("state", "event_type")


class EventLogAdmin(admin.ModelAdmin):
    list_display = ("event_obj", "username", "content")


class IssueAdmin(admin.ModelAdmin):
    pass


class ChangeAdmin(admin.ModelAdmin):
    list_display = ("name", "state")


class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ("change_obj", "username", "content")


class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ("title", "state", "creater")


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ("name", "change", "stage", "initiator")


class ConfigAdmin(admin.ModelAdmin):
    list_display = (
        "name", "state", "event_module", "issue_module", "change_module", "sla_module"
    )


class ProductInfoAdmin(admin.ModelAdmin):
    list_display = (
        "app_name", "product_id", "cloud_flag", "standard", "vswitch"
    )


class SatisfactionAdmin(admin.ModelAdmin):
    list_display = (
        "event", "comment", "checked", "dt_created"
    )

class TimeTreeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event, EventAdmin)
admin.site.register(EventProcessLog, EventLogAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Change, ChangeAdmin)
admin.site.register(ChangeProcessLog, ChangeLogAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(TimeTree, TimeTreeAdmin)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(SatisfactionLog, SatisfactionAdmin)
admin.site.register(Knowledge, KnowledgeAdmin)
admin.site.register(Release, ReleaseAdmin)
