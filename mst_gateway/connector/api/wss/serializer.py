class Serializer:
    def __init__(self, data):
        self._data = data
        self._validated_data = None

    def is_valid(self):
        self._validated_data = self._data
        return True

    @property
    def data(self):
        return self._data

    @property
    def validated_data(self):
        return self._validated_data
