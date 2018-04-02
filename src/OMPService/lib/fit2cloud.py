#!/usr/bin/env python
"""
Fit2cloud API
"""
import hashlib
import requests
import base64
import hmac
import logging
import urllib.parse as urllib
import json
from OMPService.settings import CMDB_CONF, secret_key
from OMPService.settings import CLOUD_HOST, CMDB_HOST


def my_replace(str):
    """
    replace 字符
    :param str: str
    :return:
    """
    return str.replace("=", "%3D").replace("@", "%40")


class Fit2CloudClient(object):
    """
    Fit2cloud API 签名验证
    """

    def __init__(self, conf, sk):
        """
        init
        :param conf:  公共参数
        :param sk: secret_key
        """
        self.conf = conf
        self.secret_key = sk
        self.vm_query_url = "http://{}:28080/rest/api/v1/vm/list".format(CMDB_HOST)
        self.disk_query_url = "http://{}:28080/rest/api/v1/disk/list".format(CMDB_HOST)
        self.order_create_url = "http://{}:28888/rest/api/v1/order/apply/product".format(CLOUD_HOST)
        self.order_get_url = "http://{}:28888/rest/api/v1/order/get".format(CLOUD_HOST)
        self.get_work_space_url = "http://{}:28888/rest/api/v1/group/list".format(CLOUD_HOST)
        self.product_list_url = "http://{}:28888/rest/api/v1/catalog/product/list".format(CLOUD_HOST)
        self.cluster_list_url = "http://{}:28888/rest/api/v1/cluster/list".format(CLOUD_HOST)
        self.cluster_role_list_url = "http://{}:28888/rest/api/v1/cluster/role/list".format(CLOUD_HOST)
        self.ph_device_list_url = "http://{}:28080/rest/api/v1/physical/device/list".format(CMDB_HOST)
        self.ph_cpu_add_url = "http://{}:28080/rest/api/v1/physical/cpu/add".format(CMDB_HOST)
        self.ph_disk_add_url = "http://{}:28080/rest/api/v1/physical/disk/add".format(CMDB_HOST)
        self.ph_device_add_url = "http://{}:28080/rest/api/v1/physical/device/add".format(CMDB_HOST)
        self.ph_device_delete_url = "http://{}:28080/rest/api/v1/physical/device/delete".format(CMDB_HOST)

    def build_signature(self, attrs):
        """
        生成签名
        :param attrs: dict
        :return:
        """
        temp_str = "&".join(
            ["{}={}".format(my_replace(k), my_replace(str(v)))
             for k, v in sorted(attrs.items())]
        )
        hash_obj = hmac.new(
            self.secret_key.encode(), msg=temp_str.encode(), digestmod=hashlib.sha256
        )
        signature = base64.b64encode(hash_obj.digest())
        return signature

    # def cloud_conf_build_signature(self, attrs):
    #     """
    #     生成签名
    #     :param attrs: dict
    #     :return:
    #     """
    #     temp_str = "&".join(
    #         ["{}={}".format(my_replace(k), my_replace(str(v)))
    #          for k, v in sorted(attrs.items())]
    #     )
    #     print("签名: {}".format(temp_str))
    #     hash_obj = hmac.new(
    #         cloud_secret_key.encode(), msg=temp_str.encode(), digestmod=hashlib.sha256
    #     )
    #     signature = base64.b64encode(hash_obj.digest())
    #     print(signature)
    #     return signature

    def query_ph_device(self, attrs):
        """
        查询物理设备接口
        :param attrs:
        :return:
        """
        attrs.update(self.conf)

        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature
        print(attrs)

        url = "{}?{}".format(self.ph_device_list_url, urllib.urlencode(attrs))

        res = requests.get(url)
        return res.json()

    def ph_device_add(self, attrs, post):
        """
        增加物理设备接口
        :param attrs:
        :return:
        """
        # 打包参数
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.ph_device_add_url, urllib.urlencode(attrs))
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, post, headers=headers)

        return res.json()

    def ph_device_delete(self, attrs, post):
        """
        增加物理设备接口
        :param attrs:
        :return:
        """
        # 打包参数
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.ph_device_delete_url, urllib.urlencode(attrs))
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, post, headers=headers)

        return res.json()

    def ph_cpu_add(self, attrs, post):
        """
        增加cpu接口
        :param attrs:
        :return:
        """
        # 打包参数
        attrs.update(self.conf)

        # 计算动态签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.ph_cpu_add_url, urllib.urlencode(attrs))
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, post, headers=headers)

        return res.json()

    def ph_disk_add(self, attrs, post):
        """
        增加disk接口
        :param attrs:
        :return:
        """
        # 打包参数
        attrs.update(self.conf)

        # 计算动态签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.ph_disk_add_url, urllib.urlencode(attrs))
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, post, headers=headers)

        return res.json()

    def query_vm(self, attrs):
        """
        vm 查询接口 , GET
        :param attrs: dict vm接口参数传递
        :return:
        """
        # 打包字段
        attrs.update(self.conf)

        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        url = "{}?{}".format(self.vm_query_url, urllib.urlencode(attrs))

        res = requests.get(url)
        return res.json()

    def query_disk(self, attrs):
        """
        磁盘 查询接口
        :param attrs: dict 磁盘接口参数传递
        :return:
        """
        attrs.update(self.conf)

        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        url = "{}?{}".format(self.disk_query_url, urllib.urlencode(attrs))
        res = requests.get(url)

        return res.json()

    def get_work_space(self, attrs):
        """
        云管平台获取工作空间动态ak和sk
        :param attrs: dict
        :return:
        """
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.get_work_space_url, urllib.urlencode(attrs))
        print(url)
        res = requests.get(url)
        print(res)
        print(res.json())
        data = res.json().get("data")[0]
        print(":::: ", data)
        logging.warning(data)
        if data:
            return data["accessKey"], data["secretKey"]
        logging.error(res.json)
        return 0, 0

    def order_create(self, attrs, post):
        """
        云管平台订单创建接口
        :param attrs: dict
        :param post: dict
        :return:
        """
        # 打包参数
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.order_create_url, urllib.urlencode(attrs))
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, post, headers=headers)

        return res.json()

    def order_get(self, attrs):
        """
        云管平台订单查询接口
        :param attrs: dict
        :return:
        """
        attrs.update(self.conf)

        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        url = "{}?{}".format(self.order_get_url, urllib.urlencode(attrs))
        res = requests.get(url)

        return res.json()

    def get_product_list(self, attrs):
        """
        产品列表请求
        :param attrs:
        :return:
        """
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.product_list_url, urllib.urlencode(attrs))
        res = requests.get(url)

        return res.json()

    def get_cluster_list(self, attrs):
        """
        集群列表请求
        :param attrs:
        :return:
        """
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.cluster_list_url, urllib.urlencode(attrs))
        res = requests.get(url)

        return res.json()

    def get_cluster_role_list(self, attrs):
        """
        主机组列表请求
        :param attrs:
        :return:
        """
        attrs.update(self.conf)

        # 计算签名
        signature = self.build_signature(attrs).decode()
        attrs["signature"] = signature

        # 发起请求
        url = "{}?{}".format(self.cluster_role_list_url, urllib.urlencode(attrs))
        res = requests.get(url)

        return res.json()


