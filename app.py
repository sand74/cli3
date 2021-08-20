import typing

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from network import Session
import qtawesome as qta


class Cli3App(QApplication):
    updateMainWindiwSignal = pyqtSignal()
    # Nci dict like name -> pandas table
    nci = dict()
    # Styles dict
    styles = dict()

    def __init__(self, argv: typing.List[str]):
        super().__init__(argv)
        self.setApplicationName('Cli3')
        self.setOrganizationName('ICS')
        self.setApplicationVersion('1.1.1')
        self.session = Session('http://127.0.0.1:8000', 'goodok')
        self._load_icons()

    def _load_icons(self):
        self.icons = {
            'sync': qta.icon('fa5s.sync'),
            'open': qta.icon('fa5.folder-open', color='orange'),
            'save': qta.icon('fa5.save'),
            'refresh': qta.icon('mdi.table-sync'),
            'error': qta.icon('fa5.times-circle', color='red'),
            'success': qta.icon('fa5.check-circle', color='green'),
            'table': qta.icon('mdi.file-table'),
            'send': qta.icon('mdi.send-circle'),
            'filter': qta.icon('fa.filter'),
            'folder_close': qta.icon('ei.folder-close', color='orange'),
            'folder_open': qta.icon('ei.folder-open', color='orange'),
            'file': qta.icon('fa5s.file', color='blue'),
        }
