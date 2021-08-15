from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, QModelIndex, QSortFilterProxyModel, Qt, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QSizePolicy, QTableWidget, QCompleter, QHeaderView

from globals import Globals
from models import Query, Param
from nci_table import NciCompleter, NciTableView, NciTableModel
from table import PandasTableModel
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


class ComboSelectField(ParamMixin, QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        QtWidgets.QComboBox.__init__(self, parent)
        ParamMixin.__init__(self, param)
        for key, value in param.field.desc['values'].items():
            self.addItem(key, value)

    def get_value(self):
        return self.currentData()


class NciSelectField(ParamMixin, QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        QtWidgets.QComboBox.__init__(self, parent)
        ParamMixin.__init__(self, param)
        self.table_view = NciTableView(self)
        self.table_model = NciTableModel(Globals.nci[param.field.desc['table']], 20)
        self.setView(self.table_view)
        self.setModel(self.table_model)
        self.setModelColumn(1)
        self.setMinimumWidth(400)
        self.setEditable(True)
        self.lineEdit().textEdited.connect(self.text_changed)
        self.setMaxCount(20)

    def text_changed(self, new_text):
        self.table_model.setFilter(new_text)
        self.setModel(self.table_model)

    def get_value(self):
        index = self.model().index(self.currentIndex(), 0)
        data = self.model().data(index).value()
        return data if data is not None else self.currentText()


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
                            field = NciSelectField(self, param=param)
                            field.setCurrentText(param.value)
                            field.text_changed(param.value)

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
