import pathlib
import configparser
import pathlib
import typing

import qtawesome as qta
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from network import Session


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
        path = pathlib.Path(__file__).parent.resolve()
        config = self._read_config(str(path) + '/cli3.ini')
        default_section = config['DEFAULT']
        self.session = Session(f"http://{default_section.get('server')}:{default_section.get('port')}",
                               default_section.get("schema"))
        self._load_icons()

    def _read_config(self, filename):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'server': '127.0.0.1',
            'port': 8000,
            'schema': 'common',
        }
        config.read(filename)
        return config

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
            'print': qta.icon('fa.print'),
            'excel': qta.icon('fa5.file-excel'),
            'pdf': qta.icon('fa5.file-pdf'),
        }
