from network import Session


class Globals():
    """
    Класс глобальных переменных, которые должны бать доступны из любого места приложения
    """
    session = Session('http://127.0.0.1:8000', 'goodok')

    nci = {
        'stations': None,
        'roads': None,
    }
