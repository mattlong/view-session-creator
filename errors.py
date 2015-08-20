import json
from functools import wraps


class BoxViewError(Exception):
    def __init__(self, response=None):
        super(Exception, self).__init__()
        self.status_code = response.status_code

        if response.headers.get('content-type') == 'application/json':
            self.response_json = response.json()
        else:
            self.response_json = '{}'

    def __repr__(self):
        return str(self)

    def __str__(self):
        self.response_json = json.dumps(
            self.response_json,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )

        return "\nHTTP Status: {0}\n{1}".format(
            self.status_code,
            self.response_json
        )


def raise_for_view_error(func):
    @wraps(func)
    def checked_for_view_error(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
            result.raise_for_status()
        except:
            raise BoxViewError(result)
        return result
    return checked_for_view_error
