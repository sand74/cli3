from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget


class Folder(object):
    def __init__(self, folder):
        super().__init__()
        self._name = folder['name']

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f'Folder {self._name}'


class FolderTreeItem(QTreeWidgetItem, Folder):
    def __init__(self, folder: Folder, widget: QTreeWidgetItem=None):
        super(FolderTreeItem, self).__init__(widget, folder=folder)


class Param(object):
    def __init__(self, param):
        super().__init__()
        self._name = param['name']
        self._type = param['type']
        self._value = param['value']

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    def __str__(self):
        return f'Parameter {self._name} of type {self.type} = {self._value}'



class Query(object):
    def __init__(self, query):
        super().__init__()
        self._name = query['name']
        self._url = query['url']
        self._params = []
        for param in query['params']:
            self._params.append(Param(param))


    def __str__(self):
        return f'Query {self._name} for {self._url} has {len(self._params)} params'

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def params(self):
        return self._params


class QueryTreeItem(QTreeWidgetItem, Query):
    def __init__(self, query):
        super().__init__(query=query)
