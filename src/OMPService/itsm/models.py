import jsonfield

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.core.cache import cache

from lib.models import BaseModel
from cloudres.models import VMInstance


class Event(BaseModel):

    EVENT_CHOICE = (
        ('draft', '草稿'),
        ('processing', '处理中'),
        ('issued', '转入问题'),
        ('changed', '转入变更'),
        ('checked', '审批完成'),
        ('ended', '结束')
    )

    EMERGENCY_DEGREE = (
        ("seriousness", "严重"),
        ("importance", "重要"),
        ("common", "普通")
    )

    TYPE = (
        ("incident", "故障报修"),
        ("request", "服务请求")
    )

    name = models.CharField(max_length=128, verbose_name="事件名称", null=True, blank=True)
    description = models.TextField(verbose_name="事件描述", null=True, blank=True)
    state = models.CharField(max_length=128, choices=EVENT_CHOICE, verbose_name="事件状态", null=True, blank=True)
    initiator = models.CharField("发起人", max_length=128, null=True, blank=True)
    initiator_phone = models.CharField("发起人电话", max_length=128, null=True, blank=True)
    initiator_email = models.CharField("发起人邮箱", max_length=128, null=True, blank=True)
    initiator_channel = models.CharField("发起人渠道", max_length=128, null=True, blank=True)
    department = models.CharField(max_length=128, verbose_name="部门", null=True, blank=True)
    technician = models.ForeignKey(
        User, verbose_name="处理人", null=True, blank=True
    )
    emergency_degree = models.CharField(
        verbose_name="紧急度", choices=EMERGENCY_DEGREE, max_length=128, null=True, blank=True
    )
    service_level = models.CharField(verbose_name="SLA", max_length=128, null=True, blank=True)
    event_type = models.CharField(
        max_length=128, verbose_name="事件类型", choices=TYPE, null=True, blank=True
    )
    resource = models.CharField(max_length=128, verbose_name="事件源", null=True, blank=True)
    solution = models.TextField(verbose_name="解决方法", null=True, blank=True)
    attach_file = models.FileField(verbose_name="附件", null=True, blank=True)
    flow_module = models.FileField(verbose_name="流程模板", null=True, blank=True)
    cloud_order = models.CharField(verbose_name="云管订单", max_length=128, null=True, blank=True)
    app_name = models.CharField("产品名称", max_length=128, null=True, blank=True)
    auto_deploy = models.BooleanField("是否自动化部署订单", default=0)

    def __str__(self):
        return self.name or ""

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        name = self.app_name
        query_set = ProductInfo.objects.filter(app_name=name).values("app_name")
        app_name_list = [i["app_name"] for i in query_set]
        if name in app_name_list:
            self.auto_deploy = 1
        super(Event, self).save(*args, **kwargs)


class Issue(BaseModel):

    name = models.CharField(max_length=128, verbose_name="问题名称")
    description = models.TextField(verbose_name="问题描述")
    state = models.CharField(max_length=128, verbose_name="问题状态")
    issue_type = models.CharField(max_length=128, null=True, blank=True, verbose_name="类型")
    handler = models.ForeignKey(User, verbose_name="处理人", null=True, blank=True)
    event_from = models.ForeignKey(Event, null=True, blank=True, verbose_name="事件源")
    solution = models.TextField(verbose_name="解决方法")
    attach_file = models.FileField(verbose_name="附件", null=True, blank=True)


