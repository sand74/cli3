import json

import pandas as pd
import qtawesome as qta
from PyQt5 import QtWidgets, QtCore, QtNetwork, QtGui
from PyQt5.QtCore import QAbstractTableModel, Qt, QDateTime, QDate, QModelIndex, \
    QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView

from globals import Globals
from models import Query
from network import Request
from ui.table import Ui_TableWindow


class Cli3TableModel(QAbstractTableModel):
    """
    Модель таблицы для представления датафрейма pandas
    """

    def __init__(self, data, columns):
        """
        Creqte source datafram(data, columns) (can not be changed),
        cast columns to column.type,
        create datafram for view (may be changed)
        :param data: arra of arrays data
        :param columns: columns json list
        """
        super().__init__()
        self._filters = {}
        self._columns = columns
        # Sets all names and types to upper case
        for i in range(len(self._columns)):
            columns[i]['name'] = columns[i]['name'].upper()
            columns[i]['type'] = columns[i].get('type', 'STRING').upper()
        self._source = pd.DataFrame(data, columns=[column['name'] for column in columns], dtype=str)
        # Change columns datatypes
        for name, type in [(column['name'], column.get('type', 'STRING')) for column in columns]:
            if type == 'NUMBER':
                self._source[name] = self._source[name].astype('float')
            elif type in ['DATE', 'DATETIME', 'TIME']:
                self._source[name] = pd.to_datetime(self._source[name])
            elif type == 'BOOL':
                self._source[name] = self._source[name].apply(lambda x: str(x).upper() == 'TRUE').astype('bool')

        self._visable_columns = [column['name'] for column in columns if not column['name'].startswith('STYLE')]
        self._dataframe = self._source.loc[:, self._visable_columns]

    def get_source_index(self, index: QModelIndex) -> QModelIndex:
        """
        Convert visible row col to source row col
        :param index: visible index
        :return: source index
        """
        if index.row() >= 0 and index.row() < len(self._dataframe.values):
            if index.column() >= 0 and index.column() < len(self._dataframe.columns):
                row = self._dataframe.index[index.row()]
                column = self._source.columns.get_loc(self._dataframe.columns[index.column()])
                return self.index(row=row, column=column)
        return QModelIndex()

    @property
    def source(self):
        return self._source

    # Filters section
    def get_filters(self) -> dict:
        """
        Get all filter set on columns
        :return: filters dict {column->value}
        """
        return self._filters

    def hasFilter(self, column) -> bool:
        """
        Check is column filtered
        :param column: column name
        :return:
        """
        column_name = self._dataframe.columns[column]
        return column_name in self._filters.keys()

    def setFilter(self, column, value) -> None:
        """
        Set filter value to column
        :param column:
        :param value:
        :return:
        """
        if not self.hasFilter(column):
            column_name = self._dataframe.columns[column]
            self._filters[column_name] = value
        self._applyFilters()

    def resetFilter(self, column):
        """
        Reset filter value to column
        :param column:
        :param value:
        :return:
        """
        if self.hasFilter(column):
            column_name = self._dataframe.columns[column]
            del self._filters[column_name]
        self._applyFilters()

    def _applyFilters(self) -> None:
        """
        Make visible dataframe appling all filters on source
        :return:
        """
        self._dataframe = self._source.loc[:, self._visable_columns]
        for column, value in self._filters.items():
            if value is not None:
                self._dataframe = self._dataframe[self._source[column] == value]
            else:
                self._dataframe = self._dataframe[self._source[column].isnull()]

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
            elif role == Qt.TextColorRole:
                pass
                # if index.column() == 0:
                #     return QtGui.QColor(255,0,0)
            elif role == Qt.BackgroundColorRole:
                pass
                # if index.column() == 0:
                #     return QtGui.QColor(0, 0, 255)
        return QtCore.QVariant()

    def itemData(self, index: QModelIndex):
        if index.isValid():
            if index.row() >= 0 and index.row() < len(self._dataframe.values):
                if index.column() >= 0 and index.column() < len(self._dataframe.columns):
                    return self._dataframe.iloc[index.row(), index.column()]
        return None

    def _get_cell_value(self, row: int, column: int):
        """
        Get dataframe cell value converted to column type
        :param row:
        :param column:
        :return:
        """
        if self._dataframe.iloc[row, column] == None:
            return None
        if self._columns[column].get('type', 'STRING') == 'DATETIME':
            datetime = QDateTime(self._dataframe.iloc[row, column])
            return QtCore.QVariant(datetime)
        elif self._columns[column].get('type', 'STRING') == 'DATE':
            date = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(date)
        elif self._columns[column].get('type', 'STRING') == 'TIME':
            time = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(time)
        elif self._columns[column].get('type', 'STRING') == 'NUMBER':
            number = float(self._dataframe.iloc[row, column])
            return QtCore.QVariant(number)
        elif self._columns[column].get('type', 'STRING') == 'BOOL':
            boolean = bool(self._dataframe.iloc[row, column])
            return QtCore.QVariant(boolean)
        else:
            value = str(self._dataframe.iloc[row, column])
            return QtCore.QVariant(value)

    def _get_check_value(self, row: int, column: int):
        if self._columns[column].get('type', 'STRING') == 'BOOL':
            boolean = bool(self._dataframe.iloc[row, column])
            return Qt.Checked if boolean else Qt.Unchecked
        else:
            return QtCore.QVariant()

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                col = next((c for c in self._columns if c['name'] == self._visable_columns[column]), None)
                if col is not None:
                    return QtCore.QVariant(col.get('title', col['name']))
            elif role == QtCore.Qt.DecorationRole:
                if self.hasFilter(column):
                    return qta.icon('fa.filter', color='grey')
        return QtCore.QVariant()

    # Sort section
    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        """
        Sort dataframe by column with specified sort order
        :param column: Column to sort
        :param order: ort order
        :return:
        """
        col = self._dataframe.columns[column]
        self._dataframe.sort_values(by=[col], ascending=True if order == 1 else False, inplace=True, axis=0)
        self.layoutChanged.emit()
        super().sort(column, order)


