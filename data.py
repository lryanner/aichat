import datetime
import os
from functools import total_ordering
from typing import Iterable, Iterator

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

import AIChatEnum
import event
import utils
from AIChatEnum import TranslaterAPIType


def load_data(path) -> dict:
    """
    Load data, must return a dict
    :param path: file path
    :return: dict, data
    """
    return utils.load_json(path)


def save_data(data, path):
    """
    Save data to path. Data must be a dict.
    :param data: dict
    :param path: file path
    :return:
    """
    utils.save_json(path, data)


class DataLoader(QObject):
    def __init__(self, data_path='./save', data_file='save.json'):
        super().__init__()
        self._data = None
        self._chatbots_data = None
        self._config_data = None
        self._data_path = data_path
        self._data_file = data_file
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        if not os.path.exists(os.path.join(data_path, data_file)):
            utils.save_json(os.path.join(data_path, data_file), {})

    def load_data(self):
        self._data = load_data(os.path.join(self._data_path, self._data_file))
        # if there is no 'config' key, emit a config init signal
        if 'config' not in self._data:
            first_time = True
            self._config_data = ConfigData({
                'user_config': {
                    'name': 'Me',
                    'avatar_path': './resources/images/test_avatar_me.jpg',
                },
                'openai_config': {
                    'openai_api_key': '',
                    'gpt_params': {
                        'model': 'gpt-3.5-turbo',
                        'temperature': 0.8,
                        'max_tokens': 512,
                        'top_p': 1,
                        'frequency_penalty': 0,
                        'presence_penalty': 0,
                    }
                },
                'translater_config': [
                    {
                        'api_type': TranslaterAPIType.Baidu.value,
                        'app_id': '',
                        'app_key': '',
                        'active': 0
                    },
                    {
                        'api_type': TranslaterAPIType.Google.value,
                        'api_key': '',
                        'active': 0
                    },
                    {
                        'api_type': TranslaterAPIType.Youdao.value,
                        'app_id': '',
                        'app_key': '',
                        'active': 0
                    },
                    {
                        'api_type': TranslaterAPIType.DeepL.value,
                        'api_key': '',
                        'active': 0
                    },
                    {
                        'api_type': TranslaterAPIType.OpenAI.value,
                        'gpt_model': 'gpt-3.5-turbo',
                        'active': 0
                    },
                ],
                'vits_config': [
                    {
                        'api_type': AIChatEnum.SpeakerAPIType.VitsSimpleAPI.value,
                        'api_address': '',
                        'api_port': '',
                        'active': 0,
                    },
                    {
                        'api_type': AIChatEnum.SpeakerAPIType.NeneEmotion.value,
                        'api_address': '',
                        'api_port': '',
                        'active': 0,
                    },
                ],
            })
        else:
            first_time = False
            self._config_data = ConfigData(self._data['config'])
        if 'chatbots' not in self._data:
            self._data['chatbots'] = []
        chatbots_data = self._data['chatbots']
        self._chatbots_data = ChatBotDataList([])
        if chatbots_data:
            for chatbot_data in chatbots_data:
                self._chatbots_data.append(ChatBotData(**chatbot_data))
        self._chatbots_data.sort()
        QApplication.sendEvent(self, event.DataLoadedEvent(self._config_data, self._chatbots_data, first_time))

    def save_data(self, data_type):
        match data_type:
            case AIChatEnum.DataType.Config:
                self._data['config'] = self._config_data.data
            case AIChatEnum.DataType.ChatBot:
                self._data['chatbots'] = self._chatbots_data.data
        self._save_data_to_file()

    def update_data(self, data_type, data):
        match data_type:
            case AIChatEnum.DataType.ChatBot:
                self._chatbots_data[data.chatbot_id].update(data)
                self._data['chatbots'] = self._chatbots_data.data
        self._save_data_to_file()

    def _save_data_to_file(self):
        utils.save_json(os.path.join(self._data_path, self._data_file), self._data)

    openai_api_key = property(lambda self: self._config_data.openai_config.openai_api_key)
    config_data = property(lambda self: self._config_data)
    chatbots_data = property(lambda self: self._chatbots_data)


