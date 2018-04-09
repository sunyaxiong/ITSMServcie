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
import django_cas_ng.views

from .views import login
from .views import logout
from .viewsets import ProfileViewSet, ChannelViewSet


router = routers.DefaultRouter()
router.register("profile", ProfileViewSet, base_name="profileViewset")
router.register("channel", ChannelViewSet, base_name="channelViewset")


urlpatterns = [
    url(r'', include(router.urls, namespace='profile')),
    # url(r'^login/$', login),
    # url(r'^logout/$', logout),
    url(r'^login/$', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^logout/$', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^callback/$', django_cas_ng.views.callback, name='cas_ng_proxy_callback'),
]

