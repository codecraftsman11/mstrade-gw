import httpx
from typing import Tuple


class BitmexMethodFactory:
    API_URL = 'https://www.bitmex.com/api'
    API_TESTNET_URL = 'https://testnet.bitmex.com/api'
    V1 = 'v1'

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

    @classmethod
    def info(cls, method_name, testnet=False, **params) -> Tuple[str, httpx.URL]:
        return getattr(cls, method_name)(testnet, **params)

    @classmethod
    def _api_url(cls, testnet=False):
        return cls.API_TESTNET_URL if testnet else cls.API_URL

    @classmethod
    def get_announcement(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/announcement", params=params)

    @classmethod
    def get_announcement_urgent(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/announcement/urgent", params=params)

    @classmethod
    def get_api_keys(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/apiKey", params=params)

    @classmethod
    def get_chat_pinned(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat/pinned", params=params)

    @classmethod
    def send_pinned_message_to_channel(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat/pinned", params=params)

    @classmethod
    def remove_pinned_message_from_chat(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat/pinned", params=params)

    @classmethod
    def get_chat(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat", params=params)

    @classmethod
    def send_message_to_chat(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat", params=params)

    @classmethod
    def get_available_channels(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat/channels", params=params)

    @classmethod
    def get_connected_user_to_chat(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/chat/connected", params=params)

    @classmethod
    def get_execution(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/execution", params=params)

    @classmethod
    def get_execution_trade_history(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/execution/tradeHistory", params=params)

    @classmethod
    def get_funding(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/funding", params=params)

    @classmethod
    def get_instrument(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/instrument", params=params)

    @classmethod
    def get_instrument_active(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/instrument/active", params=params)

    @classmethod
    def get_instrument_active_and_indices(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/instrument/activeAndIndices", params=params)

    @classmethod
    def get_instrument_active_intervals(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/instrument/activeIntervals", params=params)

    @classmethod
    def get_instrument_composite_index(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/instrument/compositeIndex", params=params)

    @classmethod
    def get_instrument_usd_volume(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/instrument/usdVolume", params=params)

    @classmethod
    def get_insurance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/insurance", params=params)

    @classmethod
    def get_leaderboard(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/leaderboard", params=params)

    @classmethod
    def get_leaderboard_name(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/leaderboard/name", params=params)

    @classmethod
    def get_liquidation(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/liquidation", params=params)

    @classmethod
    def get_global_notification(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/globalNotification", params=params)

    @classmethod
    def get_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def create_order(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def update_order(cls, testnet=False, **params):
        return cls.PUT, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def cancel_order(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def cancel_all_orders(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order/all", params=params)

    @classmethod
    def close_position(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order/closePosition", params=params)

    @classmethod
    def cancel_orders_after(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/order/cancelAllAfter", params=params)

    @classmethod
    def get_order_book_l2(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/orderBook/L2", params=params)

    @classmethod
    def get_position(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/position", params=params)

    @classmethod
    def update_position_isolate(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/position/isolate", params=params)

    @classmethod
    def update_position_risk_limit(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/position/riskLimit", params=params)

    @classmethod
    def update_position_transfer_margin(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/position/transferMargin", params=params)

    @classmethod
    def update_position_leverage(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/position/leverage", params=params)

    @classmethod
    def get_quote(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/quote", params=params)

    @classmethod
    def get_quote_bucketed(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/quote/bucketed", params=params)

    @classmethod
    def get_schema(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/schema", params=params)

    @classmethod
    def get_schema_websocket_help(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/schema/websocketHelp", params=params)

    @classmethod
    def get_settlement(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/settlement", params=params)

    @classmethod
    def get_stats(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/stats", params=params)

    @classmethod
    def get_stats_history(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/stats/history", params=params)

    @classmethod
    def get_status_history_usd(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/stats/historyUSD", params=params)

    @classmethod
    def get_trade(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/trade", params=params)

    @classmethod
    def get_trade_bucketed(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/trade/bucketed", params=params)

    @classmethod
    def get_user_deposit_address(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/depositAddress", params=params)

    @classmethod
    def get_user_wallet(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/wallet", params=params)

    @classmethod
    def get_user_wallet_history(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/walletHistory", params=params)

    @classmethod
    def get_user_wallet_summary(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/walletSummary", params=params)

    @classmethod
    def get_user_execution_history(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/executionHistory", params=params)

    @classmethod
    def get_user_withdrawal_fee(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/minWithdrawalFee", params=params)

    @classmethod
    def user_request_withdrawal(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/requestWithdrawal", params=params)

    @classmethod
    def user_cansel_withdrawal(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/cancelWithdrawal", params=params)

    @classmethod
    def user_confirm_withdrawal(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/confirmWithdrawal", params=params)

    @classmethod
    def user_confirm_email(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/confirmEmail", params=params)

    @classmethod
    def get_user_affiliate_status(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/affiliateStatus", params=params)

    @classmethod
    def user_check_referral_code(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/checkReferralCode", params=params)

    @classmethod
    def get_user_quote_fill_ratio(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/quoteFillRatio", params=params)

    @classmethod
    def get_user_quote_value_ratio(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/quoteValueRatio", params=params)

    @classmethod
    def get_user_trading_volume(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/tradingVolume", params=params)

    @classmethod
    def user_logout(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/logout", params=params)

    @classmethod
    def user_preferences(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/preferences", params=params)

    @classmethod
    def get_user(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user", params=params)

    @classmethod
    def get_user_commission(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/commission", params=params)

    @classmethod
    def get_user_margin(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/margin", params=params)

    @classmethod
    def user_communication_token(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/user/communicationToken", params=params)

    @classmethod
    def get_user_event(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/userEvent", params=params)

    @classmethod
    def get_wallet_assets(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/wallet/assets", params=params)

    @classmethod
    def get_wallet_networks(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V1}/wallet/networks", params=params)