class Data:
    """
    Base class for all data classes
    """

    def __init__(self, data_id):
        self._id = data_id

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if isinstance(other, Data):
            return self._id == other.id_
        return False

    id_ = property(lambda self: self._id)
    data = property(lambda self: self._get_data())
    json_safe_data = property(lambda self: self._get_json_safe_data())

    def _get_data(self):
        """
        return a dict of this class' properties
        :return: dict
        """
        return_dict = {}
        for name, obj in vars(self.__class__).items():
            if isinstance(obj, property):
                if isinstance(getattr(self, name), Data):
                    return_dict[name] = getattr(self, name).data
                else:
                    return_dict[name] = getattr(self, name)
            else:
                pass
        return return_dict

    def _get_json_safe_data(self):
        """
        return a dict of this class' properties, and the json safe version of the data, e.g. datetime.datetime
        :return: dict
        """
        return_dict = {}
        for name, obj in vars(self.__class__).items():
            if isinstance(obj, property):
                if isinstance(getattr(self, name), Data):
                    return_dict[name] = getattr(self, name).get_json_safe_data()
                elif isinstance(getattr(self, name), datetime.datetime):
                    return_dict[name] = getattr(self, name).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    return_dict[name] = getattr(self, name)
            else:
                pass
        return return_dict

    def update(self, data) -> None:
        """
        update data from another data object
        :param data: another data object
        :return: None
        """


class UserConfigData(Data):
    """
    Data class for user config
    :param name: str
    :param avatar_path: str
    """

    def __init__(self, **kwargs):
        self._name = kwargs['name']
        self._avatar_path = kwargs['avatar_path']
        super().__init__('user_config')

    def update(self, data) -> None:
        self._name = data.name
        self._avatar_path = data.avatar_path

    name = property(lambda self: self._name)
    avatar_path = property(lambda self: self._avatar_path)


class OpenAIConfigData(Data):
    """
    Data class for OpenAI config
    :param openai_api_key: str
    :param model: int, see OpenAIModel enum
    :param temperature: float
    :param top_p: float
    :param frequency_penalty: float
    :param presence_penalty: float
    :param max_tokens: int
    """

    def __init__(self, **kwargs):
        super().__init__('openai_config')
        self._openai_api_key = kwargs['openai_api_key']
        gpt_params = kwargs['gpt_params']
        self._gpt_params = GPTParamsData(**gpt_params)

    openai_api_key = property(lambda self: self._openai_api_key)
    model = property(lambda self: self._gpt_params.model)
    max_tokens = property(lambda self: self._gpt_params.max_tokens)
    temperature = property(lambda self: self._gpt_params.temperature)
    top_p = property(lambda self: self._gpt_params.top_p)
    frequency_penalty = property(lambda self: self._gpt_params.frequency_penalty)
    presence_penalty = property(lambda self: self._gpt_params.presence_penalty)

    def _get_data(self):
        return {
            'openai_api_key': self._openai_api_key,
            'gpt_params': self._gpt_params.data
        }

    def get_gpt_params(self):
        return self._gpt_params

    def update(self, data):
        self._openai_api_key = data.openai_api_key
        self._gpt_params.update(data.get_gpt_params())


