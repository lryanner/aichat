import AIChatEnum
from event_type import *


class PlaySoundEvent(QEvent):
    """
    This event is used to play sound
    :param sound_path: the path to the sound file
    :param message_serial_id: the serial id of the message
    """

    def __init__(self, sound_path, message_serial_id):
        super().__init__(QEvent.User)
        self._message_serial_id = message_serial_id
        self._sound_path = sound_path

    def type(self):
        return PlaySoundEventType

    @property
    def message_serial_id(self):
        return self._message_serial_id

    @property
    def sound_path(self):
        return self._sound_path


class AddChatBotEvent(QEvent):
    """
    This event is used to add new chatbot to the chatbot list
    :param data: chatbot data
    """

    def __init__(self, data):
        super().__init__(QEvent.User)
        self._data = data

    def type(self):
        return AddChatBotEventType

    @property
    def data(self):
        return self._data


class DeleteChatBotEvent(QEvent):
    """
    This event is used to delete chatbot.
    :param chatbot_id: the id of the chatbot.
    """

    def __init__(self, chatbot_id):
        super().__init__(QEvent.User)
        self._chatbot_id = chatbot_id

    def type(self):
        return DeleteChatBotEventType

    @property
    def chatbot_id(self):
        return self._chatbot_id


class MainWindowHintEvent(QEvent):
    """
    This event is used to show hint in the main window
    :param hint_type: the type of the hint
    :param hint_message: the message of the hint
    """

    def __init__(self, hint_type: AIChatEnum.HintType, hint_message: str, interval=3000):
        super().__init__(QEvent.User)
        self._hint_type = hint_type
        self._hint_message = hint_message
        self._interval = interval

    def type(self):
        return MainWindowHintEventType

    @property
    def hint_type(self):
        return self._hint_type

    @property
    def hint_message(self):
        return self._hint_message

    @property
    def interval(self):
        return self._interval


class DataLoadedEvent(QEvent):
    """
    This event is used to notify that the data is loaded
    :param config_data: the config data
    :param chatbots_data: the chatbots data
    :param first_time: whether it is the first time to run the app
    """

    def __init__(self, config_data, chatbots_data, first_time=False):
        super().__init__(QEvent.User)
        self._config_data = config_data
        self._chatbots_data = chatbots_data
        self._first_time = first_time

    def type(self):
        return DataLoadedEventType

    @property
    def config_data(self):
        return self._config_data

    @property
    def chatbots_data(self):
        return self._chatbots_data

    @property
    def first_time(self):
        return self._first_time


class MainWindowCloseEvent(QEvent):
    """
    This event is used to notify that the main window is closed
    """

    def __init__(self):
        super().__init__(QEvent.User)

    def type(self):
        return MainWindowCloseEventType


class SaveDataEvent(QEvent):
    """
    This event is used to save data.
    :param data_type: the type of the data.
    """

    def __init__(self, data_type):
        super().__init__(QEvent.User)
        self._data_type = data_type

    def type(self):
        return SaveDataEventType

    @property
    def data_type(self):
        return self._data_type


class DeleteMessageEvent(QEvent):
    """
    This event is used to delete message
    :param data: the data of the message to be deleted
    """

    def __init__(self, history_id, data):
        super().__init__(QEvent.User)
        self._data = data
        self._history_id = history_id

    def type(self):
        return DeleteMessageEventType

    @property
    def history_id(self):
        return self._history_id

    @property
    def data(self):
        return self._data


class SendMessageEvent(QEvent):
    """
    This event is used to send message.
    :param message: the message to be sent.
    """

    def __init__(self, history_id, message):
        super().__init__(QEvent.User)
        self._message = message
        self._history_id = history_id

    def type(self):
        return SendMessageEventType

    @property
    def history_id(self):
        return self._history_id

    @property
    def message(self):
        return self._message


class SpeakMessageEvent(QEvent):
    """
    This event is used to speak message.
    :param message: the message to be spoken.
    :param history_id: the id of the history.
    """
    def __init__(self, history_id, message):
        super().__init__(QEvent.User)
        self._message = message
        self._history_id = history_id

    def type(self):
        return SpeakMessageEventType

    @property
    def history_id(self):
        return self._history_id

    @property
    def message(self):
        return self._message
