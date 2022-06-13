import httpx


class BinanceAPIException(Exception):

    def __init__(self, response: httpx.Response):
        self.code = 0
        try:
            json_res = response.json()
        except Exception:
            self.message = 'Invalid Binance response error message'
        else:
            self.code = int(json_res['code'])
            self.message = json_res['msg'] if self.code != 0 else '504 Gateway Timeout'
        self.status_code = response.status_code
        self.response = response
        try:
            self.request = response.request
        except RuntimeError:
            self.request = None

    def __str__(self):
        return f"APIError: {self.code}, {self.message}"