class TranslaterConfigData(Data):
    """
    Data class for TranslaterAPI config
    :param api_type: int, see TranslaterAPIType enum
    :param app_id: str, when api_type is TranslaterAPIType.Baidu
    :param app_key: str, when api_type is TranslaterAPIType.Baidu
    :param api_key: str, when api_type is TranslaterAPIType.Google or TranslaterAPIType.DeepL or TranslaterAPIType.Youdao
    """

    def __init__(self, **kwargs):
        self._api_type = kwargs['api_type']
        self._active = kwargs['active']
        match self._api_type:
            case TranslaterAPIType.Baidu | TranslaterAPIType.Baidu.value| TranslaterAPIType.Youdao| TranslaterAPIType.Youdao.value:
                self._app_id = kwargs['app_id']
                self._app_key = kwargs['app_key']
                self._api_key = None
                self._gpt_model = None
                super().__init__('TL' + hex(hash(self._app_id + self._app_key)).split('x')[1].upper())
            case TranslaterAPIType.Google | TranslaterAPIType.DeepL  | TranslaterAPIType.Google.value | TranslaterAPIType.DeepL.value :
                self._api_key = kwargs['api_key']
                self._app_id = None
                self._app_key = None
                self._gpt_model = None
                super().__init__('TL' + hex(hash(self._api_key)).split('x')[1].upper())
            case TranslaterAPIType.OpenAI | TranslaterAPIType.OpenAI.value:
                self._api_key = None
                self._app_id = None
                self._app_key = None
                self._gpt_model = kwargs['gpt_model']
                super().__init__('TL' + hex(hash(self._gpt_model)).split('x')[1].upper())

    def _get_data(self):
        match self._api_type:
            case TranslaterAPIType.Baidu | TranslaterAPIType.Baidu.value| TranslaterAPIType.Youdao| TranslaterAPIType.Youdao.value:
                return {'api_type': self._api_type, 'app_id': self._app_id, 'app_key': self._app_key,
                        'active': self._active}
            case TranslaterAPIType.Google | TranslaterAPIType.DeepL  | TranslaterAPIType.Google.value | TranslaterAPIType.DeepL.value:
                return {'api_type': self._api_type, 'api_key': self._api_key, 'active': self._active}
            case TranslaterAPIType.OpenAI | TranslaterAPIType.OpenAI.value:
                return {'api_type': self._api_type, 'gpt_model': self._gpt_model,'active': self._active}

    def update(self, data):
        if isinstance(data, TranslaterConfigData):
            self._api_type = data.api_type
            self._active = data.active
            match self._api_type:
                case TranslaterAPIType.Baidu | TranslaterAPIType.Baidu.value| TranslaterAPIType.Youdao| TranslaterAPIType.Youdao.value:
                    self._app_id = data.app_id
                    self._app_key = data.app_key
                    self._api_key = None
                    self._gpt_model = None
                case TranslaterAPIType.Google | TranslaterAPIType.DeepL  | TranslaterAPIType.Google.value | TranslaterAPIType.DeepL.value:
                    self._api_key = data.api_key
                    self._app_id = None
                    self._app_key = None
                    self._gpt_model = None
                case TranslaterAPIType.OpenAI | TranslaterAPIType.OpenAI.value:
                    self._api_key = None
                    self._app_id = None
                    self._app_key = None
                    self._gpt_model = data.gpt_model

    api_type = property(lambda self: self._api_type)
    app_id = property(lambda self: self._app_id)
    app_key = property(lambda self: self._app_key)
    api_key = property(lambda self: self._api_key)
    active = property(lambda self: self._active)
    data = property(lambda self: self._get_data())
    gpt_model = property(lambda self: self._gpt_model)


class TranslaterConfigDataList(Data, Iterable):
    """
    Data class for TranslaterAPI config list.
    :param translater_config_list: list of TranslaterConfigData
    """

    def __init__(self, translater_config_list):
        super().__init__('translater_config')
        self._translater_config_list = []
        for translater_config in translater_config_list:
            self._translater_config_list.append(TranslaterConfigData(**translater_config))

    def __iter__(self)->Iterator[TranslaterConfigData]:
        return iter(self._translater_config_list)

    def __len__(self):
        return len(self._translater_config_list)

    def __getitem__(self, index):
        return self._translater_config_list[index]

    def __setitem__(self, index, value):
        self._translater_config_list[index] = value
        self._data = self._get_data()

    def __delitem__(self, index):
        del self._translater_config_list[index]
        self._data = self._get_data()

    def __contains__(self, item):
        return item in self._translater_config_list

    def __reversed__(self):
        return reversed(self._translater_config_list)

    def _get_data(self):
        return [translater_config.data for translater_config in self._translater_config_list]

    def has_active_translater(self):
        for translater_config in self._translater_config_list:
            if translater_config.active:
                return True
        return False

    def api_type_list(self) -> list:
        return [AIChatEnum.TranslaterAPIType.from_value(translater_config.api_type).name for translater_config in
                self._translater_config_list]

    def get_translater_config(self, api_type) -> TranslaterConfigData:
        for translater_config in self._translater_config_list:
            if translater_config.api_type == api_type:
                return translater_config
        raise ValueError('No such translater config')

    def get_active_translater_config(self) -> TranslaterConfigData | None:
        for translater_config in self._translater_config_list:
            if translater_config.active:
                return translater_config
        return None

    def update(self, data) -> None:
        if isinstance(data, TranslaterConfigDataList):
            for translater_config in data:
                self.get_translater_config(translater_config.api_type).update(translater_config)