class TableWindow(QtWidgets.QFrame, Ui_TableWindow):
    """
    Класс окна одной таблицы
    """

    def __init__(self, request: Request):
        """
        TableWindow creates from request object
        :param request:
        """
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
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectItems)

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
            menu.addAction("Cancel")
            menu.exec_(self.tableView.mapToGlobal(point))

    def _send_query(self, index, query) -> None:
        """
        Resen query context menu call anothe request
        :param index: column index
        :param query: Query to send
        :return:
        """
        print('Query', query)
        err, message = Globals.session.get(f'{Globals.session.QUERY_API}?id={query.id}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_query = json.loads(message)
            query = Query(json_query)
            idx = self.tableView.model().get_source_index(index)
            row = self.tableView.model().source.loc[idx.row(), :]
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

    def _update_filter_button(self) -> None:
        """
        Set filter button to checked if column has filter unchecked else
        :return:
        """
        if self.tableView.selectionModel().hasSelection():
            self.filterButton.setDisabled(False)
            indexes = self.tableView.selectionModel().selection().indexes()
            has_filter = self.tableView.model().hasFilter(indexes[0].column())
            self.filterButton.setChecked(has_filter)
        else:
            self.filterButton.setDisabled(True)

    def _filter_model(self) -> None:
        """
        Filter model for selected cell value
        :return:
        """
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
        """
        Resend request linked to this table
        :return:
        """
        self._request.getDoneSignal.connect(self._model_refreshed)
        Globals.session.send_request(self._request)
        Globals.session.requestSentSignal.emit(self._request)
        self.refreshButton.setDisabled(True)

    def _model_refreshed(self, request: Request):
        """
        Update table model with new Request
        :param request:
        :return:
        """
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
                    break
        self.refreshButton.setDisabled(False)
