from PyQt5.QtCore import pyqtSignal, QObject

from network import Session


class Globals():
    """
    Класс глобальных переменных, которые должны бать доступны из любого места приложения
    """
    # Api urls
    QUERY_API = '/api/docs/query'
    FOLDERS_API = '/api/docs/tree'
    NCI_API = '/api/nci'
    # Session with server for using in all app modules
    session = Session('http://127.0.0.1:8000', 'goodok')
    # Nci dict like name -> pandas table
    nci = {
        'stations': None,
        'roads': None,
    }
