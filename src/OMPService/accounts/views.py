import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required

from .forms import UserForm
from .forms import ProfileForm
from .models import Profile
from cas_sync import models as cas_model

logger = logging.getLogger("django")


def login(request):
    if request.method == 'GET':
        uf = UserForm()
        return render(request, "login.html")
    else:
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect("/itsm/event_list/")
            else:
                # TODO 补全报错提醒
                return render(request, "login.html")
        else:
            return render(request, "login.html")


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/accounts/login/")


def user_profile(request):
    user = request.user
    url = request.META.get("HTTP_REFERER")

    profile, profile_created = Profile.objects.get_or_create(username=user.username)

    if request.method == "POST":
        if request.POST.get("destroy"):

            # 用户销毁
            username = request.user.username
            try:
                cas_user = cas_model.app_user.objects.using("cas_db").get(username=username)
                cas_user.delete(using="cas_db")
            except Exception as e:
                logger.info("cas用户: {} 删除异常".format(username), e)
            return HttpResponseRedirect("/accounts/logout/")
        form = ProfileForm(request.POST)
        if form.is_valid():
            data = form.data
            email = data.get("email")
            phone = data.get("phone")
            profile.email = email
            profile.phone = phone
            profile.save()
            return HttpResponseRedirect(url)
        else:
            messages.warning(request, "数据收敛失败")
            return HttpResponseRedirect(url)
    else:
        if profile_created:
            messages.warning(request, "用户配置文件自动创建,请维护具体信息")
        form = ProfileForm()
        return render(request, "user_profile.html", locals())

