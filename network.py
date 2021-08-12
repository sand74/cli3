import uuid
from threading import Lock

from PyQt5 import QtNetwork, QtCore
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop

from models import Query


class NetworkException(Exception):
    def __init__(self, err: int, message: str):
        self.__init__(f"Network error {err} - {message}")


class Request(QObject):
    """
    Класс запроса по http
    """
    getDoneSignal = pyqtSignal(object)

    def __init__(self, query: Query, params: dict = None):
        super().__init__()
        self.uuid = uuid.uuid4()
        self.query = query
        self.params = params
        self.error = 0
        self.answer = None

    def send_get(self, nam: QtNetwork.QNetworkAccessManager, base_url):
        self.url = base_url + '?' + self.query.make_request(params=self.params)
        print('Send query', self.url)
        self.request = QtNetwork.QNetworkRequest(QtCore.QUrl(self.url))
        self.reply = nam.get(self.request)
        self.reply.finished.connect(self.get_done)

    def get_done(self):
        self.reply.finished.disconnect(self.get_done)
        self.error = self.reply.error()
        if self.error == QtNetwork.QNetworkReply.NoError:
            bytes = self.reply.readAll()
            self.answer = bytes.data().decode()
        else:
            self.answer = self.reply.errorString()
        print('Reqceive answer', self.answer)
        self.getDoneSignal.emit(self)

    def __str__(self):
        return self.query.name

class Session(QObject):
    """
    Класс дла хранения сессии связи с сервером профилей пользователей
    """
    _nam = QtNetwork.QNetworkAccessManager()
    LOGIN_URL = '/api/auth/signin'
    LOGOUT_URL = '/api/auth/logout'
    loggedInSignal = pyqtSignal(int, str)
    loggedOutSignal = pyqtSignal(int, str)
    getDoneSignal = pyqtSignal(int, str)
    querySentSignal = pyqtSignal(object)
    queryDoneSignal = pyqtSignal(object)

    loop = QEventLoop()

    query_lock = Lock()

    requests = dict()

    def _make_url(self, path):
        return self._server + self._schema + path

    # server like http://host:port
    def __init__(self, server, schema):
        super().__init__()
        self._server = server if server.endswith('/') else server + '/'
        self._schema = schema[:-1] if schema.endswith('/') else schema

    def login(self, username, password):
        uri = f'{self.LOGIN_URL}?username={username}&password={password}'
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(self._make_url(uri)))
        self._nam.finished.connect(self.handle_login)
        self._nam.get(req)

    def handle_login(self, reply):
        self._nam.finished.disconnect(self.handle_login)
        err = reply.error()
        if err == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            self.loggedInSignal.emit(err, str(bytes_string, 'utf-8'))
        else:
            self.loggedInSignal.emit(err, reply.errorString())

    def logout(self):
        uri = f'{self.LOGOUT_URL}'
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(self._make_url(uri)))
        self._nam.finished.connect(self.handle_logout)
        self._nam.get(req)

    def handle_logout(self, reply):
        self._nam.finished.disconnect(self.handle_logout)
        err = reply.error()
        if err == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            self.loggedOutSignal.emit(err, str(bytes_string, 'utf-8'))
        else:
            self.loggedOutSignal.emit(err, reply.errorString())

    def get(self, uri):
        with(self.query_lock):
            req = QtNetwork.QNetworkRequest(QtCore.QUrl(self._make_url(uri)))
            self._nam.finished.connect(self.loop.quit)
            reply = self._nam.get(req)
            self.loop.exec_()
            self._nam.finished.disconnect(self.loop.quit)
            err = reply.error()
            if err == QtNetwork.QNetworkReply.NoError:
                bytes = reply.readAll()
                return err, bytes.data().decode()
            else:
                return err, reply.errorString()

    def send_query(self, query: Query, params: dict = None):
        with(self.query_lock):
            request = Request(query=query, params=params)
            self.requests[request.uuid] = request
            request.getDoneSignal.connect(self.query_done)
            request.send_get(self._nam, self._make_url('/api/docs/query'))
            self.querySentSignal.emit(request)

    def query_done(self, request: Request):
        with(self.query_lock):
            self.queryDoneSignal.emit(request)
            if request.uuid in self.requests.keys():
                del self.requests[request.uuid]
