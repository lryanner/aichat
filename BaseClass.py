class DataGUIInterface:
    def __init__(self, *args, **kwargs):
        """
        init function.
        :param args:
        :param kwargs:
        """

    def _load_data(self, data):
        """
        load the data
        :param data:
        :return:
        """

    def _data(self):
        """
        :return: data
        """

    data = property(_data, _load_data)