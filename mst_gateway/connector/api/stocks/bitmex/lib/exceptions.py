import httpx


class BitmexAPIException(Exception):

    def __init__(self, response: httpx.Response):
        self.code = 0
        try:
            json_res = response.json()
        except Exception:
            self.message = 'Invalid Bitmex response error message'
        else:
            self.code = json_res['error']['name']
            self.message = json_res['error']['message']
        self.status_code = response.status_code
        self.response = response
        try:
            self.request = response.request
        except RuntimeError:
            self.request = None

    def __str__(self):
        return f"APIError: {self.code}, {self.message}"
