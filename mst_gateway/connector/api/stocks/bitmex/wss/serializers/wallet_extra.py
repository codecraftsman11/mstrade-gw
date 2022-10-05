from .wallet import BitmexWalletSerializer


class BitmexWalletExtraSerializer(BitmexWalletSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return False
