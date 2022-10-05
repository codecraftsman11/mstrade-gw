from mst_gateway.connector.api.stocks.binance.wss.serializers.wallet import BinanceWalletSerializer


class BinanceWalletExtraSerializer(BinanceWalletSerializer):
    subscription = "wallet_extra"

    def _wallet_list(self, item: dict):
        return list(self.state_data.values())
