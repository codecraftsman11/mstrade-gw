from mst_gateway.exceptions import ConnectorError


def validate_schema(schema: str, schema_handlers: iter):
    schema = schema.lower()
    if schema not in schema_handlers:
        raise ConnectorError(f"Invalid schema {schema}.")
