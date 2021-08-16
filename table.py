import json

import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtNetwork
from PyQt5.QtCore import QSortFilterProxyModel, QAbstractTableModel, Qt, QDateTime, QDate, QModelIndex, \
    QAbstractItemModel, QItemSelection, QVariant, QItemSelectionModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView
import qtawesome as qta

from globals import Globals
from models import Query
from network import Request
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


class Cli3TableModel(QAbstractTableModel):
    """
    Модель таблицы для представления датафрейма pandas
    """

    def __init__(self, data, columns):
        super().__init__()
        self._filters = {}
        self._columns = columns
        self._source = pd.DataFrame(data, columns=[column['name'] for column in columns], dtype=str)
        # Change columns datatypes
        for name, type in [(column['name'], column.get('type', 'string').lower()) for column in columns]:
            if type == 'number':
                self._source[name] = self._source[name].astype('float')
            elif type in ['date', 'datetime', 'time']:
                self._source[name] = pd.to_datetime(self._source[name])
            elif type == 'bool':
                self._source[name] = self._source[name].apply(lambda x: str(x).lower() == 'true').astype('bool')
        self._visable_columns = [column['name'] for column in columns]
        self._dataframe = self._source.loc[:, self._visable_columns]

    def get_source_index(self, index: QModelIndex):
        if index.row() >= 0 and index.row() < len(self._dataframe.values):
            if index.column() >= 0 and index.column() < len(self._dataframe.columns):
                return self._dataframe.index[index.row()], self._dataframe.columns[index.column()]
        return None, None

    @property
    def source(self):
        return self._source

    # Filters section
    def get_filters(self):
        return self._filters

    def hasFilter(self, column):
        column_name = self._dataframe.columns[column]
        return column_name in self._filters.keys()

    def setFilter(self, column, value):
        if not self.hasFilter(column):
            column_name = self._dataframe.columns[column]
            self._filters[column_name] = value
        self._applyFilters()

    def resetFilter(self, column):
        if self.hasFilter(column):
            column_name = self._dataframe.columns[column]
            del self._filters[column_name]
        self._applyFilters()

    def _applyFilters(self):
        self._dataframe = self._source.loc[:, self._visable_columns]
        for column, value in self._filters.items():
            self._dataframe = self._dataframe[self._source[column] == value]
        self.layoutChanged.emit()

    # Data section
    def rowCount(self, parent=None):
        return len(self._dataframe.values)

    def columnCount(self, parent=None):
        return self._dataframe.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._get_cell_value(index.row(), index.column())
            elif role == Qt.EditRole:
                return self._get_cell_value(index.row(), index.column())
            elif role == Qt.CheckStateRole:
                return self._get_check_value(index.row(), index.column())

        return QtCore.QVariant()

    def itemData(self, index: QModelIndex):
        if index.isValid():
            if index.row() >= 0 and index.row() < len(self._dataframe.values):
                if index.column() >= 0 and index.column() < len(self._dataframe.columns):
                    return self._dataframe.iloc[index.row(), index.column()]
        return None

    def _get_cell_value(self, row: int, column: int):
        if self._columns[column].get('type', 'string').lower() == 'datetime':
            datetime = QDateTime(self._dataframe.iloc[row, column])
            return QtCore.QVariant(datetime)
        elif self._columns[column].get('type', 'string').lower() == 'date':
            date = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(date)
        elif self._columns[column].get('type', 'string').lower() == 'time':
            time = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(time)
        elif self._columns[column].get('type', 'string').lower() == 'number':
            number = float(self._dataframe.iloc[row, column])
            return QtCore.QVariant(number)
        elif self._columns[column].get('type', 'string').lower() == 'bool':
            boolean = bool(self._dataframe.iloc[row, column])
            return QtCore.QVariant()
        else:
            value = str(self._dataframe.iloc[row, column])
            return QtCore.QVariant(value)

    def _get_check_value(self, row: int, column: int):
        if self._columns[column].get('type', 'string').lower() == 'bool':
            boolean = bool(self._dataframe.iloc[row, column])
            return Qt.Checked if boolean else Qt.Unchecked
        else:
            return QtCore.QVariant()

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                c = self._columns[column]
                return QtCore.QVariant(c.get('title', c['name']))
            elif role == QtCore.Qt.DecorationRole:
                if self.hasFilter(column):
                    return qta.icon('fa.filter', color='grey')
        return QtCore.QVariant()

    # Sort section
    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        col = self._dataframe.columns[column]
        self._dataframe.sort_values(by=[col], ascending=True if order == 1 else False, inplace=True, axis=0)
        self.layoutChanged.emit()
        super().sort(column, order)


