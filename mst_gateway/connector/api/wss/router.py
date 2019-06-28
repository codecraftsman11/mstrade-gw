from abc import ABCMeta
from abc import abstractmethod
from .serializer import Serializer


class Router:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, message) -> Serializer:
        return Serializer(message)
