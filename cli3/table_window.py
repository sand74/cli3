import json
from functools import partial

import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtNetwork, QtGui
from PyQt5.QtCore import QAbstractTableModel, Qt, QDateTime, QDate, QModelIndex, \
    QItemSelectionModel
from PyQt5.QtGui import QPainter, QTextDocument
from PyQt5.QtWidgets import QAbstractItemView
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

from cli3.app import Cli3App
from cli3.mdi_window import MdiWindow
from cli3.models import Query, Column
from cli3.network import Request
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
        self._columns = [Column(column) for column in columns]
        self._source = pd.DataFrame(data, columns=[column.name for column in self._columns], dtype=str)
        # Change columns datatypes
        for name, type in [(column.name, column.type) for column in self._columns]:
            if type == 'NUMBER':
                self._source[name] = self._source[name].astype('float')
            elif type == 'INTEGER':
#                self._source[name] = self._source[name].round()
                self._source[name] = self._source[name].astype('float')
                self._source[name].fillna(float(0), inplace=True)
                self._source[name] = self._source[name].astype(int)
            elif type in ['DATE', 'DATETIME', 'TIME']:
                self._source[name] = pd.to_datetime(self._source[name])
            elif type == 'BOOL':
                self._source[name] = self._source[name].apply(lambda x: str(x).upper() == 'TRUE').astype('bool')

        self._visable_columns = [column.name for column in self._columns if
                                 column.title is not None and column.visable == True]
        self._dataframe = self._source.loc[:, self._visable_columns]

    def get_visable_dataframe(self):
        visable_df = self._dataframe.copy()
        visable_df.columns = [self.get_column_by_name(column).title for column in visable_df.columns]
        return visable_df

    def get_column_by_name(self, name):
        columns = [column for column in self._columns if column.name == name]
        if len(columns) > 0:
            return columns[0]
        return None

    def get_column_by_index(self, column):
        if column >= 0 and column < len(self._columns):
            return self._columns[column]
        return None

    def get_source_column(self, column):
        """
        Get column index in source dataframe
        :param column:
        :return:
        """
        return self._source.columns.get_loc(self._dataframe.columns[column])

    def get_source_row(self, row):
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
        if 0 <= index.row() < len(self._dataframe.values):
            if 0 <= index.column() < len(self._dataframe.columns):
                row = self.get_source_row(index.row())
                column = self.get_source_column(index.column())
                return self.index(row, column)
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
            if self._get_cell_value(index.row(), index.column()) is None:
                return QtCore.QVariant()
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
            style = self._source.loc[self.get_source_row(row), 'STYLE']
        column_name = self._dataframe.columns[column]
        if f'STYLE_{column_name}' in self._source.columns:
            style = self._source.loc[self.get_source_row(row), f'STYLE_{column_name}']
        if style is not None:
            if style in Cli3App.instance().styles.keys():
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
        src_column = self.get_source_column(column)
        if self._columns[src_column].type == 'DATETIME':
            datetime = QDateTime(self._dataframe.iloc[row, column])
            return QtCore.QVariant(datetime)
        elif self._columns[src_column].type == 'DATE':
            date = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(date)
        elif self._columns[src_column].type == 'TIME':
            time = QDate(self._dataframe.iloc[row, column])
            return QtCore.QVariant(time)
        elif self._columns[src_column].type == 'NUMBER':
            number = float(self._dataframe.iloc[row, column])
            return QtCore.QVariant(number)
        elif self._columns[src_column].type == 'BOOL':
            boolean = bool(self._dataframe.iloc[row, column])
            return QtCore.QVariant()  # QtCore.QVariant(boolean)
        else:
            value = str(self._dataframe.iloc[row, column])
            nci = self._columns[src_column].nci
            nci_column = self._columns[src_column].nci_column
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
        src_column = self.get_source_column(column)
        if self._columns[src_column].type == 'BOOL':
            boolean = bool(self._dataframe.iloc[row, column])
            return Qt.Checked if boolean else Qt.Unchecked
        else:
            return QtCore.QVariant()

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                col = next((c for c in self._columns if c.name == self._visable_columns[column]), None)
                if col is not None:
                    if '<br>' in col.title:
                        return QtCore.QVariant(col.title.replace('<br>', '\n'))
                    return QtCore.QVariant(col.title)
            elif role == QtCore.Qt.DecorationRole:
                if self.hasFilter(column):
                    return Cli3App.instance().icons.get('filter')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self._dataframe.index[column] + 1))
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
        # Temporary column with display value of column
        self._dataframe['_FOR_SORT'] = self._dataframe.apply(
            lambda row: self._get_cell_value(self._dataframe.index.get_loc(row.name), column), axis=1)
        # Sort by temp column
        self._dataframe.sort_values(by=['_FOR_SORT'], ascending=True if order == 0 else False,
                                    inplace=True, axis=0)
        # drop temp column
        self._dataframe.drop('_FOR_SORT', axis=1, inplace=True)
        self.layoutChanged.emit()
        super().sort(column, order)

    # Restore original dataframe order
    def unsort(self, column):
        self._dataframe.sort_index(inplace=True)


