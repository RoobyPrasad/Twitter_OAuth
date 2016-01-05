import simplejson
from django.http import HttpResponse


class jsonify(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def handler(self, *args, **kwargs):
        """
        Return a JSON response
        """
        resp, status_code = self.func(*args, **kwargs)

        json_string = simplejson.dumps(resp,
                                       indent=3,
                                       use_decimal=True)

        return HttpResponse(json_string, content_type="application/json", status=status_code)