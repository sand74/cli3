import json
import typing

from PyQt5 import QtNetwork, QtCore, QtWidgets
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeView, QWidget

from app import Cli3App
from models import Folder, Query
from ui.nav_pane import Ui_navigatorPane


class TreeItem():
    def __init__(self, parent: 'TreeItem' = None):
        self._parent = parent
        self._children = []
        self._icon = None
        self._expanded = False

    def append_child(self, child: 'TreeItem'):
        self._children.append(child)

    def child(self, row: int):
        if row >= 0 and row < len(self._children):
            return self._children[row]
        return None

    def child_count(self):
        return len(self._children)

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)
        return 0

    def parent(self):
        return self._parent

    def column_count(self):
        raise NotImplemented()

    def data(self, column: int):
        raise NotImplemented()

    def get_icon(self):
        return self._icon

    def set_expanded(self, expand: bool):
        self._expanded = expand


class RootTreeItem(TreeItem):
    def __init__(self, columns: []):
        super().__init__()
        self._columns = columns

    def column_count(self):
        return len(self._columns)

    def data(self, column: int):
        if column >= 0 and column < len(self._columns):
            return self._columns[column]
        return None


class FolderTreeItem(TreeItem):
    def __init__(self, folder: Folder, parent: TreeItem = None):
        super().__init__(parent)
        self._folder = folder

    def column_count(self):
        return 1

    def data(self, column: int):
        return self._folder.name

    def get_icon(self):
        if self._expanded:
            return Cli3App.instance().icons['folder_open']
        else:
            return Cli3App.instance().icons['folder_close']

    def folder(self):
        return self._folder


class QueryTreeItem(TreeItem):
    def __init__(self, query: Query, parent: TreeItem = None):
        super().__init__(parent)
        self._query = query

    def column_count(self):
        return 1

    def data(self, column: int):
        return self._query.name

    def get_icon(self):
        return Cli3App.instance().icons['file']

    def query(self):
        return self._query


class FoldersTreeModel(QAbstractItemModel):
    def __init__(self, folders, parent):
        super().__init__()
        self._root_item = RootTreeItem(['column1'])
        self._folders = []
        for folder in folders:
            folder_item = FolderTreeItem(folder=Folder(folder), parent=self._root_item)
            item = self._make_item(folder_item, folder)
            self._folders.append(item)
            self._root_item.append_child(folder_item)

    def folders(self):
        return self._folders

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child(row)
        if child_item is not None:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()
        child_item = child.internalPointer()
        parent_item = child_item.parent()
        if parent_item == self._root_item:
            return QModelIndex()
        if parent_item == None:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        return parent_item.child_count()

    def columnCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            parent_item = parent.internalPointer()
            return parent_item.column_count()
        return self._root_item.column_count()

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())
        elif role == Qt.DecorationRole:
            item = index.internalPointer()
            if item is not None and item.get_icon() != None:
                return item.get_icon()
        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return super().flags(index)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root_item.data(section)
        return QVariant()

    def _make_item(self, parent_item: FolderTreeItem, folder: dict, level=0) -> FolderTreeItem:
        """
        Make Navigation Tree Item
        :param parent_item: Parent tree item for folder
        :param folder: folder json
        :param level: Tree level
        :return:
        """
        for sub_folder in folder['folders']:
            sub_folder_item = FolderTreeItem(Folder(sub_folder), parent_item)
            item = self._make_item(sub_folder_item, sub_folder, level + 1)
            parent_item.append_child(item)
        for query in folder['queries']:
            item = QueryTreeItem(Query(query), parent_item)
            parent_item.append_child(item)
        return parent_item


class NavigatorPane(QWidget, Ui_navigatorPane):
    sendRequestSignal = pyqtSignal(object)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setupUi(self)
        self.fill_contents()
        self.navTreeView.expandAll()
        self.navTreeView.customContextMenuRequested.connect(self._folders_tree_context_menu)
        self.navTreeView.doubleClicked.connect(self._folders_tree_dbl_click)
        self.navTreeView.collapsed.connect(self._folder_collapsed)
        self.navTreeView.expanded.connect(self._folder_expanded)

    def setupUi(self, navigatorPane):
        super().setupUi(navigatorPane)

    def fill_contents(self):
        err, message = Cli3App.instance().session.get(f'{Cli3App.instance().session.TREE_API}')
        if err == QtNetwork.QNetworkReply.NoError:
            json_tree = json.loads(message)
            tree_model = FoldersTreeModel(json_tree['folders'], None)
            self.navTreeView.setModel(tree_model)
        else:
            print("Error occurred: ", err, message)

    def _folder_expanded(self, index):
        if not index.isValid():
            return
        item = index.internalPointer()
        if item is not None:
            item.set_expanded(True)

    def _folder_collapsed(self, index):
        if not index.isValid():
            return
        item = index.internalPointer()
        if item is not None:
            item.set_expanded(False)

    def _folders_tree_context_menu(self, point) -> None:
        """
        Show context menu for Nav Tree
        :param point:
        :return:
        """
        index = self.navTreeView.indexAt(point)
        if not index.isValid():
            return
        item = index.internalPointer()
        if isinstance(item, QueryTreeItem):
            menu = QtWidgets.QMenu()
            action = menu.addAction("Query")
            action.setIcon(Cli3App.instance().icons.get('send'))
            action.triggered.connect(lambda x: self.sendRequestSignal.emit(item.query()))
            menu.addSeparator()
            menu.addAction("Cancel")
            menu.exec_(self.navTreeView.mapToGlobal(point))

    def _folders_tree_dbl_click(self, index) -> None:
        """
        Double click on Nav Tree node
        :return:
        """
        if not index.isValid():
            return
        item = index.internalPointer()
        if isinstance(item, QueryTreeItem):
            self.sendRequestSignal.emit(item.query())