class Change(BaseModel):
    EMERGENCY_DEGREE = (
        ("seriousness", "严重"),
        ("importance", "重要"),
        ("common", "普通")
    )

    STATE = (
        ("draft", "草稿"),
        ("ing", "流转中"),
        ("ended", "结束"),
    )

    name = models.CharField(max_length=128, verbose_name="变更名称", null=True, blank=True)
    description = models.TextField(verbose_name="变更描述")
    state = models.CharField(max_length=128, choices=STATE, default="draft", verbose_name="变更状态")
    initiator = models.CharField(max_length=128, null=True, blank=True, verbose_name="发起人")
    department = models.CharField(max_length=128, verbose_name="部门", null=True, blank=True)
    event = models.ForeignKey(Event, null=True, blank=True, verbose_name="关联事件")
    node_name = models.CharField(max_length=128, verbose_name="流程节点", null=True, blank=True)
    node_handler = models.ForeignKey(User, verbose_name="环节处理人", null=True, blank=True)
    emergency_degree = models.CharField(
        verbose_name="紧急度", max_length=128, null=True, blank=True,
        choices=EMERGENCY_DEGREE
    )
    service_level = models.CharField(verbose_name="SLA", max_length=128, null=True, blank=True)
    approver = models.CharField(verbose_name="变更评审", max_length=128, null=True, blank=True)
    # event_from = models.ForeignKey(VMInstance, null=True, blank=True, verbose_name="事件源")
    solution = models.TextField(verbose_name="解决方法", null=True, blank=True)
    online_plan = models.FileField(verbose_name="上线计划", null=True, blank=True)
    rollback_plan = models.FileField(verbose_name="回滚计划", null=True, blank=True)
    flow_node = models.IntegerField(verbose_name="当前流程节点", default=0)
    flow_module = models.CharField(verbose_name="流程模板", max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name or ""


class Config(BaseModel):

    name = models.CharField(max_length=128, verbose_name="名称")
    description = models.TextField(verbose_name="描述")
    state = models.BooleanField(max_length=128, verbose_name="状态", default=1)
    handler = models.CharField(max_length=128, verbose_name="处理人")
    # event_from = models.ForeignKey(VMInstance, null=True, blank=True, verbose_name="事件源")
    solution = models.TextField(verbose_name="解决方法")
    attach_file = models.FileField(verbose_name="附件", null=True, blank=True)
    event_module = jsonfield.JSONField(verbose_name="事件模板", null=True, blank=True)
    issue_module = jsonfield.JSONField(verbose_name="问题模板", null=True, blank=True)
    change_module = jsonfield.JSONField(verbose_name="变更模板", null=True, blank=True)
    sla_module = jsonfield.JSONField(verbose_name="sla配置", null=True, blank=True)

    def __str__(self):
        return self.name


class TimeTree(BaseModel):

    # generic relations
    username = models.CharField(max_length=128, null=True, blank=True, verbose_name="操作人")
    userid = models.IntegerField(verbose_name="操作人ID", null=True, blank=True)
    action = models.CharField(max_length=128, null=True, blank=True, verbose_name="操作")
    CONTENT_TYPE_LIMIT = models.Q(app_label='itsm', model='event'
                                  ) | models.Q(app_label='itsm', model='config')
    content_type = models.ForeignKey('contenttypes.ContentType', limit_choices_to=CONTENT_TYPE_LIMIT,
                                     verbose_name='content type', blank=True, null=True, editable=False)
    object_uuid = models.UUIDField(verbose_name='object uuid', editable=True, blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_uuid')


class Sla(BaseModel):
    pass


class ProductInfo(BaseModel):

    app_name = models.CharField("应用名称", max_length=128)
    product_id = models.CharField("云管产品ID", max_length=128, default=0)
    cloud_flag = models.CharField("云归属", max_length=128, default=0)
    standard = jsonfield.JSONField("规格", null=True, blank=True)
    vswitch = models.CharField("网络组", max_length=128, null=True, blank=True)

    def __str__(self):
        return self.app_name


class EventProcessLog(BaseModel):

    event_obj = models.ForeignKey(Event, related_name="logs", verbose_name="关联事件")
    username = models.CharField("用户名", max_length=256, blank=True, null=True)
    content = models.TextField("处理记录", blank=True, null=True)


class IssueProcessLog(BaseModel):
    issue_obj = models.ForeignKey(Issue, related_name="logs", verbose_name="关联问题")
    username = models.CharField("用户名", max_length=256, blank=True, null=True)
    content = models.TextField("处理记录", blank=True, null=True)


class ChangeProcessLog(BaseModel):
    change_obj = models.ForeignKey(Change, related_name="logs", verbose_name="关联变更")
    username = models.CharField("用户名", max_length=256, blank=True, null=True)
    content = models.TextField("处理记录", blank=True, null=True)