class TableWindow(MdiWindow, Ui_TableWindow):
    """
    Класс окна одной таблицы
    """

    def __init__(self, parent):
        """
        TableWindow creates from request object
        :param request:
        """
        super().__init__(parent=parent)
        self.setupUi(self)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self._show_context_menu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectItems)

    def set_request(self, request: Request):
        super().set_request(request)
        self._answer = json.loads(request.answer)
        for attribute, value in self._answer.items():
            if value['type'] == 'cursor':
                columns = value['columns']
                data = value['data']
                model = Cli3TableModel(data, columns)
                self.setModel(model)
                break

    def _show_context_menu(self, point):
        index = self.tableView.indexAt(point)
        if not index.isValid():
            return
        menu = QtWidgets.QMenu()
        column_index = self.tableView.model().get_source_column(index.column())
        column = self.tableView.model().get_column_by_index(column_index)
        if column.has_subqueries():
            for subquery in column.subqueries:
                query = self._make_query(subquery, index)
                if query is not None:
                    action = menu.addAction(query.name)
                    action.setIcon(Cli3App.instance().icons.get('table'))
                    action.triggered.connect(partial(self._send_query, query))

        if column.has_subqueries() and self._request.query.has_subqueries():
            menu.addSeparator()

        if self._request.query.has_subqueries():
            for subquery in self._request.query.subqueries:
                query = self._make_query(subquery, index)
                if query is not None:
                    action = menu.addAction(query.name)
                    action.setIcon(Cli3App.instance().icons.get('table'))
                    action.triggered.connect(partial(self._send_query, query))

        if column.has_subqueries() or self._request.query.has_subqueries():
            menu.addSeparator()
            menu.addAction("Cancel")
            menu.exec_(self.tableView.mapToGlobal(point))

    def _make_query(self, query, index):
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.QUERY_API}?id={query.id}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_query = json.loads(message)
            query = Query(json_query)
            row_idx = self.tableView.model().get_source_row(index.row())
            row = self.tableView.model().source.loc[row_idx, :]
            for param in query.in_params:
                if param.name.upper() in row.index:
                    param.value = row[param.name.upper()]
            return query
        return None

    def _send_query(self, query) -> None:
        """
        Resen query context menu call anothe request
        :param query: Query to send
        :return:
        """
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
    _last_sort_order = -1

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
            self._last_sort_order = None
        else:
            self.tableView.horizontalHeader().setSortIndicatorShown(True)
            self._last_sorted_column = column
            self._last_sort_order = self.tableView.horizontalHeader().sortIndicatorOrder()

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
                if self._last_sorted_column != -1:
                    # Resore last sort
                    self.tableView.model().sort(self._last_sorted_column, self._last_sort_order)
            else:
                self.tableView.model().setFilter(indexes[0].column(), cell)
            idx = self.tableView.model().index(0, indexes[0].column())
            self.tableView.selectionModel().select(idx, QItemSelectionModel.ClearAndSelect)
            self.tableView.resizeColumnToContents(indexes[0].column())
        Cli3App.instance().updateMainWindiwSignal.emit()

    def print(self, printer):
        df = self.tableView.model().get_visable_dataframe()
        document = QTextDocument()
        html = f"""
        <html>
            <head>
                <style>
                    table.print-friendly tr td, table.print-friendly tr th {"{"}
                        page-break-inside: avoid;
                        white-space: nowrap;
                    {"}"}
                </style>
            </head>
            <body>
                <h1>
                    {self.windowTitle()}
                </h1>
                {df.to_html(classes=['print-friendly'])}
            </body>
        </html>
        """
        html = html.replace("<table", "<table width=100% border=1")
        document.setHtml(html)
        layout = document.documentLayout()
        document_size = layout.documentSize()
        painter = QPainter()
        painter.begin(printer)
        if printer.pageRect().width() < document_size.width():
            xscale = printer.pageRect().width() / document_size.width()
            painter.scale(xscale, xscale)
        document.drawContents(painter)
        painter.end()

    def to_excel(self, filename):
        df = self.tableView.model().get_visable_dataframe()
        date_columns = df.select_dtypes(include=['datetime64[ns, UTC]']).columns
        for date_column in date_columns:
            df[date_column] = df[date_column].astype(str)
        wb = Workbook()
        ws = wb.active
        title = self.windowTitle()
        ws.title = title[:title.find('[')]
        for row in dataframe_to_rows(df, index=True, header=True):
            ws.append(row)
        wb.save(filename=filename)