class VITSConfigData(Data):
    """
    Data class for VITS config
    :param api_type: int, see VITSType enum
    :param api_address: str
    :param api_port: int
    """

    def __init__(self, **kwargs):
        self._api_type = kwargs['api_type']
        self._api_address = kwargs['api_address']
        self._api_port = kwargs['api_port']
        self._active = kwargs['active']
        super().__init__('VITS' + hex(hash(self._api_address + str(self._api_port))).split('x')[1].upper())

    api_type = property(lambda self: self._api_type)
    api_address = property(lambda self: self._api_address)
    api_port = property(lambda self: self._api_port)
    active = property(lambda self: self._active)

    def update(self, data) -> None:
        if isinstance(data, VITSConfigData):
            self._api_type = data.api_type
            self._api_address = data.api_address
            self._api_port = data.api_port
            self._active = data.active
        else:
            raise TypeError('data must be VITSConfigData')


class VITSConfigDataList(Data):
    """
    Data class for VITS config list
    :param vits_config_list: list of VITSConfigData
    """

    def __init__(self, vits_config_list):
        super().__init__('vits_config')
        self._vits_config_list = []
        for vits_config in vits_config_list:
            self._vits_config_list.append(VITSConfigData(**vits_config))

    def __getitem__(self, key):
        return self._vits_config_list[key]

    def _get_data(self):
        return [vits_config.data for vits_config in self._vits_config_list]

    def has_active_vits(self):
        for vits_config in self._vits_config_list:
            if vits_config.active:
                return True
        return False

    def get_active_vits_config(self) -> VITSConfigData | None:
        for vits_config in self._vits_config_list:
            if vits_config.active:
                return vits_config
        return None

    def get_vits_config(self, vits_api_type) -> VITSConfigData:
        for vits_config in self._vits_config_list:
            if vits_config.api_type == vits_api_type:
                return vits_config
        raise ValueError('No such vits config')

    def api_type_list(self):
        return [AIChatEnum.SpeakerAPIType(vits_config.api_type).name for vits_config in self._vits_config_list]

    def update(self, data) -> None:
        if isinstance(data, VITSConfigDataList):
            for vits_config in data:
                self.get_vits_config(vits_config.api_type).update(vits_config)


class ConfigData(Data):
    """
    Data class for config
    :param data_dict: dict

    Data structure:
    {
        'user_config': {
            'name': str
            'user_avatar': str
            },
        'openai_config': {
            'openai_api_key': str,
            'gpt_params': {
                'model': int, see OpenAIModel enum
                'temperature': float
                'top_p': float
                'frequency_penalty': float
                'presence_penalty': float
                'max_tokens': int
            },
        'translater_config': [
            {
                'api_type': int, see TranslaterAPIType enum
                'app_id': str, when api_type is TranslaterAPIType.Baidu
                'secret_key': str, when api_type is TranslaterAPIType.Baidu
                'api_key': str, when api_type is TranslaterAPIType.Google or TranslaterAPIType.Youdao or TranslaterAPIType.DeepL
                'active': bool
            }],
        'vits_config': [
        {
            'api_type': int, see VITSType enum
            'api_address': str
            'api_port': int
            'active': bool
        }]
    }
    """

    def __init__(self, data_dict):
        super().__init__('config')
        self._data_dict = data_dict
        self._user_config = UserConfigData(**data_dict['user_config']) if isinstance(data_dict['user_config'],
                                                                                     dict) else data_dict['user_config']
        self._openai_config = OpenAIConfigData(**data_dict['openai_config']) if isinstance(data_dict['openai_config'],
                                                                                           dict) else data_dict[
            'openai_config']
        self._translater_config = TranslaterConfigDataList(data_dict['translater_config']) if isinstance(
            data_dict['translater_config'], list) else data_dict['translater_config']
        self._vits_config = VITSConfigDataList(data_dict['vits_config']) if isinstance(data_dict['vits_config'],
                                                                                       list) else data_dict[
            'vits_config']

    def __getitem__(self, item):
        return self._data_dict[item]

    @property
    def user_config(self) -> UserConfigData:
        return self._user_config

    @property
    def openai_config(self) -> OpenAIConfigData:
        return self._openai_config

    @property
    def translater_config(self) -> TranslaterConfigDataList:
        return self._translater_config

    @property
    def vits_config(self) -> VITSConfigDataList:
        return self._vits_config

    def update(self, data) -> None:
        if isinstance(data, ConfigData):
            if data.data:
                self._data_dict = data.data
            if data.user_config:
                self._user_config.update(data.user_config)
            if data.openai_config:
                self._openai_config.update(data.openai_config)
            if data.translater_config:
                self._translater_config.update(data.translater_config)
            if data.vits_config:
                self._vits_config.update(data.vits_config)


