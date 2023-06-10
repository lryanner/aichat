import datetime
from enum import Enum
from functools import total_ordering

class BaseEnum(Enum):
    @classmethod
    def from_string(cls, string):
        return getattr(cls, string)

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError('No member with value {}'.format(value))

    @classmethod
    def get_name_list(cls):
        return [member.name for member in cls]
class AIChat(BaseEnum):
    AddNewChatBotMode = 0
    EditChatBotMode = 1
    BasicSettingStage = 2
    AdvancedSettingStage = 3


class SpeakerAPIType(BaseEnum):
    NeneEmotion = 0
    VitsSimpleAPI = 1


class TranslaterAPIType(BaseEnum):
    Google = 0
    Baidu = 1
    DeepL = 2
    Youdao = 3


class HintType(BaseEnum):
    Info = 0
    Warning = 1
    Error = 2

class AIGui(BaseEnum):
    VerticalAlignment = 0
    HorizontalAlignment = 1

class DataType(BaseEnum):
    Config = 0
    ChatBot = 1