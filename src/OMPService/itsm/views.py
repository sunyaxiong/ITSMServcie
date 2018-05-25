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
from django.core.mail import EmailMultiAlternatives, send_mail

from OMPService import settings
from accounts.models import Profile, MessageAlert
from .models import Event
from .models import EventProcessLog
from .models import Change
from .models import ChangeProcessLog
from .models import Issue
from .models import IssueProcessLog
from .models import Release
from .models import Knowledge
from cas_sync import models as cas_model
from .models import Config
from .models import ProductInfo
from .models import SatisfactionLog
from .forms import EventDetailForm
from .forms import EventDetailModelForm
from .forms import ChangeDetailForm
from .forms import ChangeDetailModelForm
from .forms import IssueDetailForm
from .forms import SatisfactionForm
from .forms import IssueToKnowForm
from lib.views import get_module_name_list
from lib.views import get_module_info
from lib.views import get_structure_info
from lib.fit2cloud import Fit2CloudClient

logger = logging.getLogger("django")


def index(request):
    return render(request, 'index.html')


@login_required
def events(request):

    page_header = "事件管理"

    # 系统管理员全部权限
    if request.user.is_superuser:
        data = Event.objects.filter().order_by("-dt_created")
    else:
        data = Event.objects.filter(
            technician=request.user
        ).order_by("-dt_created")

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    return render(request, 'itsm/event_list.html', locals())


@login_required
def request_list(request):

    page_header = "事件管理"

    # 系统管理员全部权限
    if request.user.is_superuser:
        data = Event.objects.filter(event_type="request").order_by("-dt_created")
    else:
        data = Event.objects.filter(
            technician=request.user,
            event_type="request",
        ).order_by("-dt_created")

    return render(request, 'itsm/event_list.html', locals())


@login_required
def incident_list(request):

    page_header = "事件管理"
    # data = Event.objects.filter(event_type="incident").order_by("-dt_created")

    # 系统管理员全部权限
    if request.user.is_superuser:
        data = Event.objects.filter(event_type="incident").order_by("-dt_created")
    else:
        data = Event.objects.filter(
            technician=request.user,
            event_type="incident",
        ).order_by("-dt_created")

    return render(request, 'itsm/event_list.html', locals())


def event_detail(request, pk):
    page_header = "事件管理"
    event = Event.objects.get(id=int(pk))
    solution_list = event.logs.all() if event.logs else []
    user_list = User.objects.all()
    degree_choice_list = Event.EMERGENCY_DEGREE
    button_submit = "保存"
    host = settings.INTERNET_HOST

    # 根据事件状态控制前端显示
    button_submit = "提交" if event.state == "draft" else "保存"
    display = 0 if event.state == "ended" else 1
    checked = 1 if event.state == "checked" else 0

    if request.method == "GET":

        return render(request, 'itsm/event_detail1.html', locals())
    elif request.method == "POST":

        # form收敛数据
        event_form = EventDetailForm(request.POST)
        if event_form.is_valid():
            data = event_form.data

            if data.get("leak_checked") == "是":
                event.leak_checked = 1

            if data.get("emergency_degree"):
                event.emergency_degree = data["emergency_degree"]

            if not data.get("technician") == "None":
                tc = User.objects.filter(username=data.get("technician"))
                event.technician = tc[0]

            if data.get("attach_file"):
                event.attach_file = data.get("attach_file")

            if event.state == "draft":
                button_submit = "提交"
                event.state = "processing"

            # 更新解决方案
            if data.get("solution"):
                EventProcessLog.objects.create(
                    event_obj=event,
                    username=data.get("technician"),
                    content=data.get("solution"),
                )
            event.save()
            return HttpResponseRedirect("/itsm/request_list/")
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


