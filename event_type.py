from PySide6.QtCore import QEvent

# event type for play sound
PlaySoundEventType = QEvent.registerEventType()
AddChatBotEventType = QEvent.registerEventType()
MainWindowHintEventType = QEvent.registerEventType()
DataLoadedEventType = QEvent.registerEventType()
MainWindowCloseEventType = QEvent.registerEventType()
SaveDataEventType = QEvent.registerEventType()
DeleteChatBotEventType = QEvent.registerEventType()
DeleteMessageEventType = QEvent.registerEventType()
SendMessageEventType = QEvent.registerEventType()
SpeakMessageEventType = QEvent.registerEventType()
ChatBotThreadStatusChangedEventType = QEvent.registerEventType()
StopChatbotThreadEventType = QEvent.registerEventType()