# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/log_pane.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_logPane(object):
    def setupUi(self, logPane):
        logPane.setObjectName("logPane")
        logPane.resize(780, 212)
        self.verticalLayout = QtWidgets.QVBoxLayout(logPane)
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.requestTableWidget = QtWidgets.QTableWidget(logPane)
        self.requestTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.requestTableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.requestTableWidget.setObjectName("requestTableWidget")
        self.requestTableWidget.setColumnCount(7)
        self.requestTableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.requestTableWidget.setHorizontalHeaderItem(6, item)
        self.verticalLayout.addWidget(self.requestTableWidget)

        self.retranslateUi(logPane)
        QtCore.QMetaObject.connectSlotsByName(logPane)

    def retranslateUi(self, logPane):
        _translate = QtCore.QCoreApplication.translate
        logPane.setWindowTitle(_translate("logPane", "Form"))
        item = self.requestTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("logPane", "status"))
        item = self.requestTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("logPane", "uuid"))
        item = self.requestTableWidget.horizontalHeaderItem(2)
        item.setText(_translate("logPane", "query"))
        item = self.requestTableWidget.horizontalHeaderItem(3)
        item.setText(_translate("logPane", "sent"))
        item = self.requestTableWidget.horizontalHeaderItem(4)
        item.setText(_translate("logPane", "done"))
        item = self.requestTableWidget.horizontalHeaderItem(5)
        item.setText(_translate("logPane", "code"))
        item = self.requestTableWidget.horizontalHeaderItem(6)
        item.setText(_translate("logPane", "info"))
