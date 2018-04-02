from django.contrib import admin
from .models import Asset, Cpu, Mem, Disk, NetworkAdapter, Port, Vlan


class AssetAdmin(admin.ModelAdmin):

    list_display = [
        "deviceName", "deviceType", "computerRoomName", "positionAtRoom", "sn", "uPosition"
    ]


class CpuAdmin(admin.ModelAdmin):

    list_display = [
        "device", "cpuType", "cpuCoreNum", "rate", "remark",
    ]


class MemAdmin(admin.ModelAdmin):

    list_display = [
        "device", "memType", "sn", "size", "manufacturer", "remark"
    ]


class DiskAdmin(admin.ModelAdmin):

    list_display = [
        "device", "diskType", "sn", "size", "interfaceType", "manufacturer", "remark"
    ]


class NetworkAdapterAdmin(admin.ModelAdmin):

    list_display = [
        "device", "ip", "front_device", "front_port", "port_state", "remote_manage"
    ]


class PortAdmin(admin.ModelAdmin):

    list_display = [
        "device", "vlanId", "portState", "connectedDevice", "port_num"
    ]


admin.site.register(Asset, AssetAdmin)
admin.site.register(Cpu, CpuAdmin)
admin.site.register(Mem, MemAdmin)
admin.site.register(Disk, DiskAdmin)
admin.site.register(NetworkAdapter, NetworkAdapterAdmin)
admin.site.register(Port, PortAdmin)
