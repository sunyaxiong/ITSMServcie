import datetime
import json
import time
import logging

from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from lib.http import ResultResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

from OMPService import settings
from .models import Event
from .models import Change
from .models import Issue
from .models import Config
from .forms import EventDetailForm
from .forms import EventDetailModelForm
from .forms import ChangeDetailForm
from .forms import ChangeDetailModelForm
from .forms import IssueDetailForm
from lib.views import get_module_name_list
from lib.views import get_module_info
from lib.views import get_structure_info
from lib.fit2cloud import Fit2CloudClient


@login_required
def index(request):
    return render(request, 'base.html')


def events(request):

    page_header = "事件管理"
    data = Event.objects.filter().order_by("-dt_created")

    return render(request, 'itsm/event_list.html', locals())


def event_detail(request, pk):
    page_header = "事件管理"
    event = Event.objects.get(id=int(pk))
    solution = event.solution if event.solution else ""
    user_list = User.objects.all()
    degree_choice_list = Event.EMERGENCY_DEGREE
    button_submit = "保存"

    # 根据事件状态控制按钮显隐和名称
    button_submit = "提交" if event.state == "draft" else "保存"
    display = 0 if event.state == "ended" else 1

    if request.method == "GET":

        # 解决方案列表,循环展示
        try:
            solution_list = solution.split("#")
        except Exception as e:
            solution_list = []

        return render(request, 'itsm/event_detail1.html', locals())
    elif request.method == "POST":

        # form收敛数据
        event_form = EventDetailForm(request.POST)
        if event_form.is_valid():
            data = event_form.data
            print(data)
            # 拼接最新解决方案,解决方案格式:username + time + text
            now = datetime.datetime.now()
            if data.get("solution"):
                _solution = event_form.data["technician"] \
                            + now.strftime('%Y-%m-%d %H:%M:%S') \
                            + event_form.data["solution"]
                event.solution = solution + "#" + _solution

            if data.get("emergency_degree"):
                event.emergency_degree = data["emergency_degree"]

            if data.get("technician"):
                tc = User.objects.filter(username=data.get("technician"))
                event.technician = tc[0]

            if data.get("attach_file"):
                event.attach_file = data.get("attach_file")

            if event.state == "draft":
                button_submit = "提交"
                event.state = "processing"
            event.save()
            return HttpResponseRedirect("/itsm/event_list/")
        else:
            messages.warning(request, event_form.errors)
        return render(request, 'itsm/event_detail1.html', locals())


def event_add(request):
    page_header = "事件管理"
    url = request.META.get('HTTP_REFERER')
    if request.method == "GET":
        form = EventDetailModelForm()
        return render(request, 'itsm/new_event_detail.html', locals())
    elif request.method == "POST":
        form = EventDetailModelForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.warning(request, "异常: {}".format(form.errors))
            return HttpResponseRedirect(url)
        return HttpResponseRedirect("/itsm/event_list/")


def event_close(request, pk):
    url = request.META.get('HTTP_REFERER')
    try:
        event = Event.objects.get(id=pk)
        if event.state == "draft":
            messages.warning(request, "当前事件未提交")
            return HttpResponseRedirect(url)
        if event.technician_id is not request.user.id:
            messages.warning(request, "您不是当前处理人,无法关闭事件")
            return HttpResponseRedirect(url)

        # 云管订单创建
        param = {
            "time_stamp": int(round(time.time() * 1000)),
        }
        post = {
            "clusterRoleId": 2,
            "count": 1,
            "description": "需要机器配置：1c1g",
            "expireTime": 1518451199999,
            "installAgent": True,
            "productId": "c8509c0d-e518-4532-90d9-be8b840b1fc9"
        }
        # 工作空间接口请求
        ak, sk = Fit2CloudClient(
            settings.CLOUD_CONF, settings.cloud_secret_key
        ).get_work_space(param)

        if ak and sk:
            _param = {
                "time_stamp": 1517905240318,
            }
            _conf = settings.CLOUD_CONF.copy()
            _conf["access_key"] = ak
            order = Fit2CloudClient(_conf, sk).order_create(_param, json.dumps(post))
            print(order)
            event.cloud_order = order.get("data")

        # 执行关闭
        event.state = "ended"
        event.save()
        return HttpResponseRedirect(url)
    except Exception as e:
        messages.warning(request, "事件查询异常: {}".format(e))
        return HttpResponseRedirect(url)


