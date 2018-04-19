"""OMPService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls import include
from rest_framework import routers
import lib.django_cas_ng.views

from .views import login
from .views import logout
from .viewsets import ProfileViewSet, ChannelViewSet, UserViewSet


router = routers.DefaultRouter()
router.register("user", UserViewSet, base_name="userViewSet")
router.register("profile", ProfileViewSet, base_name="profileViewSet")
router.register("channel", ChannelViewSet, base_name="channelViewSet")


urlpatterns = [
    url(r'', include(router.urls, namespace='profile')),
    # url(r'^login/$', login),
    # url(r'^logout/$', logout),
    url(r'^register/$', lib.django_cas_ng.views.register, name='cas_ng_register'),
    url(r'^active/(?P<active_code>\d{1,9})', lib.django_cas_ng.views.active, name='cas_ng_active'),
    url(r'^login/$', lib.django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^logout/$', lib.django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^callback/$', lib.django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
]

