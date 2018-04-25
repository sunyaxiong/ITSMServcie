import time
import json
import logging

from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from OMPService import settings
from lib.fit2cloud import Fit2CloudClient
from .models import Profile, Channel

logger = logging.getLogger("django")


@receiver(post_save, sender="accounts.Profile")
def user_sync(sender, instance, created, *args, **kwargs):
    """
    Portal提交用户 --> itsm --> 云管
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:

        # 公共参数,实例化
        _conf = settings.CLOUD_CONF.copy()
        _conf.pop("user")  # 不传user,查询全部组织
        client = Fit2CloudClient(_conf, settings.cloud_secret_key)

        # 1 组织同步创建到itsm,优先创建组织; 信号控制sync到云管
        _, channel_created = Channel.objects.get_or_create(
            name=instance.channel_name,
        )
        logger.info("{}已经创建了".format(_))
        if channel_created:
            logger.info("itsm组织创建成功")

        # 当前组织信息查询打包
        org_res = client.org_get({"time_stamp": int(round(time.time() * 1000))})
        if org_res.get("success"):
            org_list = org_res.get("data")
            org_info = {i.get("name"): i for i in org_list}
            org_id = org_info[instance.channel_name]["id"]

            # 2 工作空间sync到云管 TODO 绑定组织,先查询
            name = "{}-{}".format(instance.channel_name, instance.department)
            post = {
                "name": name,
                "description": "sync",
                "costCenterId": org_id
            }
            workspace_add_res = client.workspace_add(
                {"time_stamp": int(round(time.time() * 1000))}, json.dumps(post)
            )
        else:
            logger.info("组织信息获取失败")

        # 3 用户sync到云管 TODO
        post = {
            "accessToken": "vstecs.c0m",
            "email": instance.email,
            "name": instance.username,
            "status": "active",
            "userType": 3
        }
        user_add_res = Fit2CloudClient(_conf, settings.cloud_secret_key).user_add(
            {"time_stamp": int(round(time.time() * 1000))}, json.dumps(post)
        )
        logger.info("useraddres: ", user_add_res)
        user_id = 0
        if user_add_res.get("success"):
            user_data = user_add_res.get("data")
            user_id = user_data["id"]

        # 4 授权 工作空间id 查询用户id 加上组织ID  角色ID 通过授权接口授权

        # 工作空间信息查询
        workspace_res = client.get_all_work_space(
            {"time_stamp": int(round(time.time() * 1000))}
        )
        print("wp_res: ", workspace_res)
        workspace_id = 0
        if workspace_res.get("success"):
            workspace_list = workspace_res.get("data")
            workspace_info = {i.get("name"): i for i in workspace_list}
            workspace_id = workspace_info[instance.department]["id"]

        # 工作空间授权授权
        if user_id and workspace_id:
            logger.info("用户id: {}, 工作空间id()正常生成".format(user_id, workspace_id))
            co_permission_post = {
                "groupId": workspace_id,
                "userId": user_id,
                "groupRoleId": 3,
            }
            co_permission_res = client.co_permission(
                {"time_stamp": int(round(time.time() * 1000))},
                json.dumps(co_permission_post),
            )
            logger.info("授权成功{}".format(co_permission_res))
        else:
            logger.info("授权失败,请检查")

        # # 用户同步创建到itsm, drop此功能,创建改到用户注册方法内
        # user_obj, user_created = User.objects.get_or_create(
        #     username=instance.username,
        #     email=instance.email,
        #     is_staff=1,
        #     is_active=1,
        # )
        # if user_created:
        #     print("ITSM用户: {} 创建成功".format(user_obj))
        # else:
        #     print("ITSM用户: {} 已经存在".format(user_obj))


@receiver(post_save, sender="accounts.Channel")
def channel_sync(sender, instance, created, *args, **kwargs):
    """
    渠道-组织同步, itsm --> 云管
    :param sender:
    :param instance:
    :param created:
    :param args:
    :param kwargs:
    :return:
    """
    if created:
        post = {
            "name": instance.name,
            "description": "sync",
        }
        _param = {
            "time_stamp": int(round(time.time() * 1000)),
        }
        _conf = settings.CLOUD_CONF.copy()
        res = Fit2CloudClient(_conf, settings.cloud_secret_key).org_add(
            _param, json.dumps(post)
        )
        if not res.get("success"):
            print(res.get("message"))
