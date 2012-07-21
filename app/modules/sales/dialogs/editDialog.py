from PySide import QtGui

class EditDialog(QtGui.QDialog):
    def __init__(self, data):
        super(EditDialog, self).__init__()

        self.description = QtGui.QLineEdit()
        
        self.sellPrice = QtGui.QDoubleSpinBox()
        
        self.amount = QtGui.QDoubleSpinBox()
        self.amount.setPrefix('x')
        
        self.discount = QtGui.QDoubleSpinBox()
        self.discount.setRange(0, 100)
        self.discount.setSuffix('%')
        
        self.product = QtGui.QLineEdit()
        self.product.setReadOnly(True)
        
        self.max = QtGui.QDoubleSpinBox()
        self.max.setReadOnly(True)
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.okBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.cancelBtn.pressed.connect(self.onCancelButton)

        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        rows = (("Description", self.description),
                ("Sell Price", self.sellPrice),
                ("Amount", self.amount),
                ("Discount", self.discount),
                ("Product", self.product),
                ("Maximum Amount", self.max),
                (buttonBox,))
        
        [form.addRow(*row) for row in rows]

        self.setLayout(form)

        self.data = data
        self.populate()

    def populate(self):
        self.description.setText(self.data['description'])
        self.sellPrice.setValue(self.data['sell_price'])
        self.amount.setValue(self.data['amount'])
        self.discount.setValue(self.data['discount']*100.0)
        p = self.data['product']
        if p is None:
            self.product.setText('[None]')
            self.max.setValue(0)
        else:
            self.product.setText(p.name)
            if p.in_stock:
                self.max.setValue(p.quantity)
            else:
                self.max.setValue(0)
    
    def onOkButton(self):
        p = self.data['product']
        if p is not None and p.in_stock and p.quantity<self.amount.value():
            QtGui.QMessageBox.warning(self, 'Quantity mismatch', 'Amount exceeds the product quantity in stock!')
            return
        self.data['description'] = self.description.text()
        self.data['sell_price'] = self.sellPrice.value()
        self.data['amount'] = self.amount.value()
        self.data['discount'] = self.discount.value()/100.0
        
        self.close()
    
    def onCancelButton(self):
        self.close()

    def TransferFromWindow(self):
        try:
            win = self.GetWindow()
            if self.key == 'description':
                data = win.GetValue()
            elif self.key == 'sell_price':
                data = float(win.GetValue())
            elif self.key == 'amount':
                data = win.GetValue()
            elif self.key == 'discount':
                data = win.GetValue()/100.0
            self.dialog.data[self.key] = data
        except:
            print '-- ERROR -- in EditValidator.TransferFromWindow'
            print '--', self.key, self.dialog.data
            raise
        return True
