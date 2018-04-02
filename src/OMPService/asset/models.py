from django.db import models

from lib.models import BaseModel


class Asset(BaseModel):
    deviceName = models.CharField("设备名", max_length=128, unique=True)
    deviceType = models.CharField("设备类型", max_length=128)
    computerRoomName = models.CharField("机房名称", max_length=128)
    positionAtRoom = models.CharField("机柜位置", max_length=128)
    sn = models.CharField("SN号", max_length=128)
    uPosition = models.IntegerField("U位")
    localIp = models.GenericIPAddressField("私有IP")
    manageIp = models.GenericIPAddressField("管理IP")
    publicIp = models.GenericIPAddressField("公网IP")
    os = models.CharField("操作系统", max_length=128)
    RAID = models.CharField("RAID", max_length=128)
    assetTypeNumber = models.CharField("设备型号", max_length=128)
    manager = models.CharField("管理员", max_length=128)
    double_power = models.BooleanField("是否双电", default=0)
    des = models.CharField("备注", max_length=256)

    def __str__(self):
        return self.deviceName


class Cpu(BaseModel):
    device = models.ForeignKey(Asset, verbose_name="关联设备")
    cpuType = models.CharField("cpu型号", max_length=128)
    cpuCoreNum = models.IntegerField("核心数")
    rate = models.CharField("主频", max_length=128)
    remark = models.TextField("备注")

    def __str__(self):
        return self.device.deviceName


class Mem(BaseModel):
    device = models.ForeignKey(Asset, verbose_name="关联设备")
    memType = models.CharField("内存型号", max_length=128)
    sn = models.CharField("SN号", max_length=128)
    size = models.CharField("容量", max_length=128)
    manufacturer = models.CharField("厂家", max_length=128)
    remark = models.TextField("备注")


class Disk(BaseModel):
    device = models.ForeignKey(Asset, verbose_name="关联设备")
    diskType = models.CharField("磁盘型号", max_length=128)
    sn = models.CharField("SN号", max_length=128)
    size = models.CharField("容量", max_length=128)
    interfaceType = models.CharField("接口类型", max_length=128)
    manufacturer = models.CharField("厂商", max_length=128)
    remark = models.TextField("备注")


class NetworkAdapter(BaseModel):
    device = models.ForeignKey(Asset, verbose_name="关联设备")
    ip = models.GenericIPAddressField("IP地址")
    front_device = models.CharField("上联设备", max_length=128)
    front_port = models.CharField("上联口", max_length=128)
    port_state = models.CharField("端口状态", max_length=128)
    remote_manage = models.CharField("远程管理卡状态", max_length=128)
    remark = models.TextField("备注")


class Port(BaseModel):
    device = models.ForeignKey(Asset, verbose_name="关联设备")
    vlanId = models.CharField("vlanID", max_length=128)
    portState = models.CharField("端口状态", max_length=128)
    connectedDevice = models.CharField("连接设备", max_length=128)
    port_num = models.CharField("端口号", max_length=128)


class Vlan(BaseModel):
    device = models.ForeignKey(Asset, verbose_name="关联设备")
    vlanNo = models.CharField("vlan号", max_length=128)
    vlanif = models.CharField("vlanif", max_length=128)


from .signals import asset_sync
# from .signals import cpu_sync
from .signals import asset_del_sync
from .signals import disk_sync