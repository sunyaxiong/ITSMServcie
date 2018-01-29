#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import sys
import os
import django
from OMPService.settings import BASE_DIR
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OMPService.settings")
django.setup()
from cloudres.models import VMInstance


ec2 = boto3.client("ec2")
ec2_response = ec2.describe_instances()
data = []
for i in ec2_response["Reservations"]:
    _data = dict()
    tags = i["Instances"][0].get("Tags")
    if tags:
        _data["name"] = [k for k in tags if k.get("Key") == "Name"][0]["Value"]
    else:
        _data["name"] = ""
    # _data["name"] = i["Instances"][0].get("KeyName")
    _data["instance_id"] = i["Instances"][0].get("InstanceId")
    _data["instance_type"] = i["Instances"][0].get("InstanceType")
    _data["Launch_time"] = i["Instances"][0].get("LaunchTime")
    _data["zone"] = i["Instances"][0]["Placement"].get("AvailabilityZone")
    _data["monitoring"] = i["Instances"][0].get("Monitoring")
    _data["platform"] = i["Instances"][0].get("Platform")
    _data["vpcid"] = i["Instances"][0].get("VpcId")
    _data["private_dns"] = i["Instances"][0].get("PrivateDnsName")
    _data["private_ip"] = i["Instances"][0].get("PrivateIpAddress")
    _data["public_dns"] = i["Instances"][0].get("PublicDnsName")
    _data["security_group"] = i["Instances"][0].get("SecurityGroups")
    ins = VMInstance(**_data)
    data.append(ins)
    """
    print(dir(i))
    vm = dict()
    vm["instance_id"] = i.instance_id
    vm["instance_type"] = i.instance_type
    # vm["zone"] = ""
    vm["state"] = str(i.state)
    # vm["alert"] = ""
    vm["public_dns"] = i.public_dns_name
    vm["public_ip"] = i.public_ip_address
    vm["private_dns"] = i.private_dns_name
    vm["private_ip"] = i.private_ip_address
    # vm["key_pair"] = i.key_pair
    # vm["launch_time"] = i.launch_time
    vm["security_group"] = str(i.security_groups)
    if i.tags:
        vm["name"] = str([k for k in i.tags if k.get("Key") == "Name"][0]["Value"])
        # vm["name"] = "sss"
    else:
        vm["name"] = "syx"
    ins = VMInstance(**vm)
    data.append(ins)
    """

VMInstance.objects.bulk_create(data)
