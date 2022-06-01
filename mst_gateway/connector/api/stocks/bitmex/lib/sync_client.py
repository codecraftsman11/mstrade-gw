import httpx
from typing import Optional
from .base import BaseBitmexApiClient


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
        path = self._prepared_path if self._prepared_path else self._prepare_path(path, params)
        headers = self._get_headers(method, path, optional_headers)
        with httpx.Client(headers=headers, proxies=proxies, timeout=timeout) as client:
            url = self._request_url if self._request_url else self.create_url(path, True)
            request = client.build_request(method, url)
            self.response = client.send(request)
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
