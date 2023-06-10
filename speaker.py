import os
import random
import re
import string
import time

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

import utils
from AIChatEnum import SpeakerAPIType
from gradio_client import Client

from data import VITSConfigData, VITSConfigDataList
from exceptions import SpeakerException


class Speaker:
    def __init__(self, vits_config: VITSConfigDataList,
                 emotion_mapping_path='./resources/mapping/emotion_no_duplicated.csv'):
        """
        The speaker class.
        :param vits_config: The vits config.
        :param emotion_mapping_path: [optional] The path of the nene emotion mapping.
        """
        self._config = vits_config
        self._emotion_mapping_path = emotion_mapping_path
        self._speaker = None
        self.setup_config()


    def setup_config(self):
        """
        Set up the config.
        :return:
        """
        active_config = self._config.get_active_vits_config()
        emotion_mapping_path = self._emotion_mapping_path

        if active_config.api_type == SpeakerAPIType.NeneEmotion:
            self._speaker = SpeakerNeneEmotion(
                self.join_address(active_config.api_address, active_config.api_port), emotion_mapping_path)
        elif active_config.api_type == SpeakerAPIType.VitsSimpleAPI:
            self._speaker = SpeakerVitsSimpleApi(
                self.join_address(active_config.api_address, active_config.api_port), emotion_mapping_path)

    @staticmethod
    def join_address(api_address, api_port):
        """
        Join the api address and port.
        :param api_address: The api address.
        :param api_port: The api port.
        :return: The joined api address and port.
        """
        return 'http://' + api_address + ':' + str(api_port)

    def speak(self, text, **kwargs):
        """
        Speak the text.
        :param text:
        :param kwargs:
        :return:
        """
        return self._speaker(text, **kwargs)

    def play_emotion_sample_file(self, emotion_id, root_path):
        """
        Play the emotion sample file.
        :param emotion_id: the emotion id
        :param root_path: the root path of the emotion sample file
        :return: none
        """
        self._speaker.play_emotion_sample_file(emotion_id, root_path)

    def last_emotion_sample(self):
        """
        Get the emotion sample.
        :return: the emotion sample
        """
        return self._speaker.last_emotion_sample


class SpeakerW2V2:
    def __init__(self, api_address, emotion_mapping_path):
        """
        The speaker class for nene emotion. This class is callable.

        :param api_address: Api address of nene emotion server.
        :param emotion_model_path: The path of the nene emotion mapping.
        """
        self._last_emotion_sample = None
        self._out_put_path = os.path.join(os.path.dirname(__file__), 'download\\sounds')
        self._api_address = api_address
        self._emotion_mapping = utils.load_csv(emotion_mapping_path)
        self._all_emotions = [[emotion['arousal'], emotion['dominance'], emotion['valence']] for emotion in
                              self._emotion_mapping]
        self._nsfw_emotions = [[emotion['arousal'], emotion['dominance'], emotion['valence']] for emotion in
                               self._emotion_mapping if emotion['nsfw'] == 1]
        self._sfw_emotions = [[emotion['arousal'], emotion['dominance'], emotion['valence']] for emotion in
                              self._emotion_mapping if emotion['nsfw'] == 0]

    @property
    def last_emotion_sample(self):
        return self._last_emotion_sample

    def _get_emotion_sample(self, emotion, nsfw=None):
        """
        Get the emotion sample.
        :param emotion: the emotion. Must be a list of float.
        :return:
        """
        if nsfw is None:
            self._last_emotion_sample = \
            self._emotion_mapping[utils.get_similar_array_index(emotion, self._all_emotions)]['emotion']
        elif nsfw:
            self._last_emotion_sample = self._emotion_mapping[
                utils.get_similar_array_index(utils.get_similar_array(emotion, self._nsfw_emotions),
                                              self._all_emotions)]['emotion']
        else:
            self._last_emotion_sample = self._emotion_mapping[
                utils.get_similar_array_index(utils.get_similar_array(emotion, self._sfw_emotions),
                                              self._all_emotions)]['emotion']
        return self._last_emotion_sample

    def play_emotion_sample_file(self, emotion, root):
        """
        Play the emotion sample file.
        :param emotion: the emotion. Must be a list of float.
        :param root: the root directory of the emotion sample.
        :return:
        """
        for data in self._emotion_mapping:
            if data['emotion'] == emotion:
                file_path = os.path.join(root, data['file'] + '.wav')
                utils.play_sound(file_path)
                return


class SpeakerNeneEmotion(SpeakerW2V2):
    def __init__(self, api_address, emotion_mapping_path):
        """
        The speaker class for nene emotion. This class is callable.

        :param api_address: Api address of nene emotion server.
        :param emotion_model_path: The path of the nene emotion mapping.
        """
        self._client = Client(api_address)
        super().__init__(api_address, emotion_mapping_path)

    def __call__(self, text, **kwargs):
        """
        Speak the text.
        :param text: the text to speak.
        :param kwargs: the arguments for the speaker.
        :param nsfw: [required] whether the text is nsfw. Must be a boolean.
        :param emotion: [required] the emotion of the speaker. Must be a list of string.
        :return: file_path, emotion_sample
        """
        emotion = kwargs['emotion']
        result = self._client.predict(text, emotion, fn_index=2)
        message = result[0]
        if message != 'Success':
            raise SpeakerException(message)
        out_file_path = result[1]
        # copy the file to the current directory
        file_name = out_file_path.split('/')[-1]
        copy_file_path = self._out_put_path + file_name
        if not os.path.exists(copy_file_path):
            os.makedirs(os.path.dirname(copy_file_path), exist_ok=True)
        utils.copy_file(out_file_path, copy_file_path)
        return copy_file_path, emotion


class SpeakerVitsSimpleApi(SpeakerW2V2):
    def __init__(self, api_address, emotion_mapping_path):
        """
        The speaker class for vits simple api. This class is callable.
        """
        super().__init__(api_address, emotion_mapping_path)

    def __call__(self, text, id_=0, format_="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max_=50, **kwargs):
        """
        Speak the text.
        :param text: the text to speak.
        :param kwargs: the arguments for the speaker.
        :param nsfw: [required] whether the text is nsfw. Must be a boolean.
        :param emotion: [required] the emotion of the speaker. Must be a list of string.
        :return: file_path, emotion_sample
        """
        if 'nsfw' in kwargs:
            emotion = self._get_emotion_sample(kwargs['emotion'], kwargs['nsfw'])
        else:
            emotion = self._get_emotion_sample(kwargs['emotion'])
        fields = {
            "text": text,
            "id": str(id_),
            "format": format_,
            "lang": lang,
            "length": str(length),
            "noise": str(noise),
            "noisew": str(noisew),
            "max": str(max_),
            "emotion": str(emotion)
        }
        boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

        m = MultipartEncoder(fields=fields, boundary=boundary)
        headers = {"Content-Type": m.content_type}
        url = f"{self._api_address}/voice/w2v2-vits"
        try:
            res = requests.post(url=url, data=m, headers=headers)
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            utils.warn(f"[Vits Simple API]ConnectionError, retrying...")
            return self(text, id_, format_, lang, length, noise, noisew, max_, **kwargs)
        if res.status_code != 200:
            raise SpeakerException(f"Error: {res.status_code}, {res.text}")
        file_name = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
        path = f"{self._out_put_path}\\{file_name}"
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(res.content)
        return path, emotion
