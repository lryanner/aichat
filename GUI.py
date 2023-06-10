import datetime

from PySide6.QtCore import QTimer

import AIChatEnum
import event_type
from AIChatEnum import AIChat, TranslaterAPIType
from AIChatUI import *
from data import ConfigData, ChatBotDataList, ChatBotData, MessageData, UserConfigData, CharacterData, HistoryData


# main window class
class AppGUI(FramelessMainWindow):
    """Main window class"""
    Resized = Signal(QSize)  # signal emitted when the window is resized
    ConfigSaved = Signal(ConfigData)  # signal emitted when the config is saved
    ChatBotUpdated = Signal(ChatBotData)  # signal emitted when the chatbot config is updated
    InitFinished = Signal()  # signal emitted when the initialization is finished

    def __init__(self, config_data: ConfigData, chatbots: ChatBotDataList):
        super().__init__()
        # apply qss style sheet
        with open('app.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self._clipboard = QApplication.clipboard()
        self._set_up_ui()
        self._chatbot_setting_dialog = ChatBotSettingDialog(config_data.openai_config.get_gpt_params(), self)
        self.ConfigSaved.connect(self._chatbot_setting_dialog.update_config)
        self._chatbot_setting_dialog.installEventFilter(self)
        self._chatbot_setting_dialog.chatbotEdited.connect(self.on_chatbot_update)
        self._global_setting_dialog = GlobalSettingDialog(config_data, self)
        self._global_setting_dialog.installEventFilter(self)
        self._global_setting_dialog.configSaved.connect(lambda :QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.Config)))
        self._current_chatbot: ChatBotData | None = None
        self._chatbot_data_list: ChatBotDataList = chatbots
        self._config = config_data
        self._load_chatbots(self._chatbot_data_list)

    # set up ui
    def _set_up_ui(self):
        """
        set up the ui
        """
        # the ui is divided into 3 parts:
        # ===================================================================#
        #          #                                                        #
        #          #                                                        #
        #          #                                                        #
        #          #                                                        #
        #          #                    message area                        #
        #          #                                                        #
        #          #                  #===========#                         #
        # left bar #                  # right bar #                         #
        #          #                  #===========#                         #
        #          #                                                        #
        #          #                                                        #
        #          #========================================================#
        #          #                    button area                         #
        #          #========================================================#
        #          #                                                        #
        #          #                    input area                          #
        #          #                                                        #
        # ==========#========================================================#

        self.setWindowTitle('ChatBot')
        self.setMinimumSize(800, 600)
        self.resize(1200, 860)
        # set the window in the center of the screen
        self.move((self.screen().size().width() - self.size().width()) / 2,
                  (self.screen().size().height() - self.size().height()) / 2)
        # set up the window widget
        self._window_widget = QWidget()
        self._window_widget.setObjectName('window_widget')
        self.setCentralWidget(self._window_widget)

        # create a QVBoxLayout for the window widget
        self._window_layout = QSettableVLayout()
        self._window_widget.setLayout(self._window_layout)
        # set up the title bar
        self._title_bar = QTitleBar(self)
        self._title_bar.GlobalSettingClicked.connect(lambda: self._global_setting_dialog.show())
        self.setTitleBar(self._title_bar)
        self._window_layout.addWidget(self._title_bar)
        # set up the main content widget
        self._main_widget = QWidget()
        self._main_widget.setObjectName('main_widget')
        self._window_layout.addWidget(self._main_widget)
        # set up the main widget's layout
        self._main_layout = QSettableHLayout()
        self._main_widget.setLayout(self._main_layout)
        # create a QVBoxLayout for the left bar
        self._left_bar = QWidget()
        self._left_bar.setObjectName('left_bar')
        self._left_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._left_bar_layout = QSettableVLayout()
        self._left_bar.setLayout(self._left_bar_layout)
        # add a chatbot button list
        self._chatbot_button_list = []

        # add a spacer to the left bar
        self._left_bar_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self._left_bar_layout.addItem(self._left_bar_spacer)
        # add a QScrollArea to the left bar
        self._left_bar_scroll_area = QNoBarScrollArea(self._left_bar)
        self._main_layout.addWidget(self._left_bar_scroll_area)
        # create a button group for the left bar buttons
        self._left_bar_button_group = QButtonGroup()
        self._left_bar_button_group.setExclusive(True)
        # create a button into the left bar scroll area
        self._add_button = QLeftBarAddButton()
        self._add_button.setFixedSize(200, 80)
        self._add_button.clicked.connect(lambda: self._chatbot_setting_dialog.show_dialogue())
        self._left_bar_button_group.addButton(self._add_button, 0)
        self._left_bar_layout.insertWidget(0, self._add_button)
        # create a QVBoxLayout for the right bar
        self._right_bar = QWidget()
        self._right_bar.setObjectName('right_bar')
        self._right_bar_layout = QVBoxLayout()
        self._right_bar_layout.setContentsMargins(0, 0, 0, 0)
        self._right_bar_layout.setSpacing(0)
        self._right_bar.setLayout(self._right_bar_layout)
        self._main_layout.addWidget(self._right_bar)

        # create a message area for the right bar
        self._message_area = MessageArea()
        self._message_area.copyMessage.connect(lambda : self._hint(AIChatEnum.HintType.Info,'Message copied.', self._right_bar, 2000))
        self._message_area.copyMessage.connect(lambda text: self._clipboard.setText(text))
        self._message_area.installEventFilter(self)
        self._right_bar_layout.addWidget(self._message_area)
        # create a QScrollArea for the message area
        self._message_area_scroll_area = QNoBarScrollArea(self._message_area)
        self._message_area_scroll_area.verticalScrollBar().rangeChanged.connect(
            lambda min_, max_: self._message_area_scroll_area.verticalScrollBar().setValue(max_))
        self.ConfigSaved.connect(self._message_area.on_config_updated)
        self.ChatBotUpdated.connect(self._message_area.on_chatbot_updated)
        self._right_bar_layout.addWidget(self._message_area_scroll_area)
        # create a button area for the right bar
        self._button_area = QWidget()
        self._button_area.setObjectName('button_area')
        self._button_area.setContentsMargins(12, 0, 0, 0)
        self._button_area.setMaximumHeight(50)
        self._button_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self._button_area_layout = QHBoxLayout()
        self._button_area.setLayout(self._button_area_layout)
        self._right_bar_layout.addWidget(self._button_area)
        # crate buttons for the button area
        # the send button
        self._send_button = QPushButton('SEND')
        self._send_button.setFixedSize(60, 30)
        self._send_button.clicked.connect(self._send_message)
        self._button_area_layout.addWidget(self._send_button)
        # the retrieve button
        self._retrieve_button = QPushButton('RETRIEVE')
        self._retrieve_button.setFixedSize(90, 30)
        self._retrieve_button.clicked.connect(self._retrieve_button_clicked)
        self._button_area_layout.addWidget(self._retrieve_button)
        # create an input area for the right bar
        self._input_area = QWidget()
        self._input_area.setObjectName('input_area')
        self._input_area_layout = QSettableVLayout()
        self._input_area.setLayout(self._input_area_layout)
        self._right_bar_layout.addWidget(self._input_area)
        # create an input box for the input area
        self._input_box = QMessagePlainTextEdit(200)
        self._input_box.SendMessage.connect(self._send_message)
        self._input_area_layout.addWidget(self._input_box)

    def open_global_config_dialog(self, first_time=False):
        """
        open the global config dialog
        :param first_time: if this is the first time to open the app, that means the global config dialog should be
        :return:
        """
        if first_time:
            self._global_setting_dialog.configSaved.connect(self.InitFinished)
            self.InitFinished.connect(lambda : self._global_setting_dialog.configSaved.disconnect(self.InitFinished))
            self._global_setting_dialog.first_show()
        else:
            self._global_setting_dialog.show()

    @Slot()
    def _send_message(self):
        """
        the slot for the send button
        :return:
        """
        if not self._current_chatbot:
            self._hint(AIChatEnum.HintType.Warning, 'Please select a chatbot first.', self._right_bar, 2000)
            return
        if self._input_box.toPlainText().rstrip('\n') == '':
            self._hint(AIChatEnum.HintType.Warning, 'Please input something', self._right_bar, 2000)
            return
        message = MessageData(
            **{
                'chatbot_id': self._current_chatbot.chatbot_id,
                'message': self._input_box.toPlainText().rstrip('\n'),
                'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_user': True,
                'name': self._config.user_config.name,
            }
        )
        history_id = self._message_area.current_history_id
        self._current_chatbot.append_message(message, history_id)
        self._message_area.show_message(self._config.user_config, message)
        QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.ChatBot))
        QApplication.sendEvent(self, SendMessageEvent(history_id, message))
        self._input_box.clear()

    def receive_message(self, history_id, message: MessageData):
        """
        receive a message from the chatbot
        :param message: the message
        :param history_id: the history id
        :return:
        """
        chatbot = self._chatbot_data_list[message.chatbot_id]
        message = chatbot.histories[history_id][-1]
        if history_id == self._message_area.current_history_id:
            self._message_area.show_message(chatbot.character, message)
        QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.ChatBot))

    def _retrieve_button_clicked(self):
        """
        the slot for the reception button
        :return:
        """
        message = MessageData(
            **{
                'chatbot_id': self._current_chatbot.chatbot_id,
                'message': self._input_box.toPlainText().rstrip('\n'),
                'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_user': False,
                'name': self._current_chatbot.character.name,
            }
        )
        self.receive_message(message)

    def resizeEvent(self, e: QResizeEvent):
        """
        the resize event for the main window
        :param e: event
        :return:
        """
        # when the window is resized, emit a signal
        self.Resized.emit(e.size())

    def eventFilter(self, obj, event):
        """
        the event filter for the main window
        :param obj: which object the event is sent to
        :param event: the event
        :return:
        """
        if event.type() == event_type.AddNewChatBotEventType:
            self._add_chatbot_button(event.data)
            self._chatbot_data_list.append(event.data)
            self.set_current_chatbot(event.data)
            QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.ChatBot))
            return True
        elif event.type() == event_type.MainWindowHintEventType:
            self._hint(event.hint_type, event.hint_message, obj)
            return True
        elif event.type() == event_type.MainWindowCloseEventType:
            self.close()
            return True
        elif event.type() == event_type.DeleteMessageEventType:
            self._chatbot_data_list[event.data.chatbot_id].delete_message(event.history_id, event.data)
            QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.ChatBot))
        return super().eventFilter(obj, event)

    def _add_chatbot_button(self, data: ChatBotData):
        """
        add a new chatbot button to the left bar
        :param data: the data of the chatbot
        :return:
        """
        name = data.character.name
        chatbot_id = data.chatbot_id
        avatar_path = data.character.avatar_path
        description = data.character.description
        chatbot_button = QChatBotButton(name, id_=chatbot_id, avatar_path=avatar_path, description=description)
        chatbot_button.editClicked.connect(self._edit_chatbot_start)
        chatbot_button.deleteClicked.connect(self._delete_chatbot)
        chatbot_button.checked.connect(self._switch_current_chatbot)
        self.ChatBotUpdated.connect(chatbot_button.on_chatbot_update)
        chatbot_button.setFixedSize(200, 80)
        self._chatbot_button_list.append(chatbot_button)
        # chatbot_button.clicked.connect(lambda : self._chatbot_button_clicked(chatbot_button))
        self._left_bar_button_group.addButton(chatbot_button, self._left_bar_button_group.buttons().__len__())
        self._left_bar_layout.insertWidget(self._left_bar_button_group.buttons().__len__() - 1, chatbot_button)

    def on_chatbot_update(self, data: ChatBotData):
        """
        the slot for the chatbot update signal
        :param data: the data of the chatbot
        :return:
        """
        self.ChatBotUpdated.emit(data)
        QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.ChatBot))

    def _switch_current_chatbot(self, id_):
        """
        the slot for the chatbot button, when a chatbot button is clicked, switch the current chatbot
        :param id_: the id of the chatbot
        :return:
        """
        # get the chatbot data
        chatbot = self._chatbot_data_list[id_]
        self.set_current_chatbot(chatbot)

    def _edit_chatbot_start(self, id_):
        """
        start to edit a chatbot
        :param id_: the id of the chatbot to be edited
        :return:
        """
        # get the chatbot data
        data = self._chatbot_data_list[id_]
        # show the chatbot setting dialog
        self._chatbot_setting_dialog.show_dialogue(data, AIChatEnum.AIChat.EditChatBotMode)

    def _delete_chatbot(self, id_):
        """
        delete a chatbot
        :param id_: the id of the chatbot to be deleted
        :return:
        """
        self._chatbot_data_list.remove(id_)
        self._message_area.clear_messages()
        QApplication.sendEvent(self, SaveDataEvent(AIChatEnum.DataType.ChatBot))

    def _load_chatbots(self, chatbots_data):
        """
        load chatbots from data
        :param chatbots_data: the data of chatbots
        :return:
        """
        if not chatbots_data.data:
            return
        for chatbot_data in chatbots_data:
            self._add_chatbot_button(chatbot_data)
        self._chatbot_button_list[0].setChecked(True)
        self.set_current_chatbot(self._chatbot_data_list[0])

    def set_current_chatbot(self, chatbot):
        """
        set the current chatbot.
        :param chatbot: the chatbot to be set as current.
        :return:
        """
        self._current_chatbot = chatbot
        self._message_area.load_messages(self._config.user_config, self._current_chatbot,
                                         self._current_chatbot.histories.latest().id_)

    @staticmethod
    def _hint(hint_type, text, obj, interval=3000):
        """
        show a hint box
        :param hint_type: the type of the hint box, see HintBoxType
        :param text: text to be displayed
        :param obj: widget to add the hint box to
        :param interval: after how many milliseconds the hint box will disappear
        :return:
        """
        hint_box = HintBox(hint_type, text, obj, interval)
        hint_box.show()

    @property
    def current_chatbot(self):
        return self._current_chatbot


