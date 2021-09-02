import json
import os
import pathlib

import pandas as pd
from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QCoreApplication, QSettings
from PyQt5.QtWidgets import QApplication

from cli3.app import Cli3App
from cli3.network import NetworkException
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
        self._read_settings()
        if self.usernameLineEdit.text() != '':
            self.focusNextChild()
            self.focusNextChild()
        path = pathlib.Path(__file__).parent.parent.resolve()
        self.labelStatus.setText(f'{str(Cli3App.get_app_path())}:{Cli3App.instance().session.get_base_url()}')


    def _write_settings(self) -> None:
        """
        Write main windows  Settings
        :return:
        """
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.beginGroup(self.__class__.__name__)
        settings.setValue("last_login", self.usernameLineEdit.text())
        settings.endGroup()

    def _read_settings(self) -> None:
        """
        Read main windows  Settings
        :return:
        """
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.beginGroup(self.__class__.__name__)
        if settings.contains("last_login"):
            self.usernameLineEdit.setText(settings.value("last_login"))
        settings.endGroup()

    def login(self) -> None:
        """
        Send login request
        :return:
        """
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        Cli3App.instance().session.loggedInSignal.connect(self._handle_login)
        Cli3App.instance().session.login(username, password)

    @pyqtSlot(int, str)
    def _handle_login(self, err, message):
        Cli3App.instance().session.loggedInSignal.disconnect(self._handle_login)
        if err == QtNetwork.QNetworkReply.NoError:
            self._write_settings()
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
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.NCI_API}/{name}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_message = json.loads(message)
            Cli3App.instance().nci[name] = pd.DataFrame(data=json_message['rows'],
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
        self.loadProgressBar.setMaximum(len(Cli3App.instance().nci.keys()))
        step = 0
        self.loadProgressBar.setValue(step)
        err, message = Cli3App.instance().session.get(Cli3App.instance().session.NCI_API)
        ncis = json.loads(message)
        for nci in ncis:
            progress_message = f"Loading {nci['name']} ..."
            self.loadProgressBar.setFormat(progress_message)
            self.labelStatus.setText(progress_message)
            path = str(str(Cli3App.get_app_path())) + '/data'
            os.makedirs(path, exist_ok=True)
            data_file = f"{path}/{nci['name']}.csv"
            if os.path.exists(data_file):
                Cli3App.instance().nci[nci['name']] = pd.read_csv(data_file, dtype=str)
            else:
                self._load_nci_table(nci['name'])
                Cli3App.instance().nci[nci['name']].to_csv(data_file, index=False)
            # Prevent convert index to int
            Cli3App.instance()
            Cli3App.instance().nci[nci['name']].set_index(Cli3App.instance().nci[nci['name']].columns[0], drop=False,
                                                          inplace=True)
            self.loadProgressBar.setValue(++step)

    def _load_styles(self) -> None:
        """
        Loade styles from server
        :return:
        """
        progress_message = f"Loading styles ..."
        self.loadProgressBar.setFormat(progress_message)
        self.labelStatus.setText(progress_message)
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.STYLE_API}')
        if err == QtNetwork.QNetworkReply.NoError:
            Cli3App.instance().styles = json.loads(message)
        else:
            raise NetworkException(err, message)
