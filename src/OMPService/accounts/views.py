from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required

from .forms import UserForm
from .forms import ProfileForm
from .models import Profile


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

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            data = form.data
    else:
        user = request.user
        try:
            profile = Profile.objects.get(username=user.username)
        except Exception as e:
            messages.warning(request, "用户配置文件加载失败,请维护配置信息")
        form = ProfileForm()
        return render(request, "user_profile.html", locals())

