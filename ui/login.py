# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/login.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlgLogin(object):
    def setupUi(self, dlgLogin):
        dlgLogin.setObjectName("dlgLogin")
        dlgLogin.setWindowModality(QtCore.Qt.ApplicationModal)
        dlgLogin.resize(567, 373)
        dlgLogin.setAutoFillBackground(False)
        dlgLogin.setSizeGripEnabled(True)
        dlgLogin.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlgLogin)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.formLayout.setContentsMargins(8, 8, 8, 8)
        self.formLayout.setSpacing(8)
        self.formLayout.setObjectName("formLayout")
        self.usernameLabel = QtWidgets.QLabel(dlgLogin)
        self.usernameLabel.setObjectName("usernameLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.usernameLabel)
        self.usernameLineEdit = QtWidgets.QLineEdit(dlgLogin)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.usernameLineEdit.sizePolicy().hasHeightForWidth())
        self.usernameLineEdit.setSizePolicy(sizePolicy)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.usernameLineEdit)
        self.passwordLabel = QtWidgets.QLabel(dlgLogin)
        self.passwordLabel.setObjectName("passwordLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.passwordLabel)
        self.passwordLineEdit = QtWidgets.QLineEdit(dlgLogin)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.passwordLineEdit)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.FieldRole, spacerItem)
        self.verticalLayout.addLayout(self.formLayout)
        self.loadProgressBar = QtWidgets.QProgressBar(dlgLogin)
        self.loadProgressBar.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadProgressBar.sizePolicy().hasHeightForWidth())
        self.loadProgressBar.setSizePolicy(sizePolicy)
        self.loadProgressBar.setMinimumSize(QtCore.QSize(0, 0))
        self.loadProgressBar.setProperty("value", 0)
        self.loadProgressBar.setTextVisible(True)
        self.loadProgressBar.setObjectName("loadProgressBar")
        self.verticalLayout.addWidget(self.loadProgressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonLogin = QtWidgets.QPushButton(dlgLogin)
        self.buttonLogin.setFlat(False)
        self.buttonLogin.setObjectName("buttonLogin")
        self.horizontalLayout.addWidget(self.buttonLogin)
        self.buttonClose = QtWidgets.QPushButton(dlgLogin)
        self.buttonClose.setFlat(False)
        self.buttonClose.setObjectName("buttonClose")
        self.horizontalLayout.addWidget(self.buttonClose)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.labelStatus = QtWidgets.QLabel(dlgLogin)
        self.labelStatus.setText("")
        self.labelStatus.setObjectName("labelStatus")
        self.verticalLayout.addWidget(self.labelStatus)

        self.retranslateUi(dlgLogin)
        QtCore.QMetaObject.connectSlotsByName(dlgLogin)

    def retranslateUi(self, dlgLogin):
        _translate = QtCore.QCoreApplication.translate
        dlgLogin.setWindowTitle(_translate("dlgLogin", "Login"))
        self.usernameLabel.setText(_translate("dlgLogin", "Username:"))
        self.passwordLabel.setText(_translate("dlgLogin", "Password:"))
        self.buttonLogin.setText(_translate("dlgLogin", "Login"))
        self.buttonClose.setText(_translate("dlgLogin", "Close"))
