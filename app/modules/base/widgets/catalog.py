from PySide import QtGui, QtCore

PARENT, CHILD, UP, ALL = 0, 1, 2, 3
ITEM, TYPE = QtCore.Qt.UserRole+1, QtCore.Qt.UserRole+2

class Catalog(QtGui.QWidget):
    
    childSelected = QtCore.Signal('QVariant')
    parentSelected = QtCore.Signal('QVariant')
    searchChanged = QtCore.Signal(str)
    
    def __init__(self):
        super(Catalog, self).__init__()
        self.search = QtGui.QLineEdit()
        self.search.textChanged.connect(self.onSearchTextChanged)
        
        self.list = QtGui.QListWidget()
        self.list.setViewMode(QtGui.QListWidget.IconMode)
        self.list.itemActivated.connect(self.onListItemActivated)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.search)
        layout.addWidget(self.list)
        self.setLayout(layout)
        
        self.icons = {UP: QtGui.QIcon.fromTheme('go-up'),
                      CHILD: QtGui.QIcon.fromTheme('text-x-generic'),
                      PARENT: QtGui.QIcon.fromTheme('folder'),
                      ALL: QtGui.QIcon.fromTheme('package-x-generic')}
        
        self.show_all = True
        self.in_all = False
        
        self.__current = None
        self.__tree = []
        self.populate()

    def populate(self, parent=None, search=None, show_all=False):
        self.__current = parent
        self.__search = search
        self.in_all = show_all
        
        if self.in_all:
            parents, children = [], self.getAll(search)
        else:
            parents, children = self.getChildren(parent, search)
        
        self.list.clear()
        
        if parent is not None or self.in_all:
            self.addItem("[Up]", None, UP)
        elif self.show_all:
            self.addItem("[All]", None, ALL)
        
        for data, label in parents:
            self.addItem(label, data, PARENT)
        
        for data, label in children:
            self.addItem(label, data, CHILD)

    def addItem(self, label, data, t):
        item = QtGui.QListWidgetItem(label)
        item.setData(ITEM, data)
        item.setData(TYPE, t)
        item.setIcon(self.icons[t])
        return self.list.addItem(item)

    def onSearchTextChanged(self):
        self.populate(parent=self.__current, search=self.search.text())
        self.searchChanged.emit(self.__search)

    def onListItemActivated(self):
        item = self.list.currentItem()
        data, t = item.data(ITEM), item.data(TYPE)
        if t == PARENT:
            self.__tree.append(self.__current)
            self.populate(parent=data, search=self.__search)
            self.parentSelected.emit(data)
        elif t == CHILD:
            self.childSelected.emit(data)
        elif t == UP:
            if self.in_all:
                parent = None
            else:
                parent = self.__tree.pop()
            self.populate(parent=parent, search=self.__search)
        elif t == ALL:
            self.populate(parent=None, search=None, show_all=True)

    def getAll(self, search=None):
        raise NotImplementedError, "getAll is not defined"
    def getChildren(self, parent=None, search=None):
        raise NotImplementedError, "getChildren is not defined"
