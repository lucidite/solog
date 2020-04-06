# Reference: Testing Twisted Web Resources, https://bit.ly/2JvuMhA

import json

from twisted.internet.defer import succeed
from twisted.web.server import Site
from twisted.web.test.test_web import DummyRequest


class SimplogDummyRequest(DummyRequest):
    class Content:
        def __init__(self, content_data):
            self.content_data = content_data

        def getvalue(self):
            return json.dumps(self.content_data).encode('utf-8')

    def __init__(self, method, url, args=None, headers=None):
        if isinstance(url, bytes):
            url = url.decode('utf-8')
        segments = [segment.encode('utf-8') for segment in url.split('/')]
        super().__init__(segments)

        self.method = method

        headers = headers or {}
        args = args or {}
        for name, values in headers.items():
            if isinstance(name, str):
                name = name.encode('utf-8')
            values = [v.encode('utf-8') if isinstance(v, str) else v for v in values]
            self.setHeader(name, values)
        for arg_key, arg_value in args.items():
            if isinstance(arg_key, str):
                arg_key = arg_key.encode('utf-8')
            if isinstance(arg_value, str):
                arg_value = arg_value.encode('utf-8')
            self.addArg(arg_key, arg_value)

        self.content = self.__class__.Content(content_data=args.get('data'))

    def value(self):
        return ''.join(elem.decode('utf-8') for elem in self.written)


def _resolve_result(request, result):
    if isinstance(result, bytes):
        request.write(result)
        request.finish()
        return succeed(request)
    elif isinstance(result, str):
        request.write(result.encode('utf-8'))
        request.finish()
        return succeed(request)
    else:
        raise ValueError(f"Unexpected result: {result}")


class DummySite(Site):
    def get(self, url, args=None, headers=None):
        return self._request("GET", url, args, headers)

    def post(self, url, args=None, headers=None):
        return self._request("POST", url, args, headers)

    def _request(self, method, url, args, headers):
        request = SimplogDummyRequest(method, url, args, headers)
        resource = self.getResourceFor(request)
        result = resource.render(request)
        return _resolve_result(request, result)
