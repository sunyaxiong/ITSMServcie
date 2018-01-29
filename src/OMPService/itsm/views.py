import datetime
import json

from django.shortcuts import render
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
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
from lib.views import get_module_name_list
from lib.views import get_module_info
from lib.views import get_structure_info


@login_required
def index(request):
    return render(request, 'base.html')


def events(request):

    page_header = "事件管理"
    data = Event.objects.filter().order_by("-dt_created")

    f = open(
        "/home/syx/workspace/JiajieOMP/src/OMPService/itsm"
        "/flow_module/change_module.json", "r"
    )
    import json
    mo = {
          "module_list": [
            {
              "module_name": "事件审批",
              "flow": [
                {
                  "node0": "开始"
                },
                {
                  "node1": "部门主管",
                  "notify": "邮件"
                },
                {
                  "node2": "总监,变更评审委员会2;",
                  "notify": "邮件,短信"
                },
                {
                  "node3": "结束"
                }
              ]
            },
            {
              "module_name": "变更审批",
              "flow": [
                {
                  "node0": "开始"
                },
                {
                  "node1": "部门主管",
                  "notify": "邮件"
                },
                {
                  "node2": "总监,变更评审委员会2;",
                  "notify": "邮件,短信"
                },
                {
                  "node3": "结束"
                }
              ]
            },
            {
              "module_name": "问题升级",
              "flow": [
                {
                  "node0": "开始"
                },
                {
                  "node1": "部门主管",
                  "notify": "邮件"
                },
                {
                  "node2": "总监,变更评审委员会2;",
                  "notify": "邮件,短信"
                },
                {
                  "node3": "结束"
                }
              ]
            }
          ],
          "event_type": Event.EVENT_CHOICE
        }
    cache.set("伟仕云安", mo)
    print(type(cache.get("伟仕云安")))
    print(cache.get("伟仕云安"))
    print(cache.get("EVENT_CHOICE"))

    return render(request, 'itsm/event_list.html', locals())


def event_detail(request, pk):
    page_header = "事件管理"
    event = Event.objects.get(id=int(pk))
    solution = event.solution
    user_list = User.objects.all()
    degree_choice_list = Event.EMERGENCY_DEGREE
    if request.method == "GET":

        # 解决方案列表,循环展示
        solution_list = solution.split("#")
        return render(request, 'itsm/event_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        event_form = EventDetailForm(request.POST)
        print(event_form.errors)
        if event_form.is_valid():
            # 拼接最新解决方案,解决方案格式:username + time + text
            now = datetime.datetime.now()
            if event_form.data.get("solution"):
                _solution = event_form.data["technician"] \
                            + now.strftime('%Y-%m-%d %H:%M:%S') \
                            + event_form.data["solution"]
                event.solution = solution + "#" + _solution

            if event_form.data.get("emergency_degree"):
                event.emergency_degree = event_form.data["emergency_degree"]

            if event_form.data.get("technician"):
                tc = User.objects.get(username=event_form.data.get("technician"))
                event.technician = tc

            if event_form.data.get("attach_file"):
                event.attach_file = event_form.data.get("attach_file")

            if event.state == "draft":
                event.state = "processing"
            event.save()
            return HttpResponseRedirect("/itsm/event_list/")
        return render(request, 'itsm/event_detail.html', locals())


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

        # 执行关闭
        event.state = "ended"
        event.save()
        return HttpResponseRedirect(url)
    except Exception as e:
        messages.warning(request, "事件查询异常: {}".format(e))
        return HttpResponseRedirect(url)


def event_to_change(request):
    pass


def event_to_issue(request, pk):

    url = request.META.get('HTTP_REFERER')

    try:
        event = Event.objects.get(id=pk)
        Issue.objects.create(
            name=event.name
        )
        return HttpResponseRedirect("/itsm/issue_list")
    except Exception as e:
        messages.warning(request, "事件未找到: {}".format(e))
        return HttpResponseRedirect(url)


def changes(request):

    page_header = "变更管理"
    data = Change.objects.filter()

    return render(request, 'itsm/change_list.html', locals())


def change_detail(request, pk):
    page_header = "变更管理"
    change = Change.objects.get(id=int(pk))
    solution = change.solution
    user_list = User.objects.all()
    degree_choice_list = Change.EMERGENCY_DEGREE
    module_list = get_module_name_list()
    if request.method == "GET":

        # 解决方案列表,循环展示
        solution_list = solution.split("#")
        return render(request, 'itsm/change_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        change_form = ChangeDetailForm(request.POST)
        if change_form.is_valid():
            pass
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


def change_to_config(request):
    pass


def change_reject_back(request):
    pass


def flow_pass(request):
    """
    传入流程实例,根据流程实例状态判断下一步动作
    :param request:
    :param instance:
    :return:
    """

    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        form = ChangeDetailForm(request.POST)
        if form.is_valid():
            data = form.data
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


def issues(request):

    page_header = "问题管理"
    data = Issue.objects.filter()
    return render(request, "itsm/issue_list.html", locals())


def issue_detail(request, pk):
    page_header = "问题管理"
    issue = Issue.objects.get(id=int(pk))
    solution = issue.solution
    user_list = User.objects.all()
    # degree_choice_list = Issue.EMERGENCY_DEGREE
    if request.method == "GET":

        # 解决方案列表,循环展示
        solution_list = solution.split("#")
        return render(request, 'itsm/issue_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        event_form = EventDetailForm(request.POST)
        print(event_form.errors)
        if event_form.is_valid():
            # 拼接最新解决方案,解决方案格式:username + time + text
            now = datetime.datetime.now()
            if event_form.data.get("solution"):
                _solution = event_form.data["technician"] \
                            + now.strftime('%Y-%m-%d %H:%M:%S') \
                            + event_form.data["solution"]
                issue.solution = solution + "#" + _solution

            if event_form.data.get("emergency_degree"):
                issue.emergency_degree = event_form.data["emergency_degree"]

            if event_form.data.get("technician"):
                tc = User.objects.get(username=event_form.data.get("technician"))
                issue.technician = tc

            if event_form.data.get("attach_file"):
                issue.attach_file = event_form.data.get("attach_file")

            if issue.state == "draft":
                issue.state = "processing"
            issue.save()
            return HttpResponseRedirect("/itsm/issues_list/")
        return render(request, 'itsm/issue_detail.html', locals())


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
