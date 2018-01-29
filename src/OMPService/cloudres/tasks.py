#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def mul(x=1, y=2):
    return x * y