@total_ordering
class ChatBotData(Data):
    """
    Data class for chatbot
    :param Chatbot_id: str, start with 'CB'

    data structure:
    {
        'chatbot_id': str,[optional],
        'gpt_params': {
            'id_': str,[optional]
            'model': int,
            'max_tokens': int,
            'temperature': float,
            'top_p': float,
            'frequency_penalty': float,
            'presence_penalty': float,
            }
        'character': {
            'id_': str,[optional]
            'name': str,
            'avatar_path': str,
            'personality': str,
            'description': str,
            'greeting': str,
            'prompt': str,
            }
        'histories': [{
            'id_': str,[optional],
            'memory': dict[int, str],
            'history_list': [{
                'id_': str,[optional]
                'chatbot_id': str,
                'message': str,
                'send_time': datetime.datetime,
                'is_user': bool,
                'name': str,
            }],
            }]
    """

    def __init__(self, **kwargs):
        self._gpt_params: GPTParamsData = GPTParamsData(**kwargs['gpt_params'])
        self._character: CharacterData = CharacterData(**kwargs['character'])
        self._histories: HistoryDataList = HistoryDataList(kwargs['histories'])
        if 'chatbot_id' in kwargs:
            self._id = kwargs['chatbot_id']
        else:
            self._id = 'CB' + hex(
                hash(utils.save_json_string(self._gpt_params.data) + utils.save_json_string(
                    self._character.data))).split('x')[1].upper()
        super().__init__(self._id)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __lt__(self, other):
        if len(self._histories) > len(other.histories):
            return True
        if len(self._histories) < len(other.histories):
            return False
        if len(self._histories) == 1 and not self._histories[0]:
            return False
        elif len(other.histories) == 1 and not other.histories[0]:
            return True
        else:
            return self._histories.last_modified() > other.histories.last_modified()

    def __eq__(self, other):
        return self.data == other.data

    def get_history(self, history_id):
        """
        Get history by history_id
        :param history_id: str
        :return: HistoryData
        """
        return self._histories[history_id]

    def update(self, data):
        """
        Update chatbot data
        :param data: ChatBotData or dict
        :return:
        """
        if isinstance(data, ChatBotData):
            if data.gpt_params:
                self._gpt_params.update(data.gpt_params)
            if data.character:
                self._character.update(data.character)
            if data.histories:
                self._histories.update(data.histories)
        if isinstance(data, dict):
            if 'gpt_params' in data:
                self._gpt_params.update(GPTParamsData(**data['gpt_params']))
            if 'character' in data:
                self._character.update(CharacterData(**data['character']))
            if 'histories' in data:
                self._histories.update(HistoryDataList(data['histories']))
        return self

    def append_message(self, message, history_id=None):
        """
        Append message to chatbot history
        :param history_id: the id of history to append message, if None, append to the last history
        :param message: the message to append
        :return:
        """
        if history_id is None:
            self._histories.latest().append(message)
        else:
            self._histories[history_id].append(message)

    def delete_message(self, history_id, message):
        """
        Delete message from chatbot history
        :param history_id: the id of history to delete message
        :param message: the message to delete
        :return:
        """
        self._histories[history_id].remove(message)

    def has_history(self, history_id):
        """
        Check if the chatbot has history.
        :param history_id: the id of history to check.
        :return: bool
        """
        return history_id in self._histories

    chatbot_id = property(lambda self: self._id)
    gpt_params = property(lambda self: self._gpt_params)
    character = property(lambda self: self._character)
    histories = property(lambda self: self._histories)


