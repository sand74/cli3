from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, QAbstractTableModel, Qt

from ui.table import Ui_TableWindow


class PandasTableModel(QAbstractTableModel):
    """
    Модель таблицы для представления датафрейма pandas
    """
    ROW_INDEX_ROLE = Qt.UserRole + 1
    ROW_AS_STRING_ROLE = Qt.UserRole + 2

    def __init__(self, dataframe):
        super().__init__()
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        return len(self._dataframe.values)

    def columnCount(self, parent=None):
        return self._dataframe.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._dataframe.iloc[index.row(), index.column()]))
            elif role == Qt.EditRole:
                return QtCore.QVariant(str(
                    self._dataframe.iloc[index.row(), index.column()]))
            elif role == self.ROW_INDEX_ROLE:
                return self._dataframe.index[index.row()]
            elif role == self.ROW_AS_STRING_ROLE:
                return '|'.join(self._dataframe.iloc[index.row(), :])
        return QtCore.QVariant()

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            return QtCore.QVariant(self._dataframe.columns[column])


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
