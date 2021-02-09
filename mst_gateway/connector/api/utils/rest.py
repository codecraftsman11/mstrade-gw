from mst_gateway.exceptions import NotFoundError


def validate_exchange_order_id(exchange_order_id):
    if not exchange_order_id:
        raise NotFoundError('Exchange order ID was not provided.')
