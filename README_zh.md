# AIChatGUI
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-green)](https://www.python.org/)

[中文文档](README_zh.md) | [English Document](README.md)
## 截图
![screenshot](./screenshot.png)
## 这是什么？
这是基于[chatgpt](https://chatgpt.com/)的聊天程序，可以用来和chatgpt聊天，也可以从文本生成语音。

## 怎么用？
克隆这个仓库，然后在终端运行`python3 app.py`。需要安装python 3.10.0或更高版本。

打开程序后，你需要进行初始化设置。设置完成后点击`Save`保存设置。然后点击`+`添加一个新的聊天机器人开始聊天。

## 我需要什么？
你需要安装以下包：
- `pip install openai`
- `pip install pyside6`
- `pip install requests`
- `pip install numpy`
- `pip install pandas`
- `pip install PySideSix-Frameless-Window`

或者，你可以运行`pip install -r requirements.txt`。

要生成语音，你需要安装[nene-emotion](https://huggingface.co/spaces/innnky/nene-emotion/tree/main)或[vits-simple-api](https://github.com/Artrajz/vits-simple-api)并部署到你的服务器或本地。然后，你需要把`VITS Setting`改成你的服务器地址或本地地址。

要和chatgpt聊天，你需要从[这里](https://api.chatgpt.com/)获取一个chatgpt api key。然后，你需要把`OpenAI Setting`改成你的api key。

此外，你还需要一个翻译API。目前支持[百度](https://api.fanyi.baidu.com/)、[谷歌](https://cloud.google.com/translate/docs/reference/rest/)、[有道](https://ai.youdao.com/product-fanyi-text.s)、[DeepL](https://www.deepl.com/pro-api)、[ChatGPT](https://api.chatgpt.com/)。你需要把`Translater Setting`改成你的翻译API。
## 特性
- 和chatgpt聊天
- 生成带情感的语音
- 自动情感选择

采用emotion-vits模型生成语音，可以生成带有情感的语音，已经将绫地宁宁的语音进行chatgpt预标记。采用的情感参考是nene-emotion的情感参考id。可以实现自动情感选择，虽然效果不是很好，但是可以用来玩玩。

## 进度
- [x] 基本UI
- [x] 和chatgpt聊天
- [x] 从文本生成语音，仅测试了vits-simple-api
- [x] 翻译文本，仅测试了DeepL API
- [ ] 导出聊天记录和语音，同一个chatbot支持多聊天记录
- [ ] 完善UI
- [ ] 支持更多语言
- [ ] 支持更多聊天机器人
- [ ] 支持更多语音合成模型
- [ ] 支持更多翻译API
- [ ] 考虑加入Stable-Diffusion API生成图片
## 为什么要做这个？
单纯的想做一个聊天程序，然后就做了这个。

## 许可证
这个程序使用MIT许可证。更多信息请看[LICENSE](LICENSE)。