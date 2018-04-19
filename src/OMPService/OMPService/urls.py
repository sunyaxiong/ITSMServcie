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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


api_patterns = [
        url(r'', include('itsm.urls')),
        url(r'', include('api.urls')),
        ]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^itsm/', include('itsm.urls')),
    url(r'^asset/', include('asset.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^/', include('accounts.urls')),
    url(r'^rest/', include(api_patterns, namespace='rest_api', app_name='ops')),
]
