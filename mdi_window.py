import pickle

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt

from app import Cli3App
from network import Request


class MdiWindow(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        # preffered szie 3/4 from mdi
        self._preffered_size = QSize(parent.size().width() // 4 * 3, parent.size().height() // 4 * 3)

    def sizeHint(self):
        return self._preffered_size

    def set_request(self, request: Request):
        self._request = request
        self.setWindowTitle(request.query.get_full_name(request.params))

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
        if request.error == 0:
            self.set_request(request=request)
        Cli3App.instance().updateMainWindiwSignal.emit()

    def save(self, filename):
        with open(filename, 'wb') as outp:
            pickle.dump(self._request, outp, pickle.HIGHEST_PROTOCOL)

    def has_filter(self):
        return None

    def set_filter(self):
        pass

    def can_print(self):
        return False

    def print(self, printer):
        pass
