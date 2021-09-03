import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt5.QtGui import QColor, QPalette
from pyupdater.client import Client

from ui.update_dialog import Ui_updateDialog

logger = logging.getLogger(__name__)


class Downloader(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(object)

    def __init__(self, client: Client, updater=None):
        super().__init__()
        self._client = client
        self._updater = updater
        self._client.add_progress_hook(self._progress)

    def run(self):  # A slot takes no params
        downloaded = self._updater.download()
        if downloaded:
            self.finished.emit(0)
        else:
            self.finished.emit(-1)

    def _progress(self, info):
        self.progress.emit(info)


class UpdateDialog(QtWidgets.QDialog, Ui_updateDialog):
    """
    Диалоговое окно для установки обновлений
    """

    def __init__(self, downloader: Downloader, parent: QtWidgets = None):
        super().__init__(parent)
        self._downloader = downloader
        self.setupUi(self)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self._thread = QThread()
        self.updateButton.clicked.connect(self.update)
        self.discardButton.clicked.connect(self.ignore)
        self.updatePercentLcdNumber.setPalette(QPalette(QColor(100, 100, 100)))

    def setupUi(self, InputDialog):
        super().setupUi(self)

    def update(self) -> None:
        self.updateButton.setEnabled(False)
        self._downloader.moveToThread(self._thread)
        self._thread.started.connect(self._downloader.run)
        self._downloader.finished.connect(self._finished)
        self._downloader.progress.connect(self._progress)
        self._thread.start()

    def ignore(self) -> None:
        self._thread.terminate()
        self.reject()

    def _finished(self):
        super().accept()

    def _progress(self, info):
        self.updatesLabel.setText(f"{info['status']}: {info['downloaded']} bytes from {info['total']}")
        self.updateProgressBar.setValue(int(float(info['percent_complete'])) * 10)
        self.updatePercentLcdNumber.display(info['percent_complete'])
        self.statusLabel.setText(f"Estimated time {info['time']}")
        print('Info', info)
