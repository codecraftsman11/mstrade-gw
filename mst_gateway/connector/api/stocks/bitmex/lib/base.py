import json
import hashlib
import hmac
import time
import httpx
from urllib import parse
from typing import Optional, Tuple, Union
from .exceptions import BitmexAPIException, BitmexRequestException


class BaseBitmexApiClient:
    API_URL = 'https://www.bitmex.com'
    API_TESTNET_URL = 'https://testnet.bitmex.com'
    V1 = 'v1'

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], version: Optional[str], testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.version = version if isinstance(version, str) else self.V1
        self.base_url = self.API_TESTNET_URL if testnet else self.API_URL
        self._prepared_path = None
        self._request_url = None

    def get_method_path(self, method_name: str) -> Tuple[str, str]:
        method_map = {
            'get_announcement': (self.GET, 'announcement'),
            'get_announcement_urgent': (self.GET, 'announcement/urgent'),
            'get_api_keys': (self.GET, 'apiKey'),
            'get_chat_pinned': (self.GET, 'chat/pinned'),
            'send_pinned_message_to_channel': (self.POST, 'chat/pinned'),
            'remove_pinned_message_from_chat': (self.DELETE, 'chat/pinned'),
            'get_chat': (self.GET, 'chat'),
            'send_message_to_chat': (self.POST, 'chat'),
            'get_available_channels': (self.GET, 'chat/channels'),
            'get_connected_user_to_chat': (self.GET, 'chat/connected'),
            'get_execution': (self.GET, 'execution'),
            'get_execution_trade_history': (self.GET, 'execution/tradeHistory'),
            'get_funding': (self.GET, 'funding'),
            'get_instrument': (self.GET, 'instrument'),
            'get_instrument_active': (self.GET, 'instrument/active'),
            'get_instrument_active_and_indices': (self.GET, 'instrument/activeAndIndices'),
            'get_instrument_active_intervals': (self.GET, 'instrument/activeIntervals'),
            'get_instrument_composite_index': (self.GET, 'instrument/compositeIndex'),
            'get_instrument_usd_volume': (self.GET, 'instrument/usdVolume'),
            'get_insurance': (self.GET, 'insurance'),
            'get_leaderboard': (self.GET, 'leaderboard'),
            'get_leaderboard_name': (self.GET, 'leaderboard/name'),
            'get_liquidation': (self.GET, 'liquidation'),
            'get_global_notification': (self.GET, 'globalNotification'),
            'get_orders': (self.GET, 'order'),
            'create_order': (self.POST, 'order'),
            'update_order': (self.PUT, 'order'),
            'cancel_order': (self.DELETE, 'order'),
            'cancel_all_orders': (self.DELETE, 'order/all'),
            'close_position': (self.POST, 'order/closePosition'),
            'cancel_orders_after': (self.POST, 'order/cancelAllAfter'),
            'get_order_book_l2': (self.GET, 'orderBook/L2'),
            'get_position': (self.GET, 'position'),
            'update_position_isolate': (self.POST, 'position/isolate'),
            'update_position_risk_limit': (self.POST, 'position/riskLimit'),
            'update_position_transfer_margin': (self.POST, 'position/transferMargin'),
            'update_position_leverage': (self.POST, 'position/leverage'),
            'get_quote': (self.GET, 'quote'),
            'get_quote_bucketed': (self.GET, 'quote/bucketed'),
            'get_schema': (self.GET, 'schema'),
            'get_schema_websocket_help': (self.GET, 'schema/websocketHelp'),
            'get_settlement': (self.GET, 'settlement'),
            'get_stats': (self.GET, 'stats'),
            'get_stats_history': (self.GET, 'stats/history'),
            'get_status_history_usd': (self.GET, 'stats/historyUSD'),
            'get_trade': (self.GET, 'trade'),
            'get_trade_bucketed': (self.GET, 'trade/bucketed'),
            'get_user_deposit_address': (self.GET, 'user/depositAddress'),
            'get_user_wallet': (self.GET, 'user/wallet'),
            'get_user_wallet_history': (self.GET, 'user/walletHistory'),
            'get_user_wallet_summary': (self.GET, 'user/walletSummary'),
            'get_user_execution_history': (self.GET, 'user/executionHistory'),
            'get_user_withdrawal_fee': (self.GET, 'user/minWithdrawalFee'),
            'user_request_withdrawal': (self.POST, 'user/requestWithdrawal'),
            'user_cansel_withdrawal': (self.POST, 'user/cancelWithdrawal'),
            'user_confirm_withdrawal': (self.POST, 'user/confirmWithdrawal'),
            'user_confirm_email': (self.POST, 'user/confirmEmail'),
            'get_user_affiliate_status': (self.GET, 'user/affiliateStatus'),
            'user_check_referral_code': (self.GET, 'user/checkReferralCode'),
            'get_user_quote_fill_ratio': (self.GET, 'user/quoteFillRatio'),
            'get_user_quote_value_ratio': (self.GET, 'user/quoteValueRatio'),
            'get_user_trading_volume': (self.GET, 'user/tradingVolume'),
            'user_logout': (self.POST, 'user/logout'),
            'user_preferences': (self.POST, 'user/preferences'),
            'get_user': (self.GET, 'user'),
            'get_user_commission': (self.GET, 'user/commission'),
            'get_user_margin': (self.GET, 'user/margin'),
            'user_communication_token': (self.POST, 'user/communicationToken'),
            'get_user_event': (self.GET, 'userEvent'),
            'get_wallet_assets': (self.GET, 'wallet/assets'),
            'get_wallet_networks': (self.GET, 'wallet/networks')
        }
        if method_url := method_map.get(method_name):
            return method_url
        raise BitmexRequestException('Unknown method')

    def create_url(self, path: str, for_request: bool, **kwargs) -> str:
        if for_request:
            return f"{self.base_url}{path}"
        self._prepared_path = self._prepare_path(path, kwargs)
        self._request_url = f"{self.base_url}{self._prepared_path}"
        return self._request_url

    @staticmethod
    def generate_signature(api_secret, verb: str, path: str, expires: Union[str, int]):
        message = bytes(verb.upper() + path + str(expires), 'utf-8')
        signature = hmac.new(bytes(api_secret, 'utf-8'), message, digestmod=hashlib.sha256).hexdigest()
        return signature

    def _get_headers(self, method: str, path: str, optional_headers: Optional[dict]) -> httpx.Headers:
        headers = {
            "Accept": "application/json"
        }
        if self.api_key and self.api_secret:
            expires = str(int(time.time() + 5))
            headers['api-expires'] = expires
            headers['api-key'] = self.api_key
            headers['api-signature'] = self.generate_signature(self.api_secret, method, path, expires)
        if isinstance(optional_headers, dict):
            headers.update(optional_headers)
        return httpx.Headers(headers)

    def _prepare_path(self, path: str, params: dict) -> str:
        path = f"/api/{self.version}/{path}"
        parsed_url = parse.urlparse(path)
        params = parse.urlencode(params)
        prepared_path = f"{parsed_url.path}?{params}" if params else parsed_url.path
        return prepared_path

    def _handle_response(self, response: httpx.Response) -> dict:
        if not (200 <= response.status_code < 300):
            raise BitmexAPIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise BitmexRequestException(f"Invalid response: {response.text}")
