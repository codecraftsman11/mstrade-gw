# pylint: disable=no-self-use
from mst_gateway.connector import api
from mst_gateway.connector.api.validators import (
    type_valid,
    schema_valid
)


class TestApi:
    def test_api_order_type_valid(self):
        assert type_valid(api.OrderType.box_top)
        assert not type_valid('invalid_type')

    def test_api_order_schema_valid(self):
        assert schema_valid(api.OrderSchema.margin1)
        assert not schema_valid('invalid_schema')
