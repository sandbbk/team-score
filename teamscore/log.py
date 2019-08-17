import datetime
import json
from django.conf import settings


class Log(object):

    def __init__(self, request, response=None, exception=None):
        self.request = request
        self.response = response
        self.exception = exception
        self.lines = list()

        # Create the lines of log file( one section per request)

        self.lines.append(str(datetime.datetime.now()) + "\t")

        if not response:
            if request.method not in ('GET', 'OPTIONS'):
                req_data = {k: v for k, v in (json.loads(self.request.body)).items() if k != 'password'}
                self.lines.append(f'RAW data: {str(req_data)};\t')

            if self.request.user.is_anonymous:
                user = "anonymous;\t"
            else:
                user = f'{self.request.user.email}\t'
            self.lines.append('User: ' + user)

            #  GET data.
            if self.request.GET:
                self.lines.append(f'GET data: {str(self.request.GET)};\t')

            #  Files.
            files = self.request.FILES
            if files:
                self.lines.append(f'Files: {str(files)};\t')

            #  META.
            meta = {k: v for k, v in self.request.META.items() if k.startswith(settings.LOG_META_INFO)}
            self.lines.append(f'META data: {str(meta)};\t')

            #  Headers.
            self.lines.extend('Headers: ' + str(self.request.headers) + "\n")

        #  Response content
        else:
            resp = {k: v for k, v in response.items()}
            self.lines.append(f'Res_Headers: {str(resp)};\t')

            content = json.loads(response.content)
            self.lines.append('Content: ' + str(content) + "\n")
            self.lines.append('\n')

        # Exception content.
        if self.exception:
            self.lines.append(f'Exception: {repr(exception)}\n')

