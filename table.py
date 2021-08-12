from PyQt5 import QtWidgets
from PyQt5.QtCore import QSortFilterProxyModel

from models import PandasTableModel
from ui.table import Ui_TableWindow


class TableWindow(QtWidgets.QFrame, Ui_TableWindow):
    """
    Класс окна одной таблицы
    """
    def __init__(self, dataframe):
        super().__init__()
        self.setupUi(self)
        filter_model = QSortFilterProxyModel(self)
        filter_model.setFilterKeyColumn(-1)
        filter_model.setSourceModel(PandasTableModel(dataframe))
        self.tableView.setModel(filter_model)

    def setupUi(self, MainWindow):
        super().setupUi(self)
        # init menu actions
