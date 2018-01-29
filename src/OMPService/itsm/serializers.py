#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Event


class EventSerializers(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"
