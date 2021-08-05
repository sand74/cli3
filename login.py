from PyQt5 import QtWidgets, QtNetwork, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QApplication

from ui.login import Ui_dlgLogin
from globals import Globals

class LoginDialog(QtWidgets.QDialog, Ui_dlgLogin):
    loggedSignal = pyqtSignal(int)

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.buttonLogin.clicked.connect(self.login)
        self.buttonClose.clicked.connect(QApplication.quit)

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
            self.loggedSignal.emit(0)
            self.accept()
        else:
            print("Error occured: ", err)
            self.labelStatus.setStyleSheet("color: red")
            self.labelStatus.setText(message)