class TableWindow(QtWidgets.QFrame, Ui_TableWindow):
    """
    Класс окна одной таблицы
    """

    def __init__(self, request: Request):
        super().__init__()
        self.setupUi(self)
        self._answer = json.loads(request.answer)
        for attribute, value in self._answer.items():
            if value['type'] == 'cursor':
                columns = value['columns']
                data = value['data']
                model = Cli3TableModel(data, columns)
                self.setModel(model)
                break
        self.setWindowTitle(request.query.name)
        self._request = request
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, point):
        index = self.tableView.indexAt(point)
        if not index.isValid():
            return
        print(index.row(), index.column(), '=>', self.tableView.model().get_source_index(index))
        menu = QtWidgets.QMenu()
        if self._request.query.has_subqueries():
            for subquery in self._request.query.subqueries:
                action = menu.addAction(subquery.name)
                action.setIcon(qta.icon('fa5s.paper-plane', color='green'))
                action.triggered.connect(lambda x: self._send_query(index, subquery))
            menu.addSeparator()
            action = menu.addAction("Cancel")
            menu.exec_(self.tableView.mapToGlobal(point))

    def _send_query(self, index, query):
        print('Query', query)
        err, message = Globals.session.get(f'{Globals.QUERY_API}?id={query.id}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_query = json.loads(message)
            query = Query(json_query)
            idx = self.tableView.model().get_source_index(index)
            row = self.tableView.model().source.loc[idx[0], :]
            print(row.index)
            for param in query.in_params:
                if param.name in row.index:
                    param.value = row[param.name]
            Globals.session.send_query(query)

    def setModel(self, model: QAbstractTableModel):
        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()
        self.tableView.selectionModel().selectionChanged.connect(self._selection_changed)
        self._update_filter_button()

    def setupUi(self, MainWindow):
        super().setupUi(self)
        self.tableView.setSortingEnabled(True)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.filterButton.setIcon(qta.icon('fa5s.filter', color='grey'))
        self.refreshButton.setIcon(qta.icon('fa5s.sync', color='grey'))
        # init menu actions
        self.filterButton.clicked.connect(self._filter_model)
        self.refreshButton.clicked.connect(self._refresh_model)

    def _selection_changed(self, new_selection, old_selection):
        self._update_filter_button()

    def _update_filter_button(self):
        if self.tableView.selectionModel().hasSelection():
            self.filterButton.setDisabled(False)
            indexes = self.tableView.selectionModel().selection().indexes()
            has_filter = self.tableView.model().hasFilter(indexes[0].column())
            self.filterButton.setChecked(has_filter)
        else:
            self.filterButton.setDisabled(True)

    def _filter_model(self):
        indexes = self.tableView.selectedIndexes()
        if len(indexes) > 0:
            cell = self.tableView.model().itemData(indexes[0])
            if self.tableView.model().hasFilter(indexes[0].column()):
                self.tableView.model().resetFilter(indexes[0].column())
            else:
                self.tableView.model().setFilter(indexes[0].column(), cell)
            self._update_filter_button()
            idx = self.tableView.model().index(0, indexes[0].column())
            self.tableView.selectionModel().select(idx, QItemSelectionModel.ClearAndSelect)
            self.tableView.resizeColumnToContents(indexes[0].column())

    def _refresh_model(self):
        self._request.getDoneSignal.connect(self._model_refreshed)
        Globals.session.send_request(self._request)
        Globals.session.requestSentSignal.emit(self._request)
        self.refreshButton.setDisabled(True)

    def _model_refreshed(self, request: Request):
        self._request.getDoneSignal.disconnect(self._model_refreshed)
        self._request = request
        Globals.session.requestDoneSignal.emit(self._request)
        print(request.uuid, '- Received answer for', request.query, 'with error code', request.error)
        if request.error == 0:
            print('Answer', request.answer)
            json_answer = json.loads(request.answer)
            for attribute, value in json_answer.items():
                if value['type'] == 'cursor':
                    columns = value['columns']
                    data = value['data']
                    model = Cli3TableModel(data, columns)
                    self.setModel(model=model)
        self.refreshButton.setDisabled(False)
