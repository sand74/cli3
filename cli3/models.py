# from PyQt5 import Qt

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


class InputField(object):
    """
    Модель поля ввода
    """
    def __init__(self, field):
        super().__init__()
        self._type = field['type']
        self._nci = field.get('nci', None)
        self._nci_column = field.get('nci_column', None)
        self._values = field.get('values', None)

    @property
    def type(self):
        return self._type

    @property
    def nci(self):
        return self._nci

    @property
    def nci_column(self):
        return self._nci_column

    @property
    def values(self):
        return self._values


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

    @value.setter
    def value(self, value):
        self._value = value

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
        self._type = query.get('type', 'TABLE')
        self._params = []
        for param, value in query.get('params', {}).items():
            self._params.append(Param(value))
        self._subqueries = []
        for subquery in query.get('subqueries', []):
            self._subqueries.append(Query(subquery))

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
    def type(self):
        return self._type

    @property
    def params(self):
        return self._params

    @property
    def in_params(self):
        return [param for param in self._params if param.type not in ['CURSOR', 'TEXT']]

    @property
    def subqueries(self):
        return self._subqueries

    def has_subqueries(self):
        return len(self._subqueries) > 0

    def has_in_params(self):
        return len(self.in_params) > 0

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

    def get_full_name(self, params):
        if params is None:
            params = {}
        full_name = self.name
        if self.has_in_params():
            full_name += ' ['
        for param in self.in_params:
            if param.name in params:
                full_name += f'{param.title}={params[param.name]}, '
            else:
                full_name += f'{param.title}={param.value}, '
        if self.has_in_params():
            full_name = full_name[:-2] + ']'
        return full_name


class Column(object):
    def __init__(self, column):
        self._name = column['name'].upper()
        self._title = column.get('title', None)
        self._type = column.get('type', 'STRING').upper()
        self._width = column.get('width', 0)
        self._format = column.get('format', None)
        self._visable = column.get('visable', False)
        self._nci = column.get('nci', {})
        self._nci_column = column.get('nci_column', None)
        self._subqueries = []
        for subquery in column.get('subqueries', []):
            self._subqueries.append(Query(subquery))

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def title(self):
        return self._title

    @property
    def width(self):
        return self._width

    @property
    def format(self):
        return self._format

    @property
    def visable(self):
        return self._visable

    @property
    def nci(self):
        return self._nci

    @property
    def nci_column(self):
        return self._nci_column

    @property
    def subqueries(self):
        return self._subqueries

    def has_subqueries(self):
        return len(self._subqueries) > 0
