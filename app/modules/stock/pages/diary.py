from PySide import QtGui

import app

from app.modules.stock.objects.product import Product

class StockDiaryPage(QtGui.QWidget):
    def __init__(self):
        super(StockDiaryPage, self).__init__()
        
        self.products = QtGui.QComboBox()
        self.products.setEditable(False)
        self.products.currentIndexChanged.connect(self.onProductChange)
        
        self.operations = QtGui.QComboBox()
        self.operations.setEditable(False)
        self.operations.addItems(('In', 'Modification'))
        self.operations.currentIndexChanged.connect(self.onOperationChange)

        self.quantity = QtGui.QDoubleSpinBox()
        self.quantity.setMinimum(0)
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.editBtn = buttonBox.addButton("Edit", QtGui.QDialogButtonBox.ActionRole)
        self.editBtn.pressed.connect(self.onEditButton)
        
        self.okBtn = buttonBox.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        self.cancelBtn.pressed.connect(self.onCancelButton)

        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        form.addRow("Operation", self.operations)
        form.addRow("Quantity", self.quantity)

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(10)
        
        layout.addWidget(self.products)
        layout.addLayout(form)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)

        self.populate()

        self.setItem(None)

    def populate(self):
        session = app.database.session()
        items = session.query(Product.display, Product).all()
        self.products.clear()
        for i, item in enumerate(items):
            self.products.addItem(*item)
        self.products.setCurrentIndex(-1)

    def canEdit(self):
        return (self.item is not None and self.item.in_stock)

    def setItem(self, item, edit=False):
        self.item = item
        
        self.products.setEnabled(not edit)
        self.operations.setEnabled(item is not None and edit)
        self.quantity.setEnabled(item is not None and edit)
        self.okBtn.setEnabled(item is not None and edit)
        self.cancelBtn.setEnabled(item is not None and edit)
        self.editBtn.setEnabled(self.canEdit() and not edit)
        
        self.quantity.setValue(0)
        self.operations.setCurrentIndex(0)

    def saveChanges(self):
        quantity = self.quantity.value()
        operation = 'in' if self.operations.currentIndex() == 0 else 'edit'
        if operation == 'in':
            self.item.quantity_in(quantity)
        else:
            self.item.quantity = quantity
        return True

    def onProductChange(self):
        selected_index = self.products.currentIndex()
        item = self.products.itemData(selected_index)
        self.setItem(item, False)

    def onOperationChange(self):
        operation = 'in' if self.operations.currentIndex() == 0 else 'edit'
        if operation == 'in':
            self.quantity.setValue(0)
        else:
            self.quantity.setValue(self.item.quantity)

    def onEditButton(self):
        self.setItem(self.item, True)
    
    def onOkButton(self):
        if self.saveChanges():
            self.setItem(None, False)

    def onCancelButton(self):
        self.setItem(self.item, False)
