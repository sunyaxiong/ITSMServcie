#!/usr/bin/env python
"""
Fit2cloud API
"""
import hashlib
import requests
import base64
import hmac
import urllib.parse as urllib

from OMPService.settings import FIT2CLOUD_CONF
from OMPService.settings import secret_key


class Fit2CloudClient(object):
    """
    Fit2cloud API 签名验证
    """

    def __init__(self):
        """
        init
        :param conf:  参数
        """
        self.vm_query_url = "http://47.97.100.104:28080/rest/api/v1/vm/list"
        self.disk_query_url = "http://47.97.100.104:28080/rest/api/v1/disk/list"

    def build_signature(self, param):
        """
        生成签名
        :param param: dict
        :return:
        """
        temp_str = "&".join(
            ["{}={}".format(k, v) for k, v in sorted(param.items())]
        )
        hash_obj = hmac.new(
            secret_key.encode(), msg=temp_str.encode(), digestmod=hashlib.sha256
        )
        signature = base64.b64encode(hash_obj.digest())
        return signature

    def query_vm(self, param):
        """
        vm 查询接口 , GET
        :param param: dict vm接口参数传递
        :return:
        """
        # 打包字段
        param.update(FIT2CLOUD_CONF)

        signature = self.build_signature(param).decode()
        param["signature"] = signature

        url = "{}?{}".format(self.vm_query_url, urllib.urlencode(param))

        res = requests.get(url)
        return res.json()

    def query_disk(self, param):
        """
        磁盘 查询接口
        :param param: dict 磁盘接口参数传递
        :return:
        """
        param.update(FIT2CLOUD_CONF)

        signature = self.build_signature(param).decode()
        param["signature"] = signature

        url = "{}?{}".format(self.disk_query_url, urllib.urlencode(param))
        res = requests.get(url)

        return res.json()


if __name__ == "__main__":
    import hashlib
    import hmac
    import base64
    import urllib.parse as urllib

    params = {
                "cloud":"aws",
                "currPage":"1",
                "time_stamp":"1517158731548",
                "cloudAccountId":"1",
                "access_key":"c3VwcG9ydEBmaXQyY2xvdWQuY29t",
                "pageSize":"100",
                "signature_version":"v1",
                "version":"v1",
                "signature_method":"HmacSHA256",
                "account":"test123"
                }
    temp_str = "&".join(
        ["{}={}".format(k, v) for k, v in sorted(params.items())]
    )
    print("{}".format(temp_str))

    sk = '1f234efb-7d3c-46e8-bfed-edfc74012283'
    msg = "access_key=c3VwcG9ydEBmaXQyY2xvdWQuY29t&cloud=aws&cloudAccountId=1&signature_method=HmacSHA256&signature_version=v1&time_stamp=1517388801151&version=v1"
    j = hmac.new(sk.encode(), msg=msg.encode(), digestmod=hashlib.sha256)
    print("key: {}".format(sk))
    print("string: ", temp_str)
    print("hash: ", j.digest())
    print("base64: ", base64.b64encode(j.digest()).strip())
    print(base64.b64encode(j.digest()).strip().decode())
    print(urllib.urlencode(msg))