if __name__ == "__main__":
    # from OMPService.settings import CMDB_CONF, secret_key
    run = Fit2CloudClient(CMDB_CONF, secret_key)
    print(run)
    # import hashlib
    # import hmac
    # import base64
    # import urllib.parse as urllib
    # 
    # params = {
    #             "cloud":"aws",
    #             "currPage":"1",
    #             "time_stamp":"1517158731548",
    #             "cloudAccountId":"1",
    #             "access_key":"c3VwcG9ydEBmaXQyY2xvdWQuY29t",
    #             "pageSize":"100",
    #             "signature_version":"v1",
    #             "version":"v1",
    #             "signature_method":"HmacSHA256",
    #             "account":"test123"
    #             }
    # temp_str = "&".join(
    #     ["{}={}".format(k, v) for k, v in sorted(params.items())]
    # )
    # print("{}".format(temp_str))
    # 
    # sk = '1f234efb-7d3c-46e8-bfed-edfc74012283'
    # msg = "access_key=c3VwcG9ydEBmaXQyY2xvdWQuY29t&cloud=aws
    # &cloudAccountId=1&signature_method=HmacSHA256&signature_version=v1
    # &time_stamp=1517388801151&version=v1"
    # j = hmac.new(sk.encode(), msg=msg.encode(), digestmod=hashlib.sha256)
    # print("key: {}".format(sk))
    # print("string: ", temp_str)
    # print("hash: ", j.digest())
    # print("base64: ", base64.b64encode(j.digest()).strip())
    # print(base64.b64encode(j.digest()).strip().decode())
    # print(urllib.urlencode(msg))