from PySide import QtCore, QtGui

import app

class DummyItem:
    def __init__(self, **kwargs):
        raise RuntimeError, 'Item class not defined for %s' % (kwargs,)

class FormPage(QtGui.QWidget):
    itemClass = DummyItem
    def __init__(self):
        super(FormPage, self).__init__()

        self.editing = False

        self.list = QtGui.QListView()
        self.list.activated.connect(self.onItemActivated)
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.deleteBtn = buttonBox.addButton("Delete", QtGui.QDialogButtonBox.DestructiveRole)
        self.deleteBtn.pressed.connect(self.onDeleteButton)
        
        self.newBtn = buttonBox.addButton("New", QtGui.QDialogButtonBox.ActionRole)
        self.newBtn.pressed.connect(self.onNewButton)
        
        self.editBtn = buttonBox.addButton("Edit", QtGui.QDialogButtonBox.ActionRole)
        self.editBtn.pressed.connect(self.onEditButton)
        
        self.okBtn = buttonBox.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        self.cancelBtn.pressed.connect(self.onCancelButton)
        
        fields = self.fields()
        rows = []
        self.f = dict()
        self.defaults = dict()
        for f in fields:
            self.f[f[0]] = f[2]
            self.defaults[f[0]] = f[3]
            rows.append((f[1], f[2]))
        
        self.formContainer = QtGui.QWidget()
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        [form.addRow(*row) for row in rows]
        
        self.formContainer.setLayout(form)
        self.formContainer.setEnabled(False)
        
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.formContainer)
        
        formLayout = QtGui.QVBoxLayout()
        formLayout.setSpacing(10)
        formLayout.addWidget(self.scrollArea)
        formLayout.addWidget(buttonBox)
        
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(10)
        
        layout.addWidget(self.list)
        layout.addLayout(formLayout)
        
        self.setLayout(layout)
        
        self.populate()
    
    def populate(self):
        model = SimpleList(self.items())
        self.list.setModel(model)
        self.editing = False
        self.setItem(None)
        self.formContainer.setEnabled(False)
    
    def setItem(self, item=None):
        self.item = item
        if item is None:
            for f in self.f:
                self.setDataOnControl(f, self.defaults[f])
            self.deleteBtn.setEnabled(False)
            self.editBtn.setEnabled(False)
        else:
            for f in self.f:
                self.setDataOnControl(f, self.getDataFromItem(f, item))
            self.deleteBtn.setEnabled(not self.editing and self.canDeleteItem(item))
            self.editBtn.setEnabled(not self.editing and self.canEditItem(item))
        self.newBtn.setEnabled(not self.editing and self.canAddItem())
        self.okBtn.setEnabled(self.editing)
        self.cancelBtn.setEnabled(self.editing)
        self.list.setEnabled(not self.editing)
    
    def onItemActivated(self, index):
        self.editing = False
        item = self.list.model().contents[index.row()][1]
        self.setItem(item)
    
    def onOkButton(self):
        # TODO: validation
        if self.item is None:
            self.new()
        else:
            self.update(self.item)
        self.populate()
    
    def onEditButton(self):
        self.editing = True
        self.formContainer.setEnabled(True)
        self.setItem(self.item)
    
    def onCancelButton(self):
        self.editing = False
        self.setItem(self.item)
        self.formContainer.setEnabled(False)
    
    def onDeleteButton(self):
        if self.item is not None:
            self.delete(self.item)
            self.populate()
    
    def onNewButton(self):
        self.editing = True
        self.setItem(None)
        self.formContainer.setEnabled(True)
    
    def new(self):
        data = dict()
        for f in self.f:
            key, value = self.getDataFromControl(f)
            if key is None: continue
            data[key] = value
        item = self.itemClass(**data)
        session = app.database.session()
        session.add(item)
        session.commit()
    
    def delete(self, item):
        item.delete()
    
    def update(self, item):
        data = dict()
        for f in self.f:
            key, value = self.getDataFromControl(f)
            if key is None: continue
            data[key] = value
        item.update(**data)
    
    def fields(self):
        return []
    
    def items(self):
        return []
    
    def canDeleteItem(self, item):
        return True
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        return (None, None)
    
    def setDataOnControl(self, field, data):
        pass
    
    def getDataFromItem(self, field, item):
        return None

class SimpleList(QtCore.QAbstractListModel):
    def __init__(self, contents):
        super(SimpleList, self).__init__()
        self.contents = contents

    def rowCount(self, parent):
        return len(self.contents)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return str(self.contents[index.row()][0])
