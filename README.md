# AIChatGUI
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10%2B-green)](https://www.python.org/)

[中文文档](README_zh.md) | [English Document](README.md)
## What's this?
This is a GUI program that can be used to chat with chatgpt, and also generate speaking audio from text.
## How to use?
clone this repo, and run `python3 app.py` in the terminal. This program is based on python3.10, so you need to install python 3.10.0 or higher version.
## What you need?
You need to install the following packages:
- `pip install openai`
- `pip install pyside6`
- `pip install requests`
- `pip install numpy`
- `pip install pandas`
- `pip install PySideSix-Frameless-Window`

To generate audio, you need to install [nene-emotion](https://huggingface.co/spaces/innnky/nene-emotion/tree/main) or [vits-simple-api](https://github.com/Artrajz/vits-simple-api) and deploy it on your server or localhost. Then, you need to change the `VITS Setting` to your server address or localhost address.

To chat with chatgpt, you need to get a chatgpt api key from [here](https://api.chatgpt.com/). Then, you need to change the `OpenAI Setting` to your api key.
## Progress
- [x] Basic UI
- [x] Chat with chatgpt
- [ ] Generate audio from text
- [ ] Translate text
- [ ] Support more languages
- [ ] Support more chatbot
## License
This program is licensed under the MIT License. See [LICENSE](LICENSE) for more details.

If you use this program, please star this repo. Thanks!

For Chinese users, you can read the Chinese version of the README [here](README_zh.md).