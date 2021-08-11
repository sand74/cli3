import datetime
import json
import sys

import pandas as pd
import qtawesome as qta
from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtWidgets import QApplication, QToolButton, QTableWidgetItem, QTableWidget, QHeaderView

from globals import Globals
from input_dialog import InputDialog
from login import LoginDialog
from models import Query, Folder, QueryTreeItem, FolderTreeItem
from network import Request
from table import TableWindow
from ui.main_window import Ui_MainWindow


class RequestTableColumns:
    STATUS = (0, 'sent')
    UUID = (1, 'uuid')
    QUERY = (2, 'query')
    SENT = (3, 'sent')
    DONE = (4, 'done')
    ERROR = (5, 'error')
    INFO = (6, 'info')


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
        self.requestTableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.requestTableWidget.horizontalHeaderItem(RequestTableColumns.STATUS[0]).setText('')
        self.requestTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def insert_request(self, request: Request):
        self.requestTableWidget.insertRow(0)
        status_widget = qta.IconWidget()
        spin_icon = qta.icon('fa5s.spinner', color='green', animation=qta.Spin(status_widget))
        status_widget.setIcon(spin_icon)
        self.requestTableWidget.setCellWidget(0, RequestTableColumns.STATUS[0], status_widget)
        self.requestTableWidget.setItem(0, RequestTableColumns.UUID[0],
                                        QTableWidgetItem(str(request.uuid)))
        self.requestTableWidget.setItem(0, RequestTableColumns.QUERY[0],
                                        QTableWidgetItem(str(request.query.name)))
        self.requestTableWidget.setItem(0, RequestTableColumns.SENT[0],
                                        QTableWidgetItem(str(datetime.datetime.now())))
        self.requestTableWidget.resizeColumnsToContents()

    def update_request(self, request: Request):
        item = None
        idx = 0
        for idx in range(self.requestTableWidget.rowCount()):
            item = self.requestTableWidget.item(idx, 1)
            if item.text() == str(request.uuid):
                break
        if item is not None:
            self.requestTableWidget.setItem(idx, RequestTableColumns.DONE[0],
                                            QTableWidgetItem(str(datetime.datetime.now())))
            self.requestTableWidget.setItem(idx, RequestTableColumns.ERROR[0],
                                            QTableWidgetItem(str(request.error)))
            status_widget = self.requestTableWidget.cellWidget(idx, RequestTableColumns.STATUS[0])
            if request.error == 0:
                status_widget.setIcon(qta.icon('fa5s.check', color='blue'))
                self.requestTableWidget.setItem(idx, RequestTableColumns.INFO[0],
                                                QTableWidgetItem(f'{len(request.answer)} bytes received'))
            else:
                status_widget.setIcon(qta.icon('fa5s.skull-crossbones', color='red'))
                self.requestTableWidget.setItem(idx, RequestTableColumns.INFO[0],
                                                QTableWidgetItem(str(request.answer)))
            self.requestTableWidget.resizeColumnsToContents()

    def query_sent_handler(self, request: Request) -> None:
        print(request.uuid, '- Query sent', request.query, 'with error code', request.error)
        self.insert_request(request)

    def query_done_handler(self, request: Request) -> None:
        print(request.uuid, '- Query done', request.query, 'with error code', request.error)
        self.update_request(request)

    def answer_received(self, request: Request) -> None:
        print(request.uuid, '- Received answer for', request.query, 'with error code', request.error)
        if request.error == 0:
            print('Answer', request.answer)
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
        #        Globals.session.getDoneSignal.connect(self._handle_fill)
        err, message = Globals.session.get('/api/docs/tree')
        if err == QtNetwork.QNetworkReply.NoError:
            json_tree = json.loads(message)
            for folder in json_tree['folders']:
                folderItem = FolderTreeItem(folder=Folder(folder), widget=self.foldersTreeWidget)
                item = self._makeItem(folderItem, folder)
                folderItem.addChild(item)
        else:
            print("Error occured: ", err, message)

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
