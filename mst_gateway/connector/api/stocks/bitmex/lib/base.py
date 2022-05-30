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

    def get_method_url(self, method_name: str) -> Tuple[str, str]:
        method_map = {
            'get_announcement': (self.GET, self._create_url('announcement')),
            'get_announcement_urgent': (self.GET, self._create_url('announcement/urgent')),
            'get_api_keys': (self.GET, self._create_url('apiKey')),
            'get_chat_pinned': (self.GET, self._create_url('chat/pinned')),
            'send_pinned_message_to_channel': (self.POST, self._create_url('chat/pinned')),
            'remove_pinned_message_from_chat': (self.DELETE, self._create_url('chat/pinned')),
            'get_chat': (self.GET, self._create_url('chat')),
            'send_message_to_chat': (self.POST, self._create_url('chat')),
            'get_available_channels': (self.GET, self._create_url('chat/channels')),
            'get_connected_user_to_chat': (self.GET, self._create_url('chat/connected')),
            'get_execution': (self.GET, self._create_url('execution')),
            'get_execution_trade_history': (self.GET, self._create_url('execution/tradeHistory')),
            'get_funding': (self.GET, self._create_url('funding')),
            'get_instrument': (self.GET, self._create_url('instrument')),
            'get_instrument_active': (self.GET, self._create_url('instrument/active')),
            'get_instrument_active_and_indices': (self.GET, self._create_url('instrument/activeAndIndices')),
            'get_instrument_active_intervals': (self.GET, self._create_url('instrument/activeIntervals')),
            'get_instrument_composite_index': (self.GET, self._create_url('instrument/compositeIndex')),
            'get_instrument_usd_volume': (self.GET, self._create_url('instrument/usdVolume')),
            'get_insurance': (self.GET, self._create_url('insurance')),
            'get_leaderboard': (self.GET, self._create_url('leaderboard')),
            'get_leaderboard_name': (self.GET, self._create_url('leaderboard/name')),
            'get_liquidation': (self.GET, self._create_url('liquidation')),
            'get_global_notification': (self.GET, self._create_url('globalNotification')),
            'get_orders': (self.GET, self._create_url('order')),
            'create_order': (self.GET, self._create_url('order')),
            'update_order': (self.GET, self._create_url('order')),
            'cancel_order': (self.GET, self._create_url('order')),
            'cancel_all_orders': (self.GET, self._create_url('order/all')),
            'close_position': (self.GET, self._create_url('order/closePosition')),
            'cancel_orders_after': (self.GET, self._create_url('order/cancelAllAfter')),
            'get_order_book_l2': (self.GET, self._create_url('orderBook/L2')),
            'get_position': (self.GET, self._create_url('position')),
            'update_position_isolate': (self.GET, self._create_url('position/isolate')),
            'update_position_risk_limit': (self.GET, self._create_url('position/riskLimit')),
            'update_position_transfer_margin': (self.GET, self._create_url('position/transferMargin')),
            'update_position_leverage': (self.GET, self._create_url('position/leverage')),
            'get_quote': (self.GET, self._create_url('quote')),
            'get_quote_bucketed': (self.GET, self._create_url('quote/bucketed')),
            'get_schema': (self.GET, self._create_url('schema')),
            'get_schema_websocket_help': (self.GET, self._create_url('schema/websocketHelp')),
            'get_settlement': (self.GET, self._create_url('settlement')),
            'get_stats': (self.GET, self._create_url('stats')),
            'get_stats_history': (self.GET, self._create_url('stats/history')),
            'get_status_history_usd': (self.GET, self._create_url('stats/historyUSD')),
            'get_trade': (self.GET, self._create_url('trade')),
            'get_trade_bucketed': (self.GET, self._create_url('trade/bucketed')),
            'get_user_deposit_address': (self.GET, self._create_url('user/depositAddress')),
            'get_user_wallet': (self.GET, self._create_url('user/wallet')),
            'get_user_wallet_history': (self.GET, self._create_url('user/walletHistory')),
            'get_user_wallet_summary': (self.GET, self._create_url('user/walletSummary')),
            'get_user_execution_history': (self.GET, self._create_url('user/executionHistory')),
            'get_user_withdrawal_fee': (self.GET, self._create_url('user/minWithdrawalFee')),
            'user_request_withdrawal': (self.GET, self._create_url('user/requestWithdrawal')),
            'user_cansel_withdrawal': (self.GET, self._create_url('user/cancelWithdrawal')),
            'user_confirm_withdrawal': (self.GET, self._create_url('user/confirmWithdrawal')),
            'user_confirm_email': (self.GET, self._create_url('user/confirmEmail')),
            'get_user_affiliate_status': (self.GET, self._create_url('user/affiliateStatus')),
            'user_check_referral_code': (self.GET, self._create_url('user/checkReferralCode')),
            'get_user_quote_fill_ratio': (self.GET, self._create_url('user/quoteFillRatio')),
            'get_user_quote_value_ratio': (self.GET, self._create_url('user/quoteValueRatio')),
            'get_user_trading_volume': (self.GET, self._create_url('user/tradingVolume')),
            'user_logout': (self.GET, self._create_url('user/logout')),
            'user_preferences': (self.GET, self._create_url('user/preferences')),
            'get_user': (self.GET, self._create_url('user')),
            'get_user_commission': (self.GET, self._create_url('user/commission')),
            'get_user_margin': (self.GET, self._create_url('user/margin')),
            'user_communication_token': (self.GET, self._create_url('user/communicationToken')),
            'get_user_event': (self.GET, self._create_url('userEvent')),
            'get_wallet_assets': (self.GET, self._create_url('wallet/assets')),
            'get_wallet_networks': (self.GET, self._create_url('wallet/networks'))
        }
        if method_url := method_map.get(method_name):
            return method_url
        raise BitmexRequestException('Unknown method')

    def _create_url(self, path: str, for_request: bool = False) -> str:
        if for_request:
            return f"{self.base_url}{path}"
        return f"{self.base_url}/api/{self.version}/{path}"

    @staticmethod
    def generate_signature(api_secret, verb: str, path: str, expires: Union[str, int]):
        message = bytes(verb.upper() + path + str(expires), 'utf-8')
        signature = hmac.new(bytes(api_secret, 'utf-8'), message, digestmod=hashlib.sha256).hexdigest()
        return signature

    def _get_headers(self, method: str, url: str, optional_headers: Optional[dict]) -> httpx.Headers:
        headers = {
            "Accept": "application/json"
        }
        if self.api_key and self.api_secret:
            expires = str(int(time.time() + 5))
            headers['api-expires'] = expires
            headers['api-key'] = self.api_key
            headers['api-signature'] = self.generate_signature(self.api_secret, method, url, expires)
        if isinstance(optional_headers, dict):
            headers.update(optional_headers)
        return httpx.Headers(headers)

    def _prepare_path(self, path: str, params: dict) -> str:
        path = f"/api/{self.version}/{path}"
        parsed_url = parse.urlparse(path)
        params = parse.urlencode(params)
        return f"{parsed_url.path}?{params}"

    def _handle_response(self, response: httpx.Response) -> dict:
        if not (200 <= response.status_code < 300):
            raise BitmexAPIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise BitmexRequestException(f"Invalid response: {response.text}")
