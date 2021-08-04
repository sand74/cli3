import requests as requests
from PyQt5 import QtNetwork, QtCore
from PyQt5.QtWidgets import QTreeView


class FoldersTree(QTreeView):
    '''
    Вариант представления списка запросов в виде дерева
    '''
    def __init__(self, parent=None, net_manager=None):
        super().__init__(parent)
        self.nam = net_manager
        url = f'http://127.0.0.1:8000/common/api/docs/tree'
#        result = requests.get(url)
#        print(result)
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        self.nam.authenticationRequired.connect(self.authenticate)
        self.nam.finished.connect(self.handleFill)
        self.nam.get(req)

    def authenticate(self, reply, auth):

        print('Authenticating')

        self.auth += 1

        if self.auth >= 3:
            reply.abort()

        auth.setUser('sand')
        auth.setPassword('twister')


    def handleFill(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
        else:
            print("Error occured: ", er)

