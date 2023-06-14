from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from GUI import AppGUI


class EventCenter(QObject):
    """
    The event center. This class is used to send and receive events.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        The singleton.
        :param args:
        :param kwargs:
        """
        if cls._instance is None:
            cls._instance = super(EventCenter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    @staticmethod
    def send_event(event):
        """
        Send the event.
        :param event: the event.
        :return:
        """
        if not EventCenter._instance:
            EventCenter._instance = EventCenter()
        QApplication.postEvent(AppGUI.get_instance(), event)
