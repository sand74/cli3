from PyQt5 import QtWidgets

from models import PandasTableModel
from ui.table import Ui_TableWindow


class TableWindow(QtWidgets.QFrame, Ui_TableWindow):
    def __init__(self, dataframe):
        super().__init__()
        self.setupUi(self)
        self.tableView.setModel(PandasTableModel(dataframe))

    def setupUi(self, MainWindow):
        super().setupUi(self)
        # init menu actions
