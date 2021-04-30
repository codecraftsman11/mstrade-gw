from typing import Tuple, Optional
from abc import ABCMeta
from abc import abstractmethod
from .....wss.serializer import Serializer
from ...utils import stock2symbol


class BitmexSerializer(Serializer):
    __metaclass__ = ABCMeta
    subscription = "bitmex"

    @classmethod
    def _get_data_action(cls, message) -> str:
        return message.get('action', 'update')

    @classmethod
    def _update_data(cls, data: list, item: dict):
        data.append(item)

    @abstractmethod
    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        return item

    @abstractmethod
    def is_item_valid(self, message: dict, item: dict) -> bool:
        return False

    async def _get_data(self, message: dict) -> Tuple[str, list]:
        data = []
        for item in message['data']:
            await self._append_item(data, message, item)
        return self._get_data_action(message), data

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_state(stock2symbol(valid_item.get('symbol')), valid_item)
        self._update_data(data, valid_item)
