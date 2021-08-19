import datetime
import json
import sys
from functools import partial

import qtawesome as qta
from PyQt5 import QtWidgets, QtNetwork, QtGui
from PyQt5.QtCore import QSettings, QCoreApplication, pyqtSignal
from PyQt5.QtWidgets import QApplication, QToolButton, QTableWidgetItem, QTableWidget, QHeaderView, QMdiArea, \
    QFileDialog, QTreeWidgetItem

from app import Cli3App
from input_dialog import InputDialog
from login import LoginDialog
from models import Query, Folder
from network import Request
from table import TableWindow, Cli3WindowMixin
from ui.main_window import Ui_MainWindow


class RequestTableColumns:
    STATUS = (0, 'sent')
    UUID = (1, 'uuid')
    QUERY = (2, 'query')
    SENT = (3, 'sent')
    DONE = (4, 'done')
    ERROR = (5, 'error')
    INFO = (6, 'info')


class FolderTreeItem(QTreeWidgetItem):
    """
    модель папки для отображения в дереве
    """

    def __init__(self, folder: Folder, widget: QTreeWidgetItem = None):
        super(FolderTreeItem, self).__init__(widget)
        self._folder = folder
        self.setText(0, folder.name)
        self.setIcon(0, Cli3App.instance().icons.get('folder'))

    @property
    def folder(self):
        return self._folder


