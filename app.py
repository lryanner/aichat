import threading

from PySide6.QtCore import QObject

from ChatBot import ChatBotFactory, ChatBot
from GUI import AppGUI
from PySide6.QtWidgets import QApplication
import sys

from data import DataLoader
from event import MainWindowHintEvent
from event_type import *


class App(QObject):
    """
    The app class.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        The singleton.
        :param args:
        :param kwargs:
        """
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        super().__init__()
        App._instance = self
        self.app = QApplication([])
        self.data_loader = DataLoader()
        # install event filter
        self.data_loader.installEventFilter(self)
        self.gui:AppGUI|None = None
        self.chatbot_factory:ChatBotFactory|None = None

    def run(self):
        self.data_loader.load_data()
        sys.exit(self.app.exec())

    def eventFilter(self, obj, event):
        if event.type() == DataLoadedEventType:
            self.init_gui(event)
        elif event.type() == SaveDataEventType:
            self.data_loader.save_data(event.data_type)
        elif event.type() == SendMessageEventType:
            if isinstance(obj, AppGUI):
                self.chatbot_factory.receive_message(event.history_id, event.message)
            if isinstance(obj, ChatBotFactory):
                self.gui.receive_message(event.history_id, event.message)
        elif event.type() == SpeakMessageEventType:
            if isinstance(obj, AppGUI):
                self.chatbot_factory.speak_it(event.history_id, event.message)
            if isinstance(obj, ChatBotFactory):
                self.gui.speak_message(event.history_id, event.message)
        elif event.type() == AddChatBotEventType:
            self.chatbot_factory.create_chatbot(event.data)
        elif event.type() == DeleteChatBotEventType:
            self.chatbot_factory.delete_chatbot(event.chatbot_id)
        return super().eventFilter(obj, event)

    def event(self, e):
        if isinstance(e, MainWindowHintEvent):
            self.gui.hint(e.hint_type, e.hint_message, self.gui.default_hint_area, e.interval)
            return True
        return super().event(e)

    def init_gui(self, event: QEvent):
        self.gui = AppGUI(event.config_data, event.chatbots_data)
        self.gui.InitFinished.connect(lambda : self.init_chatbot_factory(event))
        self.gui.ConfigSaved.connect(lambda : self.chatbot_factory.setup_config())
        self.gui.installEventFilter(self)
        if event.first_time:
            self.gui.open_global_config_dialog(first_time=True)
        else:
            self.gui.InitFinished.emit()
        self.gui.show()

    def init_chatbot_factory(self, event: QEvent):
        self.chatbot_factory = ChatBotFactory(event.config_data, event.chatbots_data)
        self.chatbot_factory.installEventFilter(self)

    @staticmethod
    def get_instance():
        if not App._instance:
            App._instance = App()
        return App._instance


if __name__ == '__main__':
    app = App()
    app.run()
