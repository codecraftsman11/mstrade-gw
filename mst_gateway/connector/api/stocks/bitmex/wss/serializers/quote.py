from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from copy import copy
from mst_gateway.connector import api
from .base import BitmexSerializer
from ...utils import (
    load_quote_data, load_quote_bin_data,
    quote2bin, update_quote_bin
)


if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexQuoteBinSerializer(BitmexSerializer):
    subscription = "quote_bin"

    def __init__(self, wss_api: BitmexWssApi):
        self._bins = {}
        self._initialized = False
        super().__init__(wss_api)

    @classmethod
    def _get_data_action(cls, message) -> str:
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

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['symbol'].lower())
        if not state_data:
            return None
        if self._bin_closed(message, item, state_data):
            return copy(self._reset_quote_bin(message, item, state_data))
        return copy(self._update_quote_bin(item, state_data))

    def _get_quote_bin(self, item: dict, state_data: dict) -> dict:
        quote = load_quote_data(item, state_data, is_iso_datetime=True)
        quote_bin = self._bins.get(item['symbol'])
        if not quote_bin:
            return quote2bin(quote)
        return update_quote_bin(quote_bin, quote)

    def _update_quote_bin(self, item, state_data: dict) -> dict:
        self._bins[item['symbol']] = self._get_quote_bin(item, state_data)
        return self._get_quote_bin(item, state_data)

    def _reset_quote_bin(self, message: dict, item: dict, state_data: dict) -> dict:
        # pylint: disable=unused-argument
        self._bins[item['symbol']] = None
        return load_quote_bin_data(item, state_data, is_iso_datetime=True)

    def _update_data(self, data: list, item: dict):
        for ditem in data:
            if ditem['symbol'] == item['symbol']:
                return
        data.append(item)

    def _bin_closed(self, message: dict, item: dict, state_data: dict) -> bool:
        # pylint:disable=no-self-use,unused-argument
        return message['table'] == 'tradeBin1m'


class BitmexQuoteBinFromTradeSerializer(BitmexQuoteBinSerializer):
    @classmethod
    def _minute_updated(cls, ts_old: str, ts_new: str) -> bool:
        try:
            ts_old = datetime.strptime(ts_old, api.DATETIME_OUT_FORMAT)
            ts_new = datetime.strptime(ts_new, api.DATETIME_OUT_FORMAT)
        except ValueError:
            return False
        if (ts_new - ts_old).total_seconds() >= 60:
            return True
        return ts_new.minute > ts_old.minute

    def _bin_closed(self, message: dict, item: dict, state_data: dict) -> bool:
        if message['table'] == 'tradeBin1m':
            return True
        if message['table'] == 'trade':
            new = load_quote_data(item, state_data, is_iso_datetime=True)
            old = self._bins.get(item['symbol'])
            if not old:
                return False
            return self._minute_updated(old['time'], new['time'])
        return False

    def _reset_quote_bin(self, message: dict, item: dict, state_data: dict) -> dict:
        if message['table'] == 'tradeBin1m':
            self._bins[item['symbol']] = load_quote_bin_data(item, state_data, is_iso_datetime=True)
        else:
            self._bins[item['symbol']] = quote2bin(load_quote_data(item, state_data, is_iso_datetime=True))
        return self._bins[item['symbol']]
