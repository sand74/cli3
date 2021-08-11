from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QSizePolicy, QTableWidget

from globals import Globals
from models import Query, Param, PandasTableModel
from ui.input_dialog import Ui_InputDialog
from datetime import datetime

class ParamMixin():
    def __init__(self, param: Param):
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


class ComboSelectField(QtWidgets.QComboBox, ParamMixin):
    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        super().__init__(parent=parent, param=param)
        if 'values' in param.field.desc.keys():
            print('Common combo', param.field.desc['values'])
            for key, value in param.field.desc['values'].items():
                self.addItem(key, value)
        elif 'table' in param.field.desc.keys():
            print('Table combo', param.field.desc['table'])
            self.setEditable(True)
            table_view = QtWidgets.QTableView()
            table_view.setSelectionBehavior(QTableWidget.SelectRows)
            self.setModel(PandasTableModel(Globals.nci['roads']))
            self.setModelColumn(0)
            self.setView(table_view)
            self.setMinimumWidth(500)

    def get_value(self):
        data = self.currentData()
        return data


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
                        field = ComboSelectField(self, param=param)
                        index = field.findData(param.value)
                        if index >= 0:
                            field.setCurrentIndex(index)
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
