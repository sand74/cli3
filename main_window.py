from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from folders_tree import FoldersTree
from ui.main_window import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, net_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.nam = net_manager

    def show(self) -> None:
        super().show()
        self.foldersTree = FoldersTree(self, self.nam)

    def showMaximized(self) -> None:
        super().showMaximized()
        self.foldersTree = FoldersTree(self, self.nam)
