# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/text_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TextWindow(object):
    def setupUi(self, TextWindow):
        TextWindow.setObjectName("TextWindow")
        TextWindow.resize(735, 534)
        self.verticalLayout = QtWidgets.QVBoxLayout(TextWindow)
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(TextWindow)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.textBrowser.setFont(font)
        self.textBrowser.setAutoFormatting(QtWidgets.QTextEdit.AutoAll)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.retranslateUi(TextWindow)
        QtCore.QMetaObject.connectSlotsByName(TextWindow)

    def retranslateUi(self, TextWindow):
        _translate = QtCore.QCoreApplication.translate
        TextWindow.setWindowTitle(_translate("TextWindow", "Form"))
