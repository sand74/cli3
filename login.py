import json

import pandas as pd
import requests
from PyQt5 import QtWidgets, QtNetwork, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QApplication

from network import NetworkException
from ui.login import Ui_dlgLogin
from globals import Globals


class LoginDialog(QtWidgets.QDialog, Ui_dlgLogin):
    """
    Форма входа в приложение
    """
    loggedSignal = pyqtSignal(int)

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.buttonLogin.clicked.connect(self.login)
        self.buttonClose.clicked.connect(QApplication.quit)
        self.loadProgressBar.setMinimum(0)
        self.loadProgressBar.setTextVisible(True)

    def login(self) -> None:
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        Globals.session.loggedInSignal.connect(self.handle_login)
        Globals.session.login(username, password)

#    @pyqtSlot()
    def handle_login(self, err, message):
        Globals.session.loggedInSignal.disconnect(self.handle_login)
        if err == QtNetwork.QNetworkReply.NoError:
            self.labelStatus.setStyleSheet("color: green")
            self.labelStatus.setText('Success')
            self.load_nci()
            self.loggedSignal.emit(0)
            self.accept()
        else:
            self.labelStatus.setStyleSheet("color: red")
            self.labelStatus.setText(message)

    def _load_nci(self, name):
        progress_message = f"Loading {name} ..."
        self.loadProgressBar.setFormat(progress_message)
        self.labelStatus.setText(progress_message)
        err, message = Globals.session.get(f'/api/nci/{name}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_message = json.loads(message)
            Globals.nci[name] = pd.DataFrame(data=json_message['rows'],
                                             columns=json_message['columns'],
                                             index=json_message['index'])
        else:
            raise NetworkException(err, message)

    def load_nci(self):
        self.loadProgressBar.setMaximum(len(Globals.nci.keys()))
        step = 0
        self.loadProgressBar.setValue(step)
        for key in Globals.nci.keys():
            self._load_nci(key)
            self.loadProgressBar.setValue(++step)
