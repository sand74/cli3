from datetime import datetime
from typing import Any

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate

from app import Cli3App
from models import Query, Param
from nci_table import NciTableView, NciTableModel
from ui.input_dialog import Ui_InputDialog


class ParamMixin(object):
    """
    Mixin for using in all input field
    """

    def __init__(self, param: Param, *args, **kwargs):
        self._param = param

    @property
    def name(self) -> str:
        """
        Field name for field label
        :return: field name
        """
        return self._param.name

    def get_value(self) -> Any:
        """
        Field value for collect values from all fields when submit
        :return: field value
        """
        return self._param.value


class StringInputField(QtWidgets.QLineEdit, ParamMixin):
    """
    Input field for string line input
    """

    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        """
        Constructor for QLineText + ParamMixin
        :param parent: parent widget
        :param param: param model for associate
        """
        super().__init__(parent=parent, param=param)
        self.setText(param.value)

    def get_value(self) -> str:
        """
        Overrides from ParamMixin
        :return: value of this field
        """
        return self.text()


class NumberInputField(QtWidgets.QSpinBox, ParamMixin):
    """
    Input field for input number
    """

    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        """
        Constructor for QSpinBox + ParamMixin
        :param parent: parent widget
        :param param: param model for associate
        """
        super().__init__(parent=parent, param=param)
        self.setValue(int(param.value))

    def get_value(self) -> str:
        """
        Overrides from ParamMixin
        :return: value of this field
        """
        return str(self.value())


class DateInputField(QtWidgets.QDateEdit, ParamMixin):
    """
    Input field for input date
    """

    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        """
        Constructor for QDateEdit + ParamMixin
        :param parent: parent widget
        :param param: param model for associate
        """
        super().__init__(parent=parent, param=param)
        if param.value.startswith('func='):
            # TODO Здесь надо придумать что-то другое - небезопасно
            date = eval(param.value[5:])
            self.setDate(date)
        else:
            self.setDate(QDate.fromString(param.value))

    def get_value(self) -> datetime.date:
        """
        Overrides from ParamMixin
        :return: value of this field
        """
        return self.date().toPyDate()


class ComboSelectField(QtWidgets.QComboBox, ParamMixin):
    """
    Input field for static combo values
    """

    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        """
        Constructor for QComboBox + ParamMixin
        For construct combo uses param.field.desc['values']
        :param parent: parent widget
        :param param: param model for associate
        """
        super(ComboSelectField, self).__init__(parent=parent, param=param)
        if param.field.values is not None:
            for value in param.field.values.split('\n'):
                key, value = value.split('=', maxsplit=1)
                self.addItem(key, value)
            index = self.findData(param.value)
            if index >= 0:
                self.setCurrentIndex(index)

    def get_value(self):
        """
        Overrides from ParamMixin
        :return: value of this field
        """
        return self.currentData()


class NciSelectField(QtWidgets.QComboBox, ParamMixin):
    """
    Input field for nci combo values
    """

    def __init__(self, parent: QtWidgets.QWidget, param: Param):
        """
        Constructor for QComboBox + ParamMixin
        For construct combo uses param.field.desc['table']
        :param parent: parent widget
        :param param: param model for associate
        """
        super(NciSelectField, self).__init__(parent=parent, param=param)
        self.table_view = NciTableView(self)
        self.table_model = NciTableModel(Cli3App.instance().nci[param.field.nci['name']], 20)
        self.setView(self.table_view)
        self.setModel(self.table_model)
        self.setModelColumn(1)
        self.setMinimumWidth(400)
        self.setEditable(True)
        self.lineEdit().textEdited.connect(self._text_changed)
        self.setMaxCount(20)
        self.lineEdit().setClearButtonEnabled(True)
        # Set current value
        self.setCurrentText(param.value)
        self._text_changed(param.value)

    def _text_changed(self, new_text):
        # TODO Заполнить значение в поле из values если осталось только одно
        self.table_model.setFilter(new_text)
        self.setModel(self.table_model)
        if self.model().rowCount() == 1:
            self.lineEdit().setStyleSheet("color: black;")
            self.setCurrentIndex(0)
        elif self.model().rowCount() == 0:
            self.lineEdit().setStyleSheet("color: red;")
        else:
            self.lineEdit().setStyleSheet("color: black;")

    def get_value(self):
        """
        Overrides from ParamMixin
        :return: value of this field
        """
        index = self.model().index(self.currentIndex(), 0)
        data = self.model().data(index).value()
        print(self.currentText())
        return data if data is not None else self.currentText()


class InputDialog(QtWidgets.QDialog, Ui_InputDialog):
    """
    Диалоговое окно для означивания параметров запрося
    """

    def __init__(self, query: Query, parent: QtWidgets = None):
        super().__init__(parent)
        self._query = query
        self._items = []
        self.setupUi(self)
        self.setWindowTitle(query.name)
        self.accepted.connect(self.process_request)

    def setupUi(self, InputDialog):
        """
        :param InputDialog: this class
        :return:
        """
        super().setupUi(self)
        for param in self._query.params:
            if param.type not in ['CURSOR', 'TEXT']:
                field = None
                if param.field is not None:
                    if param.field.type == 'LINE':
                        field = StringInputField(self, param=param)
                    elif param.field.type == 'NUMBER':
                        field = NumberInputField(self, param=param)
                    elif param.field.type == 'DATE':
                        field = DateInputField(self, param=param)
                    elif param.field.type == 'COMBOBOX':
                        field = ComboSelectField(self, param=param)
                    elif param.field.type == 'COMBONCI':
                        field = NciSelectField(self, param=param)
                    else:
                        field = StringInputField(self, param=param)
                else:
                    field = StringInputField(self, param=param)
                # Append field to form
                self._items.append(field)
                self.fieldsFormLayout.addRow(param.title, field)
            else:
                if param.type == 'CURSOR':
                    self._items.append(ParamMixin(param))
                elif param.type == 'TEXT':
                    self._items.append(ParamMixin(param))

    def get_params(self) -> dict:
        """
        Construct param->value dictionary
        :return: param->value dictionary
        """
        params = dict()
        for item in self._items:
            if isinstance(item, ParamMixin):
                params[item.name] = item.get_value()
        return params

    def process_request(self) -> None:
        """
        Send request from this dialog
        :return: None
        """
        Cli3App.instance().session.send_query(self._query, self.get_params())
