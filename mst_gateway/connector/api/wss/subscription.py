from abc import ABCMeta, abstractmethod


class Subscription:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._is_subscribed = False

    def subscribe(self, data):
        self._subscribe(data)
        self._is_subscribed = True

    def unsubscribe(self, data):
        self._unsubscribe(data)
        self._is_subscribed = False

    @abstractmethod
    def _subscribe(self, data):
        pass

    @abstractmethod
    def _unsubscribe(self, data):
        pass
