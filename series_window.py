import json

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSize, QObject
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from mdi_window import MdiWindow
from models import Column
from network import Request
from ui.series_window import Ui_SeriesWindow

import pandas as pd


class Cli3SeriesModel(QObject):
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
            elif type in ['DATE', 'DATETIME', 'TIME']:
                self._source[name] = pd.to_datetime(self._source[name])
            elif type == 'BOOL':
                self._source[name] = self._source[name].apply(lambda x: str(x).upper() == 'TRUE').astype('bool')

        self._visable_columns = [column.name for column in self._columns if
                                 column.title is not None and column.visable == True]
        self._dataframe = self._source.loc[:, self._visable_columns]

    def get_dataframe(self):
        return self._dataframe

    def get_column_by_name(self, name):
        return next((c for c in self._columns if c.name == name), None)


class SeriesWindow(MdiWindow, Ui_SeriesWindow):
    """
    Класс окна одной таблицы
    """

    def __init__(self, parent):
        """
        SeriesWindow creates from request object
        :param request:
        """
        super().__init__(parent=parent)
        self.setupUi(self)
        self.toolBox = QtWidgets.QToolBox(self)
        self.toolBox.setObjectName("toolBox")
        self.verticalLayout.addWidget(self.toolBox)
        # preffered szie 3/4 from mdi
        self._model = None

    def set_request(self, request: Request):
        super().set_request(request)
        self._answer = json.loads(request.answer)
        for attribute, value in self._answer.items():
            if value['type'] == 'cursor':
                columns = value['columns']
                data = value['data']
                model = Cli3SeriesModel(data, columns)
                self.set_model(model)
                break

    def set_model(self, model: Cli3SeriesModel):
        self._model = model
        for i in range(self.toolBox.count(), 0, -1):
            self.toolBox.removeItem(i - 1)
        model.get_dataframe().apply(lambda row: self._create_page(row), axis=1)
        self.toolBox.setCurrentIndex(0)

    def _create_page(self, series: pd.Series):
        page = QtWidgets.QWidget()
        page.setGeometry(QtCore.QRect(0, 0, 730, 535))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(page.sizePolicy().hasHeightForWidth())
        page.setSizePolicy(sizePolicy)
        page.setObjectName(f"{series.name}Page")
        verticalLayout = QtWidgets.QVBoxLayout(page)
        verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        verticalLayout.setContentsMargins(6, 6, 6, 6)
        verticalLayout.setObjectName(f"{series.name}VerticalLayout")
        tableWidget = QtWidgets.QTableWidget(page)
        tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        tableWidget.setGridStyle(QtCore.Qt.DotLine)
        tableWidget.setColumnCount(2)
        tableWidget.setObjectName(f"{series.name}TableWidget")
        tableWidget.setRowCount(0)
        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setVisible(True)
        tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('Параметр'))
        tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('Значение'))
        tableWidget.verticalHeader().setVisible(True)
        verticalLayout.addWidget(tableWidget)
        tableWidget.setSortingEnabled(True)

        self._fill_table(tableWidget, series)

        self.toolBox.setItemText(self.toolBox.indexOf(page), f"{series.name}")
        col = self._model.get_column_by_name(series.index[0])
        self.toolBox.addItem(page, f'{col.title}: {series.to_numpy()[0]}')

    def _fill_table(self, table: QTableWidget, series: pd.Series):
        row = 0
        for index, value in series.items():
            table.insertRow(row)
            col = self._model.get_column_by_name(index)
            if col is not None:
                table.setItem(row, 0, QTableWidgetItem(col.title))
            else:
                table.setItem(row, 0, QTableWidgetItem(index))

            table.setItem(row, 1, QTableWidgetItem(value))
            row += 1
        table.resizeColumnToContents(0)
