from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from .forms import UserForm


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
                return HttpResponseRedirect("/itsm/")
            else:
                # TODO 补全报错提醒
                return render(request, "login.html")
        else:
            return render(request, "login.html")


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/accounts/login/")
