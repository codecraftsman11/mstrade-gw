from mst_gateway.connector.api.types import OrderSchema, ExchangeDrivers


def to_exchange_asset(driver: str, schema: str, asset: str) -> str:
    asset = asset.lower()
    if driver == ExchangeDrivers.bitmex and schema == OrderSchema.margin and asset == 'btc':
        return 'xbt'
    if schema != OrderSchema.margin_coin and asset == 'usd':
        return 'usdt'
    return asset
