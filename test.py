import datetime
import json
import time

import openai
import winsound

import ChatBot
import utils
from AIChatEnum import *
from data import HistoryDataList, GPTParamsData, ChatBotDataList
from speaker import Speaker

if __name__ == '__main__':
    # openai.api_key = "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"
    # speaker = Speaker(SpeakerAPIType.VitsSimpleAPI, api_address='http://127.0.0.1:7860/', emotion_mapping_path='./resources/mapping/emotion.csv')
    # text = '啊，我好想吃冰淇淋啊！'
    # emotion, nsfw = get_adv_emotion_from_gpt(text)
    # print(emotion, nsfw)
    # sound_path, sample = speaker.speak(text, id_=0, emotion=nsfw)
    # emotion_sample = speaker.last_emotion_sample()
    # print(sample)
    # # play the sound
    # winsound.PlaySound(sound_path, winsound.SND_FILENAME)
    # time.sleep(2)
    # speaker.play_emotion_sample_file(emotion_sample, r"D:\AIChat\dataset\nene_wav")
    # chatbots = ChatBotDataList([])
    # print(chatbots.data)
    print([1, 2, 3, 4, 5, 6, 7, 8, 9, 10][-20:])
