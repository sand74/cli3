# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/nav_pane.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_navigatorPane(object):
    def setupUi(self, navigatorPane):
        navigatorPane.setObjectName("navigatorPane")
        navigatorPane.resize(341, 574)
        self.verticalLayout = QtWidgets.QVBoxLayout(navigatorPane)
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.navTreeView = QtWidgets.QTreeView(navigatorPane)
        self.navTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.navTreeView.setObjectName("navTreeView")
        self.navTreeView.header().setVisible(False)
        self.verticalLayout.addWidget(self.navTreeView)

        self.retranslateUi(navigatorPane)
        QtCore.QMetaObject.connectSlotsByName(navigatorPane)

    def retranslateUi(self, navigatorPane):
        _translate = QtCore.QCoreApplication.translate
        navigatorPane.setWindowTitle(_translate("navigatorPane", "Form"))
