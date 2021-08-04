from PyQt5 import QtNetwork
from PyQt5.QtWidgets import *
import sys
from login import LoginDialog
from main_window import MainWindow


def main():
    net_manager = QtNetwork.QNetworkAccessManager()
    app = QApplication(sys.argv)
    login = LoginDialog(net_manager)
    login.show()
    mainWindow = MainWindow(net_manager)
    login.loggedSignal.connect(mainWindow.showMaximized)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()