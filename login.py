from PyQt5 import QtWidgets, QtNetwork, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QApplication

from ui.login import Ui_dlgLogin

class LoginDialog(QtWidgets.QDialog, Ui_dlgLogin):
    loggedSignal = pyqtSignal(int)

    def __init__(self, net_manger):
        # Это здесь нужно для доступа к переменным, методам
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.nam = net_manger
        self.buttonLogin.clicked.connect(self.login)
        self.buttonClose.clicked.connect(QApplication.quit)

    def login(self) -> None:
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        url = f'http://127.0.0.1:8000/common/api/auth/signin?username={username}&password={password}'
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        self.nam.finished.connect(self.handleLogin)
        self.nam.get(req)

    def handleLogin(self, reply):
        self.nam.finished.disconnect(self.handleLogin)
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
            self.labelStatus.setStyleSheet("color: green")
            self.labelStatus.setText('Success')
            self.loggedSignal.emit(0)
            self.accept()
        else:
            print("Error occured: ", er)
            self.labelStatus.setStyleSheet("color: red")
            self.labelStatus.setText(reply.errorString())



