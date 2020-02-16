class ThreadData:
    """
    Class for representing a thread safe piece of data
    """

    def __init__(self, data=None):
        self._data = [data]

    @property
    def data(self):
        return self._data[0]

    @data.setter
    def data(self, dataPiece):
        self._data[0] = dataPiece
