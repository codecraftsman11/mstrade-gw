import json


class BitmexAPIException(Exception):

    def __init__(self, response, status_code, text):
        self.code = 0
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = f"Invalid JSON error message from Bitmex: {response.text}"
        else:
            self.code = json_res['error']['name']
            self.message = json_res['error']['message']
        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):
        return f"APIError({self.code}={self.message})"


class BitmexRequestException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"BitmexRequestException: {self.message}"