class ChatBotDataList(Data):
    """
    Data class for chatbot list.
    :param chatbot_list: list of ChatBotData
    """

    def __init__(self, chatbot_list):
        if chatbot_list:
            self._chatbot_list = [ChatBotData(**chatbot) for chatbot in chatbot_list]
        else:
            self._chatbot_list = []
        super().__init__('CL' + hex(hash(utils.save_json_string(chatbot_list))).split('x')[1].upper())

    def __getitem__(self, key) -> ChatBotData:
        if isinstance(key, int):
            return self._chatbot_list[key]
        elif isinstance(key, str):
            for chatbot in self._chatbot_list:
                if chatbot.chatbot_id == key:
                    return chatbot
            raise ValueError('No such chatbot')
        else:
            raise ValueError('Invalid key type')

    def __len__(self):
        return len(self._chatbot_list)

    def __iter__(self):
        return iter(self._chatbot_list)

    def _get_data(self):
        return [chatbot.data for chatbot in self._chatbot_list]

    def append(self, chatbot_data):
        self._chatbot_list.append(chatbot_data)

    def remove(self, chatbot_id):
        for chatbot in self._chatbot_list:
            if chatbot.chatbot_id == chatbot_id:
                self._chatbot_list.remove(chatbot)
                return True
        return False

    def get_chatbot_by_id(self, chatbot_id):
        for chatbot in self._chatbot_list:
            if chatbot.chatbot_id == chatbot_id:
                return chatbot
        return None

    def sort(self):
        self._chatbot_list.sort()

    def update(self, data) -> None:
        """
        Update chatbot list data
        :param data: ChatBotDataList or list
        :return:
        """
        if isinstance(data, ChatBotDataList):
            for chatbot in self._chatbot_list:
                if not chatbot.chatbot_id in data:
                    self.remove(chatbot.chatbot_id)
            for chatbot in data:
                if chatbot.chatbot_id in self:
                    self[chatbot.chatbot_id].update(chatbot)
                else:
                    self.append(chatbot)

    chatbot_list = property(lambda self: self._chatbot_list)


class GPTParamsData(Data):
    """
    Data class for GPT parameters
    :param GPTParams_id: str, start with 'GP'
    :param model: str
    :param max_tokens: int
    :param temperature: float
    :param top_p: float
    :param frequency_penalty: float
    :param presence_penalty: float
    """

    def __init__(self, **kwargs):
        self._model = kwargs['model']
        self._max_tokens = kwargs['max_tokens']
        self._temperature = kwargs['temperature']
        self._top_p = kwargs['top_p']
        self._frequency_penalty = kwargs['frequency_penalty']
        self._presence_penalty = kwargs['presence_penalty']
        # generate id
        self._id = 'GP' + hex(hash(
            self._model + str(self._max_tokens) + str(self._temperature) + str(self._top_p) + str(
                self._frequency_penalty) + str(self._presence_penalty)))[
                          2:]
        super().__init__(self._id)

    def update(self, data) -> None:
        if isinstance(data, GPTParamsData):
            self._model = data.model
            self._max_tokens = data.max_tokens
            self._temperature = data.temperature
            self._top_p = data.top_p
            self._frequency_penalty = data.frequency_penalty
            self._presence_penalty = data.presence_penalty

    model = property(lambda self: self._model)
    max_tokens = property(lambda self: self._max_tokens)
    temperature = property(lambda self: self._temperature)
    top_p = property(lambda self: self._top_p)
    frequency_penalty = property(lambda self: self._frequency_penalty)
    presence_penalty = property(lambda self: self._presence_penalty)


