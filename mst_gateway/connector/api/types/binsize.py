from mst_gateway.utils import ClassWithAttributes


class BinSize(ClassWithAttributes):
    m1 = ('1m', '1 minute')
    m5 = ('5m', '5 minutes')
    h1 = ('1h', '1 hour')
    d1 = ('1d', '1 day')

    def __init__(self, bin_size):
        self._binsize = bin_size.lower()

    @classmethod
    def valid_sizes(cls):
        return tuple(i[1][0] for i in cls._attributes())

    @classmethod
    def pairs(cls):
        return tuple(i[1] for i in cls._attributes())

    @property
    def to_sec(self):
        if self._binsize == self.m1[0]:
            return 60
        if self._binsize == self.m5[0]:
            return 300
        if self._binsize == self.h1[0]:
            return 3600
        if self._binsize == self.d1[0]:
            return 86400
        return 0
