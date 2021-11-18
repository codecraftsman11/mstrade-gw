from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from mst_gateway.connector import api
from mst_gateway.connector.api.stocks.bitmex import utils
from .base import BitmexSerializer

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexQuoteBinSerializer(BitmexSerializer):
    subscription = 'quote_bin'

    def __init__(self, wss_api: BitmexWssApi):
        super().__init__(wss_api)
        self._bins = {}
        self._initialized = None

    def prefetch(self, message: dict) -> None:
        if message['table'] == 'tradeBin1m':
            data = []
            for item in message.pop('data', []):
                if time := utils.to_date(item['timestamp']):
                    item['timestamp'] = time.replace(minute=time.minute - 1, second=59, microsecond=999999)
                data += [item, self.create_open_data(item)]
            message['data'] = data

    @staticmethod
    def create_open_data(item: dict) -> dict:
        if bin_time := utils.to_date(item.get('timestamp')):
            bin_time = bin_time.replace(minute=bin_time.minute + 1, second=0, microsecond=000000)
        close = item.get('close')
        return {
            'timestamp': utils.to_iso_datetime(bin_time),
            'symbol': item.get('symbol'),
            'open': close,
            'close': close,
            'high': close,
            'low': close,
            'volume': 0
        }

    @classmethod
    def _get_data_action(cls, message) -> str:
        if message.get('action') == 'partial':
            return 'partial'
        return 'update'

    def is_item_valid(self, message: dict, item: dict) -> bool:
        table = message['table']
        if not self._initialized:
            if table != 'tradeBin1m':
                return False
            self._initialized = utils.to_date(item.get('timestamp'))
            return True
        time = utils.to_date(item.get('timestamp'))
        if time and time < self._initialized:
            return False
        return table in ('trade', 'tradeBin1m')

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(item.get('symbol'))) is None:
                return None
        if message['table'] == 'tradeBin1m':
            return utils.load_ws_quote_bin_data(item, state_data)
        if (minute_updated := self._minute_updated(item)) is None:
            return None
        if minute_updated:
            return self._reset_quote_bin(item, state_data)
        return self._update_quote_bin(item, state_data)

    def _update_quote_bin(self, item, state_data: dict) -> dict:
        symbol = item['symbol'].lower()
        quote = utils.load_ws_quote_data(item, state_data)
        if quote_bin := self._bins.get(symbol):
            self._bins[symbol] = utils.update_quote_bin(quote_bin, quote)
        else:
            self._bins[symbol] = utils.quote2bin(quote)
        return self._bins[symbol]

    def _reset_quote_bin(self, item: dict, state_data: dict) -> dict:
        symbol = item['symbol'].lower()
        prev_bin = self._bins[symbol]
        prev_bin_cl = prev_bin['clp']
        new_bin = utils.quote2bin(utils.load_ws_quote_data(item, state_data))
        new_bin.update({
            'opp': prev_bin_cl,
            'hip': max(new_bin['hip'], prev_bin_cl),
            'lop': min(new_bin['lop'], prev_bin_cl),
        })
        self._bins[symbol] = new_bin
        return self._bins[symbol]

    def _minute_updated(self, item: dict) -> Optional[bool]:
        if old := self._bins.get(item['symbol'].lower()):
            try:
                ts_old = datetime.strptime(old['tm'].split('Z')[0], api.DATETIME_FORMAT)
                ts_new = datetime.strptime(item['timestamp'].split('Z')[0], api.DATETIME_FORMAT)
            except (ValueError, TypeError, IndexError):
                return None
            if ts_new < ts_old:
                return None
            return ts_new.minute > ts_old.minute
        return False
