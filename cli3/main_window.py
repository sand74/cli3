import json
import json
import pickle
import sys
from functools import partial

from PyQt5 import QtWidgets, QtNetwork, QtGui
from PyQt5.QtCore import QSettings, QCoreApplication, pyqtSignal
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QApplication, QMdiArea, \
    QFileDialog, QMenu, QAction, QMessageBox, QDialog

from cli3.app import Cli3App
from cli3.input_dialog import InputDialog
from cli3.log_view import LogPane
from cli3.login import LoginDialog
from cli3.mdi_window import MdiWindow
from cli3.models import Query
from cli3.navigator import QueryTreeItem, NavigatorPane, FolderTreeItem
from cli3.network import Request
from cli3.series_window import SeriesWindow
from cli3.table_window import TableWindow
from cli3.text_window import TextWindow
from ui.main_window import Ui_MainWindow


def show_eror(error_text, e: Exception):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(error_text)
    msg.setInformativeText(e)
    msg.setWindowTitle("Error")
    msg.setDetailedText(e)


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
        self.navDockWidget.visibilityChanged.connect(self._update_actions)
        self.logDocWidget.visibilityChanged.connect(self._update_actions)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super().showEvent(a0)
        self._update_actions()

    def setupUi(self, MainWindow):
        super().setupUi(self)
        self.read_settings()
        # init widgets
        self.navigatorPane = NavigatorPane(self)
        self.navDockWidget.setWidget(self.navigatorPane)
        self.navigatorPane.sendRequestSignal.connect(self._send_query)
        self.logPane = LogPane(self)
        self.logDocWidget.setWidget(self.logPane)
        # init actions
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        self.actionOpen.setIcon(Cli3App.instance().icons.get('open'))
        self.actionOpen.triggered.connect(self._open_answer)
        self.actionSave.setIcon(Cli3App.instance().icons.get('save'))
        self.actionSave.triggered.connect(self._save_answer)
        self.actionFilter.setIcon(Cli3App.instance().icons.get('filter'))
        self.actionFilter.triggered.connect(self._set_filter)
        self.actionRefresh.setIcon(Cli3App.instance().icons.get('refresh'))
        self.actionRefresh.triggered.connect(self._refresh)
        self.actionNavigator.triggered.connect(self._invert_nav_visable)
        self.actionLog.triggered.connect(self._invert_log_visable)
        self.actionUpdateFolders.setIcon(Cli3App.instance().icons.get('sync'))
        self.actionUpdateFolders.triggered.connect(self.navigatorPane.fill_contents)
        self.actionPrint.setIcon(Cli3App.instance().icons.get('print'))
        self.actionPrint.triggered.connect(self._print_answer)
        self.actionToExcel.setIcon(Cli3App.instance().icons.get('excel'))
        self.actionToExcel.triggered.connect(self._export_answer_to_excel)
        self.actionToPdf.setIcon(Cli3App.instance().icons.get('pdf'))
        self.actionToPdf.triggered.connect(self._export_answer_to_pdf)
        # Menu
        self.menuWindow.aboutToShow.connect(self._update_window_list)
        self._create_query_menu()
        # Toolbar
        self._fill_toolbar()
        Cli3App.instance().session.answerReceivedSignal.connect(self.answer_received)

    def _create_query_menu(self):
        self.menuQuery.clear()
        self._query_menus = []
        model = self.navigatorPane.navTreeView.model()
        for folder in model.folders():
            menu = self._create_sub_menu(folder)
            menu.setIcon(Cli3App.instance().icons['folder_close'])
            self.menuQuery.addMenu(menu)
            self._query_menus.append(menu)

    def _create_sub_menu(self, folder: FolderTreeItem):
        menu = QMenu(folder.folder().name)
        for i in range(folder.child_count()):
            if isinstance(folder.child(i), FolderTreeItem):
                sub_menu = self._create_sub_menu(folder.child(i))
                sub_menu.setIcon(Cli3App.instance().icons['folder_close'])
                menu.addMenu(sub_menu)
                self._query_menus.append(sub_menu)
            elif isinstance(folder.child(i), QueryTreeItem):
                query = folder.child(i).query()
                action = QAction(self)
                action.setText(query.name)
                action.setIcon(Cli3App.instance().icons['file'])
                action.triggered.connect(partial(self._send_query, query))
                menu.addAction(action)

        return menu

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
        self.actionSave.setEnabled(active_sub_window is not None)
        self.actionFilter.setEnabled(False)
        self.actionRefresh.setEnabled(False)
        self.actionToExcel.setEnabled(False)
        self.actionToPdf.setEnabled(False)
        self.actionPrint.setEnabled(False)
        if active_sub_window is not None:
            sub_widget = active_sub_window.widget()
            if isinstance(sub_widget, MdiWindow):
                has_filter = sub_widget.has_filter()
                if has_filter is not None:
                    self.actionFilter.setEnabled(True)
                    self.actionFilter.setChecked(has_filter)
                else:
                    self.actionFilter.setEnabled(False)
                    self.actionFilter.setChecked(False)
                is_locked = sub_widget.is_locked()
                self.actionRefresh.setEnabled(not is_locked)
                self.actionToExcel.setEnabled(
                    hasattr(sub_widget, 'to_excel') and callable(getattr(sub_widget, 'to_excel')))
                self.actionToPdf.setEnabled(
                    hasattr(sub_widget, 'to_pdf') and callable(getattr(sub_widget, 'to_pdf')))
                self.actionPrint.setEnabled(
                    hasattr(sub_widget, 'print') and callable(getattr(sub_widget, 'print')))

    def _fill_toolbar(self):
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionPrint)
        self.toolBar.addAction(self.actionToExcel)
        self.toolBar.addAction(self.actionToPdf)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionUpdateFolders)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionFilter)
        self.toolBar.addAction(self.actionRefresh)

    def _save_answer(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), MdiWindow):
            filename = QFileDialog.getSaveFileName(self, 'Save to ...')[0]
            if filename is not None and len(filename) > 0:
                window.widget().save(filename)

    def _print_answer(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), MdiWindow):
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            dialog.setWindowTitle("Print Document")
            if (dialog.exec() == QDialog.Accepted):
                window.widget().print(printer)

    def _export_answer_to_pdf(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), MdiWindow):
            filename = QFileDialog.getSaveFileName(self, 'Export pdf to ...')[0]
            if filename is not None and len(filename) > 0:
                window.widget().to_pdf(filename)

    def _export_answer_to_excel(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), MdiWindow):
            filename = QFileDialog.getSaveFileName(self, 'Export excel to ...')[0]
            if filename is not None and len(filename) > 0:
                window.widget().to_excel(filename)

    def _open_answer(self):
        filename = QFileDialog.getOpenFileName(self, 'Open')[0]
        if filename is not None and len(filename) > 0:
            with open(filename, 'rb') as inp:
                try:
                    request = pickle.load(inp)
                    self.answer_received(request)
                except Exception as e:
                    show_eror('Can not open answer', e)

    def _set_filter(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), MdiWindow):
            window.widget().set_filter()

    def _refresh(self):
        window = self.mdiArea.activeSubWindow()
        if window is not None and isinstance(window.widget(), MdiWindow):
            window.widget().refresh()

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

    def answer_received(self, request: Request) -> None:
        """
        Show received answer
        :param request: Done request
        :return:
        """
        if request.error == 0:
            if request.query.type == 'TABLE':
                window = TableWindow(self.mdiArea)
                window.set_request(request=request)
            elif request.query.type == 'SERIES':
                window = SeriesWindow(self.mdiArea)
                window.set_request(request=request)
            elif request.query.type == 'TEXT':
                window = TextWindow(self.mdiArea)
                window.set_request(request=request)
            else:
                window = TableWindow(self.mdiArea)
                window.set_request(request=request)
            self.mdiArea.addSubWindow(window).show()

    def _send_query(self, query: Query) -> Query:
        """
        Send query
        :param query: Query for send
        :return: Query from server
        """
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
