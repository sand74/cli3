from PyQt5.QtCore import pyqtSignal, QObject

from network import Session


class Globals():
    """
    Класс глобальных переменных, которые должны бать доступны из любого места приложения
    """
    QUERY_API = '/api/docs/query'
    FOLDERS_API = '/api/docs/tree'

    session = Session('http://127.0.0.1:8000', 'goodok')

    nci = {
        'stations': None,
        'roads': None,
    }