class MessageArea(QWidget):
    """
    the area to display history_list
    """
    resendMessage = Signal(str) # history id
    copyMessage = Signal(str) # message text

    def __init__(self):
        super().__init__()
        self.setObjectName('message_area')
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(15, 15, 15, 15)
        self._layout.setSpacing(15)
        self._layout.setAlignment(Qt.AlignBottom)
        self.setLayout(self._layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._message_container_list: list[QMessageContainer] = []
        self._current_history_id = None

    def addWidget(self, widget):
        """
        add a widget to the message area's layout
        :param widget: the widget to be added
        :return:
        """
        self._layout.addWidget(widget)

    def load_messages(self, user_config: UserConfigData, chatbot_data: ChatBotData, history_id):
        """
        load history_list from database
        :param user_config: the user config data
        :param chatbot_data: chatbot data
        :param history_id: the id of the history or an index of the history
        :return:
        """
        # clear the message area
        self.clear_messages()
        self._current_history_id = history_id
        history = chatbot_data.histories[history_id]
        for message in history:
            if message.is_user:
                self.show_message(user_config, message)
            else:
                self.show_message(chatbot_data.character, message)

    def show_message(self, sender_data: UserConfigData | CharacterData, message_data: MessageData, resendable=True):
        """
        show a message in the message area
        :param resendable: if the message is resendable
        :param sender_data: the sender of the data. It can be a user or a character.
        :param message_data: message data
        :return:
        """
        max_width = self.parent().parent().parent().parent().parent().parent().width() - 230
        # create a message container
        message_container = QMessageContainer(sender_data, message_data, max_width)
        message_container.startPlay.connect(lambda: print('start play'))
        message_container.stopPlay.connect(lambda: print('stop play'))
        message_container.resendClicked.connect(self.resend_message)
        message_container.copyClicked.connect(lambda: self.copyMessage.emit(message_data.message))
        message_container.deleteClicked.connect(self.delete_message)

        # if not resendable, disable the resend button
        if not resendable:
            message_container.set_resendable(False)
        # add the message container to the message area
        self._message_container_list.append(message_container)
        # if the message list is more than 2, set the resend button disabled except the latest 2 history_list
        if len(self._message_container_list) > 2:
            self._message_container_list[-3].set_resendable(False)
        # add the message container to the layout to show it
        self.addWidget(message_container)
        # when the window is resized, the max width of the message container should be changed
        self.parent().parent().parent().parent().parent().parent().Resized.connect(message_container.mainWindowResized)

    def resend_message(self, message_data: MessageData):
        """
        resend a message
        :param message_data: the message to be resent
        :return:
        """
        # delete all the history_list after the message to be resent
        for message_container in self._message_container_list:
            if message_container.message_data > message_data:
                self.delete_message(message_container.message_data)
        self.resendMessage.emit(self._current_history_id)

    def delete_message(self, message_data: MessageData):
        """
        delete a message
        :param message_data: the message to be deleted
        :return:
        """
        # delete the message container
        for message_container in self._message_container_list:
            if message_container.message_data == message_data:
                self._message_container_list.remove(message_container)
                message_container.deleteLater()
                QApplication.sendEvent(self, DeleteMessageEvent(self._current_history_id, message_data))
        # set the latest 2 message container's resend button enabled
        if len(self._message_container_list) >= 2:
            self._message_container_list[-2].set_resendable(True)
            self._message_container_list[-1].set_resendable(True)
    def clear_messages(self):
        """
        clear all history_list
        :return:
        """
        for message_container in self._message_container_list:
            message_container.deleteLater()
        self._message_container_list.clear()

    def on_config_updated(self, data: ConfigData):
        """
        when the config is updated, update the message area
        :param data: config data or chatbot data
        :return:
        """
        for message_container in self._message_container_list:
            if message_container.is_user:
                message_container.set_avatar(data.user_config.avatar_path)
                message_container.set_name(data.user_config.name)

    def on_chatbot_updated(self, data: ChatBotData):
        """
        when the chatbot is updated, update the message area
        :param data: chatbot data
        :return:
        """
        if not data:
            return
        # if the chatbot is not the current chatbot, do nothing
        if data.chatbot_id != self.parent().parent().parent().parent().parent().parent().current_chatbot.chatbot_id:
            return
        for message_container in self._message_container_list:
            if not message_container.is_user:
                message_container.set_avatar(data.character.avatar_path)
                message_container.set_name(data.character.name)

    @property
    def current_history_id(self):
        return self._current_history_id


class ChatBotSettingDialog(QInWindowDialog):
    """
    This is a dialog for chatbot setting
    :param parent: the parent widget
    :param save_mode: if this dialog is used to add a new chatbot
    """
    chatbotEdited = Signal(ChatBotData)

    def __init__(self, gpt_params_config, parent=None, save_mode=AIChat.AddNewChatBotMode):
        super().__init__(parent)
        self._gpt_params_config = gpt_params_config
        self._setting_stage = AIChat.BasicSettingStage
        self._save_mode = save_mode
        self._chatbot = None

        self.setting_area_layout.setContentsMargins(0, 15, 0, 0)
        self.setting_area_layout.setAlignment(Qt.AlignTop)
        self.setting_area_layout.setSpacing(0)
        # add a setting button to the title bar
        self._setting_button = QTitleBarSettingButton(30, 30, 2.5, 3.4)
        self._setting_button.setObjectName('setting_button')
        self._setting_button.setFixedSize(30, 30)
        # in the first row, there is an avatar label
        self._avatar_label = QAvatarLabel('./resources/images/test_avatar_me.jpg', 80, editable=True)
        self._image = './resources/images/test_avatar_me.jpg'
        # if avatar clicked, open a file dialog to select a new avatar
        self._avatar_label.clicked.connect(self._update_avatar)
        self.setting_area_layout.addWidget(self._avatar_label, alignment=Qt.AlignCenter)
        # if setting button is clicked, change the setting stage and show the corresponding setting group
        self._setting_button.clicked.connect(self._change_setting_stage)
        self.title_bar_layout.insertWidget(1, self._setting_button)
        # add a basic setting group to the setting area
        self._basic_setting_group = QWidget()
        self._basic_setting_group.setObjectName('basic_setting_group')
        self._basic_setting_group.setContentsMargins(15, 15, 15, 15)
        self._basic_setting_group_layout = QSettableVLayout(content_margin=(15, 15, 15, 15), spacing=15)
        self._basic_setting_group.setLayout(self._basic_setting_group_layout)
        self.setting_area_layout.addWidget(self._basic_setting_group)

        # in the second row, there is a label and a name input box in a container
        self._name_input_box = QLabelInput('Name: ')
        self._basic_setting_group_layout.addWidget(self._name_input_box)
        # in the third row, there is a personality input box
        self._personality_input_box = QLabelInput('Personality: ')
        self._basic_setting_group_layout.addWidget(self._personality_input_box)
        # in the fourth row, there is a description input box
        self._description_input_box = QLabelInput('Description: ')
        self._basic_setting_group_layout.addWidget(self._description_input_box)
        # in the fifth row, there is a greeting input box
        self._greeting_input_box = QLabelInput('Greeting: ')
        self._basic_setting_group_layout.addWidget(self._greeting_input_box)
        # in the sixth row, there is a prompts plain text edit
        self._prompts_plain_text_edit = QPlainTextEdit()
        self._prompts_plain_text_edit.setObjectName('prompts_plain_text_edit')
        self._prompts_plain_text_edit.setPlaceholderText('Please input the prompts here, one prompt per line')
        self._basic_setting_group_layout.addWidget(self._prompts_plain_text_edit)
        # add an advanced setting group to the setting area, but hide it
        self._advanced_setting_group = QWidget()
        self._advanced_setting_group.setObjectName('advanced_setting_group')
        self._advanced_setting_group.setContentsMargins(15, 15, 15, 15)
        self._advanced_setting_group_layout = QSettableVLayout(content_margin=(15, 15, 15, 15), spacing=15)
        self._advanced_setting_group.setLayout(self._advanced_setting_group_layout)
        self.setting_area_layout.addWidget(self._advanced_setting_group)
        self._advanced_setting_group.hide()
        # in the first row, there is a label and a combobox in a container
        self._model_combobox = QLabelComboBox('Model: ', ['gpt-3.5-turbo', 'gpt-4'])
        self._advanced_setting_group_layout.addWidget(self._model_combobox)
        # in the second row, there is a label, a horizontal slider and an input box in a container
        self._temperature_input_box = QLabelSliderInput('Temperature: ', (0, 20))
        self._advanced_setting_group_layout.addWidget(self._temperature_input_box)
        # in the third row, there is a label, a horizontal slider and an input box in a container
        self._top_p_input_box = QLabelSliderInput('Top P: ', (0, 10))
        self._advanced_setting_group_layout.addWidget(self._top_p_input_box)
        # in the fourth row, there is a label, a horizontal slider and an input box in a container
        self._frequency_penalty_input_box = QLabelSliderInput('Frequency: ', (-20, 20))
        self._advanced_setting_group_layout.addWidget(self._frequency_penalty_input_box)
        # in the fifth row, there is a label, a horizontal slider and an input box in a container
        self._presence_penalty_input_box = QLabelSliderInput('Presence: ', (-20, 20))
        self._advanced_setting_group_layout.addWidget(self._presence_penalty_input_box)
        # in the sixth row, there is a label, a horizontal slider and an input box in a container
        self._max_tokens_input_box = QLabelSliderInput('Max Tokens: ', (0, 2048), False)
        self._advanced_setting_group_layout.addWidget(self._max_tokens_input_box)
        # add a button box to the setting area
        self._button_box = QWidget()
        self._button_box.setObjectName('button_box')
        self._button_box.setFixedHeight(60)
        self._button_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._button_box_layout = QSettableHLayout(content_margin=(15, 0, 15, 15), spacing=15, alignment=Qt.AlignCenter)
        self._button_box.setLayout(self._button_box_layout)
        self.setting_area_layout.addWidget(self._button_box, alignment=Qt.AlignBottom)
        # add two buttons into the button box
        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.setObjectName('cancel_button')
        self._cancel_button.setFixedSize(100, 30)
        self._cancel_button.clicked.connect(self._cancel_setting)
        self._button_box_layout.addWidget(self._cancel_button)
        self._save_button = QPushButton('Save')
        self._save_button.setObjectName('save_button')
        self._save_button.setFixedSize(100, 30)
        self._save_button.clicked.connect(self._save_setting)
        self._button_box_layout.addWidget(self._save_button)

    def show_dialogue(self, data=None, mode=AIChat.AddNewChatBotMode):
        """
        Show the dialog.
        :param data: the data of the chat
        :param mode: the mode of the dialog
        :return:
        """
        self._save_mode = mode
        if mode == AIChat.AddNewChatBotMode:
            self._clear_setting()
            self._load_gpt_params(self._gpt_params_config)
        elif mode == AIChat.EditChatBotMode:
            if isinstance(data, ChatBotData):
                self._chatbot = data
                self._load_chatbot_data(data)
        super().show()

    def _change_setting_stage(self):
        """
        Change the setting stage. When the setting stage is changed, change the setting content.
        :return:
        """
        if self._setting_stage == AIChat.BasicSettingStage:
            self._setting_stage = AIChat.AdvancedSettingStage
            self._basic_setting_group.hide()
            self._advanced_setting_group.show()
            self.set_title('')
        else:
            self._setting_stage = AIChat.BasicSettingStage
            self._basic_setting_group.show()
            self._advanced_setting_group.hide()
            self.set_title('')

    def _cancel_setting(self):
        """
        Close the dialog. When the cancel button is clicked, this function will be called.
        :return:
        """
        self.close()

    def _save_setting(self):
        """
        save the setting and close the dialog.
        :return:
        """
        if self._name_input_box.input_content == '':
            QApplication.sendEvent(self, MainWindowHintEvent(AIChatEnum.HintType.Warning,
                                                             'Please input the name of the chat bot'))
            return
        if self._prompts_plain_text_edit.toPlainText() == '':
            QApplication.sendEvent(self, MainWindowHintEvent(AIChatEnum.HintType.Warning,
                                                             'Please input the prompts of the chat bot'))
            return
        self.close()
        if self._save_mode == AIChat.AddNewChatBotMode:
            chatbot_data = ChatBotData(**self.input_data)
            QApplication.sendEvent(self, AddNewChatBotEvent(chatbot_data))
        elif self._save_mode == AIChat.EditChatBotMode:
            self._chatbot.update(self.input_data)
            self.chatbotEdited.emit(self._chatbot)
        self._chatbot = None
        self._clear_setting()

    def update_config(self, config: ConfigData):
        """
        This function will be called when the config is saved.
        :param config:
        :return:
        """
        self._gpt_params_config = config.openai_config.get_gpt_params()

    def _change_save_model(self, model):
        """
        Change the save model.
        :return:
        """
        self._save_mode = model

    def _load_gpt_params(self, gpt_params: GPTParamsData):
        """
        This function will load the gpt params from the config.
        :return:
        """
        self._model_combobox.setCurrentText(gpt_params.model)
        self._temperature_input_box.set_value(gpt_params.temperature)
        self._top_p_input_box.set_value(gpt_params.top_p)
        self._frequency_penalty_input_box.set_value(gpt_params.frequency_penalty)
        self._presence_penalty_input_box.set_value(gpt_params.presence_penalty)
        self._max_tokens_input_box.set_value(gpt_params.max_tokens)

    def _clear_setting(self):
        """
        Clear the setting.
        :return:
        """
        self._name_input_box.input_content = ''
        self._avatar_label.set_image('./resources/images/test_avatar_me.jpg')
        self._personality_input_box.input_content = ''
        self._description_input_box.input_content = ''
        self._greeting_input_box.input_content = ''
        self._prompts_plain_text_edit.setPlainText('')

    def _load_chatbot_data(self, data: ChatBotData):
        """
        This function will load the chatbot data.
        :param data: the chatbot data
        :return:
        """
        character = data.character
        self._name_input_box.input_content = character.name
        self._avatar_label.set_image(character.avatar_path)
        self._personality_input_box.input_content = character.personality
        self._description_input_box.input_content = character.description
        self._greeting_input_box.input_content = character.greeting
        self._prompts_plain_text_edit.setPlainText(character.prompt)
        self._load_gpt_params(data.gpt_params)

    @property
    def input_data(self):
        result = {
            'gpt_params': {
                'model': self._model_combobox.currentText(),
                'temperature': self._temperature_input_box.value,
                'top_p': self._top_p_input_box.value,
                'frequency_penalty': self._frequency_penalty_input_box.value,
                'presence_penalty': self._presence_penalty_input_box.value,
                'max_tokens': self._max_tokens_input_box.value
            },
            'character': {
                'name': self._name_input_box.input_content,
                'avatar_path': self._avatar_label.avatar_path,
                'personality': self._personality_input_box.input_content,
                'description': self._description_input_box.input_content,
                'greeting': self._greeting_input_box.input_content,
                'prompt': self._prompts_plain_text_edit.toPlainText()
            }
        }
        if self._save_mode == AIChat.AddNewChatBotMode:
            result['histories'] = [{'memory': {}, 'history_list':[]}]
        return result

    @property
    def avatar_label(self):
        return self._avatar_label

    @avatar_label.setter
    def avatar_label(self, avatar):
        self._image = avatar
        self._avatar_label.set_image(avatar)

    def _update_avatar(self):
        image_path = \
            QFileDialog.getOpenFileName(self, 'Open Image', './resources/images', 'Image Files (*.png *.jpg *.bmp)')[0]
        if image_path:
            self.avatar_label = image_path


class GlobalSettingDialog(QInWindowDialog):

    configSaved = Signal()# signal for config saved

    def __init__(self, data: ConfigData, parent=None):
        """
        the dialog for global setting
        :type parent: QWidget
        :type data: ConfigData
        :param data: data to initialize the dialog
        :param parent: parent widget
        """
        super().__init__(parent)
        self._data = data
        self._save_flag = True
        self.set_size(500, 800)
        self.set_title('Global Setting')
        self.setting_area_layout.setContentsMargins(30, 15, 30, 15)
        self.setting_area_layout.setSpacing(15)
        # add an avatar label to the setting area
        self._avatar_label = QAvatarLabel('./resources/images/test_avatar_me.jpg', 100, editable=True)
        self._avatar_label.clicked.connect(self._update_avatar)
        self._avatar_label.setObjectName('avatar_label')
        self.setting_area_layout.addWidget(self._avatar_label, alignment=Qt.AlignCenter)
        # add a name input box to the setting area
        self._name_input_box = QLineEdit()
        self._name_input_box.setObjectName('name_input_box')
        self._name_input_box.setPlaceholderText('Me')
        self._name_input_box.setAlignment(Qt.AlignCenter)
        self.setting_area_layout.addWidget(self._name_input_box, alignment=Qt.AlignCenter)

        # add a box group to the setting area
        self._box_group = QSelectableGroupBox(['OpenAI Setting', 'Translater Setting', 'VITS Setting'])
        self._box_group.selectionChanged.connect(self._change_setting_stage)
        self.setting_area_layout.addWidget(self._box_group)

        # add a openai setting group
        self._openai_setting_group = OpenAISettingGroup(data.openai_config)
        self.setting_area_layout.addWidget(self._openai_setting_group)
        self.set_size(500, self._openai_setting_group.sizeHint().height() + 320)

        # add a translater setting group
        self._translater_setting_group = TranslaterSettingGroup(data.translater_config)
        self._translater_setting_group.setHidden(True)
        self.setting_area_layout.addWidget(self._translater_setting_group)

        # add a vits setting group
        self._vits_setting_group = VITSSettingGroup(data.vits_config)
        self._vits_setting_group.setHidden(True)
        self.setting_area_layout.addWidget(self._vits_setting_group)

        # add a save button
        self._save_button = QPushButton('Save')
        self._save_button.setObjectName('save_button')
        self._save_button.setFixedHeight(30)
        self._save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._save_button.clicked.connect(self._save_setting)
        self.setting_area_layout.addWidget(self._save_button)
        self._setting_area_containers = [self._openai_setting_group, self._translater_setting_group,
                                         self._vits_setting_group]
        self._load_setting(data)

    def _load_setting(self, data: ConfigData):
        """
        load setting from config data.
        :param data: Config data.
        :return:
        """
        # load user config
        user_config = data.user_config
        self._name_input_box.setText(user_config.name)
        self._avatar_label.set_image(user_config.avatar_path)
        # load openai config
        openai_config = data.openai_config
        self._openai_setting_group.data = openai_config
        # load translater config
        translater_config = data.translater_config
        self._translater_setting_group.data = translater_config
        # load vits config
        vits_config = data.vits_config
        self._vits_setting_group.data = vits_config

    def _change_setting_stage(self, index):
        """
        change setting stage, called when user click the tab button in the setting area.
        :param index: index of the combo box
        :type index: int
        """
        container_height = 0
        for i, container in enumerate(self._setting_area_containers):
            if i == index:
                container.setHidden(False)
                container_height = container.sizeHint().height()
            else:
                container.setHidden(True)
        self.set_size(self._main_content.width(), 320 + container_height)

    def _save_setting(self):
        """
        save setting
        """
        openai_ready = self._openai_setting_group.is_set()
        translater_ready = self._translater_setting_group.has_active_translater()
        vits_ready = self._vits_setting_group.has_active_vits()
        if openai_ready and translater_ready and vits_ready:
            self.close()
            self._data.update(self._get_config_data())
            self._save_flag = True
            self.configSaved.emit()
        else:
            if not openai_ready:
                hint_msg = 'Please set OpenAI api key.'
            elif not translater_ready:
                hint_msg = 'Please set Translater.'
            else:
                hint_msg = 'Please set VITS api address and port.'
            QApplication.sendEvent(self, MainWindowHintEvent(AIChatEnum.HintType.Warning, hint_msg))

    def _get_config_data(self):
        """
        get config data
        :return:
        """
        return ConfigData({
            'user_config': {'name': self._name_input_box.text(), 'avatar_path': self._avatar_label.avatar_path},
            'openai_config': self._openai_setting_group.data,
            'translater_config': self._translater_setting_group.data,
            'vits_config': self._vits_setting_group.data
        })

    def _update_avatar(self):
        image_path = \
            QFileDialog.getOpenFileName(self, 'Open Image', './resources/images', 'Image Files (*.png *.jpg *.bmp)')[0]
        if image_path:
            self._avatar_label.avatar_path = image_path

    def safe_close(self):
        """
        When user click the space area, this function will be called.
        :return:
        """
        if not self._save_flag:
            openai_ready = self._openai_setting_group.is_set()
            translater_ready = self._translater_setting_group.has_active_translater()
            vits_ready = self._vits_setting_group.has_active_vits()

            if openai_ready and translater_ready and vits_ready:
                self.close()
            else:
                if not openai_ready:
                    hint_msg = 'Please set OpenAI setting.'
                elif not translater_ready:
                    hint_msg = 'Please set Translater setting.'
                else:
                    hint_msg = 'Please set VITS setting.'
                QApplication.sendEvent(self, MainWindowHintEvent(AIChatEnum.HintType.Warning, hint_msg))
        else:
            self.close()

    def area_safe_close(self):
        """
        When user click the close button, this function will be called.
        :return:
        """
        # if the save flag is true, then close the dialog
        if self._save_flag:
            self.close()
        # if the save flag is false, then close the app
        else:
            QApplication.sendEvent(self, MainWindowCloseEvent())

    def show(self) -> None:
        """
        Show the dialog.
        """
        self._load_setting(self._data)
        super().show()

    def first_show(self):
        """ first show
        """
        # need to send the hint event to the main window
        QApplication.sendEvent(self, MainWindowHintEvent(AIChatEnum.HintType.Info,
                                                         'Welcome to AI Chat! Please input your name and setup the config.',
                                                         5000))
        # connect the close button to close the app
        self._save_flag = False
        self.setHidden(False)


class QMessageContainer(QWidget):
    """ message container widget
    :param sender_data: sender data.
    :type sender_data: UserConfigData | CharacterData
    :param message_data: message data.
    :type message_data: MessageData
    :param max_width: max width of the message container.
    :type max_width: int
    """
    startPlay = Signal(MessageData)
    stopPlay = Signal(MessageData)
    copyClicked = Signal(MessageData)
    deleteClicked = Signal(MessageData)
    resendClicked = Signal(MessageData)
    mainWindowResized = Signal(QSize)

    def __init__(self, sender_data: UserConfigData | CharacterData, message_data: MessageData, max_width):
        super().__init__()
        self._message_data = message_data
        self._sender_data = sender_data
        self._is_user = message_data.is_user
        self.setFixedWidth(max_width)
        self.setObjectName('message_container')

        # create a main widget
        self._main_widget = QWidget()
        self._main_widget.setObjectName('massage_main_widget')
        self._main_widget.setFixedWidth(max_width)
        self._main_widget.move(0, 0)
        self._main_widget.setParent(self)
        self._main_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        # create a main layout
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self._main_layout.setAlignment(Qt.AlignRight if self._is_user else Qt.AlignLeft)
        self._main_widget.setLayout(self._main_layout)

        # create an overflow button container
        self._overflow_button_container = QMessageOverflowButtonsContainer(
            size=QSize(120, 26),
            move_point=QPoint(max_width - 200, 0),
            is_user=self._is_user,
            parent=self,
            startPlay=lambda: self.startPlay.emit(
                self._message_data),
            stopPlay=lambda: self.stopPlay.emit(
                self._message_data),
            copyClicked=lambda: self.copyClicked.emit(
                self._message_data),
            deleteClicked=lambda: self.deleteClicked.emit(
                self._message_data),
            resendClicked=lambda: self.resendClicked.emit(
                self._message_data))
        self._overflow_button_container.hide()

        # create a images label container
        self._image_label_container = QWidget()
        self._image_label_container.setObjectName('image_label_container')
        self._image_label_container_layout = QVBoxLayout()
        self._image_label_container_layout.setContentsMargins(2, 2, 2, 2)
        self._image_label_container_layout.setSpacing(0)
        self._image_label_container_layout.setAlignment(Qt.AlignTop)
        self._image_label_container.setLayout(self._image_label_container_layout)
        self._main_layout.addWidget(self._image_label_container)

        # create a image label
        self._image_label = QAvatarLabel(self._sender_data.avatar_path, 40)
        self._image_label_container_layout.addWidget(self._image_label)

        # create a message area
        self._message_area = QWidget()
        self._message_area.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self._message_area.setObjectName('inner_message_area')
        self._message_area_layout = QVBoxLayout()
        if self._is_user:
            self._message_area_layout.setContentsMargins(0, 0, 10, 0)
        else:
            self._message_area_layout.setContentsMargins(10, 0, 0, 0)
        self._message_area_layout.setSpacing(5)
        self._message_area_layout.setAlignment(Qt.AlignRight if self._is_user else Qt.AlignLeft)
        self._message_area.setLayout(self._message_area_layout)
        self._main_layout.insertWidget(0 if self._is_user else 1, self._message_area)
        # create a name label
        self._name_label = QLabel(self._sender_data.name)
        self._name_label.setObjectName('name_label')
        self._name_label.setAlignment(Qt.AlignRight if self._is_user else Qt.AlignLeft)
        self._message_area_layout.addWidget(self._name_label)
        # create a message label
        self._message_label = QMessageLabel(self._message_data.message, self._is_user, max_width - 108)
        self._message_area_layout.addWidget(self._message_label)
        # create a spacer item, and add it to the layout's left if is_user is True, else add it to the layout's right
        self._spacer_item = QSpacerItem(54, 0, QSizePolicy.Fixed, QSizePolicy.Preferred)
        self._main_layout.insertSpacerItem(0 if self._is_user else 2, self._spacer_item)
        self.set_max_width(max_width)
        self.mainWindowResized.connect(lambda size: self.set_max_width(size.width() - 230))

    def set_max_width(self, width):
        self._overflow_button_container.move(width - 200, 10)
        self._main_widget.setFixedWidth(width)
        self._message_label.set_max_width(width - 108)
        height = self._message_label.sizeHint().height() + 30
        self._main_widget.setFixedHeight(height)
        self.setFixedSize(width, height)

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        self._overflow_button_container.show()
        self._overflow_button_container.raise_()
        self.update()

    def leaveEvent(self, event: QEvent) -> None:
        super().leaveEvent(event)
        self._overflow_button_container.hide()
        self.update()

    def eventFilter(self, watched, event):
        if watched == self._overflow_button_container:
            if event.type() == PlaySoundEventType:
                self._play_sound()
                return True
        return super().eventFilter(watched, event)

    def set_resendable(self, resendable):
        self._overflow_button_container.set_resendable(resendable)

    @property
    def is_user(self):
        return self._is_user

    @property
    def message_data(self):
        return self._message_data

    def set_avatar(self, image):
        self._image_label.set_image(image)

    def set_name(self, name):
        self._name_label.setText(name)

    def _play_sound(self):
        pass


class HintBox(QWidget):
    def __init__(self, hint_type: AIChatEnum.HintType, hint_text, parent, interval=3000):
        super().__init__(parent)
        self._hint_type = hint_type
        self._hint_text = hint_text
        self._init_ui()
        # set the hint box to the top layer of the parent widget
        self.raise_()
        # add a timer to hide the widget after 3 seconds
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.deleteLater())
        self._timer.start(interval)

    def _init_ui(self):
        # set a fixed height
        self.setFixedHeight(40)
        self.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=10, xOffset=0, yOffset=0))
        # set width according to the hint text
        self.setFixedWidth(len(self._hint_text) * 10)
        # move the widget to the top center of the parent widget
        self.move(int((self.parent().width() - self.width()) / 2), 25)
        # add a main layout
        self._main_layout = QSettableHLayout(content_margin=(0, 0, 0, 0), spacing=0, alignment=Qt.AlignCenter)
        self.setLayout(self._main_layout)
        # add a hint text label
        self._hint_text_label = QLabel(self._hint_text)
        self._hint_text_label.setObjectName('hint_text_label')
        self._main_layout.addWidget(self._hint_text_label)
        match self._hint_type:
            case AIChatEnum.HintType.Info:
                self.setObjectName('info_hint_box')
            case AIChatEnum.HintType.Warning:
                self.setObjectName('warning_hint_box')
            case AIChatEnum.HintType.Error:
                self.setObjectName('error_hint_box')

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        match self._hint_type:
            case AIChatEnum.HintType.Info:
                painter.setBrush(QColor('#78C2C4'))
            case AIChatEnum.HintType.Warning:
                painter.setBrush(QColor('#D19826'))
            case AIChatEnum.HintType.Error:
                painter.setBrush(QColor('#F44336'))
        painter.drawRoundedRect(self.rect(), 13, 12)
