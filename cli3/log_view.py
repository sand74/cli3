import datetime

import qtawesome as qta
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QTableWidget, QHeaderView, QTableWidgetItem

from cli3.app import Cli3App
from cli3.network import Request
from ui.log_pane import Ui_logPane


class RequestTableColumns:
    STATUS = (0, 'sent')
    UUID = (1, 'uuid')
    QUERY = (2, 'query')
    SENT = (3, 'sent')
    DONE = (4, 'done')
    ERROR = (5, 'error')
    INFO = (6, 'info')


class LogPane(QWidget, Ui_logPane):
    sendRequestSignal = pyqtSignal(object)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setupUi(self)
        self.requestTableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.requestTableWidget.horizontalHeaderItem(RequestTableColumns.STATUS[0]).setText('')
        self.requestTableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        Cli3App.instance().session.requestSentSignal.connect(self.insert_request)
        Cli3App.instance().session.requestDoneSignal.connect(self.update_request)

    def setupUi(self, logPane):
        super().setupUi(logPane)

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
