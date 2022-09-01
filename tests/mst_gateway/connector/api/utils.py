from typing import Optional
from mst_gateway.connector.api import BUY
from mst_gateway.connector.api.rest import StockRestApi


def get_order_price(rest: StockRestApi, schema: str, symbol: str, side: int) -> Optional[float]:
    symbol = rest.get_symbol(schema=schema, symbol=symbol)
    if side == BUY:
        return round(symbol.get('bid_price') / 1.05, 0)
    return round(symbol.get('ask_price') * 1.05, 0)


def get_order_stop_price(price: float, side):
    if side == BUY:
        return round(price * 1.05 * 1.1, 0)
    return round(price / 1.05 / 1.1, 0)
