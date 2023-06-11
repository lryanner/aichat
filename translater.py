import deepl
import requests
from PySide6.QtCore import QObject

import utils
from AIChatEnum import TranslaterAPIType
from data import TranslaterConfigData, TranslaterConfigDataList


class TranslaterFactory(QObject):
    """
    The translater factory.
    :param translater_config_data_list: the translater config data.
    """

    def __init__(self, translater_config_data_list: TranslaterConfigDataList):
        super().__init__()
        self._translater_config_data_list = translater_config_data_list
        self._translater_list= []
        self._active_translater = None

    def setup_config(self):
        """
        Set up the config.
        :return:
        """
        self._translater_list.clear()
        for translater_config_data in self._translater_config_data_list:
            translater = Translater(translater_config_data)
            self._translater_list.append(translater)
            if translater_config_data.active:
                self._active_translater = translater

    def get_translater(self, translater_type: TranslaterAPIType):
        """
        Get the translater.
        :param translater_type:
        :return:
        """
        for translater in self._translater_list:
            if translater.type == translater_type:
                return translater
        return None

    @property
    def active_translater(self):
        """
        Get the active translater.
        :return:
        """
        return self._active_translater


class Translater(QObject):
    """
    The translater class.
    :param translater_config_data: the translater config data.
    """

    def __init__(self, translater_config_data: TranslaterConfigData):
        super().__init__()
        self._translater_config_data = translater_config_data
        self._type = TranslaterAPIType.from_value(translater_config_data.api_type)
        self._api_key = None
        self._app_id = None
        self._app_key = None
        self._api_address = None
        self._deepl_translater: deepl.Translator | None = None
        self.setup_config()

    def setup_config(self):
        """
        Set up the config.
        :return:
        """
        match self._translater_config_data.api_type:
            case TranslaterAPIType.Google.value:
                self._api_key = self._translater_config_data.api_key
                self._api_address = 'https://translation.googleapis.com/language/translate/v2'
            case TranslaterAPIType.Youdao.value:
                self._api_key = self._translater_config_data.api_key
                self._api_address = 'https://openapi.youdao.com/api'
            case TranslaterAPIType.DeepL.value:
                self._deepl_translater = deepl.Translator(self._translater_config_data.api_key)
            case TranslaterAPIType.Baidu.value:
                self._app_id = self._translater_config_data.app_id
                self._app_key = self._translater_config_data.app_key
                self._api_address = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    def translate(self, text):
        """
        Translate the text.
        :param text:
        :return:
        """
        match self._type:
            case TranslaterAPIType.Google:
                return self._translate_google(text)
            case TranslaterAPIType.Youdao:
                return self._translate_youdao(text)
            case TranslaterAPIType.DeepL:
                return self._translate_deepl(text)
            case TranslaterAPIType.Baidu:
                return self._translate_baidu(text)

    def _translate_google(self, text):
        """
        Translate the text by google.
        :param text: the text.
        :return:
        """
        params = {
            'key': self._api_key,
            'q': text,
            'target': 'ja',
            'format': 'text',
            'model': 'base'
        }
        response = requests.get(self._api_address, params=params)
        if response.status_code == 200:
            return response.json()['data']['translations'][0]['translatedText']
        else:
            return None

    def _translate_youdao(self, text):
        """
        Translate the text by youdao.
        :param text: the text.
        :return:
        """
        salt = utils.get_random_salt()
        time_stamp = utils.get_time_stamp()
        # input=q前10个字符 + q长度 + q后10个字符（当q长度大于20）或 input=q字符串（当q长度小于等于20）；
        input_ = text[:10] + str(len(text)) + text[-10:] if len(text) > 20 else text
        sign = utils.get_sha256_sign(self._app_id + input_ + str(time_stamp) + salt + self._app_key)
        params = {
            'q': text,
            'from': 'auto',
            'to': 'ja',
            'appKey': self._app_id,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': time_stamp
        }
        response = requests.get(self._api_address, params=params)
        if response.status_code == 200:
            return response.json()['translations'][0]
        else:
            return None

    def _translate_deepl(self, text):
        """
        Translate the text by deepl.
        :param text: the text.
        :return:
        """
        return self._deepl_translater.translate_text(text, target_lang='JA').text

    def _translate_baidu(self, text):
        """
        Translate the text by baidu.
        :param text: the text.
        :return:
        """
        salt = utils.get_random_salt()
        sign = utils.get_md5_sign(self._app_id + text + salt + self._app_key)
        params = {
            'q': text,
            'from': 'auto',
            'to': 'jp',
            'appid': self._app_id,
            'salt': salt,
            'sign': sign
        }
        response = requests.get(self._api_address, params=params)
        if response.status_code == 200:
            return response.json()['trans_result'][0]['dst']
        else:
            return None

    @property
    def type(self):
        return self._type
