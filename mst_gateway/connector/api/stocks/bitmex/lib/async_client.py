import httpx
from typing import Optional
from .base import BaseBitmexApiClient


class AsyncBitmexApiClient(BaseBitmexApiClient):
    """
    Async client for bitmex api exchange
    For details of request params see: https://testnet.bitmex.com/api/explorer/
    """

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], testnet: bool = False, version=None):
        super().__init__(api_key, api_secret, version, testnet)

    async def _request(self, method: str, path: str, **params) -> dict:
        optional_headers = params.pop('headers', None)
        proxies = params.pop('proxies', None)
        timeout = params.pop('timeout', None)
        path = self._prepare_path(path, params)
        headers = self._get_headers(method, path, optional_headers)
        async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=timeout) as client:
            url = self._create_url(path, True)
            request = client.build_request(method, url)
            self.response = await client.send(request)
        return self._handle_response(self.response)

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
