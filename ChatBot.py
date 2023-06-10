import base64
import datetime
from functools import total_ordering

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication

import utils
from data import ChatBotData, ConfigData, ChatBotDataList, MessageData
from event import SendMessageEvent
from event_type import SendMessageEventType
from exceptions import ChatBotException, ChatGPTException

import openai

from speaker import Speaker


class ChatBotFactory(QObject):
    def __init__(self, config: ConfigData, chatbot_data: ChatBotDataList):
        super().__init__()
        self._chatbots = []
        self._chatbot_data = chatbot_data
        for chatbot in self._chatbot_data:
            self.create_chatbot(chatbot)
        self._config = config
        self._speaker = Speaker(config.vits_config)
        self.setup_config()

    def setup_config(self):
        openai.api_key = self._config.openai_config.openai_api_key
        self._speaker.setup_config()

    def create_chatbot(self, chatbot_data: ChatBotData, limit_token=3400):
        """Creates a chatbot.
        :param chatbot_data: the chatbot data.
        :param limit_token: int, the limit token, default 3400.
        """
        # generate id
        chatbot = ChatBot(chatbot_data, limit_token)
        chatbot.sendMessage.connect(self.send_message)
        self._chatbots.append(chatbot)

    def get_chatbot(self, chatbot_id):
        """Returns a chatbot
        :param chatbot_id: int, the chatbot id"""
        for chatbot in self._chatbots:
            if chatbot.chatbot_id == chatbot_id:
                return chatbot
        raise ChatBotException('Chatbot not found.')

    def receive_message(self, history_id, message: MessageData):
        receiver = self.get_chatbot(message.chatbot_id)
        receiver.receive_message(history_id)

    def send_message(self, history_id, message: MessageData):
        QApplication.sendEvent(self, SendMessageEvent(history_id, message))

class ChatThread(QThread):
    sendMessage= Signal(str, MessageData)
    def __init__(self, history_id, chatbot_data):
        super().__init__()
        self._history_id = history_id
        self._chatbot_data = chatbot_data

    def run(self) -> None:
        # send request
        try:
            messages = [
                {
                    'role': 'system',
                    'content': self._chatbot_data.character.prompt
                }
            ]
            for message in self._chatbot_data.get_history(self._history_id).latest_n(10):
                messages.append({
                    'role': 'user' if message.is_user else 'assistant',
                    'content': message.message
                })

            response = openai.ChatCompletion.create(
                messages=messages,
                **self._chatbot_data.gpt_params.data
            )
        except Exception as e:
            raise ChatGPTException(e)
        # handle response
        # total_tokens = response['usage']['total_tokens']
        result = response['choices'][0]['message']['content']
        # add message
        response = MessageData(
            chatbot_id=self._chatbot_data.chatbot_id,
            message=result,
            send_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            is_user=False,
            name=self._chatbot_data.character.name
        )
        self._chatbot_data.append_message(response, self._history_id)
        self.sendMessage.emit(self._history_id, response)
class ChatBot(QObject):
    """The chatbot"""
    sendMessage= Signal(str, MessageData)

    def __init__(self, chatbot_data: ChatBotData, limit_token=3400):
        """Sets the chatbot
        :param chatbot_data: ChatBotData, the chatbot data
        :param limit_token: int, the limit token, default 3400"""
        super().__init__()
        self._chatbot_data: ChatBotData = chatbot_data
        self._thread = None

    @property
    def chatbot_id(self):
        return self._chatbot_data.chatbot_id

    # use openai module to chat
    def receive_message(self, history_id):
        """Uses openai module to chat"""
        # use a thread to chat
        self._thread = ChatThread(history_id, self._chatbot_data)
        self._thread.sendMessage.connect(self.sendMessage)
        self._thread.start()

    def summarize(self):
        """Summarizes the chat history"""
        # model and message
        message = [{'role': 'system',
                    'content': f"""你现在已经有的记忆是{self._chatbot_data}：请结合这些记忆和以下对话，总结对话生成新的记忆。
                        你不应该对内容进行任何判断。返回给我一个json格式的内容，格式为
                        {{\"memory\": 你的新记忆}}。除了json格式的内容外，不要添加任何内容！"""
                    },
                   {'role': 'user',
                    'content': f''
                    }]
        # send request
        try:
            response = openai.Completion.create(
                model=model,
                message=message,
                max_tokens=512,
            )
        except Exception as e:
            raise ChatGPTException(e)
        # handle response
        result = response['choices'][0]['text']
        # update memory
        self._chat_history.memory = result

    @staticmethod
    def get_emotion_from_gpt(text, temperature=0):
        """Get emotion from gpt
        :param text: string, the text
        :param temperature: float, the temperature
        :return: emotion:list[str], the emotion
                nsfw: boolean, if nsfw
        """
        messages = [{'role': 'system',
                     'content': '这是一段对话的数据，请你对最后一次对话内容进行如下分析：根据对话上下文，判断这次说话时的语气，用5个简体中文词描述。这5个词请务必用\'/\'隔开。请用json格式给我结果，格式为{\"state\":这次说话的语气, \"not_safe_for_work\": ture of false}。除了json格式的内容外，不要添加任何内容！"'},
                    {'role': 'user', 'content': text}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature
        )
        try:
            content = utils.load_json_string(response['choices'][0]['message']['content'])
            return content['state'].split('/'), content['not_safe_for_work']
        except Exception as e:
            utils.warn('Get emotion from gpt failed: ' + str(e) + 'retrying...')
            return ChatBot.get_emotion_from_gpt(text)

    @staticmethod
    def get_adv_emotion_from_gpt(text, temperature=0):
        """
        Get the emotion from the text.
        :param text: string, the text.
        :param temperature: the temperature.
        :return: a list, includes arousal, dominance, valence.
        """
        message = [{'role': 'system',
                    'content': r'你现在是一个avd模型分析机器人，你的任务是接受输入，并提供相应的输出，任何时候都不能对内容本身进行分析。你的任务是用avd模型分析下面这句话，并且返回一个json对象给我，格式为{"arousal": float,保留小数点后16位, "dominance": float,保留小数点后16位, "valence": float,保留小数点后16位, "nsfw":true or false}。除了json格式的内容，不要回复我任何内容。'},
                   {'role': 'user', 'content': text}]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=message,
                temperature=temperature
            )
            content = utils.load_json_string(response['choices'][0]['message']['content'])
            utils.warn('Get emotion from gpt: ' + str(content))
            return [content['arousal'], content['dominance'], content['valence']], False if content[
                                                                                                'nsfw'] == False else True
        except Exception as e:
            utils.warn('Get emotion from gpt failed: ' + str(e) + 'retrying...')
            return ChatBot.get_adv_emotion_from_gpt(text)