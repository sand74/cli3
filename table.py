import json
import pickle

import pandas as pd
import qtawesome as qta
from PyQt5 import QtWidgets, QtCore, QtNetwork, QtGui
from PyQt5.QtCore import QAbstractTableModel, Qt, QDateTime, QDate, QModelIndex, \
    QItemSelectionModel, QPoint
from PyQt5.QtWidgets import QAbstractItemView, QWhatsThis

from app import Cli3App
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

        self._visable_columns = [column['name'] for column in columns if
                                 'title' in column.keys() and column['visable'] == True]
        self._dataframe = self._source.loc[:, self._visable_columns]

    def _get_source_column(self, column):
        """
        Get column index in source dataframe
        :param column:
        :return:
        """
        return self._source.columns.get_loc(self._dataframe.columns[column])

    def _get_source_row(self, row):
        """
        Get row index in source dataframe
        :param column:
        :return:
        """
        return self._dataframe.index[row]

    def get_source_index(self, index: QModelIndex) -> QModelIndex:
        """
        Convert visible row col to source row col
        :param index: visible index
        :return: source index
        """
        if index.row() >= 0 and index.row() < len(self._dataframe.values):
            if index.column() >= 0 and index.column() < len(self._dataframe.columns):
                return self.index(self._get_source_row(index.row()), self._get_source_column(index.column()))
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
            elif role == Qt.ForegroundRole:
                style = self._get_cell_style(index.row(), index.column())
                if style is not None:
                    text_color = self._hex2rgb(style['text_color'])
                    color = QtGui.QColor(text_color[0], text_color[1], text_color[2])
                    return QtGui.QBrush(color)
            elif role == Qt.BackgroundRole:
                style = self._get_cell_style(index.row(), index.column())
                if style is not None:
                    text_color = self._hex2rgb(style['background_color'])
                    color = QtGui.QColor(text_color[0], text_color[1], text_color[2])
                    color.setAlphaF(0.5)
                    return QtGui.QBrush(color)
            elif role == Qt.ToolTipRole:
                return f'{self._get_cell_value(index.row(), index.column()).value()}'
            elif role == Qt.WhatsThisRole:
                return f'{self._get_cell_value(index.row(), index.column()).value()}'
        return QtCore.QVariant()

    def itemData(self, index: QModelIndex):
        if index.isValid():
            if index.row() >= 0 and index.row() < len(self._dataframe.values):
                if index.column() >= 0 and index.column() < len(self._dataframe.columns):
                    return self._dataframe.iloc[index.row(), index.column()]
        return None

    def _hex2rgb(self, hex_color):
        color = hex_color[-6:]
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

    def _get_cell_style(self, row: int, column: int):
        """
        Get cell style from hiden styeles column
        :param row:
        :param column:
        :return:
        """
        style = None
        if 'STYLE' in self._source.columns:
            style = self._source.loc[row, 'STYLE']
        column_name = self._dataframe.columns[column]
        if f'STYLE_{column_name}' in self._source.columns:
            style = self._source.loc[row, f'STYLE_{column_name}']
        if style is not None and style in Cli3App.instance().styles.keys():
            return Cli3App.instance().styles[style]
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
        src_column = self._get_source_column(column)
        if self._columns[src_column].get('type', 'STRING') == 'DATETIME':
            datetime = QDateTime(self._dataframe.iloc[row, column])
            return QtCore.QVariant(datetime)
        elif self._columns[src_column].get('type', 'STRING') == 'DATE':
            date = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(date)
        elif self._columns[src_column].get('type', 'STRING') == 'TIME':
            time = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(time)
        elif self._columns[src_column].get('type', 'STRING') == 'NUMBER':
            number = float(self._dataframe.iloc[row, column])
            return QtCore.QVariant(number)
        elif self._columns[src_column].get('type', 'STRING') == 'BOOL':
            boolean = bool(self._dataframe.iloc[row, column])
            return QtCore.QVariant(boolean)
        else:
            value = str(self._dataframe.iloc[row, column])
            nci = self._columns[src_column].get('nci', None)
            nci_column = self._columns[src_column].get('nci_column', None)
            if nci is not None and nci_column is not None:
                value = self._get_value_from_nci(value, nci.get('name', None), nci_column.upper())
            return QtCore.QVariant(value)

    def _get_value_from_nci(self, key, nci_table, nci_column):
        """
        Translate value in nci column
        :param key: value to translate
        :param nci_table:
        :param nci_column:
        :return:
        """
        nci_df = Cli3App.instance().nci.get(nci_table, None)
        if nci_df is not None:
            if key in nci_df.index.values:
                if nci_column in nci_df.columns:
                    return nci_df.loc[key, nci_column]
        return key

    def _get_check_value(self, row: int, column: int):
        src_column = self._get_source_column(column)
        if self._columns[src_column].get('type', 'STRING') == 'BOOL':
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
                    return Cli3App.instance().icons.get('filter')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self._dataframe.index[column]))
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
        self._dataframe.sort_values(by=[col], ascending=True if order == 0 else False, inplace=True, axis=0)
        self.layoutChanged.emit()
        super().sort(column, order)

    # Restore original dataframe order
    def unsort(self, column):
        self._dataframe.sort_index(inplace=True)