class QueryTreeItem(QTreeWidgetItem):
    """
    модель запрося для отображения в дереве
    """

    def __init__(self, query):
        super().__init__()
        self._query = query
        self.setText(0, query.name)
        self.setIcon(0, Cli3App.instance().icons.get('file'))

    @property
    def query(self):
        return self._query


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    Главное окно приложения
    """
    updateActionsSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.login_dialog = LoginDialog()
        if not self.login_dialog.exec():
            sys.exit(0)
        self.setupUi(self)
        self.mdiArea.subWindowActivated.connect(self._update_actions)
        self.tabifiedDockWidgetActivated.connect(self._update_actions)
        Cli3App.instance().updateMainWindiwSignal.connect(self._update_actions)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super().showEvent(a0)
        self._update_actions()

    def setupUi(self, MainWindow):
        super().setupUi(self)
        self.read_settings()
        # init actions
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        self.actionOpen.setIcon(Cli3App.instance().icons.get('open'))
        self.actionOpen.triggered.connect(self._open_answer)
        self.actionSave.setIcon(Cli3App.instance().icons.get('save'))
        self.actionSave.triggered.connect(self._save_answer)
        self.actionFilter.setIcon(Cli3App.instance().icons.get('filter'))
        self.actionFilter.triggered.connect(self._save_answer)
        self.actionRefresh.setIcon(Cli3App.instance().icons.get('refresh'))
        self.actionRefresh.triggered.connect(self._save_answer)
        self.actionNavigator.triggered.connect(self._invert_nav_visable)
        self.actionLog.triggered.connect(self._invert_log_visable)
        # Menu
        self.menuWindow.aboutToShow.connect(self._update_window_list)
        # Toolbar
        self._fill_toolbar()
        # init widgets
        self.setup_nav_pane()
        self.setup_log_pane()
        # init query actions
        Cli3App.instance().session.answerReceivedSignal.connect(self.answer_received)
        Cli3App.instance().session.requestSentSignal.connect(self.insert_request)
        Cli3App.instance().session.requestDoneSignal.connect(self.update_request)

    def _update_window_list(self):
        self.menuWindow.clear()
        self.menuWindow.addAction(self.actionTile)
        self.actionTile.triggered.connect(partial(self.mdiArea.tileSubWindows))
        self.menuWindow.addAction(self.actionCascade)
        self.actionCascade.triggered.connect(partial(self.mdiArea.cascadeSubWindows))
        self.menuWindow.addSeparator()
        windows = self.mdiArea.subWindowList(QMdiArea.CreationOrder)
        for window in windows:
            action = QtWidgets.QAction(self)
            action.setCheckable(True)
            action.setChecked(window == self.mdiArea.activeSubWindow())
            self.menuWindow.addAction(action)
            action.setText(window.windowTitle())
            action.triggered.connect(partial(self.mdiArea.setActiveSubWindow, window))

    def _update_actions(self):
        self.actionNavigator.setChecked(self.navDockWidget.isVisible())
        self.actionLog.setChecked(self.logDocWidget.isVisible())
        active_sub_window = self.mdiArea.activeSubWindow()
        self.actionSave.setEnabled(active_sub_window != None)
        self.actionFilter.setEnabled(False)
        self.actionRefresh.setEnabled(False)
        if active_sub_window != None:
            if isinstance(active_sub_window.widget(), Cli3WindowMixin):
                self.actionRefresh.setEnabled(active_sub_window.widget().can_refresh())
                has_filter = active_sub_window.widget().has_filter()
                if has_filter is not None:
                    self.actionFilter.setEnabled(True)
                    self.actionFilter.setChecked(has_filter)
                else:
                    self.actionFilter.setEnabled(False)
                    self.actionFilter.setChecked(False)

    def _fill_toolbar(self):
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionFilter)
        self.toolBar.addAction(self.actionRefresh)

    def _save_answer(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), Cli3WindowMixin):
            filename = QFileDialog.getSaveFileName(self, 'Save to')[0]
            if filename is not None and len(filename) > 0:
                window.widget().save(filename)

    def _open_answer(self):
        filename = QFileDialog.getOpenFileName(self, 'Open')[0]
        if filename is not None and len(filename) > 0:
            window = TableWindow().load(filename)
            if window is not None:
                self.mdiArea.addSubWindow(window).show()

    def _invert_nav_visable(self):
        """
        Show/Hide navigator
        :return:
        """
        self.navDockWidget.setVisible(not self.navDockWidget.isVisible())

    def _invert_log_visable(self):
        """
        Show/Hide log
        :return:
        """
        self.logDocWidget.setVisible(not self.logDocWidget.isVisible())

    def setup_nav_pane(self) -> None:
        """
        Setup navigation floating pane
        TODO Перенести в отдельный класс все что связано с NavPane
        :return:
        """
        self.refreshFoldersButton.setIcon(Cli3App.instance().icons.get('sync'))
        self.refreshFoldersButton.clicked.connect(self._fill_tree)
        self._fill_tree()
        self.foldersTreeWidget.expandAll()
        # init folders tree actions
        self.foldersTreeWidget.customContextMenuRequested.connect(self._folders_tree_context_menu)
        self.foldersTreeWidget.itemDoubleClicked.connect(self._folders_tree_dbl_click)

    def setup_log_pane(self):
        """
        Setup Request Log floating Pane
        TODO Перенести в отдельный класс все что связано с LogPane
        :return:
        """
        self.requestTableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.requestTableWidget.horizontalHeaderItem(RequestTableColumns.STATUS[0]).setText('')
        self.requestTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        All to need before close
        :param a0:
        :return:
        """
        self.write_settings()
        super(MainWindow, self).closeEvent(a0)

    def write_settings(self) -> None:
        """
        Write main windows  Settings
        :return:
        """
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.beginGroup(self.__class__.__name__)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.endGroup()

    def read_settings(self) -> None:
        """
        Read main windows  Settings
        :return:
        """
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

    def insert_request(self, request: Request) -> None:
        """
        Add request info to log pane
        TODO Перенести в отдельный класс все что связано с LogPane
        :param request: Sent request
        :return:
        """
        self.requestTableWidget.insertRow(0)
        status_widget = qta.IconWidget()
        spin_icon = qta.icon('fa5s.spinner', color='blue', animation=qta.Spin(status_widget))
        status_widget.setIcon(spin_icon)
        self.requestTableWidget.setCellWidget(0, RequestTableColumns.STATUS[0], status_widget)
        self.requestTableWidget.setItem(0, RequestTableColumns.UUID[0],
                                        QTableWidgetItem(str(request.uuid)))
        self.requestTableWidget.setItem(0, RequestTableColumns.QUERY[0],
                                        QTableWidgetItem(str(request.query.name)))
        self.requestTableWidget.setItem(0, RequestTableColumns.SENT[0],
                                        QTableWidgetItem(str(datetime.datetime.now())))
        self.requestTableWidget.resizeColumnsToContents()

    def update_request(self, request: Request) -> None:
        """
        Update request info to log pane
        TODO Перенести в отдельный класс все что связано с LogPane
        :param request: Done request
        :return:
        """
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
                status_widget.setIcon(Cli3App.instance().icons.get('success'))
                self.requestTableWidget.setItem(idx, RequestTableColumns.INFO[0],
                                                QTableWidgetItem(f'{len(request.answer)} bytes received'))
            else:
                status_widget.setIcon(Cli3App.instance().icons.get('error'))
                self.requestTableWidget.setItem(idx, RequestTableColumns.INFO[0],
                                                QTableWidgetItem(str(request.answer)))
            self.requestTableWidget.resizeColumnsToContents()

    def answer_received(self, request: Request) -> None:
        """
        Show received answer
        :param request: Done request
        :return:
        """
        print(request.uuid, '- Received answer for', request.query, 'with error code', request.error)
        if request.error == 0:
            print('Answer', request.answer)
            if request.query.type == 'table':
                window = TableWindow()
                window.set_request(request=request)
            else:
                window = TableWindow()
                window.set_request(request=request)
            self.mdiArea.addSubWindow(window).show()

    def _folders_tree_context_menu(self, point) -> None:
        """
        Show context menu for Nav Tree
        TODO Перенести в отдельный класс все что связано с NavPane
        :param point:
        :return:
        """
        index = self.foldersTreeWidget.indexAt(point)
        if not index.isValid():
            return
        item = self.foldersTreeWidget.itemAt(point)
        if isinstance(item, QueryTreeItem):
            menu = QtWidgets.QMenu()
            action = menu.addAction("Query")
            action.setIcon(Cli3App.instance().icons.get('send'))
            action.triggered.connect(lambda x: self._send_query(item.query))
            menu.addSeparator()
            menu.addAction("Cancel")
            menu.exec_(self.foldersTreeWidget.mapToGlobal(point))

    def _folders_tree_dbl_click(self, item) -> None:
        """
        Double click on Nav Tree node
        TODO Перенести в отдельный класс все что связано с NavPane
        :return:
        """
        if isinstance(item, QueryTreeItem):
            self._send_query(item.query)

    def _send_query(self, query: Query) -> Query:
        """
        Send query
        :param query: Query for send
        :return: Query from server
        """
        print('Query', query)
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.QUERY_API}?id={query.id}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_query = json.loads(message)
            query = Query(json_query)
        if query.has_in_params():
            input_dialog = InputDialog(query, self)
            input_dialog.setModal(True)
            input_dialog.show()
        else:
            Cli3App.instance().session.send_query(query)
        return query

    def _fill_tree(self) -> None:
        """
        Fill Navigation Tree
        TODO Перенести в отдельный класс все что связано с NavPane
        :return:
        """
        self.foldersTreeWidget.clear()
        #        Globals.session.getDoneSignal.connect(self._handle_fill)
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.TREE_API}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_tree = json.loads(message)
            for folder in json_tree['folders']:
                folder_item = FolderTreeItem(folder=Folder(folder), widget=self.foldersTreeWidget)
                item = self._make_item(folder_item, folder)
                folder_item.addChild(item)
        else:
            print("Error occurred: ", err, message)

    def _make_item(self, parent_item: FolderTreeItem, folder: dict, level=0) -> FolderTreeItem:
        """
        Make Navigation Tree Item
        TODO Перенести в отдельный класс все что связано с NavPane
        :param parent_item: Parent tree item for folder
        :param folder: folder json
        :param level: Tree level
        :return:
        """
        for sub_folder in folder['folders']:
            sub_folder_item = FolderTreeItem(Folder(sub_folder))
            item = self._make_item(sub_folder_item, sub_folder, level + 1)
            parent_item.addChild(item)
        for query in folder['queries']:
            item = QueryTreeItem(Query(query))
            button = QToolButton()
            button.setMaximumSize(button.sizeHint())
            self.foldersTreeWidget.setItemWidget(item, 1, button)
            parent_item.addChild(item)
        return parent_item
