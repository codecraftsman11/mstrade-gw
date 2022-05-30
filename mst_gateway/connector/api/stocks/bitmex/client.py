import hashlib
import hmac
import time
import httpx
from urllib import parse
from typing import Optional, Tuple
from mst_gateway.exceptions import BitmexAPIException, BitmexRequestException


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

    def _generate_signature(self, verb: str, path: str, expires: int):
        message = bytes(verb.upper() + path + str(expires), 'utf-8')
        signature = hmac.new(bytes(self.api_secret, 'utf-8'), message, digestmod=hashlib.sha256).hexdigest()
        return signature

    def _get_headers(self, method: str, url: str, optional_headers: Optional[dict]) -> httpx.Headers:
        headers = {
            "Accept": "application/json"
        }
        if self.api_key and self.api_secret:
            expires = int(round(time.time()) + 20)
            headers['api-expires'] = str(expires)
            headers['api-key'] = self.api_key
            headers['api-signature'] = self._generate_signature(method, url, expires)
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
            raise BitmexRequestException(f"Invalid Response: {response.text}")


class BitmexApiClient(BaseBitmexApiClient):
    """
    Client for bitmex api exchange
    For details of request params see: https://testnet.bitmex.com/api/explorer/
    """

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], testnet: bool = False, version=None):
        super().__init__(api_key, api_secret, version, testnet)

    def _request(self, method: str, path: str, **params) -> dict:
        optional_headers = params.pop('headers', None)
        proxies = params.pop('proxies', None)
        timeout = params.pop('timeout', None)
        path = self._prepare_path(path, params)
        headers = self._get_headers(method, path, optional_headers)
        client = httpx.Client(headers=headers, proxies=proxies, timeout=timeout)
        url = self._create_url(path, True)
        request = client.build_request(method, url)
        self.response = client.send(request)
        client.close()
        return self._handle_response(self.response)

    # ANNOUNCEMENT
    def get_announcement(self, **params) -> dict:
        return self._request(self.GET, 'announcement', **params)

    def get_announcement_urgent(self, **params) -> dict:
        return self._request(self.GET, 'announcement/urgent', **params)

    # API
    def get_api_keys(self, **params) -> dict:
        return self._request(self.GET, 'apiKey', **params)

    # CHAT
    def get_chat_pinned(self, **params) -> dict:
        return self._request(self.GET, 'chat/pinned', **params)

    def send_pinned_message_to_channel(self, **params) -> dict:
        return self._request(self.POST, 'chat/pinned', **params)

    def remove_pinned_message_from_chat(self, **params) -> dict:
        return self._request(self.DELETE, 'chat/pinned', **params)

    def get_chat(self, **params) -> dict:
        return self._request(self.GET, 'chat', **params)

    def send_message_to_chat(self, **params) -> dict:
        return self._request(self.POST, 'chat', **params)

    def get_available_channels(self, **params) -> dict:
        return self._request(self.GET, 'chat/channels', **params)

    def get_connected_user_to_chat(self, **params) -> dict:
        return self._request(self.GET, 'chat/connected', **params)

    # EXECUTION
    def get_execution(self, **params) -> dict:
        return self._request(self.GET, 'execution', **params)

    def get_execution_trade_history(self, **params) -> dict:
        return self._request(self.GET, 'execution/tradeHistory', **params)

    # FUNDING
    def get_funding(self, **params) -> dict:
        return self._request(self.GET, 'funding', **params)

    # INSTRUMENT
    def get_instrument(self, **params) -> dict:
        return self._request(self.GET, 'instrument', **params)

    def get_instrument_active(self, **params) -> dict:
        return self._request(self.GET, 'instrument/active', **params)

    def get_instrument_indices(self, **params) -> dict:
        return self._request(self.GET, 'instrument/indices', **params)

    def get_instrument_active_and_indices(self, **params) -> dict:
        return self._request(self.GET, 'instrument/activeAndIndices', **params)

    def get_instrument_active_intervals(self, **params) -> dict:
        return self._request(self.GET, 'instrument/activeIntervals')

    def get_instrument_composite_index(self, **params) -> dict:
        return self._request(self.GET, 'instrument/compositeIndex', **params)

    def get_instrument_usd_volume(self, **params) -> dict:
        return self._request(self.GET, 'instrument/usdVolume', **params)

    # INSURANCE
    def get_insurance(self, **params) -> dict:
        return self._request(self.GET, 'insurance', **params)

    # LEADERBOARD
    def get_leaderboard(self, **params) -> dict:
        return self._request(self.GET, 'leaderboard', **params)

    def get_leaderboard_name(self, **params) -> dict:
        return self._request(self.GET, 'leaderboard/name', **params)

    # LIQUIDATION
    def get_liquidation(self, **params) -> dict:
        return self._request(self.GET, 'liquidation', **params)

    # NOTIFICATION
    def get_global_notification(self, **params) -> dict:
        return self._request(self.GET, 'globalNotification', **params)

    # ORDER
    def get_orders(self, **params) -> dict:
        return self._request(self.GET, 'order', **params)

    def create_order(self, **params) -> dict:
        return self._request(self.POST, 'order', **params)

    def update_order(self, **params) -> dict:
        return self._request(self.PUT, 'order', **params)

    def cancel_order(self, **params) -> dict:
        return self._request(self.DELETE, 'order', **params)

    def cancel_all_orders(self, **params) -> dict:
        return self._request(self.DELETE, 'order/all', **params)

    def close_position(self, **params) -> dict:
        return self._request(self.POST, 'order/closePosition', **params)

    def cancel_orders_after(self, **params) -> dict:
        return self._request(self.POST, 'order/cancelAllAfter', **params)

    # ORDERBOOK
    def get_order_book_l2(self, **params) -> dict:
        return self._request(self.GET, 'orderBook/L2', **params)

    # POSITION
    def get_position(self, **params) -> dict:
        return self._request(self.GET, 'position', **params)

    def update_position_isolate(self, **params) -> dict:
        return self._request(self.POST, 'position/isolate', **params)

    def update_position_risk_limit(self, **params) -> dict:
        return self._request(self.POST, 'position/riskLimit', **params)

    def update_position_transfer_margin(self, **params) -> dict:
        return self._request(self.POST, 'position/transferMargin', **params)

    def update_position_leverage(self, **params) -> dict:
        return self._request(self.POST, 'position/leverage', **params)

    # QUOTE
    def get_quote(self, **params) -> dict:
        return self._request(self.GET, 'quote', **params)

    def get_quote_bucketed(self, **params) -> dict:
        return self._request(self.GET, 'quote/bucketed', **params)

    # SCHEMA
    def get_schema(self, **params) -> dict:
        return self._request(self.GET, 'schema', **params)

    def get_schema_websocket_help(self, **params) -> dict:
        return self._request(self.GET, 'schema/websocketHelp', **params)

    # SETTLEMENT
    def get_settlement(self, **params) -> dict:
        return self._request(self.GET, 'settlement', **params)

    # STATS
    def get_stats(self, **params) -> dict:
        return self._request(self.GET, 'stats', **params)

    def get_stats_history(self, **params) -> dict:
        return self._request(self.GET, 'stats/history', **params)

    def get_status_history_usd(self, **params) -> dict:
        return self._request(self.GET, 'stats/historyUSD', **params)

    # TRADE
    def get_trade(self, **params) -> dict:
        return self._request(self.GET, 'trade', **params)

    def get_trade_bucketed(self, **params) -> dict:
        return self._request(self.GET, 'trade/bucketed', **params)

    # USER
    def get_user_deposit_address(self, **params) -> dict:
        return self._request(self.GET, 'user/depositAddress', **params)

    def get_user_wallet(self, **params) -> dict:
        return self._request(self.GET, 'user/wallet', **params)

    def get_user_wallet_history(self, **params) -> dict:
        return self._request(self.GET, 'user/walletHistory', **params)

    def get_user_wallet_summary(self, **params) -> dict:
        return self._request(self.GET, 'user/walletSummary', **params)

    def get_user_execution_history(self, **params) -> dict:
        return self._request(self.GET, 'user/executionHistory', **params)

    def get_user_withdrawal_fee(self, **params) -> dict:
        return self._request(self.GET, 'user/minWithdrawalFee', **params)

    def user_request_withdrawal(self, **params) -> dict:
        return self._request(self.POST, 'user/requestWithdrawal', **params)

    def user_cansel_withdrawal(self, **params) -> dict:
        return self._request(self.POST, 'user/cancelWithdrawal', **params)

    def user_confirm_withdrawal(self, **params) -> dict:
        return self._request(self.POST, 'user/confirmWithdrawal', **params)

    def user_confirm_email(self, **params) -> dict:
        return self._request(self.POST, 'user/confirmEmail', **params)

    def get_user_affiliate_status(self, **params) -> dict:
        return self._request(self.GET, 'user/affiliateStatus', **params)

    def user_check_referral_code(self, **params) -> dict:
        return self._request(self.GET, 'user/checkReferralCode', **params)

    def get_user_quote_fill_ratio(self, **params) -> dict:
        return self._request(self.GET, 'user/quoteFillRatio', **params)

    def get_user_quote_value_ratio(self, **params) -> dict:
        return self._request(self.GET, 'user/quoteValueRatio', **params)

    def get_user_trading_volume(self, **params) -> dict:
        return self._request(self.GET, 'user/tradingVolume', **params)

    def user_logout(self, **params) -> dict:
        return self._request(self.POST, 'user/logout', **params)

    def user_preferences(self, **params) -> dict:
        return self._request(self.POST, 'user/preferences', **params)

    def get_user(self, **params) -> dict:
        return self._request(self.GET, 'user', **params)

    def get_user_commission(self, **params) -> dict:
        return self._request(self.GET, 'user/commission', **params)

    def get_user_margin(self, **params) -> dict:
        return self._request(self.GET, 'user/margin', **params)

    def user_communication_token(self, **params) -> dict:
        return self._request(self.POST, 'user/communicationToken', **params)

    def get_user_event(self, **params) -> dict:
        return self._request(self.GET, 'userEvent', **params)

    # WALLET
    def get_wallet_assets(self, **params) -> dict:
        return self._request(self.GET, 'wallet/assets', **params)

    def get_wallet_networks(self, **params) -> dict:
        return self._request(self.GET, 'wallet/networks', **params)


