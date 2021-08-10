# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(986, 714)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mdiArea = QtWidgets.QMdiArea(self.centralwidget)
        self.mdiArea.setObjectName("mdiArea")
        self.verticalLayout.addWidget(self.mdiArea)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 986, 24))
        self.menubar.setDefaultUp(True)
        self.menubar.setNativeMenuBar(True)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.navDockWidget = QtWidgets.QDockWidget(MainWindow)
        self.navDockWidget.setObjectName("navDockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.refreshFoldersButton = QtWidgets.QToolButton(self.dockWidgetContents)
        self.refreshFoldersButton.setObjectName("refreshFoldersButton")
        self.horizontalLayout_2.addWidget(self.refreshFoldersButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.foldersTreeWidget = QtWidgets.QTreeWidget(self.dockWidgetContents)
        self.foldersTreeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.foldersTreeWidget.setHeaderHidden(True)
        self.foldersTreeWidget.setColumnCount(1)
        self.foldersTreeWidget.setObjectName("foldersTreeWidget")
        self.foldersTreeWidget.headerItem().setText(0, "1")
        self.foldersTreeWidget.header().setVisible(False)
        self.verticalLayout_2.addWidget(self.foldersTreeWidget)
        self.navDockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.navDockWidget)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.logDocWidget = QtWidgets.QDockWidget(MainWindow)
        self.logDocWidget.setObjectName("logDocWidget")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.requestTableWidget = QtWidgets.QTableWidget(self.dockWidgetContents_2)
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
        self.horizontalLayout.addWidget(self.requestTableWidget)
        self.logDocWidget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.logDocWidget)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.refreshFoldersButton.setText(_translate("MainWindow", "..."))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        item = self.requestTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "status"))
        item = self.requestTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "uuid"))
        item = self.requestTableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "query"))
        item = self.requestTableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "sent"))
        item = self.requestTableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "done"))
        item = self.requestTableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "code"))
        item = self.requestTableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "info"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
