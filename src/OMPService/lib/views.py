import os
import json

from OMPService.settings import BASE_DIR


def get_module_name_list():
    """
    该函数获取flow_module下所有流程模板的文件名列表
    :return: module_name_list
    """
    file_list = os.listdir(BASE_DIR + "/itsm/flow_module")
    module_name_list = [i.split(".")[0] for i in file_list]

    return module_name_list


def get_module_info(module_name):
    """
    获取模板信息
    :param module_name: 模板名称
    :return:
    """
    with open(BASE_DIR + "/itsm/flow_module/{0}.json".format(module_name), "r") as f:
        data = json.load(f)
    return data


def get_structure_info(channel_name):
    """
    获取公司组织信息
    :param channel_name: 渠道\公司名称
    :return:
    """
    with open(
        BASE_DIR + "/itsm/organization_structure/{0}.json".format(channel_name), "r"
    ) as info:
        data = json.load(info)
    return data




def flow_judge(instance_type, **kwargs):
    """
    流程流转方法,根据流程实例类型和实例属性判断下一节点
    :param instance_type: 流程类型
    :param kwargs: 参数
    :return:
    """

if __name__ == "__main__":
    lst = get_module_info("event_module")
    print(lst)
