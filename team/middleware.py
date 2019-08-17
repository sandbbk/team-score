import io
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from teamscore.log import Log


class LoggerMiddleware(MiddlewareMixin):
    """
        This middleware provides logging for any
        requests and responses.
    """

    def __init__(self, get_response):
        super().__init__(get_response)

    def write(self, request, file, response=None, exception=None):

        log = Log(request, response=response, exception=exception)
        buffer = io.StringIO()
        buffer.writelines(log.lines)

        with open(file, 'a') as f:
            if f.writable():
                f.writelines(buffer.getvalue())
        buffer.close()

    def process_request(self, request):
        self.write(request, settings.LOG_FILE)

    def process_response(self, request, response):
        self.write(request, settings.LOG_FILE, response=response)
        return response

    def process_exception(self, request, exception):
        self.write(request, settings.LOG_FILE, exception=exception)


class AllowCorsMiddleware(MiddlewareMixin):
    """
        This middleware checks for Origin header in requests
        and responses respective headers.
    """

    def process_response(self, request, response):

        origin = request.headers.get('Origin')

        allow_origin = settings.CORS_ORIGIN_ALLOW_ALL
        if allow_origin:
            response["Access-Control-Allow-Origin"] = '*'

        if origin is not None and request.method == 'OPTIONS':
            response['Allow'] += ', Origin'
            for header, value in settings.CORS_HEADERS.items():
                response[header] = value
        return response

