import json
import sys

import pandas as pd
import qtawesome as qta
from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtWidgets import QApplication, QToolButton

from globals import Globals
from input_dialog import InputDialog
from login import LoginDialog
from models import Query, Folder, QueryTreeItem, FolderTreeItem, QueryListItem, RequestTableModel
from network import RequestInfo
from table import TableWindow
from ui.main_window import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    Главное окно приложения
    """
    def __init__(self):
        super().__init__()
        self.login_dialog = LoginDialog()
        if (not self.login_dialog.exec()):
            sys.exit(0)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super().setupUi(self)
        # init widgets
        self.setupNav()
        self.setupLog()
        # init actions
        # init menu actions
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        # init query actions
        Globals.session.querySentSignal.connect(self.query_sent_handler)
        Globals.session.queryDoneSignal.connect(self.query_done_handler)
        Globals.session.queryDoneSignal.connect(self.answer_received)

    def setupNav(self):
        self.refreshFoldersButton.setIcon(qta.icon('fa5s.sync', color='green'))
        self.refreshFoldersButton.clicked.connect(self._fill_tree)
        self._fill_tree()
        # init folders tree actions
        self.foldersTreeWidget.customContextMenuRequested.connect(self._folders_tree_context_menu)
        self.foldersTreeWidget.itemDoubleClicked.connect(self._folders_tree_dbl_click)

    def setupLog(self):
        self.requestTableModel = RequestTableModel()
        self.requestTableView.setModel(self.requestTableModel)

    def query_sent_handler(self, request: RequestInfo) -> None:
        print(request.uuid, '- Query sent', request.query, 'with error code', request.error)
#        item = QueryListItem(query=request.query, uuid=request.uuid)
#        item.setText(request.query.name)
#        item.setIcon(qta.icon('fa5s.spinner', color='green'))
#        self.queriesListWidget.insertItem(0, item)
        self.requestTableModel.insert(request)


    def query_done_handler(self, request: RequestInfo) -> None:
        print(request.uuid, '- Query done', request.query, 'with error code', request.error)
 #       for i in range(self.queriesListWidget.count()):
 #           item = self.queriesListWidget.item(i)
 #           if item.uuid == request.uuid:
 #               if request.error == 0:
 #                   item.setIcon(qta.icon('fa5s.check-double', color='blue'))
 #               else:
 #                   item.setIcon(qta.icon('fa5s.skull-crossbones', color='red'))
 #               #                self.queriesListWidget.takeItem(i)
 #               break
        self.requestTableModel.update(request)

    def answer_received(self, request: RequestInfo) -> None:
        print(request.uuid, '- Received answer for', request.query, 'with error code', request.error)
        if request.error == 0:
            json_answer = json.loads(request.answer)
            for attribute, value in json_answer.items():
                if value['type'] == 'cursor':
                    columns = [column['name'] for column in value['columns']]
                    data = value['data']
                    df = pd.DataFrame(data=data, columns=columns)
                    table_window = TableWindow(df)
                    table_window.setWindowTitle(request.query.name)
                    self.mdiArea.addSubWindow(table_window)
                    table_window.show()

    def _folders_tree_context_menu(self, point):
        index = self.foldersTreeWidget.indexAt(point)
        if not index.isValid():
            return
        item = self.foldersTreeWidget.itemAt(point)
        if isinstance(item, QueryTreeItem):
            menu = QtWidgets.QMenu()
            action = menu.addAction("Query")
            action.setIcon(qta.icon('fa5s.paper-plane', color='green'))
            action.triggered.connect(lambda x: self._send_query(item.query))
            menu.addSeparator()
            action = menu.addAction("Cancel")
            menu.exec_(self.foldersTreeWidget.mapToGlobal(point))

    def _folders_tree_dbl_click(self, item):
        if isinstance(item, QueryTreeItem):
            self._send_query(item.query)

    def _send_query(self, query: Query):
        print('Query', query)
        if query.has_in_params():
            input_dialog = InputDialog(query, self)
            input_dialog.setModal(True)
            input_dialog.show()
        else:
            Globals.session.send_query(query)

    def _fill_tree(self):
        self.foldersTreeWidget.clear()
        Globals.session.getDoneSignal.connect(self._handle_fill)
        Globals.session.get('/api/docs/tree')

    def _makeItem(self, folderItem, folder, level=0):
        for subfolder in folder['folders']:
            subFolderItem = FolderTreeItem(Folder(subfolder))
            item = self._makeItem(subFolderItem, subfolder, level + 1)
            folderItem.addChild(item)
        for query in folder['queries']:
            item = QueryTreeItem(Query(query))
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
                folderItem = FolderTreeItem(folder=Folder(folder), widget=self.foldersTreeWidget)
                item = self._makeItem(folderItem, folder)
                folderItem.addChild(item)
        else:
            print("Error occured: ", err, message)