def event_to_change(request, pk):

    url = request.META.get('HTTP_REFERER')

    try:
        event = Event.objects.get(id=pk)
        Change.objects.create(
            name=event.name,
            state="draft",
            node_handler=event.technician,
            initiator=event.technician.username,
        )
        return HttpResponseRedirect("/itsm/change_list")
    except Exception as e:
        messages.warning(request, "事件id{}未找到: {}".format(pk, e))
        return HttpResponseRedirect(url)


def event_to_issue(request, pk):

    url = request.META.get('HTTP_REFERER')

    try:
        event = Event.objects.get(id=pk)
        Issue.objects.create(
            name=event.name,
            state="on",
            handler=event.technician,
        )
        return HttpResponseRedirect("/itsm/issue_list")
    except Exception as e:
        messages.warning(request, "事件id{}未找到: {}".format(pk, e))
        return HttpResponseRedirect(url)


def changes(request):

    page_header = "变更管理"
    data = Change.objects.filter().order_by("-dt_created")

    return render(request, 'itsm/change_list.html', locals())


def change_detail(request, pk):
    page_header = "变更管理"
    change = Change.objects.get(id=int(pk))
    solution = change.solution
    user_list = User.objects.all()
    degree_choice_list = Change.EMERGENCY_DEGREE
    module_list = get_module_name_list()

    # 根据事件状态控制按钮显隐和名称
    button_submit = "提交" if change.state == "draft" else "同意"
    display = 0 if change.state == "ended" else 1

    if button_submit == "提交":
        action = "/itsm/change/{}".format(change.id)
    elif button_submit == "同意":
        action = "/itsm/change/pass/"

    if request.method == "GET":

        # 解决方案列表,循环展示
        if solution:
            solution_list = solution.split("#")
        return render(request, 'itsm/change_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        change_form = ChangeDetailForm(request.POST)
        if change_form.is_valid():
            data = change_form.data
            if change.state == "draft":
                change.state = "ing"
            if data.get("emergency_degree"):
                change.emergency_degree = data.get("emergency_degree")

            change.save()
            return HttpResponseRedirect("/itsm/change_list/")
        return render(request, 'itsm/change_detail.html', locals())


def change_add(request):
    page_header = "变更管理"

    if request.method == "GET":
        form = ChangeDetailModelForm()
        return render(request, 'itsm/new_change_detail.html', locals())
    elif request.method == "POST":
        form = ChangeDetailModelForm(request.POST)

        form.save()
        return HttpResponseRedirect("/itsm/change_list")


def change_close(request, pk):
    url = request.META.get('HTTP_REFERER')
    try:
        change = Change.objects.get(id=pk)
        if change.state == "ended":
            messages.warning(request, "当前变更已关闭")
            return HttpResponseRedirect(url)
        if change.node_handler_id is not request.user.id:
            messages.warning(request, "您不是当前处理人,无法处理该变更")
            return HttpResponseRedirect(url)

        # 执行关闭
        change.state = "ended"
        change.save()
        return HttpResponseRedirect(url)
    except Exception as e:
        messages.warning(request, "变更查询异常: {}".format(e))
        return HttpResponseRedirect(url)


def change_to_config(request):
    pass


def change_reject_back(request):
    pass


def flow_pass(request):
    """
    传入流程实例,根据流程实例状态判断下一步动作
    :param request:
    :return:
    """

    url = request.META.get('HTTP_REFERER')
    print(url)
    if request.method == "POST":
        form = ChangeDetailForm(request.POST)
        print(form.errors)
        if form.is_valid():
            data = form.data
            print(data)
            try:
                change_id = data.get("id")

                # 当前流程节点信息
                now = datetime.datetime.now()
                change = Change.objects.get(id=change_id)
                now_node = int(change.flow_node)
                solution = change.solution

                # 获取模板信息
                module_name = change.flow_module
                module_info = get_module_info(module_name)

                # 获取组织结构信息
                channel_name = "伟仕云安"
                organization_structure_info = get_structure_info(channel_name)

                # 下一环节
                _solution = "syx" + now.strftime('%Y-%m-%d %H:%M:%S') \
                            + data["solution"]
                next_node = now_node + 1
                next_node_name = module_info["flow"][next_node]["node{}".format(next_node)]
                if next_node_name == "结束":
                    change.state = "ended   "
                next_node_handler_name = "syx"
                next_node_user = User.objects.get(username=next_node_handler_name)

                # 修改
                if change.state == "draft":
                    change.state = "ing"

                change.node_handler = next_node_user
                change.flow_node = next_node
                change.node_name = next_node_name
                change.node_handler = next_node_user
                change.solution = solution + "#" + _solution
                change.save()
            except Exception as e:
                messages.info(request, "debug: {}".format(e))
                return HttpResponseRedirect(url)
            messages.info(request, "跳转成功")
            return HttpResponseRedirect(url)
        messages.warning(request, form.errors)
        return HttpResponseRedirect(url)


def issues(request):

    page_header = "问题管理"
    data = Issue.objects.filter()
    return render(request, "itsm/issue_list.html", locals())


def issue_detail(request, pk):
    page_header = "问题管理"
    issue = Issue.objects.get(id=int(pk))
    solution = issue.solution
    user_list = User.objects.all()
    degree_choice_list = Change.EMERGENCY_DEGREE

    # 根据事件状态控制按钮显隐和名称
    button_submit = "保存"
    display = 0 if issue.state == "off" else 1

    if request.method == "GET":

        # 解决方案列表,循环展示
        solution_list = solution.split("#")
        return render(request, 'itsm/issue_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        issue_form = IssueDetailForm(request.POST)
        if issue_form.is_valid():
            data = issue_form.data
            # 拼接最新解决方案,解决方案格式:username + time + text
            now = datetime.datetime.now()
            if data.get("solution"):
                _solution = data["handler"] \
                            + now.strftime('%Y-%m-%d %H:%M:%S') \
                            + data["solution"]
                issue.solution = solution + "#" + _solution

            if data.get("emergency_degree"):
                issue.emergency_degree = data["emergency_degree"]

            if data.get("handler"):
                tc = User.objects.get(username=data.get("handler"))
                issue.handler = tc

            if data.get("attach_file"):
                issue.attach_file = data.get("attach_file")

            if issue.state == "draft":
                issue.state = "processing"
            issue.save()
            return HttpResponseRedirect("/itsm/issue_list/")
        messages.warning(request, issue_form.errors)
        return render(request, 'itsm/issue_detail.html', locals())


def issue_close(request, pk):
    url = request.META.get('HTTP_REFERER')
    try:
        issue = Issue.objects.get(id=pk)
        if issue.state == "off":
            messages.warning(request, "当前问题已关闭")
            return HttpResponseRedirect(url)
        if issue.handler_id is not request.user.id:
            messages.warning(request, "您不是当前处理人,无法处理该问题")
            return HttpResponseRedirect(url)

        # 执行关闭
        issue.state = "off"
        issue.save()
        return HttpResponseRedirect(url)
    except Exception as e:
        messages.warning(request, "问题查询异常: {}".format(e))
        return HttpResponseRedirect(url)


def config(request):
    url = request.META.get('HTTP_REFERER')

    if request.method == "GET":

        # 获取配置文件
        res = cache.get("伟仕云安")
        module_name_list = [i["module_name"] for i in res["module_list"]]

        return render(request, 'itsm/config.html', locals())


@csrf_exempt
def config_overview(request):
    url = request.META.get('HTTP_REFERER')

    print(request.user.groups)
    res = cache.get("伟仕云安")
    import pprint
    pprint.pprint(res)
    module_name_list = [i["module_name"] for i in res["module_list"]]
    if request.method == "POST":
        return HttpResponse(json.dumps(module_name_list), content_type='application/json')


def get_vm_list(request):

    # 收敛前端提交参数
    param = {
        "cloudAccountId": 1,
        "time_stamp": int(round(time.time() * 1000)),
        "cloud": "aws",
    }

    # 获取vm接口数据
    res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).query_vm(param)
    return JsonResponse(res)


def get_disk_list(request):

    # 收敛前端提交参数
    param = {
        "cloudAccountId": 1,
        "time_stamp": int(round(time.time() * 1000)),
        "cloud": "aws",
    }

    # 获取disk接口数据
    res = Fit2CloudClient(settings.CMDB_CONF, settings.secret_key).query_disk(param)
    return JsonResponse(res)


def get_product_list(request):

    # 工作空间接口请求
    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }
    ak, sk = Fit2CloudClient(
        settings.CLOUD_CONF, settings.cloud_secret_key
    ).get_work_space(param)
    logging.error("ak, sk: ", ak, sk)

    # 打包生成的ak\sk
    if ak and sk:
        _param = {
            "currPage": 1,
            "pageSize": 1000,
            "time_stamp": int(round(time.time() * 1000)),
        }
        _conf = settings.CLOUD_CONF.copy()
        _conf["access_key"] = ak

        res = Fit2CloudClient(
            _conf, sk
        ).get_product_list(_param)
        return JsonResponse(res)
    logging.error("not product list")
    return JsonResponse({
        "code": "1001",
        "msg": "not product list"
    })


