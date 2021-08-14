# from PyQt5 import Qt

import qtawesome as qta
from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QTreeWidgetItem

'''
Модели объектов приложения
'''


class Folder(object):
    """
    Модель папки
    """

    def __init__(self, folder):
        super().__init__()
        self._name = folder['name']

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f'Folder {self._name}'


class FolderTreeItem(QTreeWidgetItem):
    """
    модель папки для отображения в дереве
    """
    def __init__(self, folder: Folder, widget: QTreeWidgetItem = None):
        super(FolderTreeItem, self).__init__(widget)
        self._folder = folder
        self.setText(0, folder.name)
        self.setIcon(0, qta.icon('fa5s.folder', color='orange'))

    @property
    def folder(self):
        return self._folder


class InputField(object):
    """
    Модель поля ввода
    """

    def __init__(self, field):
        super().__init__()
        self._type = field['type']
        self._desc = field['desc']

    @property
    def type(self):
        return self._type

    @property
    def desc(self):
        return self._desc


class Param(object):
    """
    Модель параметра запрося
    """
    def __init__(self, param):
        super().__init__()
        self._name = param['name']
        self._title = param['title'] or param['name']
        self._type = param['type']
        self._value = param['value']
        self._field = InputField(param['input']) if param['input'] is not None else None

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def field(self):
        return self._field

    def __str__(self):
        return f'Parameter {self._name} of type {self.type} = {self._value}'



class Query(object):
    """
    модель запрося
    """
    def __init__(self, query):
        super().__init__()
        self._id = query['id']
        self._name = query['name']
        self._url = query['url']
        self._params = []
        for param in query['params']:
            self._params.append(Param(param))

    def __str__(self):
        return f'Query {self._name} for {self._url} has {len(self._params)} params'

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def params(self):
        return self._params

    def has_in_params(self):
        return len([param for param in self._params if param.type not in ['CURSOR', 'TEXT']]) > 0

    def make_request(self, params=None):
        if params is None:
            params = {}
        request = f'id={self._id}'
        for param in self._params:
            if param.name in params:
                request += f'&{param.name}={params[param.name]}'
            else:
                request += f'&{param.name}={param.value}'
        return request




class QueryTreeItem(QTreeWidgetItem):
    """
    модель запрося для отображения в дереве
    """
    def __init__(self, query):
        super().__init__()
        self._query = query
        self.setText(0, query.name)
        self.setIcon(0, qta.icon('fa5s.share-square', color='blue'))

    @property
    def query(self):
        return self._query



