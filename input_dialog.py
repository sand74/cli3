from PyQt5 import QtWidgets

from models import Query, Param
from ui.input_dialog import Ui_InputDialog


class InputDialog(QtWidgets.QDialog, Ui_InputDialog):
    def __init__(self, query: Query, parent: QtWidgets = None):
        super().__init__(parent)
        self._query = query
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super().setupUi(self)
        for param in self._query.params:
            if param.type not in ['CURSOR', 'TEXT']:
                if param.field is not None:
                    if param.type == 'LINE':
                        self._create_line_field(param)
                    else:
                        self._create_line_field(param)
                else:
                    self._create_line_field(param)

    def _create_line_field(self, param: Param):
        line_edit = QtWidgets.QLineEdit()
        line_edit.setText(param.value)
        self.fieldsFormLayout.addRow(param.title, line_edit)
