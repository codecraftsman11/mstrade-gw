from typing import Tuple, Union, Optional
from abc import ABCMeta
from abc import abstractmethod
from .....wss.serializer import Serializer


class BinanceSerializer(Serializer):
    __metaclass__ = ABCMeta
    subscription = "binance"

    @classmethod
    def _get_data_action(cls, message) -> str:
        return message.get('action', 'update')

    @classmethod
    def _update_data(cls, data: list, item: Union[dict, list]):
        if not isinstance(item, list):
            return data.append(item)
        data.extend(item)

    @abstractmethod
    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        return item

    @abstractmethod
    def is_item_valid(self, message: dict, item: dict) -> bool:
        return bool(item)

    def _get_data(self, message: dict) -> Tuple[str, list]:
        data = []
        for item in message['data']:
            self._append_item(data, message, item)
        return self._get_data_action(message), data

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        if not valid_item:
            return None
        self._update_state(valid_item['symbol'], valid_item)
        self._update_data(data, valid_item)
