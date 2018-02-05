#!/usr/bin/env python
from django.http import JsonResponse


class ResultResponse(JsonResponse):
    def __init__(self, result, data='', msg='', safe=True, status=200):
        '''
        Result represent the error code, while bad things happend,
        and the data gives a blank string default.

        Using JsonResponse to make sure the `Content-Type` header
        is set to 'application/json'.
        '''

        content = {'code': result, 'data': data, 'msg': msg}
        super(ResultResponse, self).__init__(content, status=status, safe=safe)