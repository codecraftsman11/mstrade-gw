from mst_gateway.connector.api import BUY, OrderType
from mst_gateway.connector.api.rest import StockRestApi


def get_order_price(rest: StockRestApi, schema: str, symbol: str, side: int):
    symbol = rest.get_symbol(schema=schema, symbol=symbol)
    if side == BUY:
        return round(symbol.get('bid_price') / 1.05, 0), symbol.get('price')
    return round(symbol.get('ask_price') * 1.05, 0), symbol.get('price')


def get_order_stop_price(price: float, side: int, order_type: str):
    if order_type in (OrderType.take_profit_limit, OrderType.take_profit_market, OrderType.trailing_stop):
        if side == BUY:
            return round(price / 1.02 / 1.1, 0)
        return round(price * 1.02 * 1.1, 0)

    if side == BUY:
        return round(price * 1.05 * 1.1, 0)
    return round(price / 1.05 / 1.1, 0)
