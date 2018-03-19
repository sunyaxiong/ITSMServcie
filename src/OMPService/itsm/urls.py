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

from .viewsets import EventViewSet
from .views import index
from .views import request_list
from .views import events
from .views import incident_list
from .views import event_detail
from .views import event_add
from .views import event_close
from .views import event_to_change
from .views import event_to_issue
from .views import event_upgrade
from .views import changes
from .views import change_detail
from .views import change_add
from .views import change_to_config
from .views import flow_pass
from .views import issues
from .views import issue_detail
from .views import issue_close
from .views import config
from .views import config_overview
from .views import get_vm_list
from .views import get_disk_list
from .views import get_product_list
from .views import get_cluster_list
from .views import get_cluster_role_list
from .views import order_create
from .views import order_get


router = routers.DefaultRouter()

router.register("event", EventViewSet, base_name="EventViewSet")


urlpatterns = [
    url(r'', include(router.urls, namespace='restapi')),
    url(r'^$', index),

    # 事件管理
    url(r'^event_list/$', events),
    url(r'^request_list/$', request_list),
    url(r'^incident_list/$', incident_list),
    url(r'^event/(?P<pk>\d{1,9})', event_detail),
    url(r'^events/add/$', event_add),
    url(r'^events/close/(?P<pk>\d{1,9})', event_close),
    url(r'^events/event_to_change/(?P<pk>\d{1,9})', event_to_change),
    url(r'^events/event_to_issue/(?P<pk>\d{1,9})', event_to_issue),
    url(r'^events/event_upgrade/$', event_upgrade),

    # 变更管理
    url(r'^change_list/$', changes),
    url(r'^change/(?P<pk>\d{1,9})', change_detail),
    url(r'^change/pass/', flow_pass),
    url(r'^changes/add/$', change_add),
    url(r'^changes/change_to_config/(?P<pk>\d{1,9})', change_to_config),

    # 问题管理
    url(r'^issue_list/$', issues),
    url(r'^issue/(?P<pk>\d{1,9})', issue_detail),
    url(r'^issue/close/(?P<pk>\d{1,9})', issue_close),

    # 配置管理
    url(r'^config/$', config),
    url(r'^config_overview/$', config_overview),

    # CMDB
    url(r'cmdb/query_vm/$', get_vm_list),
    url(r'cmdb/query_disk/$', get_disk_list),

    # cloud config
    url(r'cloud/get_product_list/$', get_product_list),
    url(r'cloud/get_cluster_list/$', get_cluster_list),
    url(r'cloud/get_cluster_role_list/$', get_cluster_role_list),
    url(r'cloud/order_create/$', order_create),
    url(r'cloud/order_get/$', order_get),
]