def event_create_order(request, pk):
    url = request.META.get('HTTP_REFERER')
    try:
        event = Event.objects.get(id=pk)
        if event.state == "draft":
            messages.warning(request, "当前事件未提交")
            return HttpResponseRedirect(url)
        if event.technician_id is not request.user.id:
            messages.warning(request, "您不是当前处理人,无法关闭事件")
            return HttpResponseRedirect(url)

        if event.event_type == "request":

            # 应用对照信息查询
            app_name = event.app_name
            product_info = ProductInfo.objects.filter(app_name=app_name)
            if not product_info:
                messages.warning(request, "当前应用名称无法部署,请联系管理员维护应用对照信息")
                return HttpResponseRedirect(url)

            # 云管订单创建
            param = {
                "time_stamp": int(round(time.time() * 1000)),
            }
            post = {
                "clusterRoleId": 1,
                "count": 1,
                "description": "需要机器配置：1c1g",
                "expireTime": 4679277169,
                "installAgent": True,
                "productId": product_info[0].product_id
            }
            # 用户信息查询
            _conf = settings.CLOUD_CONF.copy()
            user_res = Fit2CloudClient(_conf, settings.cloud_secret_key).user_get(
                {"time_stamp": int(round(time.time() * 1000))}
            )
            if user_res.get("success"):
                user_data = user_res.get("data")
                user_info = {i["name"]: i for i in user_data}
                user_email = user_info[request.user.username]["email"]
                _conf["user"] = user_email
                # 工作空间接口请求
                ak, sk = Fit2CloudClient(
                    _conf, settings.cloud_secret_key
                ).get_work_space(param)

                if ak and sk:
                    _param = {
                        "time_stamp": int(round(time.time() * 1000)),
                    }
                    # _conf = settings.CLOUD_CONF.copy()
                    _conf["access_key"] = ak
                    order = Fit2CloudClient(_conf, sk).order_create(_param, json.dumps(post))
                    logger.info("新生成订单:  ", order)
                    event.cloud_order = order.get("data")
        else:
            # TODO 故障报修事件关闭逻辑
            pass
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
            emergency_degree="P3"
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


def event_upgrade(request):

    url = request.META.get('HTTP_REFERER')
    username = request.GET.get("username")
    event_id = request.GET.get("event_id")
    logging.warning("ajax test: {}: {}: {}".format(url, username, event_id))

    technician = User.objects.filter(username=username)
    event = Event.objects.filter(id=event_id)[0]
    event.technician = technician[0]
    event.save()

    return HttpResponseRedirect(url)


def event_to_close(request, pk):
    url = request.META.get("HTTP_REFERER")

    event = Event.objects.filter(id=pk)
    if event:

        #检查漏扫
        if not event.first().leak_checked:
            messages.warning(request, "请执行漏洞扫描")
            return HttpResponseRedirect(url)

        # 根据事件创建满意度调查
        sati_log = SatisfactionLog.objects.create(
            event=event[0]
        )
        # 组织邮件
        mail_to = event[0].initiator_email
        link = "http://111.13.61.171:9999/itsm/satisfaction/?log_id={}".format(sati_log.id)
        message = "您好,您的事件:{}已经处理完成,请对我们的服务做出评价,感谢您的支持. {}".format(
            event[0].name, link
        )
        send_mail("满意度调查", message, settings.EMAIL_HOST_USER, [mail_to])
        logger.info("满意度调查发送成功")

        # 修改事件状态
        event[0].state = "ended"
        event[0].save()
        return HttpResponseRedirect(url)
    else:
        messages.warning(request, "事件不存在,无法关闭,请联系管理员")
        return HttpResponseRedirect(url)


def changes(request):

    page_header = "变更管理"
    data = Change.objects.filter().order_by("-dt_created")

    return render(request, 'itsm/change_list.html', locals())


