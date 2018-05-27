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
from .views import event_create_order
from .views import event_to_change
from .views import event_to_issue
from .views import event_upgrade
from .views import event_to_close
from .views import changes
from .views import change_detail
from .views import change_add
from .views import change_to_config
from .views import flow_pass
from .views import change_reject_back
from .views import issues
from .views import issue_detail
from .views import issue_close
from .views import issue_upgrade
from .views import issue_to_knowledge
from .views import releases
from .views import release_detail
from .views import knowledges
from .views import sla_dashboard
from .views import sla_event_dash
from .views import sla_change_dash
from .views import sla_issue_dash
from .views import sla_release_dash
from .views import knowledge_detail
from .views import user_confirm
from .views import user_confirm_accept
from .views import user_confirm_reject
from .views import satisfaction_log
from .views import config
from .views import config_overview
from .views import get_vm_list
from .views import get_disk_list
from .views import get_product_list
from .views import get_cluster_list
from .views import get_cluster_role_list
from .views import order_create
from .views import order_get
from .views import user_get
from .views import get_instance_list
from .views import resource_info
from .views import get_department_name_list


router = routers.DefaultRouter()

router.register("event", EventViewSet, base_name="EventViewSet")


urlpatterns = [
    url(r'^rest/', include(router.urls)),
    url(r'^$', index),

    # 事件管理
    url(r'^event_list/$', events),
    url(r'^request_list/$', request_list),
    url(r'^incident_list/$', incident_list),
    url(r'^event/(?P<pk>\d{1,9})', event_detail),
    url(r'^events/add/$', event_add),
    url(r'^events/create_order/(?P<pk>\d{1,9})', event_create_order),
    url(r'^events/event_to_change/(?P<pk>\d{1,9})', event_to_change),
    url(r'^events/event_to_issue/(?P<pk>\d{1,9})', event_to_issue),
    url(r'^events/event_upgrade/$', event_upgrade),
    url(r'^events/close/(?P<pk>\d{1,9})', event_to_close),

    # 变更管理
    url(r'^change_list/$', changes),
    url(r'^change/(?P<pk>\d{1,9})', change_detail),
    url(r'^change/pass/$', flow_pass),
    url(r'^change/reject/$', change_reject_back),
    url(r'^changes/add/$', change_add),
    url(r'^changes/change_to_config/(?P<pk>\d{1,9})', change_to_config),

    # 问题管理
    url(r'^issue_list/$', issues),
    url(r'^issue/(?P<pk>\d{1,9})', issue_detail),
    url(r'^issue/close/(?P<pk>\d{1,9})', issue_close),
    url(r'^issue/upgrade/$', issue_upgrade),
    url(r'^issue/issue_to_knowledge/$', issue_to_knowledge),

    # 配置管理
    url(r'^config/$', config),
    url(r'^config/get_department_name_list/$', get_department_name_list),
    url(r'^config_overview/$', config_overview),


    # 发布管理
    url(r'^release_list/$', releases),
    url(r'^release/(?P<pk>\d{1,9})', release_detail),

    # 知识库管理
    url(r'^knowledge_list/$', knowledges),
    url(r'^knowledge/(?P<pk>\d{1,9})', knowledge_detail),

    # sla管理
    url(r'^sla/$', sla_dashboard),
    url(r'^sla/event_dash/$', sla_event_dash),
    url(r'^sla/issue_dash/$', sla_issue_dash),
    url(r'^sla/change_dash/$', sla_change_dash),
    url(r'^sla/release_dash/$', sla_release_dash),

    # CMDB
    url(r'cmdb/query_vm/$', get_vm_list),
    url(r'cmdb/query_disk/$', get_disk_list),

    # cloud config
    url(r'cloud/get_product_list/$', get_product_list),
    url(r'cloud/get_cluster_list/$', get_cluster_list),
    url(r'cloud/get_cluster_role_list/$', get_cluster_role_list),
    url(r'cloud/order_create/$', order_create),
    url(r'cloud/order_get/$', order_get),
    url(r'cloud/user_get/$', user_get),
    url(r'cloud/get_instance_list/$', get_instance_list),
    url(r'cloud/resource_info/$', resource_info),

    # message alert
    url(r'^user_confirm/(?P<pk>\d{1,9})', user_confirm),
    url(r'^user_confirm/accept/', user_confirm_accept),
    url(r'^user_confirm/reject/', user_confirm_accept),

    # 满意度
    url(r'^satisfaction/', satisfaction_log),
]