@total_ordering
class MessageData(Data):
    """
    Data class for message
    :param chatbot_id: str, start with 'CB'
    :param message: str
    :param send_time: str, format: '%Y-%m-%d %H:%M:%S'
    :param is_user: bool
    :param name: str
    """

    def __init__(self, **kwargs):
        self._chatbot_id = kwargs['chatbot_id']
        self._message = kwargs['message']
        self._send_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') if 'send_time' not in kwargs else \
            kwargs['send_time']
        self._is_user = kwargs['is_user']
        self._name = kwargs['name']
        self._id = 'ME' + self._chatbot_id[2:] + self._send_time.replace('-', '').replace(':', '').replace(' ',
                                                                                                           '') if 'message_id' not in kwargs else \
            kwargs['message_id']
        super().__init__(self._id)

    def __lt__(self, other):
        self_send_time = datetime.datetime.strptime(self._send_time, '%Y-%m-%d %H:%M:%S')
        other_send_time = datetime.datetime.strptime(other.send_time, '%Y-%m-%d %H:%M:%S')
        return self_send_time < other_send_time

    def __gt__(self, other):
        self_send_time = datetime.datetime.strptime(self._send_time, '%Y-%m-%d %H:%M:%S')
        other_send_time = datetime.datetime.strptime(other.send_time, '%Y-%m-%d %H:%M:%S')
        return self_send_time > other_send_time

    def __le__(self, other):
        self_send_time = datetime.datetime.strptime(self._send_time, '%Y-%m-%d %H:%M:%S')
        other_send_time = datetime.datetime.strptime(other.send_time, '%Y-%m-%d %H:%M:%S')
        return self_send_time <= other_send_time

    def __ge__(self, other):
        self_send_time = datetime.datetime.strptime(self._send_time, '%Y-%m-%d %H:%M:%S')
        other_send_time = datetime.datetime.strptime(other.send_time, '%Y-%m-%d %H:%M:%S')
        return self_send_time >= other_send_time

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if isinstance(other, MessageData):
            return self._id == other.id_
        return False

    def update(self, data) -> None:
        if isinstance(data, MessageData):
            self._chatbot_id = data.chatbot_id
            self._message = data.message
            self._send_time = data.send_time
            self._is_user = data.is_user
            self._name = data.name

    message_id = property(lambda self: self._id)
    chatbot_id = property(lambda self: self._chatbot_id)
    message = property(lambda self: self._message)
    send_time = property(lambda self: self._send_time)
    is_user = property(lambda self: self._is_user)
    name = property(lambda self: self._name)


class HistoryData(Data):
    """
    Data class for message history.
    :param memory: str, the memory of chatbot in this conversation.
    :param history_list: list of MessageData or message data dict.
    """

    def __init__(self, **kwargs):
        self._memory = '' if 'memory' not in kwargs else kwargs['memory']
        self._message_list = [MessageData(**message) if isinstance(message, dict) else message for message in
                              kwargs['history_list']]
        self._message_list.sort()
        super().__init__('HD' + hex(hash(utils.save_json_string(self.data))).split('x')[1].upper())

    def __len__(self):
        return len(self._message_list)

    def __hash__(self):
        return hash(tuple(self._message_list))

    def __eq__(self, other):
        if isinstance(other, HistoryData):
            return self._message_list == other.history_list
        return False

    def __getitem__(self, key) -> MessageData:
        """
        :param key:
        :return: message data
        """
        if isinstance(key, str):
            for message in self._message_list:
                if message.message_id == key:
                    return message
        if isinstance(key, int):
            return self._message_list[key]

    def __iter__(self):
        return iter(self._message_list)

    def sort(self):
        self._message_list.sort()

    @property
    def memory(self):
        return self._memory

    @property
    def history_list(self):
        return self._message_list

    def get_message(self, message_id):
        for message in self._message_list:
            if message.message_id == message_id:
                return message
        return None

    def oldest(self):
        return self._message_list[0]

    def latest(self):
        if len(self._message_list) == 0:
            return None
        return self._message_list[-1]

    def _get_data(self):
        return {'memory': self._memory, 'history_list': [message.data for message in self._message_list]}

    def _get_json_safe_data(self):
        return {'memory': self._memory, 'history_list': [message.json_safe_data for message in self._message_list]}

    def append(self, message):
        self._message_list.append(message)
        self._message_list.sort()

    def remove(self, message):
        self._message_list.remove(message)
        self._message_list.sort()

    def latest_n(self, n):
        return self._message_list[-n:]

    def update(self, data) -> None:
        if isinstance(data, HistoryData):
            self._memory = data.memory
            for message in self.history_list:
                if message.message_id not in data:
                    self.remove(message)
            for message in data.history_list:
                if message.message_id not in self:
                    self.append(message)
                else:
                    self[message.message_id].update(message)
        if isinstance(data, dict):
            if 'memory' in data:
                self._memory = data['memory']
            if 'history_list' in data:
                for message in self.history_list:
                    if message.message_id not in data['history_list']:
                        self.remove(message)
                for message in data['history_list']:
                    if message['message_id'] not in self:
                        self.append(MessageData(**message))
                    else:
                        self[message['message_id']].update(MessageData(**message))


