import json

import requests as requests
from PyQt5 import QtNetwork, QtCore
from PyQt5.QtCore import QModelIndex, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon
from PyQt5.QtWidgets import QTreeView
import qtawesome as qta

from globals import Globals


class FoldersTreeModel(QStandardItemModel):
    '''
    Вариант представления списка запросов в виде дерева
    '''
    filledSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        url = f'http://127.0.0.1:8000/common/api/docs/tree'
        Globals.session.getDoneSignal.connectNotyfy(self._handle_fill)
        Globals.session.get('/api/docs/tree')

    def _makeItem(self, folder, level=0):
        folderItem = QStandardItem(folder['name'])
        folderItem.setEditable(False)
        folderItem.setData(folder)
        print(QIcon.themeSearchPaths())
        folderItem.setIcon(qta.icon('fa5s.folder', color='orange'))
        for subfolder in folder['folders']:
            item = self._makeItem(subfolder, level + 1)
            folderItem.appendRow(item)
        for query in folder['queries']:
            item = QStandardItem(query['name'])
            item.setEditable(False)
            item.setData(query)
            item.setIcon(qta.icon('fa5s.share-square', color='blue'))
            folderItem.appendRow(item)
        return folderItem

    def _handle_fill(self, err, message):
        Globals.session.getDoneSignal.disconnect(self._handle_fill)
        self.setColumnCount(1)
        if err == QtNetwork.QNetworkReply.NoError:
            json_tree = json.loads(message)
            for folder in json_tree['folders']:
                item = self._makeItem(folder)
                self.appendRow(item)
            self.filledSignal.emit(0)
        else:
            print("Error occured: ", err, message)
            self.filledSignal.emit(err)