class Cli3WindowMixin():
    def save(self, filename):
        pass

    def load(self, filename):
        pass

    def has_filter(self):
        return None

    def set_filter(self):
        pass

    def is_locked(self) -> bool:
        return False

    def refresh(self):
        pass

class TableWindow(QtWidgets.QFrame, Ui_TableWindow, Cli3WindowMixin):
    """
    Класс окна одной таблицы
    """

    def __init__(self):
        """
        TableWindow creates from request object
        :param request:
        """
        super().__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self._show_context_menu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectItems)

    def set_request(self, request: Request):
        self._request = request
        self._answer = json.loads(request.answer)
        for attribute, value in self._answer.items():
            if value['type'] == 'cursor':
                columns = value['columns']
                data = value['data']
                model = Cli3TableModel(data, columns)
                self.setModel(model)
                break
        self.setWindowTitle(request.query.get_full_name())

    def _show_context_menu(self, point):
        index = self.tableView.indexAt(point)
        if not index.isValid():
            return
        menu = QtWidgets.QMenu()
        if self._request.query.has_subqueries():
            for subquery in self._request.query.subqueries:
                action = menu.addAction(subquery.name)
                action.setIcon(Cli3App.instance().icons.get('table'))
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
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.QUERY_API}?id={query.id}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_query = json.loads(message)
            query = Query(json_query)
            idx = self.tableView.model().get_source_index(index)
            row = self.tableView.model().source.loc[idx.row(), :]
            for param in query.in_params:
                if param.name.upper() in row.index:
                    param.value = row[param.name.upper()]
            Cli3App.instance().session.send_query(query)

    def setModel(self, model: QAbstractTableModel):
        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()
        self.tableView.selectionModel().selectionChanged.connect(self._selection_changed)

    def setupUi(self, MainWindow):
        super().setupUi(self)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.verticalHeader().setVisible(True)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setSortIndicatorShown(False)
        self.tableView.horizontalHeader().sectionClicked.connect(self._change_sort_order)
        # init menu actions

    _last_sorted_column = -1

    def _change_sort_order(self, column):
        """
        Dance with buben to restore original sort state
        :param column:
        :return:
        """
        if self.tableView.horizontalHeader().sortIndicatorOrder() == Qt.AscendingOrder and \
                column == self._last_sorted_column:
            self.tableView.horizontalHeader().setSortIndicator(column, Qt.DescendingOrder)
            self.tableView.horizontalHeader().setSortIndicatorShown(False)
            self.tableView.model().unsort(column)
            self._last_sorted_column = -1
        else:
            self.tableView.horizontalHeader().setSortIndicatorShown(True)
            self._last_sorted_column = column

    def _selection_changed(self, new_selection, old_selection):
        Cli3App.instance().updateMainWindiwSignal.emit()

    def has_filter(self):
        if self.tableView.selectionModel().hasSelection():
            indexes = self.tableView.selectionModel().selection().indexes()
            has_filter = self.tableView.model().hasFilter(indexes[0].column())
            return has_filter
        else:
            return None

    def set_filter(self):
        self._filter_model()

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
            idx = self.tableView.model().index(0, indexes[0].column())
            self.tableView.selectionModel().select(idx, QItemSelectionModel.ClearAndSelect)
            self.tableView.resizeColumnToContents(indexes[0].column())
        Cli3App.instance().updateMainWindiwSignal.emit()

    locked = False

    def is_locked(self):
        return self.locked

    def refresh(self):
        self._refresh_model()

    def _refresh_model(self):
        """
        Resend request linked to this table
        :return:
        """
        self._request.getDoneSignal.connect(self._model_refreshed)
        Cli3App.instance().session.send_request(self._request)
        Cli3App.instance().session.requestSentSignal.emit(self._request)
        self.locked = True
        Cli3App.instance().updateMainWindiwSignal.emit()

    def _model_refreshed(self, request: Request):
        """
        Update table model with new Request
        :param request:
        :return:
        """
        self._request.getDoneSignal.disconnect(self._model_refreshed)
        self._request = request
        Cli3App.instance().session.requestDoneSignal.emit(self._request)
        self.locked = False
        print(request.uuid, '- Received answer for', request.query, 'with error code', request.error)
        if request.error == 0:
            self.set_request(request=request)
        Cli3App.instance().updateMainWindiwSignal.emit()

    def save(self, filename):
        with open(filename, 'wb') as outp:
            pickle.dump(self._request, outp, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, 'rb') as inp:
            request = pickle.load(inp)
            self.set_request(request=request)
            return self
