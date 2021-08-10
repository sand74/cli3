from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate

from globals import Globals
from models import Query, Param
from ui.input_dialog import Ui_InputDialog


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
                if param.field is not None:
                    if param.type == 'LINE':
                        self._create_input_string(param)
                    elif param.type == 'NUMBER':
                        self._create_number_field(param)
                    elif param.type == 'DATE':
                        self._create_date_field(param)
                    else:
                        self._create_input_string(param)
                else:
                    self._create_input_string(param)
            else:
                if param.type == 'CURSOR':
                    self._create_output_cursor(param)
                elif param.type == 'TEXT':
                    self._create_output_text(param)

    def _create_output_cursor(self, param: Param) -> None:
        self._items.append(ParamMixin(param))

    def _create_output_text(self, param: Param) -> None:
        self._items.append(ParamMixin(param))

    def _create_input_string(self, param: Param) -> None:
        '''
        QLineEdit для ввода строковых значений
        :param param: Модель параметра
        '''
        field = StringInputField(self, param=param)
        field.setText(param.value)
        self._items.append(field)
        self.fieldsFormLayout.addRow(param.title, field)

    def _create_number_field(self, param: Param) -> None:
        '''
        QSpinBox для ввода числовых значений
        :param param: Модель параметра
        '''
        field = NumberInputField(self, param=param)
        field.setValue(int(param.value))
        self._items.append(field)
        self.fieldsFormLayout.addRow(param.title, field)

    def _create_date_field(self, param: Param) -> None:
        '''
        QDateEdit для ввода даты
        :param param: Модель параметра
        '''
        field = DateInputField(self, param=param)
        if param.value.startswith('func='):
            # TODO Здесь надо придумать что-то другое - небезопасно
            date = eval(param.value[5:])
            field.setDate(date)
        else:
            field.setDate(QDate.fromString(param.value))
        self._items.append(field)
        self.fieldsFormLayout.addRow(param.title, field)

    def get_params(self):
        params = dict()
        for item in self._items:
            if isinstance(item, ParamMixin):
                params[item.name] = item.get_value()
        return params

    def process_request(self) -> None:
        Globals.session.send_query(self._query, self.get_params())
