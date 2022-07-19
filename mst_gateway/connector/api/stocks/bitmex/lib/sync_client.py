import httpx
from .base import BaseBitmexApiClient


class BitmexApiClient(BaseBitmexApiClient):
    """
    Client for bitmex api exchange
    For details of request params see: https://testnet.bitmex.com/api/explorer/
    """

    def _request(self, method: str, url: httpx.URL, **kwargs) -> httpx.Response:
        optional_headers = kwargs.pop('headers', None)
        proxies = kwargs.pop('proxies', None)
        timeout = kwargs.pop('timeout', None)
        headers = self._get_headers(method, url, optional_headers, kwargs)
        request_params = self._prepare_request_params(**kwargs)
        return self.get_client(proxies).request(method, url, headers=headers, timeout=timeout, **request_params)

    def get_client(self, proxies) -> httpx.Client:
        if session := self._session_map.get(proxies):
            return session
        session = httpx.Client(proxies=proxies)
        self._session_map[proxies] = session
        return session

    # ANNOUNCEMENT
    def get_announcement(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_announcement')
        return self._request(method, url, **params)

    def get_announcement_urgent(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_announcement_urgent')
        return self._request(method, url, **params)

    # API
    def get_api_keys(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_api_keys')
        return self._request(method, url, **params)

    # CHAT
    def get_chat_pinned(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_chat_pinned')
        return self._request(method, url, **params)

    def send_pinned_message_to_channel(self, **params) -> httpx.Response:
        method, url = self.get_method_info('send_pinned_message_to_channel')
        return self._request(method, url, **params)

    def remove_pinned_message_from_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('remove_pinned_message_from_chat')
        return self._request(method, url, **params)

    def get_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_chat')
        return self._request(method, url, **params)

    def send_message_to_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('send_message_to_chat')
        return self._request(method, url, **params)

    def get_available_channels(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_available_channels')
        return self._request(method, url, **params)

    def get_connected_user_to_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_connected_user_to_chat')
        return self._request(method, url, **params)

    # EXECUTION
    def get_execution(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_execution')
        return self._request(method, url, **params)

    def get_execution_trade_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_execution_trade_history')
        return self._request(method, url, **params)

    # FUNDING
    def get_funding(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_funding')
        return self._request(method, url, **params)

    # INSTRUMENT
    def get_instrument(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument')
        return self._request(method, url, **params)

    def get_instrument_active(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_active')
        return self._request(method, url, **params)

    def get_instrument_indices(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_indices')
        return self._request(method, url, **params)

    def get_instrument_active_and_indices(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_active_and_indices')
        return self._request(method, url, **params)

    def get_instrument_active_intervals(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_active_intervals')
        return self._request(method, url, **params)

    def get_instrument_composite_index(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_composite_index')
        return self._request(method, url, **params)

    def get_instrument_usd_volume(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_usd_volume')
        return self._request(method, url, **params)

    # INSURANCE
    def get_insurance(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_insurance')
        return self._request(method, url, **params)

    # LEADERBOARD
    def get_leaderboard(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_insurance')
        return self._request(method, url, **params)

    def get_leaderboard_name(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_leaderboard_name')
        return self._request(method, url, **params)

    # LIQUIDATION
    def get_liquidation(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_liquidation')
        return self._request(method, url, **params)

    # NOTIFICATION
    def get_global_notification(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_global_notification')
        return self._request(method, url, **params)

    # ORDER
    def get_orders(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_orders')
        return self._request(method, url, **params)

    def create_order(self, **params) -> httpx.Response:
        method, url = self.get_method_info('create_order')
        return self._request(method, url, **params)

    def update_order(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_order')
        return self._request(method, url, **params)

    def cancel_order(self, **params) -> httpx.Response:
        method, url = self.get_method_info('cancel_order')
        return self._request(method, url, **params)

    def cancel_all_orders(self, **params) -> httpx.Response:
        method, url = self.get_method_info('cancel_all_orders')
        return self._request(method, url, **params)

    def close_position(self, **params) -> httpx.Response:
        method, url = self.get_method_info('close_position')
        return self._request(method, url, **params)

    def cancel_orders_after(self, **params) -> httpx.Response:
        method, url = self.get_method_info('cancel_orders_after')
        return self._request(method, url, **params)

    # ORDERBOOK
    def get_order_book_l2(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_order_book_l2')
        return self._request(method, url, **params)

    # POSITION
    def get_position(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_position')
        return self._request(method, url, **params)

    def update_position_isolate(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_isolate')
        return self._request(method, url, **params)

    def update_position_risk_limit(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_risk_limit')
        return self._request(method, url, **params)

    def update_position_transfer_margin(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_transfer_margin')
        return self._request(method, url, **params)

    def update_position_leverage(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_leverage')
        return self._request(method, url, **params)

    # QUOTE
    def get_quote(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_quote')
        return self._request(method, url, **params)

    def get_quote_bucketed(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_quote_bucketed')
        return self._request(method, url, **params)

    # SCHEMA
    def get_schema(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_schema')
        return self._request(method, url, **params)

    def get_schema_websocket_help(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_schema_websocket_help')
        return self._request(method, url, **params)

    # SETTLEMENT
    def get_settlement(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_settlement')
        return self._request(method, url, **params)

    # STATS
    def get_stats(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_stats')
        return self._request(method, url, **params)

    def get_stats_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_stats_history')
        return self._request(method, url, **params)

    def get_status_history_usd(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_status_history_usd')
        return self._request(method, url, **params)

    # TRADE
    def get_trade(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_trade')
        return self._request(method, url, **params)

    def get_trade_bucketed(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_trade_bucketed')
        return self._request(method, url, **params)

    # USER
    def get_user_deposit_address(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_deposit_address')
        return self._request(method, url, **params)

    def get_user_wallet(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_wallet')
        return self._request(method, url, **params)

    def get_user_wallet_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_wallet_history')
        return self._request(method, url, **params)

    def get_user_wallet_summary(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_wallet_summary')
        return self._request(method, url, **params)

    def get_user_execution_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_execution_history')
        return self._request(method, url, **params)

    def get_user_withdrawal_fee(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_withdrawal_fee')
        return self._request(method, url, **params)

    def user_request_withdrawal(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_request_withdrawal')
        return self._request(method, url, **params)

    def user_cansel_withdrawal(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_cansel_withdrawal')
        return self._request(method, url, **params)

    def user_confirm_withdrawal(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_confirm_withdrawal')
        return self._request(method, url, **params)

    def user_confirm_email(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_confirm_email')
        return self._request(method, url, **params)

    def get_user_affiliate_status(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_affiliate_status')
        return self._request(method, url, **params)

    def user_check_referral_code(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_check_referral_code')
        return self._request(method, url, **params)

    def get_user_quote_fill_ratio(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_quote_fill_ratio')
        return self._request(method, url, **params)

    def get_user_quote_value_ratio(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_quote_value_ratio')
        return self._request(method, url, **params)

    def get_user_trading_volume(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_trading_volume')
        return self._request(method, url, **params)

    def user_logout(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_logout')
        return self._request(method, url, **params)

    def user_preferences(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_preferences')
        return self._request(method, url, **params)

    def get_user(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user')
        return self._request(method, url, **params)

    def get_user_commission(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_commission')
        return self._request(method, url, **params)

    def get_user_margin(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_margin')
        return self._request(method, url, **params)

    def user_communication_token(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_communication_token')
        return self._request(method, url, **params)

    def get_user_event(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_event')
        return self._request(method, url, **params)

    # WALLET
    def get_wallet_assets(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_wallet_assets')
        return self._request(method, url, **params)

    def get_wallet_networks(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_wallet_networks')
        return self._request(method, url, **params)

    def close(self):
        for session in self._session_map.values():
            session.close()
        self._session_map.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
