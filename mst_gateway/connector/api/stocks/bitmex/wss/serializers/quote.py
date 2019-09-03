from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from copy import copy
from .base import BitmexSerializer
from ...utils import load_quote_data
from ...utils import load_quote_bin_data
from ...utils import quote2bin
from ...utils import update_quote_bin

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexQuoteBinSerializer(BitmexSerializer):
    subscription = "quote_bin"

    def __init__(self, wss_api: BitmexWssApi):
        self._bins = {}
        self._initialized = False
        super().__init__(wss_api)

    @classmethod
    def _get_data_action(cls, message):
        if message.get('action') == "partial":
            return "partial"
        return "update"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if not self._initialized:
            if message['table'] != "tradeBin1m":
                return False
            self._initialized = True
            return True
        return message['table'] in ("trade", "tradeBin1m")

    def _load_data(self, message: dict, item: dict) -> dict:
        if self._bin_closed(message, item):
            return copy(self._reset_quote_bin(message, item))
        return copy(self._update_quote_bin(item))

    def _get_quote_bin(self, item: dict) -> dict:
        quote = load_quote_data(item)
        quote_bin = self._bins.get(item['symbol'])
        if not quote_bin:
            return quote2bin(quote)
        return update_quote_bin(quote_bin, quote)

    def _update_quote_bin(self, item):
        self._bins[item['symbol']] = self._get_quote_bin(item)
        return self._bins[item['symbol']]

    def _reset_quote_bin(self, message: dict, item: dict) -> dict:
        # pylint: disable=unused-argument
        self._bins[item['symbol']] = None
        return load_quote_bin_data(item)

    def _update_data(self, data: list, item: dict) -> dict:
        for ditem in data:
            if ditem['symbol'] == item['symbol']:
                return data
        data.append(item)
        return data

    def _bin_closed(self, message: dict, item: dict) -> bool:
        # pylint:disable=no-self-use,unused-argument
        return message['table'] == 'tradeBin1m'


class BitmexQuoteBinFromTradeSerializer(BitmexQuoteBinSerializer):
    @classmethod
    def _minute_updated(cls, ts_old: datetime, ts_new: datetime) -> bool:
        if (ts_new - ts_old).total_seconds() >= 60:
            return True
        return ts_new.minute > ts_old.minute

    def _bin_closed(self, message: dict, item: dict) -> bool:
        if message['table'] == 'tradeBin1m':
            return True
        if message['table'] == 'trade':
            new = load_quote_data(item)
            old = self._bins.get(item['symbol'])
            if not old:
                return False
            return self._minute_updated(old['timestamp'], new['timestamp'])
        return False

    def _reset_quote_bin(self, message: dict, item: dict) -> dict:
        if message['table'] == 'tradeBin1m':
            self._bins[item['symbol']] = load_quote_bin_data(item)
        else:
            self._bins[item['symbol']] = quote2bin(load_quote_data(item))
        return self._bins[item['symbol']]
