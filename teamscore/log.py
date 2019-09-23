import datetime
import json
from django.conf import settings
from django.http import request as Req
from rest_framework.response import Response


class Log(object):

    def __init__(self, request, response=None, exception=None):
        self.request = request
        self.response = response
        self.exception = exception
        self.lines = list()

        # Create the lines of log file( one section per request)

        self.lines.append(str(datetime.datetime.now()) + " ")

        if not response:
            if request.method not in ('GET', 'OPTIONS'):
                if not isinstance(request, Req.HttpRequest):
                    req_data = {k: v for k, v in (json.loads(self.request.body)).items() if k != 'password'}
                    self.lines.append(f'RAW data: {str(req_data)}; ')

            if self.request.user.is_anonymous:
                user = "anonymous; "
            else:
                user = f'{self.request.user.email} '
            self.lines.append('User: ' + user)

            # path
            self.lines.append('Path: ' + request.path + '; ')

            #  GET data.
            if self.request.GET:
                self.lines.append(f'GET data: {str(self.request.GET)}; ')

            #  Files.
            files = self.request.FILES
            if files:
                self.lines.append(f'Files: {str(files)}; ')

            #  META.
            meta = {k: v for k, v in self.request.META.items() if k.startswith(settings.LOG_META_INFO)}
            self.lines.append(f'META data: {str(meta)}; ')

            #  Headers.
            self.lines.extend('Headers: ' + str(self.request.headers) + "\n")

        #  Response content
        else:
            resp = {k: v for k, v in response.items()}
            self.lines.append(f'Res_Headers: {str(resp)}; ')

            self.lines.append(f'Status-code: {response.status_code}; ')

            # if isinstance(response, Response):
            try:
                content = json.loads(response.content)
                self.lines.append('Content: ' + str(content) + "\n")

            except json.JSONDecodeError:
                content = response.content.decode("utf-8").split('\n')
                for line in content:
                    if line.strip().startswith('<title'):
                        self.lines.append('Content: ' + line.strip(' </title>') + "\n")

            self.lines.append('\n')

        # Exception content.
        if self.exception:
            self.lines.append(f'Exception: {repr(exception)}\n')
