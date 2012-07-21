from PySide import QtGui

import app

from app.modules.currency.objects.currency import Currency

class CurrencyConfigPage(QtGui.QWidget):
    label = 'Currency'
    
    def __init__(self):
        super(CurrencyConfigPage, self).__init__()
        
        self.default = QtGui.QComboBox()
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        form.addRow('Default Currency', self.default)
        
        self.setLayout(form)

    def populate(self):
        session = app.database.session()
        currencies = session.query(Currency.name, Currency).all()
        default_id = app.config['mod.currency', 'default']
        
        self.default.clear()
        for i, c in enumerate(currencies):
            self.default.addItem(c[0], c[1])
            if int(default_id) == c[1].id:
                self.default.setCurrentIndex(i)
    
    def update(self):
        default = self.default.itemData(self.default.currentIndex())
        app.config['mod.currency', 'default'] = str(default.id)
