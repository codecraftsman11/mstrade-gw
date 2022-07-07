import httpx
from .base import BaseBitmexApiClient


class AsyncBitmexApiClient(BaseBitmexApiClient):
    """
    Async client for bitmex api exchange
    For details of request params see: https://testnet.bitmex.com/api/explorer/
    """

    async def aclose(self):
        for proxy, session in self._session_map.copy().items():
            await session.aclose()
            if session.is_closed:
                del self._session_map[proxy]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def _request(self, method: str, url: httpx.URL, **kwargs) -> httpx.Response:
        optional_headers = kwargs.pop('headers', None)
        proxies = kwargs.pop('proxies', None)
        timeout = kwargs.pop('timeout', None)
        headers = self._get_headers(method, url, optional_headers, kwargs)
        request_params = self._prepare_request_params(**kwargs)
        if not (session := self._session_map.get(proxies)):
            session = httpx.AsyncClient(proxies=proxies)
            self._session_map[proxies] = session
        return await session.request(method, url, headers=headers, timeout=timeout, **request_params)
    
    # ANNOUNCEMENT
    async def get_announcement(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_announcement')
        return await self._request(method, url, **params)

    async def get_announcement_urgent(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_announcement_urgent')
        return await self._request(method, url, **params)

    # API
    async def get_api_keys(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_api_keys')
        return await self._request(method, url, **params)

    # CHAT
    async def get_chat_pinned(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_chat_pinned')
        return await self._request(method, url, **params)

    async def send_pinned_message_to_channel(self, **params) -> httpx.Response:
        method, url = self.get_method_info('send_pinned_message_to_channel')
        return await self._request(method, url, **params)

    async def remove_pinned_message_from_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('remove_pinned_message_from_chat')
        return await self._request(method, url, **params)

    async def get_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_chat')
        return await self._request(method, url, **params)

    async def send_message_to_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('send_message_to_chat')
        return await self._request(method, url, **params)

    async def get_available_channels(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_available_channels')
        return await self._request(method, url, **params)

    async def get_connected_user_to_chat(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_connected_user_to_chat')
        return await self._request(method, url, **params)

    # EXECUTION
    async def get_execution(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_execution')
        return await self._request(method, url, **params)

    async def get_execution_trade_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_execution_trade_history')
        return await self._request(method, url, **params)

    # FUNDING
    async def get_funding(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_funding')
        return await self._request(method, url, **params)

    # INSTRUMENT
    async def get_instrument(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument')
        return await self._request(method, url, **params)

    async def get_instrument_active(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_active')
        return await self._request(method, url, **params)

    async def get_instrument_indices(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_indices')
        return await self._request(method, url, **params)

    async def get_instrument_active_and_indices(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_active_and_indices')
        return await self._request(method, url, **params)

    async def get_instrument_active_intervals(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_active_intervals')
        return await self._request(method, url, **params)

    async def get_instrument_composite_index(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_composite_index')
        return await self._request(method, url, **params)

    async def get_instrument_usd_volume(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_instrument_usd_volume')
        return await self._request(method, url, **params)

    # INSURANCE
    async def get_insurance(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_insurance')
        return await self._request(method, url, **params)

    # LEADERBOARD
    async def get_leaderboard(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_insurance')
        return await self._request(method, url, **params)

    async def get_leaderboard_name(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_leaderboard_name')
        return await self._request(method, url, **params)

    # LIQUIDATION
    async def get_liquidation(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_liquidation')
        return await self._request(method, url, **params)

    # NOTIFICATION
    async def get_global_notification(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_global_notification')
        return await self._request(method, url, **params)

    # ORDER
    async def get_orders(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_orders')
        return await self._request(method, url, **params)

    async def create_order(self, **params) -> httpx.Response:
        method, url = self.get_method_info('create_order')
        return await self._request(method, url, **params)

    async def update_order(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_order')
        return await self._request(method, url, **params)

    async def cancel_order(self, **params) -> httpx.Response:
        method, url = self.get_method_info('cancel_order')
        return await self._request(method, url, **params)

    async def cancel_all_orders(self, **params) -> httpx.Response:
        method, url = self.get_method_info('cancel_all_orders')
        return await self._request(method, url, **params)

    async def close_position(self, **params) -> httpx.Response:
        method, url = self.get_method_info('close_position')
        return await self._request(method, url, **params)

    async def cancel_orders_after(self, **params) -> httpx.Response:
        method, url = self.get_method_info('cancel_orders_after')
        return await self._request(method, url, **params)

    # ORDERBOOK
    async def get_order_book_l2(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_order_book_l2')
        return await self._request(method, url, **params)

    # POSITION
    async def get_position(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_position')
        return await self._request(method, url, **params)

    async def update_position_isolate(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_isolate')
        return await self._request(method, url, **params)

    async def update_position_risk_limit(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_risk_limit')
        return await self._request(method, url, **params)

    async def update_position_transfer_margin(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_transfer_margin')
        return await self._request(method, url, **params)

    async def update_position_leverage(self, **params) -> httpx.Response:
        method, url = self.get_method_info('update_position_leverage')
        return await self._request(method, url, **params)

    # QUOTE
    async def get_quote(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_quote')
        return await self._request(method, url, **params)

    async def get_quote_bucketed(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_quote_bucketed')
        return await self._request(method, url, **params)

    # SCHEMA
    async def get_schema(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_schema')
        return await self._request(method, url, **params)

    async def get_schema_websocket_help(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_schema_websocket_help')
        return await self._request(method, url, **params)

    # SETTLEMENT
    async def get_settlement(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_settlement')
        return await self._request(method, url, **params)

    # STATS
    async def get_stats(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_stats')
        return await self._request(method, url, **params)

    async def get_stats_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_stats_history')
        return await self._request(method, url, **params)

    async def get_status_history_usd(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_status_history_usd')
        return await self._request(method, url, **params)

    # TRADE
    async def get_trade(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_trade')
        return await self._request(method, url, **params)

    async def get_trade_bucketed(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_trade_bucketed')
        return await self._request(method, url, **params)

    # USER
    async def get_user_deposit_address(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_deposit_address')
        return await self._request(method, url, **params)

    async def get_user_wallet(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_wallet')
        return await self._request(method, url, **params)

    async def get_user_wallet_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_wallet_history')
        return await self._request(method, url, **params)

    async def get_user_wallet_summary(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_wallet_summary')
        return await self._request(method, url, **params)

    async def get_user_execution_history(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_execution_history')
        return await self._request(method, url, **params)

    async def get_user_withdrawal_fee(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_withdrawal_fee')
        return await self._request(method, url, **params)

    async def user_request_withdrawal(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_request_withdrawal')
        return await self._request(method, url, **params)

    async def user_cansel_withdrawal(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_cansel_withdrawal')
        return await self._request(method, url, **params)

    async def user_confirm_withdrawal(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_confirm_withdrawal')
        return await self._request(method, url, **params)

    async def user_confirm_email(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_confirm_email')
        return await self._request(method, url, **params)

    async def get_user_affiliate_status(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_affiliate_status')
        return await self._request(method, url, **params)

    async def user_check_referral_code(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_check_referral_code')
        return await self._request(method, url, **params)

    async def get_user_quote_fill_ratio(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_quote_fill_ratio')
        return await self._request(method, url, **params)

    async def get_user_quote_value_ratio(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_quote_value_ratio')
        return await self._request(method, url, **params)

    async def get_user_trading_volume(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_trading_volume')
        return await self._request(method, url, **params)

    async def user_logout(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_logout')
        return await self._request(method, url, **params)

    async def user_preferences(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_preferences')
        return await self._request(method, url, **params)

    async def get_user(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user')
        return await self._request(method, url, **params)

    async def get_user_commission(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_commission')
        return await self._request(method, url, **params)

    async def get_user_margin(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_margin')
        return await self._request(method, url, **params)

    async def user_communication_token(self, **params) -> httpx.Response:
        method, url = self.get_method_info('user_communication_token')
        return await self._request(method, url, **params)

    async def get_user_event(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_user_event')
        return await self._request(method, url, **params)

    # WALLET
    async def get_wallet_assets(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_wallet_assets')
        return await self._request(method, url, **params)

    async def get_wallet_networks(self, **params) -> httpx.Response:
        method, url = self.get_method_info('get_wallet_networks')
        return await self._request(method, url, **params)
