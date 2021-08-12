from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, QModelIndex, QSortFilterProxyModel, Qt, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QSizePolicy, QTableWidget, QCompleter, QHeaderView

from globals import Globals
from models import Query, Param, PandasTableModel
from ui.input_dialog import Ui_InputDialog
from datetime import datetime


class ParamMixin(object):
    def __init__(self, param: Param, *args, **kwargs):
        self._param = param

    @property
    def name(self):
        return self._param.name

    def get_value(self) -> str:
        return self._param.value


class StringInputField(QtWidgets.QLineEdit, ParamMixin):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        super().__init__(parent=parent, param=param)

    def get_value(self):
        return self.text()


class NumberInputField(QtWidgets.QSpinBox, ParamMixin):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        super().__init__(parent=parent, param=param)

    def get_value(self):
        return str(self.value())


class DateInputField(QtWidgets.QDateEdit, ParamMixin):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        super().__init__(parent=parent, param=param)

    def get_value(self):
        return self.date().toPyDate()


class ExtendedComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setPopup(self.view())
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def view(self):
        return self.completer.popup()

    def index(self):
        return self.currentIndex()

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


class CustomComplter(QCompleter):
    activatedSignal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activated[QtCore.QModelIndex].connect(self.item_activated)

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
            return data.value()


class TableSelectField(ParamMixin, QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        QtWidgets.QLineEdit.__init__(self, parent)
        ParamMixin.__init__(self, param)

        self.value = None

        self.setFocusPolicy(Qt.StrongFocus)
        # TableView
        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().hide()
        # Table model
        self.table_model = PandasTableModel(Globals.nci[param.field.desc['table']])
        self.filter_model = QSortFilterProxyModel(self)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_model.setFilterKeyColumn(-1)
        self.filter_model.setSourceModel(self.table_model)
        # add a completer, which uses the filter model
        self.completer = CustomComplter(self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setPopup(self.table_view)
        self.completer.setCompletionColumn(1)
        self.completer.setModel(self.table_model)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)
        self.completer.setCompletionRole(PandasTableModel.ROW_AS_STRING_ROLE)
        self.completer.activated[QtCore.QModelIndex].connect(self.item_activated)
        self.textChanged.connect(self.text_changed)

    @pyqtSlot(str)
    def text_changed(self, text: str):
        self.value = None

    @pyqtSlot(QModelIndex)
    def item_activated(self, index: QModelIndex):
        self.blockSignals(True)
        data = index.model().data(index, self.completer.completionRole())
        index_list = self.completer.model().match(
            self.completer.model().index(0, self.completer.completionColumn()),
            self.completer.completionRole(), data,
            1, Qt.MatchExactly)
        if len(index_list) > 0:
            self.value = self.completer.model().data(index_list[0], PandasTableModel.ROW_INDEX_ROLE)
        else:
            self.value = None
        self.blockSignals(False)

    def get_value(self):
        if self.value is not None:
            return self.value
        else:
            return self.text()


class ComboSelectField(ParamMixin, QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        QtWidgets.QComboBox.__init__(self, parent)
        ParamMixin.__init__(self, param)
        for key, value in param.field.desc['values'].items():
            self.addItem(key, value)

    def get_value(self):
        return self.currentData()


class RoadSelectField(QtWidgets.QComboBox, ParamMixin):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        super().__init__(parent=parent, param=param)

    def get_value(self):
        return self.date().toPyDate()


class InputDialog(QtWidgets.QDialog, Ui_InputDialog):
    """
    Диалоговое окно для означивания параметров запрося
    """

    def __init__(self, query: Query, parent: QtWidgets = None):
        super().__init__(parent)
        self._query = query
        self._items = []
        self.setupUi(self)
        self.accepted.connect(self.process_request)

    def setupUi(self, MainWindow):
        super().setupUi(self)
        for param in self._query.params:
            if param.type not in ['CURSOR', 'TEXT']:
                field = None
                if param.field is not None:
                    if param.field.type == 'LINE':
                        field = StringInputField(self, param=param)
                        field.setText(param.value)
                    elif param.field.type == 'NUMBER':
                        field = NumberInputField(self, param=param)
                        field.setValue(int(param.value))
                    elif param.field.type == 'DATE':
                        field = DateInputField(self, param=param)
                        if param.value.startswith('func='):
                            # TODO Здесь надо придумать что-то другое - небезопасно
                            date = eval(param.value[5:])
                            field.setDate(date)
                        else:
                            field.setDate(QDate.fromString(param.value))
                    elif param.field.type == 'COMBOBOX':
                        if 'values' in param.field.desc.keys():
                            field = ComboSelectField(self, param=param)
                            index = field.findData(param.value)
                            if index >= 0:
                                field.setCurrentIndex(index)
                        elif 'table' in param.field.desc.keys():
                            field = TableSelectField(self, param=param)

                    else:
                        field = StringInputField(self, param=param)
                        field.setText(param.value)
                else:
                    field = StringInputField(self, param=param)
                    field.setText(param.value)
                # Append field to form
                self._items.append(field)
                self.fieldsFormLayout.addRow(param.title, field)
            else:
                if param.type == 'CURSOR':
                    self._items.append(ParamMixin(param))
                elif param.type == 'TEXT':
                    self._items.append(ParamMixin(param))

    def get_params(self):
        params = dict()
        for item in self._items:
            if isinstance(item, ParamMixin):
                params[item.name] = item.get_value()
        return params

    def process_request(self) -> None:
        Globals.session.send_query(self._query, self.get_params())
