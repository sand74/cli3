# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/input_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_InputDialog(object):
    def setupUi(self, InputDialog):
        InputDialog.setObjectName("InputDialog")
        InputDialog.resize(460, 102)
        self.verticalLayout = QtWidgets.QVBoxLayout(InputDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.fieldsFormLayout = QtWidgets.QFormLayout()
        self.fieldsFormLayout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.fieldsFormLayout.setObjectName("fieldsFormLayout")
        self.verticalLayout.addLayout(self.fieldsFormLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(InputDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(InputDialog)
        self.buttonBox.accepted.connect(InputDialog.accept)
        self.buttonBox.rejected.connect(InputDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InputDialog)

    def retranslateUi(self, InputDialog):
        _translate = QtCore.QCoreApplication.translate
        InputDialog.setWindowTitle(_translate("InputDialog", "Dialog"))