import datetime
import uuid

from PyQt5 import QtNetwork, QtCore
from PyQt5.QtCore import QObject, pyqtSignal

from models import Query


class QueryRequestInfo(QObject):
    def __init__(self, query, request):
        super().__init__()
        self.request = request
        self.query = query
        self.time = datetime.datetime.now()
        self.uuid = uuid.uuid4()

    def __str__(self):
        return self.query


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
    querySentSignal = pyqtSignal(int, object, object)
    queryDoneSignal = pyqtSignal(int, object, object, object)

    queryRequests = dict()

    def _create_query_request(self, query):
        query_params = ''
        for param in query.params:
            query_params += '&' + param.name + (
                '=' + param.value if param.value is not None and len(param.value) > 0 else '')
        url = self._make_url('/api/docs/query?id=' + str(query.id)) + query_params
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        req_info = QueryRequestInfo(query=query, request=req)
        req.setOriginatingObject(req_info)
        self.queryRequests[req_info.uuid] = req_info
        return req_info

    def _destroy_query_request(self, req_info):
        del self.queryRequests[req_info.uuid]

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
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(self._make_url(uri)))
        self._nam.finished.connect(self.handle_get)
        self._nam.get(req)

    def handle_get(self, reply):
        self._nam.finished.disconnect(self.handle_get)
        err = reply.error()
        if err == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            self.getDoneSignal.emit(err, str(bytes_string, 'utf-8'))
        else:
            self.getDoneSignal.emit(err, reply.errorString())

    def send_query(self, query: Query):
        req_info = self._create_query_request(query)
        self._nam.finished.connect(self.query_done)
        self._nam.get(req_info.request)
        self.querySentSignal.emit(0, req_info.uuid, req_info.query)

    def query_done(self, reply):
        self._nam.finished.disconnect(self.query_done)
        req_info = reply.request().originatingObject()
        err = reply.error()
        if err == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            self.queryDoneSignal.emit(err, req_info.uuid, req_info.query, str(bytes_string, 'utf-8'))
        else:
            self.queryDoneSignal.emit(err, req_info.uuid, req_info.query, reply.errorString())
        self._destroy_query_request(req_info)
