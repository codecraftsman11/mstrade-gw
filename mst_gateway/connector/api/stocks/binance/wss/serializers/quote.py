from __future__ import annotations
from typing import TYPE_CHECKING
from .base import BinanceSerializer
from ..utils import load_quote_bin_ws_data

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BinanceQuoteBinSerializer(BinanceSerializer):
    subscription = "quote_bin"

    def __init__(self, wss_api: BitmexWssApi):
        self._bins = {}
        self._initialized = False
        super().__init__(wss_api)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('e') == "kline"

    def _load_data(self, message: dict, item: dict) -> dict:
        return load_quote_bin_ws_data(item, item['s'])

    # def _get_quote_bin(self, item: dict) -> dict:
    #     quote = load_quote_data(item)
    #     quote_bin = self._bins.get(item['symbol'])
    #     if not quote_bin:
    #         return quote2bin(quote)
    #     return update_quote_bin(quote_bin, quote)

    # def _update_quote_bin(self, item) -> dict:
    #     self._bins[item['symbol']] = self._get_quote_bin(item)
    #     return self._bins[item['symbol']]

    # def _reset_quote_bin(self, message: dict, item: dict) -> dict:
    #     # pylint: disable=unused-argument
    #     self._bins[item['symbol']] = None
    #     return load_quote_bin_data(item)
    #
    # def _update_data(self, data: list, item: dict):
    #     for ditem in data:
    #         if ditem['symbol'] == item['symbol']:
    #             return
    #     data.append(item)
    #
    # def _bin_closed(self, message: dict, item: dict) -> bool:
    #     # pylint:disable=no-self-use,unused-argument
    #     return message['table'] == 'tradeBin1m'


# class BitmexQuoteBinFromTradeSerializer(BitmexQuoteBinSerializer):
#     @classmethod
#     def _minute_updated(cls, ts_old: datetime, ts_new: datetime) -> bool:
#         if (ts_new - ts_old).total_seconds() >= 60:
#             return True
#         return ts_new.minute > ts_old.minute
#
#     def _bin_closed(self, message: dict, item: dict) -> bool:
#         if message['table'] == 'tradeBin1m':
#             return True
#         if message['table'] == 'trade':
#             new = load_quote_data(item)
#             old = self._bins.get(item['symbol'])
#             if not old:
#                 return False
#             return self._minute_updated(old['time'], new['time'])
#         return False
#
#     def _reset_quote_bin(self, message: dict, item: dict) -> dict:
#         if message['table'] == 'tradeBin1m':
#             self._bins[item['symbol']] = load_quote_bin_data(item)
#         else:
#             self._bins[item['symbol']] = quote2bin(load_quote_data(item))
#         return self._bins[item['symbol']]
