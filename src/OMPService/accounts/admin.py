from django.contrib import admin

from .models import Profile
from .models import Channel


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "email")


class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "event_module", "issue_module", "change_module")


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Channel, ChannelAdmin)
