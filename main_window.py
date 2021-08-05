import json
import sys

from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTreeWidgetItem, QToolButton, QPushButton

from folders_tree import FoldersTreeModel
from globals import Globals
from login import LoginDialog
from models import Query, Folder, QueryTreeItem, FolderTreeItem
from ui.main_window import Ui_MainWindow
import qtawesome as qta


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.login_dialog = LoginDialog()
        if ( not self.login_dialog.exec() ):
            sys.exit(0)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super().setupUi(self)
        # init menu actions
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        # init widgets
        # self.foldersTreeModel = FoldersTreeModel()
        # self.foldersTreeModel.filledSignal.connect(self._tree_filled)
        self._fill_tree()
        self.foldersTreeWidget.customContextMenuRequested.connect(self._folders_tree_context_menu)
        Globals.session.queryDoneSignal.connect(self.answer_received)

    def answer_received(self, err, query, answer):
        print('Received answer for', query, 'with error code', err)
        print(answer)

    def _folders_tree_context_menu(self, point):
        index = self.foldersTreeWidget.indexAt(point)
        if not index.isValid():
            return
        item = self.foldersTreeWidget.itemAt(point)
#        if isinstance(item, Folder):
#            print(item)
        if isinstance(item, Query):
#            print(item)
            menu = QtWidgets.QMenu()
            action = menu.addAction("Query")
            action.setIcon( qta.icon('fa5s.paper-plane', color='green'))
            action.triggered.connect(lambda x: self._send_query(item))
            menu.addSeparator()
            action = menu.addAction("Cancel")
            menu.exec_(self.foldersTreeWidget.mapToGlobal(point))

    def _send_query(self, query: Query):
        Globals.session.send_query(query)

    def _fill_tree(self):
        Globals.session.getDoneSignal.connect(self._handle_fill)
        Globals.session.get('/api/docs/tree')

    def _makeItem(self, folderItem, folder, level=0):
        folderItem.setData(1, 0, Folder(folder))
        folderItem.setText(0, folder['name'])
        folderItem.setIcon(0, qta.icon('fa5s.folder', color='orange'))
        for subfolder in folder['folders']:
            subFolderItem = FolderTreeItem(subfolder)
            item = self._makeItem(subFolderItem, subfolder, level + 1)
            folderItem.addChild(item)
        for query in folder['queries']:
            item = QueryTreeItem(query)
            item.setText(0, query['name'])
            item.setIcon(0, qta.icon('fa5s.share-square', color='blue'))
            button = QToolButton()
            button.setMaximumSize(button.sizeHint())
            self.foldersTreeWidget.setItemWidget(item, 1, button)
            folderItem.addChild(item)
        return folderItem

    def _handle_fill(self, err, message):
        Globals.session.getDoneSignal.disconnect(self._handle_fill)
        if err == QtNetwork.QNetworkReply.NoError:
            json_tree = json.loads(message)
            for folder in json_tree['folders']:
                folderItem = FolderTreeItem(folder=folder, widget=self.foldersTreeWidget)
                item = self._makeItem(folderItem, folder)
                folderItem.addChild(item)
        else:
            print("Error occured: ", err, message)
