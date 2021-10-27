from mst_gateway.exceptions import ConnectorError, NotFoundError


def validate_exchange_order_id(exchange_order_id):
    if not exchange_order_id:
        raise NotFoundError('Exchange order ID was not provided.')


def validate_schema(schema: str, schema_handlers: iter):
    schema = schema.lower()
    if schema not in schema_handlers:
        raise ConnectorError(f"Invalid schema {schema}.")
