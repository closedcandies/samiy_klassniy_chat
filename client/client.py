from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QLineEdit, QPushButton, QButtonGroup
from PyQt5 import uic, QtGui
import socket
import threading


class MainWindow(QWidget):
    def __init__(self, client, chats, name, surname, profile_image):
        super().__init__()
        self.client, self.chats, self.name, self.surname, self.profile_image = client, chats, name, surname, profile_image
        self.initUi()

    def initUi(self):
        uic.loadUi('uic_models/mainWindow.ui', self)
        self.new_chat_button.clicked.connect(self.new_chat)
        self.chats_cbox.currentTextChanged.connect(self.open_chat)

    def new_chat(self):
        self.hide()
        cw = CreateChatWindow(self.client)



class CreateChatWindow(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.initUi()

    def initUi(self):
        uic.loadUi('uic_models/startChatWindow.ui', self)
        button_group = QButtonGroup(self)
        button_group.addButton(self.anonymous_rb)
        button_group.addButton(self.non_anonymous_rb)
        self.search_button.clicked.connect(self.search_profile)
        self.start_chat_button.clicked.connect(self.new_chat)

    def search_profile(self):
        response = self.client.search_new_chat(self.search_field.text)
        for profile in response:
            self.results_cbox.addItem(profile[1])

    def new_chat(self):
        if self.use_default_nick_chbox.isChecked():
            nickname = 'default'
        else:
            nickname = self.nick_field.text

        if self.anonymous_rb.isChecked():
            self.client.start_new_achat(nickname)
        else:
            companion = self.results_cbox.currentText()
            self.client.start_new_chat(companion, nickname)
        self.close()