def change_detail(request, pk):
    page_header = "变更管理"
    change = Change.objects.get(id=int(pk))
    solution_list = change.logs.all().order_by("-dt_created") if change.logs else []
    user_list = User.objects.all()
    degree_choice_list = Change.EMERGENCY_DEGREE

    # 根据事件状态控制按钮显隐和名称
    button_submit = "提交" if change.state == "draft" else "同意"
    display = 0 if change.state == "ended" else 1

    if button_submit == "提交":
        action = "/itsm/change/{}".format(change.id)
    elif button_submit == "同意":
        action = "/itsm/change/pass/"

    change_form = ChangeDetailForm()
    if request.method == "GET":

        return render(request, 'itsm/change_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        change_form = ChangeDetailForm(request.POST)
        if change_form.is_valid():
            logger.info("变更数据收敛成功")
            data = change_form.data
            if change.state == "draft":
                change.state = "ing"
            if data.get("emergency_degree"):
                change.emergency_degree = data.get("emergency_degree")

            change.save()
            return HttpResponseRedirect("/itsm/change_list/")
        else:
            print(change_form)
            messages.warning(request, change_form.errors)
        return render(request, 'itsm/change_detail.html', locals())


def flow_pass(request):
    """
    传入流程实例,根据流程实例状态判断下一步动作
    :param request:
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
                change = Change.objects.get(id=change_id)
                now_node = int(change.flow_node)

                # 获取模板信息
                try:
                    module = change.node_handler.profile.channel.change_module
                    module_name = module.get("name")
                except Exception as e:
                    messages.warning(request, "模板获取失败")
                    return HttpResponseRedirect(url)

                next_node = now_node + 1
                next_node_name = module["flow"][next_node]["name"] if module else ""

                if next_node_name == "结束":
                    change.state = "ended"

                # TODO 环节处理人,根据模板查询
                channel = change.node_handler.profile.channel
                try:
                    next_node_handler_profile = Profile.objects.get(channel=channel, position=next_node_name)
                except Exception as e:
                    messages.warning(request, "岗位信息未维护")
                    return HttpResponseRedirect(url)
                next_node_handler_name = "syx"
                next_node_handler = User.objects.get(username=next_node_handler_name)

                # 修改
                if change.state == "draft":
                    change.state = "ing"
                if next_node == len(module["flow"]):
                    change.state = "ended"

                # 更新操作记录 节点加1
                if data.get("solution"):
                    ChangeProcessLog.objects.create(
                        change_obj=change,
                        username=request.user.username,
                        content=data.get("solution")
                    )
                change.node_handler = next_node_handler
                change.flow_node = next_node
                change.node_name = next_node_name
                change.node_handler = next_node_handler_profile.user
                change.save()
            except Exception as e:
                messages.info(request, "debug: {}".format(e))
                return HttpResponseRedirect(url)
            messages.info(request, "跳转成功")
            return HttpResponseRedirect(url)
        messages.warning(request, form.errors)
        return HttpResponseRedirect(url)


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

    url = request.META.get('HTTP_REFERER')

    change_id = request.GET.get("id")

    # 获取变更对象,并修改状态
    change = Change.objects.filter(id=change_id).first()
    if change.state == "draft":
        messages.warning(request, "事件未提交")
        return HttpResponseRedirect(url)
    change.state = "draft"
    change.flow_node = 0
    change.node_name = "开始"
    change.save()

    return HttpResponseRedirect(url)


def issues(request):

    page_header = "问题管理"
    data = Issue.objects.filter()
    return render(request, "itsm/issue_list.html", locals())


def issue_detail(request, pk):
    page_header = "问题管理"
    issue = Issue.objects.get(id=int(pk))
    solution_list = issue.logs.all() if issue.logs else []
    user_list = User.objects.all()
    degree_choice_list = Change.EMERGENCY_DEGREE

    # 根据事件状态控制按钮显隐和名称
    button_submit = "保存"
    display = 0 if issue.state == "off" else 1

    if request.method == "GET":

        # 解决方案列表,循环展示
        # solution_list = solution.split("#")
        return render(request, 'itsm/issue_detail.html', locals())
    elif request.method == "POST":

        # form收敛数据
        issue_form = IssueDetailForm(request.POST)
        if issue_form.is_valid():
            data = issue_form.data

            # 拼接最新解决方案,解决方案格式:username + time + text
            # now = datetime.datetime.now()
            # if data.get("solution"):
            #     _solution = data["handler"] \
            #                 + now.strftime('%Y-%m-%d %H:%M:%S') \
            #                 + data["solution"]
            #     issue.solution = solution + "#" + _solution

            if data.get("emergency_degree"):
                issue.emergency_degree = data["emergency_degree"]

            if data.get("handler"):
                tc = User.objects.get(username=data.get("handler"))
                issue.handler = tc

            if data.get("attach_file"):
                issue.attach_file = data.get("attach_file")

            if issue.state == "draft":
                issue.state = "processing"

                # 更新解决方案
            if data.get("solution"):
                IssueProcessLog.objects.create(
                    issue_obj=issue,
                    username=data.get("handler"),
                    content=data.get("solution"),
                )
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


def issue_upgrade(request):

    url = request.META.get('HTTP_REFERER')
    username = request.GET.get("username")
    issue_id = request.GET.get("issue_id")
    logging.warning("ajax test: {}: {}: {}".format(url, username, issue_id))

    handler = User.objects.filter(username=username)
    issue = Issue.objects.filter(id=issue_id)[0]
    issue.handler = handler[0]
    issue.save()

    return HttpResponseRedirect(url)


def issue_to_knowledge(request):
    url = request.META.get('HTTP_REFERER')

    if request.method == "POST":
        form = IssueToKnowForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info("问题转换知识库收据收敛成功")
            data = form.cleaned_data
            print("clean_data: ", form.cleaned_data)

            knowledge = Knowledge.objects.create(
                issue_id=data.get("issue_id"),
                issue_name=data.get("issue_name"),
                title=data.get("title"),
                content=data.get("content"),
                attach_file=data.get("attach_file"),
                creater=request.user.username,
                creater_id=request.user.id,
                classify=data.get("classify")
            )

            # 创建消息提醒组织管理员或者系统管理员
            if knowledge:
                try:
                    creater = Profile.objects.get(username=request.user.username)
                    org_admin = Profile.objects.filter(
                        channel_name=creater.channel_name,
                        org_admin=1,
                    ).first()
                    user = User.objects.filter(username=org_admin.username)
                except Exception as e:
                    logger.info("知识库审核消息异常: ", e)
                    user = User.objects.get(username="admin")

                content = "有新的知识库被创建,请审核"
                MessageAlert.objects.create(
                    user=user,
                    initiator=request.user.username,
                    content=content,
                    action_type="knowledge_info",
                )

            return HttpResponseRedirect("/itsm/knowledge_list/")
        messages.warning(request, form.errors)
        return HttpResponseRedirect(url)


@login_required
def releases(request):

    page_header = "发布管理"
    data = Release.objects.filter(
        technician=request.user
    ).order_by("-dt_created")

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    return render(request, 'itsm/release_list.html', locals())


def knowledges(request):
    page_header = "知识库"
    data = Knowledge.objects.filter(
    ).order_by("-dt_created")

    if request.GET.get("state") == "1":
        data = data.filter(state=1)

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    return render(request, 'itsm/knowledge_list.html', locals())


def knowledge_detail(request, pk):
    page_header = "事件管理"
    knowledge = Knowledge.objects.get(id=int(pk))
    if request.method == "GET":

        return render(request, 'itsm/knowledge_detail.html', locals())
    elif request.method == "POST":

        event_form = EventDetailForm(request.POST)

        messages.warning(request, event_form.errors)
        return render(request, 'itsm/knowledge_detail.html', locals())


def sla_dashboard(request):

    page_header = "SLA水平管理"

    event_count = Event.objects.all().count()
    change_count = Change.objects.all().count()
    issue_count = Issue.objects.all().count()
    releases_count = Release.objects.all().count()

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    if request.method == "POST":
        pass
    else:
        return render(request, "itsm/sla_dashboard.html", locals())


def sla_event_dash(request):

    page_header = "SLA水平管理-事件分析"

    event_queryset = Event.objects.all()
    event_sum_count = event_queryset.count()
    # 事件量统计
    req_count = event_queryset.filter(event_type="request").count()
    incident_count = event_queryset.filter(event_type="incident").count()
    done_event_count = event_queryset.filter(state="ended").count()
    ing_event_count = event_queryset.exclude(state="ended").count()

    late_event = event_queryset.filter(late_flag=1).count()
    normal_event = event_queryset.exclude(late_flag=1).count()
    done_p1_event = event_queryset.filter(service_level="P1", state="ended").count()
    ing_p1_event = event_queryset.exclude(service_level="P1", state="ended").count()

    print(req_count, incident_count, done_event_count, ing_event_count)

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    if request.method == "POST":
        pass
    else:
        return render(request, "itsm/sla_event_dash.html", locals())


def sla_change_dash(request):

    page_header = "SLA水平管理-变更分析"

    queryset = Change.objects.all()
    sum_count = queryset.count()
    # 变更量统计
    succ_count = queryset.filter(state="ended").count()
    fail_count = queryset.filter(state="failed").count()

    # 变更类型
    req_type = 10
    incident_type = 40

    reject_count = queryset.filter(state="reject").count()
    ended_count = queryset.filter(state="ended").count()

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    if request.method == "POST":
        pass
    else:
        return render(request, "itsm/sla_change_dash.html", locals())


def sla_issue_dash(request):

    page_header = "SLA水平管理-问题分析"

    queryset = Change.objects.all()
    sum_count = queryset.count()
    # 变更量统计
    req_count = queryset.filter().count()
    incident_count = queryset.filter().count()
    done_event_count = queryset.filter().count()
    ing_event_count = queryset.exclude().count()

    late_event = queryset.filter().count()
    normal_event = queryset.exclude().count()
    done_p1_event = queryset.filter().count()
    ing_p1_event = queryset.exclude().count()

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    if request.method == "POST":
        pass
    else:
        return render(request, "itsm/sla_issue_dash.html", locals())


def sla_release_dash(request):

    page_header = "SLA水平管理-发布分析"

    queryset = Change.objects.all()
    sum_count = queryset.count()
    # 变更量统计
    req_count = queryset.filter().count()
    incident_count = queryset.filter().count()
    done_event_count = queryset.filter().count()
    ing_event_count = queryset.exclude().count()

    late_event = queryset.filter().count()
    normal_event = queryset.exclude().count()
    done_p1_event = queryset.filter().count()
    ing_p1_event = queryset.exclude().count()

    message_alert_queryset = MessageAlert.objects.filter(
        user=request.user,
        checked=0,
    )
    message_alert_count = message_alert_queryset.count()

    if request.method == "POST":
        pass
    else:
        return render(request, "itsm/sla_release_dash.html", locals())


@csrf_exempt
def config(request):
    url = request.META.get('HTTP_REFERER')

    username = request.user.username
    org_name = Profile.objects.get(username=username).channel_name
    if org_name:
        department_obj, created = Config.objects.get_or_create(name=org_name)
        if created:
            department_obj.department = {"department": []}
        department_info = department_obj.department

    if request.method == "GET":
        try:
            # 获取配置文件
            res = cache.get("伟仕云安")
            module_name_list = [i["module_name"] for i in res["module_list"]]

            return render(request, 'itsm/config.html', locals())
        except Exception as e:
            logger.info(e)
            messages.warning(request, e)
            return render(request, 'itsm/config.html', locals())
    elif request.method == "POST":
        data = request.POST
        logger.info("config 收敛成功: ", data)

        # 部门新增逻辑
        if data.get("department"):
            config = Config.objects.get(name=org_name)
            config.department["department"].append(data.get("department"))
            config.save()
            logger.info("部门新增完成")

        return HttpResponseRedirect("/itsm/config/")


def get_department_name_list(request):
    """
    根据组织名称获取部门名称列表
    :param request:
    :return:
    """
    if request.method == "GET":

        data = request.GET
        org_name = data.get("org_name")
        department = Config.objects.get(name=org_name).department
        return JsonResponse(department)


def user_confirm(request, pk):
    page_header = "新用户审核"
    confirm_message = MessageAlert.objects.get(id=int(pk))
    content_list = confirm_message.content.split("-")
    org, department, username = content_list[0], content_list[1], content_list[2]
    profile = Profile.objects.filter(username=username).first()

    if request.method == "GET":

        return render(request, 'itsm/user_info_confirm.html', locals())
    elif request.method == "POST":
        pass
        return render(request, 'itsm/issue_detail.html', locals())


def user_confirm_accept(request):

    message_id = request.GET.get("id")
    try:
        message_info = MessageAlert.objects.get(id=int(message_id))

        # 用户激活
        user = User.objects.get(username=message_info.initiator)
        user.is_active = 1
        user.is_staff = 1
        user.save()

        # 消息查阅
        message_info.checked = 1
        message_info.save()

        # cas 用户创建逻辑放到审核消息
        cas_user, _ = cas_model.app_user.objects.using("cas_db").get_or_create(
            username=user.username,
        )
        if _:
            cas_user.password = user.password
            cas_user.save(using="cas_db")
            logger.info("CAS用户: {} 注册成功".format(cas_user.username))

        logger.info("用户信息审核成功")
        return HttpResponseRedirect("/itsm/event_list/")
    except Exception as e:
        logger.info(e, "用户信息审核失败")
        messages.warning(request, "用户信息审核失败")
        return HttpResponseRedirect("/itsm/event_list/")


def user_confirm_reject(request):
    url = request.META.get('HTTP_REFERER')

    message_id = request.GET.get("message_id")
    try:
        message_info = MessageAlert.objects.get(id=message_id)

        # 消息查阅
        message_info.checked = 1
        message_info.save()

    except Exception as e:
        logger.info(e)
        return HttpResponseRedirect(url)


def satisfaction_log(request):

    if request.method == "POST":
        form = SatisfactionForm(request.POST)
        if form.is_valid():
            logger.info("满意度数据收敛成功")
            data = form.data
            sati_id = data.get("sati_id")
            comment = data.get("comment")
            content = data.get("content")
            sati_info = SatisfactionLog.objects.filter(id=int(sati_id), checked=0)
            if sati_info:
                sati = sati_info.first()
                sati.comment = comment
                sati.content = content
                sati.checked = 1
                sati.save()
            return HttpResponse("评价成功")
        else:
            logger.info(form.errors)
    else:
        sati_log_id = request.GET.get("log_id")
        print(sati_log_id)
        try:
            sati_info = SatisfactionLog.objects.get(id=sati_log_id, checked=0)
            event = sati_info.event
        except Exception as e:
            logger.info(e)
            return HttpResponse("满意度调查已回复或者不存在")
        form = SatisfactionForm()
        return render(request, "satisfaction.html", locals())


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


def order_get(request):

    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }

    ak, sk = Fit2CloudClient(
        settings.CLOUD_CONF, settings.cloud_secret_key
    ).get_work_space(param)

    if ak and sk:
        _param = {
            "orderId": request.GET.get("order_id"),
            "time_stamp": int(round(time.time() * 1000)),
            # "time_stamp": 1517905240318,
        }
        _conf = settings.CLOUD_CONF.copy()
        _conf["access_key"] = ak
        _res = Fit2CloudClient(_conf, sk).order_get(_param)

        print(_res["success"])
        if _res["success"]:
            res = {
                "status": _res.get("data")["status"],
            }
        else:
            res = {
                "status": "NONE",
            }

        return JsonResponse(res)


def user_get(request):
    param = {
        "time_stamp": int(round(time.time() * 1000)),
    }
    _conf = settings.CLOUD_CONF.copy()
    _conf.pop("user")
    client = Fit2CloudClient(_conf, settings.cloud_secret_key)
    res = client.user_get(param)

    return JsonResponse(res)