def get_cluster_list(request):

    # 工作空间接口请求
    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }
    ak, sk = Fit2CloudClient(
        settings.CLOUD_CONF, settings.cloud_secret_key
    ).get_work_space(param)
    logging.error("ak, sk: ", ak, sk)

    if ak and sk:
        _param = {
            # "currPage": 1,
            # "pageSize": 1000,
            "time_stamp": int(round(time.time() * 1000)),
        }
        _conf = settings.CLOUD_CONF.copy()
        _conf["access_key"] = ak

        res = Fit2CloudClient(_conf, sk).get_cluster_list(_param)

        return JsonResponse(res)

    logging.error("not cluster list")
    return JsonResponse({
        "code": "1001",
        "msg": "not cluster list"
    })


def get_cluster_role_list(request):

    # 工作空间接口请求
    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }
    ak, sk = Fit2CloudClient(
        settings.CLOUD_CONF, settings.cloud_secret_key
    ).get_work_space(param)
    # logging.error("ak, sk: ", ak, sk)

    if ak and sk:
        _param = {
            # "currPage": 1,
            # "pageSize": 1000,
            "clusterId": 1,
            "time_stamp": int(round(time.time() * 1000)),
        }
        _conf = settings.CLOUD_CONF.copy()
        _conf["access_key"] = ak

        res = Fit2CloudClient(_conf, sk).get_cluster_role_list(_param)

        return JsonResponse(res)

    logging.error("not cluster role list")
    return JsonResponse({
        "code": "1001",
        "msg": "not cluster role list"
    })


def order_create(request):

    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }

    post = {
        "clusterRoleId": 2,
        "count": 1,
        "description": "需要机器配置：1c1g",
        "expireTime": 1518451199999,
        "installAgent": True,
        "productId": "c8509c0d-e518-4532-90d9-be8b840b1fc9"
    }

    # 工作空间接口请求
    ak, sk = Fit2CloudClient(
        settings.CLOUD_CONF, settings.cloud_secret_key
    ).get_work_space(param)
    print("ak, sk : ", ak, sk)

    if ak and sk:
        _param = {
            # "time_stamp": int(round(time.time() * 1000)),
            "time_stamp": 1517905240318,
        }
        _conf = settings.CLOUD_CONF.copy()
        _conf["access_key"] = ak
        print("_conf: ", _conf)
        res = Fit2CloudClient(_conf, sk).order_create(_param, json.dumps(post))

        return JsonResponse(res)

    logging.error("not cluster create")
    return JsonResponse({
        "code": "1001",
        "msg": "not order create"
    })