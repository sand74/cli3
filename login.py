import json
import os

import pandas as pd
from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

from globals import Globals
from network import NetworkException
from ui.login import Ui_dlgLogin


class LoginDialog(QtWidgets.QDialog, Ui_dlgLogin):
    """
    Форма входа в приложение
    """
    loggedSignal = pyqtSignal(int)

    def __init__(self):
        """
        Constructor for login form
        """
        super().__init__()
        self.setupUi(self)
        self.buttonLogin.clicked.connect(self.login)
        self.buttonClose.clicked.connect(QApplication.quit)
        self.loadProgressBar.setMinimum(0)
        self.loadProgressBar.setTextVisible(True)

    def login(self) -> None:
        """
        Send login request
        :return:
        """
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        Globals.session.loggedInSignal.connect(self._handle_login)
        Globals.session.login(username, password)

    @pyqtSlot(int, str)
    def _handle_login(self, err, message):
        Globals.session.loggedInSignal.disconnect(self._handle_login)
        if err == QtNetwork.QNetworkReply.NoError:
            self.labelStatus.setStyleSheet("color: green")
            self.labelStatus.setText('Success')
            self._load_nci()
            self._load_styles()
            self.loggedSignal.emit(0)
            self.accept()
        else:
            self.labelStatus.setStyleSheet("color: red")
            self.labelStatus.setText(message)

    def _load_nci_table(self, name) -> None:
        """
        Load nci table into Globals nci dictionary
        :param name: name associated with table
        :return:
        """
        err, message = Globals.session.get(f'{Globals.session.NCI_API}/{name}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_message = json.loads(message)
            Globals.nci[name] = pd.DataFrame(data=json_message['rows'],
                                             columns=[column.upper() for column in json_message['columns']])
        else:
            raise NetworkException(err, message)

    def _load_nci(self) -> None:
        """
        Load all nci tables into Globals nci dictionary
        TODO добавить проверку изменились ли НСИ из метки версии
        from file if exists, else from server
        :return:
        """
        self.loadProgressBar.setMaximum(len(Globals.nci.keys()))
        step = 0
        self.loadProgressBar.setValue(step)
        for key in Globals.nci.keys():
            progress_message = f"Loading {key} ..."
            self.loadProgressBar.setFormat(progress_message)
            self.labelStatus.setText(progress_message)
            data_file = f'data/{key}.csv'
            if os.path.exists(data_file):
                Globals.nci[key] = pd.read_csv(data_file, dtype=str)
            else:
                self._load_nci_table(key)
                Globals.nci[key].to_csv(data_file, index=False)
            # Prevent convert index to int
            Globals.nci[key].set_index(Globals.nci[key].columns[0], drop=False, inplace=True)
            self.loadProgressBar.setValue(++step)

    def _load_styles(self) -> None:
        """
        Loade styles from server
        :return:
        """
        progress_message = f"Loading styles ..."
        self.loadProgressBar.setFormat(progress_message)
        self.labelStatus.setText(progress_message)
        err, message = Globals.session.get(f'{Globals.session.STYLE_API}')
        if err == QtNetwork.QNetworkReply.NoError:
            Globals.styles = json.loads(message)
        else:
            raise NetworkException(err, message)
