from typing import Tuple, Optional
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import BinanceSerializer
from mst_gateway.connector.api.stocks.binance.wss.serializers.wallet import BinanceWalletSerializer


class BinanceWalletExtraSerializer(BinanceSerializer):
    subscription = "wallet_extra"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return False

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        return None

    async def _get_data(self, message: any) -> Tuple[str, list]:
        return self._get_data_action(message), []


class BinanceMarginCrossWalletExtraSerializer(BinanceWalletSerializer):
    subscription = "wallet_extra"

    def _wallet_list(self, item: dict):
        return list(self.wallet_state.values())
