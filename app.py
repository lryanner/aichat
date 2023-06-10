from PySide6.QtCore import QObject

from ChatBot import ChatBotFactory, ChatBot
from GUI import AppGUI
from PySide6.QtWidgets import QApplication
import sys

from data import DataLoader
from event_type import *


class App(QObject):
    def __init__(self):
        super().__init__()
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
            return True
        elif event.type() == SaveDataEventType:
            self.data_loader.save_data(event.data_type)
            return True
        elif event.type() == SendMessageEventType:
            if isinstance(obj, AppGUI):
                self.chatbot_factory.receive_message(event.history_id, event.message)
            if isinstance(obj, ChatBotFactory):
                self.gui.receive_message(event.history_id, event.message)
        elif event.type() == SpeakMessageEventType:
            self.gui.speak_message(event.history_id, event.message)
        elif event.type() == AddChatBotEventType:
            self.chatbot_factory.create_chatbot(event.data)
        elif event.type() == DeleteChatBotEventType:
            self.chatbot_factory.delete_chatbot(event.chatbot_id)
        return super().eventFilter(obj, event)

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


if __name__ == '__main__':
    app = App()
    app.run()
