from typing import Tuple
from abc import ABCMeta
from abc import abstractmethod
from .....wss.serializer import Serializer
from ...utils import stock2symbol


class BitmexSerializer(Serializer):
    __metaclass__ = ABCMeta
    subscription = "base"

    @classmethod
    def _get_data_action(cls, message) -> str:
        return message.get('action', 'update')

    @classmethod
    def _update_data(cls, data: list, item: dict):
        data.append(item)

    @abstractmethod
    def _load_data(self, message: dict, item: dict) -> dict:
        return item

    @abstractmethod
    def is_item_valid(self, message: dict, item: dict) -> bool:
        return False

    def _get_data(self, message: dict) -> Tuple[str, list]:
        data = []
        for item in message['data']:
            self._append_item(data, message, item)
        return (self._get_data_action(message), data)

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        self._update_state(stock2symbol(valid_item['symbol']), valid_item)
        self._update_data(data, valid_item)
