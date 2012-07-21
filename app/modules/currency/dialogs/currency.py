from PySide import QtGui

from app.modules.currency.objects.currency import Currency
import app

class CurrencyDialog(QtGui.QWidget):
    
    def __init__(self):
        super(CurrencyDialog, self).__init__()

        self.name = QtGui.QLineEdit()
        self.symbol = QtGui.QLineEdit()
        self.value = QtGui.QSpinBox()
        self.value.setMinimum(0)
        self.value.setSingleStep(1)
        self.decimalPlaces = QtGui.QSpinBox()
        self.decimalPlaces.setRange(0, 10)
        self.decimalPlaces.setSingleStep(1)
        self.digitGrouping = QtGui.QCheckBox()
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.okBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.cancelBtn.pressed.connect(self.onCancelButton)
        
        rows = [["Name", self.name],
                ["Symbol", self.symbol],
                ["Value", self.value],
                ["Decimal Places", self.decimalPlaces],
                ["Digit Grouping", self.digitGrouping],
                [buttonBox]]
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        [form.addRow(*row) for row in rows]
        
        self.setLayout(form)
    
    def onOkButton(self):
        currency = Currency(name=self.name.text(),
                            symbol=self.symbol.text(),
                            value=self.value.text(),
                            decimal_places=self.decimalPlaces.value(),
                            digit_grouping=self.digitGrouping.isChecked()
                            )
        session = app.database.session()
        session.add(currency)
        session.commit()
        
        app.config["mod.currency", "default"] = str(currency.id)
        self.close()
        
        app.start()
    
    def onCancelButton(self):
        self.close()
