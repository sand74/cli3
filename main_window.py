import datetime
import json
import sys

import pandas as pd
import qtawesome as qta
from PyQt5 import QtWidgets, QtNetwork, QtGui
from PyQt5.QtCore import QSettings, QCoreApplication, pyqtSignal
from PyQt5.QtWidgets import QApplication, QToolButton, QTableWidgetItem, QTableWidget, QHeaderView
from django.core.serializers import deserialize

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
        self.readSettings()
        # init actions
        # init menu actions
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        # init query actions
        Globals.session.answerReceivedSignal.connect(self.answer_received)
        Globals.session.requestSentSignal.connect(self.insert_request)
        Globals.session.requestDoneSignal.connect(self.update_request)

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

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.writeSettings()
        super(MainWindow, self).closeEvent(a0)

    def writeSettings(self):
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.beginGroup(self.__class__.__name__)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.endGroup()

    def readSettings(self):
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.beginGroup(self.__class__.__name__)
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        if settings.contains("windowState"):
            self.restoreState(settings.value("windowState"))
        settings.endGroup()

    def get_window_list(self):
        sub_windows = self.mdiArea.subWindowList()
        for sub_window in sub_windows:
            print(sub_window.windowTitle())

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
        found = False
        for idx in range(self.requestTableWidget.rowCount()):
            item = self.requestTableWidget.item(idx, 1)
            if item.text() == str(request.uuid):
                found = True
                break
        if found:
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

    def answer_received(self, request: Request) -> None:
        print(request.uuid, '- Received answer for', request.query, 'with error code', request.error)
        if request.error == 0:
            print('Answer', request.answer)
            window = None
            if request.query.type == 'table':
                window = TableWindow(request)
            else:
                window = TableWindow(request)
            self.mdiArea.addSubWindow(window)
            window.show()

        self.get_window_list()

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
        err, message = Globals.session.get(f'{Globals.QUERY_API}?id={query.id}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_query = json.loads(message)
            query = Query(json_query)
        if query.has_in_params():
            input_dialog = InputDialog(query, self)
            input_dialog.setModal(True)
            input_dialog.show()
        else:
            Globals.session.send_query(query)
        return query

    def _fill_tree(self):
        self.foldersTreeWidget.clear()
        #        Globals.session.getDoneSignal.connect(self._handle_fill)
        err, message = Globals.session.get(f'{Globals.FOLDERS_API}')
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