class AsyncBitmexApiClient(BaseBitmexApiClient):
    """
    Async client for bitmex api exchange
    For details of request params see: https://testnet.bitmex.com/api/explorer/
    """

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], testnet: bool = False, version=None):
        super().__init__(api_key, api_secret, version, testnet)

    async def _request(self, method: str, path: str, **params) -> dict:
        path = self._prepare_path(path, params)
        headers = self._get_headers(method, path, params.pop('headers', None))
        client = httpx.AsyncClient(headers=headers, proxies=params.get('proxies', None), timeout=params.get('timeout', None))
        url = self._create_url(path)
        request = client.build_request(method, url)
        response = await client.send(request)
        await client.aclose()
        return self._handle_response(response)

    # ANNOUNCEMENT
    async def get_announcement(self, **params) -> dict:
        return await self._request(self.GET, 'announcement', **params)

    async def get_announcement_urgent(self, **params) -> dict:
        return await self._request(self.GET, 'announcement/urgent', **params)

    # API
    async def get_api_keys(self, **params) -> dict:
        return await self._request(self.GET, 'apiKey', **params)

    # CHAT
    async def get_chat_pinned(self, **params) -> dict:
        return await self._request(self.GET, 'chat/pinned', **params)

    async def send_pinned_message_to_channel(self, **params) -> dict:
        return await self._request(self.POST, 'chat/pinned', **params)

    async def remove_pinned_message_from_chat(self, **params) -> dict:
        return await self._request(self.DELETE, 'chat/pinned', **params)

    async def get_chat(self, **params) -> dict:
        return await self._request(self.GET, 'chat', **params)

    async def send_message_to_chat(self, **params) -> dict:
        return await self._request(self.POST, 'chat', **params)

    async def get_available_channels(self, **params) -> dict:
        return await self._request(self.GET, 'chat/channels', **params)

    async def get_connected_user_to_chat(self, **params) -> dict:
        return await self._request(self.GET, 'chat/connected', **params)

    # EXECUTION
    async def get_execution(self, **params) -> dict:
        return await self._request(self.GET, 'execution', **params)

    async def get_execution_trade_history(self, **params) -> dict:
        return await self._request(self.GET, 'execution/tradeHistory', **params)

    # FUNDING
    async def get_funding(self, **params) -> dict:
        return await self._request(self.GET, 'funding', **params)

    # INSTRUMENT
    async def get_instrument(self, **params) -> dict:
        return await self._request(self.GET, 'instrument', **params)

    async def get_instrument_active(self, **params) -> dict:
        return await self._request(self.GET, 'instrument/active', **params)

    async def get_instrument_indices(self, **params) -> dict:
        return await self._request(self.GET, 'instrument/indices', **params)

    async def get_instrument_active_and_indices(self, **params) -> dict:
        return await self._request(self.GET, 'instrument/activeAndIndices', **params)

    async def get_instrument_active_intervals(self, **params) -> dict:
        return await self._request(self.GET, 'instrument/activeIntervals')

    async def get_instrument_composite_index(self, **params) -> dict:
        return await self._request(self.GET, 'instrument/compositeIndex', **params)

    async def get_instrument_usd_volume(self, **params) -> dict:
        return await self._request(self.GET, 'instrument/usdVolume', **params)

    # INSURANCE
    async def get_insurance(self, **params) -> dict:
        return await self._request(self.GET, 'insurance', **params)

    # LEADERBOARD
    async def get_leaderboard(self, **params) -> dict:
        return await self._request(self.GET, 'leaderboard', **params)

    async def get_leaderboard_name(self, **params) -> dict:
        return await self._request(self.GET, 'leaderboard/name', **params)

    # LIQUIDATION
    async def get_liquidation(self, **params) -> dict:
        return await self._request(self.GET, 'liquidation', **params)

    # NOTIFICATION
    async def get_global_notification(self, **params) -> dict:
        return await self._request(self.GET, 'globalNotification', **params)

    # ORDER
    async def get_orders(self, **params) -> dict:
        return await self._request(self.GET, 'order', **params)

    async def create_order(self, **params) -> dict:
        return await self._request(self.POST, 'order', **params)

    async def update_order(self, **params) -> dict:
        return await self._request(self.PUT, 'order', **params)

    async def cancel_order(self, **params) -> dict:
        return await self._request(self.DELETE, 'order', **params)

    async def cancel_all_orders(self, **params) -> dict:
        return await self._request(self.DELETE, 'order/all', **params)

    async def close_position(self, **params) -> dict:
        return await self._request(self.POST, 'order/closePosition', **params)

    async def cancel_orders_after(self, **params) -> dict:
        return await self._request(self.POST, 'order/cancelAllAfter', **params)

    # ORDERBOOK
    async def get_order_book_l2(self, **params) -> dict:
        return await self._request(self.GET, 'orderBook/L2', **params)

    # POSITION
    async def get_position(self, **params) -> dict:
        return await self._request(self.GET, 'position', **params)

    async def update_position_isolate(self, **params) -> dict:
        return await self._request(self.POST, 'position/isolate', **params)

    async def update_position_risk_limit(self, **params) -> dict:
        return await self._request(self.POST, 'position/riskLimit', **params)

    async def update_position_transfer_margin(self, **params) -> dict:
        return await self._request(self.POST, 'position/transferMargin', **params)

    async def update_position_leverage(self, **params) -> dict:
        return await self._request(self.POST, 'position/leverage', **params)

    # QUOTE
    async def get_quote(self, **params) -> dict:
        return await self._request(self.GET, 'quote', **params)

    async def get_quote_bucketed(self, **params) -> dict:
        return await self._request(self.GET, 'quote/bucketed', **params)

    # SCHEMA
    async def get_schema(self, **params) -> dict:
        return await self._request(self.GET, 'schema', **params)

    async def get_schema_websocket_help(self, **params) -> dict:
        return await self._request(self.GET, 'schema/websocketHelp', **params)

    # SETTLEMENT
    async def get_settlement(self, **params) -> dict:
        return await self._request(self.GET, 'settlement', **params)

    # STATS
    async def get_stats(self, **params) -> dict:
        return await self._request(self.GET, 'stats', **params)

    async def get_stats_history(self, **params) -> dict:
        return await self._request(self.GET, 'stats/history', **params)

    async def get_status_history_usd(self, **params) -> dict:
        return await self._request(self.GET, 'stats/historyUSD', **params)

    # TRADE
    async def get_trade(self, **params) -> dict:
        return await self._request(self.GET, 'trade', **params)

    async def get_trade_bucketed(self, **params) -> dict:
        return await self._request(self.GET, 'trade/bucketed', **params)

    # USER
    async def get_user_deposit_address(self, **params) -> dict:
        return await self._request(self.GET, 'user/depositAddress', **params)

    async def get_user_wallet(self, **params) -> dict:
        return await self._request(self.GET, 'user/wallet', **params)

    async def get_user_wallet_history(self, **params) -> dict:
        return await self._request(self.GET, 'user/walletHistory', **params)

    async def get_user_wallet_summary(self, **params) -> dict:
        return await self._request(self.GET, 'user/walletSummary', **params)

    async def get_user_execution_history(self, **params) -> dict:
        return await self._request(self.GET, 'user/executionHistory', **params)

    async def get_user_withdrawal_fee(self, **params) -> dict:
        return await self._request(self.GET, 'user/minWithdrawalFee', **params)

    async def user_request_withdrawal(self, **params) -> dict:
        return await self._request(self.POST, 'user/requestWithdrawal', **params)

    async def user_cansel_withdrawal(self, **params) -> dict:
        return await self._request(self.POST, 'user/cancelWithdrawal', **params)

    async def user_confirm_withdrawal(self, **params) -> dict:
        return await self._request(self.POST, 'user/confirmWithdrawal', **params)

    async def user_confirm_email(self, **params) -> dict:
        return await self._request(self.POST, 'user/confirmEmail', **params)

    async def get_user_affiliate_status(self, **params) -> dict:
        return await self._request(self.GET, 'user/affiliateStatus', **params)

    async def user_check_referral_code(self, **params) -> dict:
        return await self._request(self.GET, 'user/checkReferralCode', **params)

    async def get_user_quote_fill_ratio(self, **params) -> dict:
        return await self._request(self.GET, 'user/quoteFillRatio', **params)

    async def get_user_quote_value_ratio(self, **params) -> dict:
        return await self._request(self.GET, 'user/quoteValueRatio', **params)

    async def get_user_trading_volume(self, **params) -> dict:
        return await self._request(self.GET, 'user/tradingVolume', **params)

    async def user_logout(self, **params) -> dict:
        return await self._request(self.POST, 'user/logout', **params)

    async def user_preferences(self, **params) -> dict:
        return await self._request(self.POST, 'user/preferences', **params)

    async def get_user(self, **params) -> dict:
        return await self._request(self.GET, 'user', **params)

    async def get_user_commission(self, **params) -> dict:
        return await self._request(self.GET, 'user/commission', **params)

    async def get_user_margin(self, **params) -> dict:
        return await self._request(self.GET, 'user/margin', **params)

    async def user_communication_token(self, **params) -> dict:
        return await self._request(self.POST, 'user/communicationToken', **params)

    async def get_user_event(self, **params) -> dict:
        return await self._request(self.GET, 'userEvent', **params)

    # WALLET
    async def get_wallet_assets(self, **params) -> dict:
        return await self._request(self.GET, 'wallet/assets', **params)

    async def get_wallet_networks(self, **params) -> dict:
        return await self._request(self.GET, 'wallet/networks', **params)
