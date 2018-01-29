#!/usr/bin/env python


from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .models import Alert
from .models import DeployInstance
from .serializers import AlertSerializers
from .serializers import DeployInstanceSerializers


class AlertViewSet(viewsets.ModelViewSet):

    model = Alert
    serializer_class = AlertSerializers

    def get_queryset(self):
        queryset = Alert.objects.filter()
        return queryset


class DeployInstanceViewSet(viewsets.ModelViewSet):

    model = DeployInstance
    serializer_class = DeployInstanceSerializers

    def get_queryset(self):
        queryset = DeployInstance.objects.filter()
        return queryset
