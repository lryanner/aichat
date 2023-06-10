# AIChatGUI
[![License](https://img.shields.io/github/license/lryaner/aichat.svg)](LICENSE)


## 这是什么？
这是基于[chatgpt](https://chatgpt.com/)的聊天程序，可以用来和chatgpt聊天，也可以从文本生成语音。

## 怎么用？
克隆这个仓库，然后在终端运行`python3 app.py`。需要安装python 3.10.0或更高版本。

## 我需要什么？
你需要安装以下包：
- `pip install openai`
- `pip install pyside6`
- `pip install requests`
- `pip install numpy`
- `pip install pandas`
- `pip install PySideSix-Frameless-Window`

要生成语音，你需要安装[nene-emotion](https://huggingface.co/spaces/innnky/nene-emotion/tree/main)或[vits-simple-api](https://github.com/Artrajz/vits-simple-api)并部署到你的服务器或本地。然后，你需要把`VITS Setting`改成你的服务器地址或本地地址。

要和chatgpt聊天，你需要从[这里](https://api.chatgpt.com/)获取一个chatgpt api key。然后，你需要把`OpenAI Setting`改成你的api key。

## 进度
- [x] 基本UI
- [x] 和chatgpt聊天
- [ ] 从文本生成语音
- [ ] 翻译文本
- [ ] 支持更多语言
- [ ] 支持更多聊天机器人
- [ ] 支持更多语音合成模型

## 许可证
这个程序使用MIT许可证。更多信息请看[LICENSE](LICENSE)。