"""CAS login/logout replacement views"""

from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from django.utils.six.moves import urllib_parse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import (
    logout as auth_logout,
    login as auth_login,
    authenticate
)
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib.auth.models import User

from importlib import import_module

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from datetime import timedelta

from accounts.forms import RegisterForm
from accounts.models import Profile, Channel
from .signals import cas_user_logout
from .models import ProxyGrantingTicket, SessionTicket
from .utils import (get_cas_client, get_service_url,
                    get_protocol, get_redirect_url,
                    get_user_from_session)

logger = logging.getLogger("django")

__all__ = ['login', 'logout', 'callback', 'register']


@require_http_methods(["GET", "POST"])
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            logger.info("用户注册数据收敛成功")
            logger.info(form.data)
            data = form.data
            channels = Channel.objects.all().values("name")

            # 是否首次注册组织
            org_first_regist = True
            if data.get("org") in channels:
                org_first_regist = False

            Profile.objects.create(
                username=data.get("username"),
                channel_name=data.get("org"),
                position=data.get("position"),
                department=data.get("department"),
                email=data.get("email"),
                phone=data.get("phone"),
            )
            user = User.objects.create(
                username=data.get("username"),
                password=data.get("password"),
                email=data.get("email"),
                is_staff=1,
                is_active=0,
            )
            if user:
                logger.info("本地用户创建成功")

            # TODO 组织首次创建邮件激活;已存在组织创建用户,需要组织管理员审核
            if org_first_regist:
                # TODO 邮件激活 send mail
                subject = "{}您好,欢迎注册,请点击链接激活账户".format(data.get("username"))
                message = "点击激活: http://111.13.61.171:9999/accounts/active/{}".format(user.id)
                send_mail(subject, message, settings.EMAIL_HOST_USER, [data.get("email")])
                logger.info("itsm组织创建成功")
            else:
                # TODO 管理员审核消息MessageAlert创建
                pass

            return HttpResponseRedirect("/")
        else:
            return HttpResponse(form.errors)
    else:
        return render(request, "register.html")


def active(request, active_code):
    """
    激活用户
    :param request:
    :param active_code:
    :return:
    """
    try:
        user = User.objects.get(id=int(active_code))
        user.is_active = 1
        user.save()
        return HttpResponse("激活成功,请访问{}".format("http://111.13.61.171:9999/itsm/event_list"))
    except Exception as e:
        logger.info(e)
        return HttpResponse("激活失败,请联系管理员")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""
    service_url = get_service_url(request, next_page)
    client = get_cas_client(service_url=service_url)

    if not next_page and settings.CAS_STORE_NEXT and 'CASNEXT' in request.session:
        next_page = request.session['CASNEXT']
        del request.session['CASNEXT']

    if not next_page:
        next_page = get_redirect_url(request)

    if request.method == 'POST' and request.POST.get('logoutRequest'):
        clean_sessions(client, request)
        return HttpResponseRedirect(next_page)

    if request.user.is_authenticated():
        if settings.CAS_LOGGED_MSG is not None:
            message = settings.CAS_LOGGED_MSG % request.user.get_username()
            messages.success(request, message)
        return HttpResponseRedirect(next_page)

    ticket = request.GET.get('ticket')
    if ticket:
        user = authenticate(ticket=ticket,
                            service=service_url,
                            request=request)
        pgtiou = request.session.get("pgtiou")
        if user is not None:
            if not request.session.exists(request.session.session_key):
                request.session.create()
            auth_login(request, user)
            SessionTicket.objects.create(
                session_key=request.session.session_key,
                ticket=ticket
            )

            if pgtiou and settings.CAS_PROXY_CALLBACK:
                # Delete old PGT
                ProxyGrantingTicket.objects.filter(
                    user=user,
                    session_key=request.session.session_key
                ).delete()
                # Set new PGT ticket
                try:
                    pgt = ProxyGrantingTicket.objects.get(pgtiou=pgtiou)
                    pgt.user = user
                    pgt.session_key = request.session.session_key
                    pgt.save()
                except ProxyGrantingTicket.DoesNotExist:
                    pass

            if settings.CAS_LOGIN_MSG is not None:
                name = user.get_username()
                message = settings.CAS_LOGIN_MSG % name
                messages.success(request, message)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(client.get_login_url())
        else:
            raise PermissionDenied(_('Login failed.'))
    else:
        if settings.CAS_STORE_NEXT:
            request.session['CASNEXT'] = next_page
        return HttpResponseRedirect(client.get_login_url())


@require_http_methods(["GET"])
def logout(request, next_page=None):
    """Redirects to CAS logout page"""
    # try to find the ticket matching current session for logout signal
    try:
        st = SessionTicket.objects.get(session_key=request.session.session_key)
        ticket = st.ticket
    except SessionTicket.DoesNotExist:
        ticket = None
    # send logout signal
    cas_user_logout.send(
        sender="manual",
        user=request.user,
        session=request.session,
        ticket=ticket,
    )
    auth_logout(request)
    # clean current session ProxyGrantingTicket and SessionTicket
    ProxyGrantingTicket.objects.filter(session_key=request.session.session_key).delete()
    SessionTicket.objects.filter(session_key=request.session.session_key).delete()
    print("before", next_page)
    next_page = next_page or get_redirect_url(request)
    print("after: ", next_page)
    if settings.CAS_LOGOUT_COMPLETELY:
        protocol = get_protocol(request)
        host = request.get_host()
        redirect_url = urllib_parse.urlunparse(
            (protocol, host, next_page, '', '', ''),
        )
        client = get_cas_client()
        return HttpResponseRedirect(client.get_logout_url(redirect_url))
    else:
        # This is in most cases pointless if not CAS_RENEW is set. The user will
        # simply be logged in again on next request requiring authorization.
        return HttpResponseRedirect(next_page)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def callback(request):
    """Read PGT and PGTIOU sent by CAS"""
    if request.method == 'POST' and request.POST.get('logoutRequest'):
        clean_sessions(get_cas_client(), request)
        return HttpResponse("{0}\n".format(_('ok')), content_type="text/plain")
    elif request.method == 'GET':
        pgtid = request.GET.get('pgtId')
        pgtiou = request.GET.get('pgtIou')
        pgt = ProxyGrantingTicket.objects.create(pgtiou=pgtiou, pgt=pgtid)
        pgt.save()
        ProxyGrantingTicket.objects.filter(
            session_key=None,
            date__lt=(timezone.now() - timedelta(seconds=60))
        ).delete()
        return HttpResponse("{0}\n".format(_('ok')), content_type="text/plain")


def clean_sessions(client, request):
    for slo in client.get_saml_slos(request.POST.get('logoutRequest')):
        try:
            st = SessionTicket.objects.get(ticket=slo.text)
            session = SessionStore(session_key=st.session_key)
            # send logout signal
            cas_user_logout.send(
                sender="slo",
                user=get_user_from_session(session),
                session=session,
                ticket=slo.text,
            )
            session.flush()
            print(123123)
            # clean logout session ProxyGrantingTicket and SessionTicket
            ProxyGrantingTicket.objects.filter(session_key=st.session_key).delete()
            SessionTicket.objects.filter(session_key=st.session_key).delete()
        except SessionTicket.DoesNotExist:
            pass
