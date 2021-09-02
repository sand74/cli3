import json

from cli3.mdi_window import MdiWindow
from cli3.network import Request
from ui.text_window import Ui_TextWindow


class TextWindow(MdiWindow, Ui_TextWindow):
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
        self._model = None

    def set_request(self, request: Request):
        super().set_request(request)
        self._answer = json.loads(request.answer)
        for attribute, value in self._answer.items():
            if value['type'] == 'text':
                self.textBrowser.setText(value.get('data', 'Bad text format'))
                break
