from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, Qt, pyqtSignal, QModelIndex, pyqtSlot
from PyQt5.QtWidgets import QTableView, QWidget, QTableWidget, QHeaderView, QCompleter


class NciTableModel(QAbstractTableModel):
    """
    Модель таблицы для представления датафрейма nci
    """
    def __init__(self, dataframe, max_rows=None):
        super().__init__()
        self._source = dataframe
        if max_rows is None:
            self.max_rows = len(self._source.values)
        else:
            self.max_rows = max_rows
        self._dataframe = dataframe.iloc[:self.max_rows, :]

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
        return QtCore.QVariant()

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            return QtCore.QVariant(self._dataframe.columns[column])

    def setFilter(self, value: str):
        columns = self._dataframe.columns
        self._dataframe = self._source[
                              self._source[columns[0]].str.contains(str(value)) | self._source[columns[1]].str.contains(
                                  str(value))].iloc[:self.max_rows, :]


class NciCompleter(QCompleter):
    """
    Autocompleter for nci fields
    TODO Не работает
    """
    activatedSignal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterMode(Qt.MatchContains)
        self.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.activated[QtCore.QModelIndex].connect(self.item_activated)
        self.setCompletionMode(QCompleter.PopupCompletion)

    @pyqtSlot(QtCore.QModelIndex)
    def item_activated(self, index: QModelIndex):
        data = index.model().data(index, self.completionRole())
        index_list = self.model().match(self.model().index(0, self.completionColumn()),
                                        self.completionRole(), data,
                                        1, Qt.MatchExactly)
        if len(index_list) > 0:
            self.activatedSignal.emit(index_list[0])

    def pathFromIndex(self, index: QtCore.QModelIndex) -> str:
        new_idx = self.model().index(index.row(), self.completionColumn())
        data = self.model().data(new_idx)
        if isinstance(data, str):
            return data
        else:
            return data.field_value()


class NciTableView(QTableView):
    """
    TableView for nci tables
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().hide()