class CharacterData(Data):
    """
    Data class for character
    :param chatbot_id: str, start with 'CB'
    :param name: str
    :param avatar_path: str
    :param personality: str
    :param description: str
    :param greeting: str
    :param prompt: str
    """

    def __init__(self, **kwargs):
        self._name = kwargs['name']
        self._avatar_path = kwargs['avatar_path']
        self._personality = kwargs['personality']
        self._description = kwargs['description']
        self._greeting = kwargs['greeting']
        self._prompt = kwargs['prompt']
        # generate chatbot id
        self._id = kwargs['character_id'] if 'character_id' in kwargs else 'CH' + hex(
            hash(self._name + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))).split('x')[1].upper()
        super().__init__(self._id)

    def update(self, data) -> None:
        if isinstance(data, CharacterData):
            self._name = data.name
            self._avatar_path = data.avatar_path
            self._personality = data.personality
            self._description = data.description
            self._greeting = data.greeting
            self._prompt = data.prompt

    character_id = property(lambda self: self._id)
    name = property(lambda self: self._name)
    avatar_path = property(lambda self: self._avatar_path)
    personality = property(lambda self: self._personality)
    description = property(lambda self: self._description)
    greeting = property(lambda self: self._greeting)
    prompt = property(lambda self: self._prompt)


class HistoryDataList(Data):
    """
    Data class for list of chatbot histories
    :param history_list: list of HistoryData
    """

    def __init__(self, history_list):
        super().__init__('HL' + hex(hash(utils.save_json_string(history_list))).split('x')[1].upper())
        self._history_list = [HistoryData(**history) for history in history_list]

    def __getitem__(self, key) -> HistoryData:
        if isinstance(key, int):
            return self._history_list[key]
        elif isinstance(key, str):
            for history in self._history_list:
                if history.id_ == key:
                    return history
            raise ValueError('No such history')
        else:
            raise ValueError('Invalid key type')

    def __iter__(self):
        return iter(self._history_list)

    def __len__(self):
        return len(self._history_list)

    def __contains__(self, item):
        if isinstance(item, HistoryData):
            return item in self._history_list
        elif isinstance(item, str):
            for history in self._history_list:
                if history.id_ == item:
                    return True
            return False
        else:
            return False

    def append(self, history):
        self._history_list.append(HistoryData(history))

    def latest(self) -> HistoryData:
        # compare each history's latest message time
        latest_history = None
        for history in self._history_list:
            if latest_history is None:
                latest_history = history
            elif history.latest() > latest_history.latest():
                latest_history = history
        return latest_history

    def last_modified(self) -> datetime.datetime:
        """
        :return: datetime.datetime, the last modified time of the history list
        """
        last_modified = None
        for history in self._history_list:
            if last_modified is None:
                last_modified = history.latest().send_time
            elif history.latest().send_time > last_modified:
                last_modified = history.latest().send_time
        return last_modified

    def _get_data(self):
        return [history.data for history in self._history_list]

    def remove(self, history):
        self._history_list.remove(history)

    def update(self, data) -> None:
        if isinstance(data, HistoryDataList):
            for history in self:
                if history.id_ not in data:
                    self.remove(history)
            for history in data:
                if history.id_ not in self:
                    self.append(history)
                else:
                    self[history.id_].update(history)

    history_list = property(lambda self: self._history_list)
