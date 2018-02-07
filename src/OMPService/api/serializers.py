#!/usr/bin/env python


from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Alert
from .models import DeployInstance


class AlertSerializers(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("state") == "off":
            raise ValidationError("告警关闭")
        return attrs


class DeployInstanceSerializers(serializers.ModelSerializer):

    class Meta:
        model = DeployInstance
        fields = "__all__"

    # def validate(self, attrs):
    #     pass
