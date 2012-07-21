from PySide import QtCore, QtGui

import app

from app.modules.currency.objects.currency import Currency

from app.modules.base.pages import FormPage

class CurrenciesPage(FormPage):
    itemClass = Currency
    def fields(self):
        value = QtGui.QDoubleSpinBox()
        value.setMinimum(0)
        value.setSingleStep(1)
        
        decimalPlaces = QtGui.QSpinBox()
        decimalPlaces.setRange(0, 10)
        decimalPlaces.setSingleStep(1)
        
        return [("name", "Name", QtGui.QLineEdit(), ""),
                ("symbol", "Symbol", QtGui.QLineEdit(), ""),
                ("value", "Value", value, 0),
                ("decimal_places", "Decimal Places", decimalPlaces, 0),
                ("digit_grouping", "Digit Grouping", QtGui.QCheckBox(), True),
                ]
    
    def items(self):
        session = app.database.session()
        items = session.query(Currency.display, Currency).all()
        return items
    
    def canDeleteItem(self, item):
        return True
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field in ('name', 'symbol'):
            data = self.f[field].text()
        elif field in ('value', 'decimal_places'):
            data = self.f[field].value()
        elif field == 'digit_grouping':
            data = self.f[field].isChecked()
        return (field, data)
    
    def setDataOnControl(self, field, data):
        if field in ('name', 'symbol'):
            self.f[field].setText(data)
        elif field in ('value', 'decimal_places'):
            self.f[field].setValue(data)
        elif field == 'digit_grouping':
            self.f[field].setChecked(data)
    
    def getDataFromItem(self, field, item):
        return getattr(item, field)
