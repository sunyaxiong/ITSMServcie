#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms

from .models import Event
from .models import Change


class EventDetailForm(forms.Form):

    emergency_degree = forms.ChoiceField(choices=Event.EMERGENCY_DEGREE)
    solution = forms.CharField(required=False)
    technician = forms.CharField()
    attach_file = forms.FileField(required=False)


class ChangeDetailForm(forms.Form):

    emergency_degree = forms.ChoiceField(choices=Change.EMERGENCY_DEGREE)
    solution = forms.CharField(required=False)
    node_handler = forms.CharField()
    attach_file = forms.FileField(required=False)
    description = forms.CharField(required=False)


class ChangeDetailModelForm(forms.ModelForm):

    description = forms.Textarea(attrs={"class": "type"})

    class Meta:
        model = Change
        fields = "__all__"


class EventDetailModelForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-group"}), label="事件名称"
    )
    description = forms.CharField(
        widget=forms.Select(attrs={"class": "form-control"}), label="事件描述"
    )

    class Meta:
        model = Event
        fields = "__all__"
