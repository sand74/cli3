from PyQt5 import QtNetwork
from PyQt5.QtWidgets import *
import sys
from login import LoginDialog
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Cli3')
    app.setOrganizationName('ICS')
    app.setApplicationVersion('1.1.1')
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()