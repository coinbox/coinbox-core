from PySide import QtGui

import app

import app.modules.currency.objects.currency as currency
from app.modules.currency.objects.currency import Currency
from app.modules.stock.objects.product import Product
from app.modules.stock.objects.category import Category

from app.modules.base.pages import FormPage

class ProductsPage(FormPage):
    itemClass = Product
    def fields(self):
        price = QtGui.QDoubleSpinBox()
        price.setMinimum(0)

        in_stock = QtGui.QCheckBox()
        in_stock.stateChanged.connect(self.onInStockCheckBox)
        
        quantity = QtGui.QDoubleSpinBox()
        quantity.setMinimum(0)

        return [("name", "Name", QtGui.QLineEdit(), ""),
                ("description", "Description", QtGui.QTextEdit(), ""),
                ("reference", "Reference", QtGui.QLineEdit(), ""),
                ("code", "Code", QtGui.QLineEdit(), ""),
                ("price", "Price", price, 0),
                ("currency", "Currency", QtGui.QComboBox(), currency.get_default()),
                ("in_stock", "In Stock", in_stock, True),
                ("quantity", "Quantity", quantity, 0),
                ("category", "Category", QtGui.QComboBox(), None)
                ]
    
    def onInStockCheckBox(self, event):
        in_stock = self.f["in_stock"].isChecked()
        self.f["quantity"].setEnabled(in_stock)
    
    def items(self):
        session = app.database.session()
        items = session.query(Product.display, Product).all()
        return items
    
    def canDeleteItem(self, item):
        return True
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field in ('name', 'reference', 'code'):
            data = self.f[field].text()
        elif field == 'description':
            data = self.f[field].toPlainText()
        elif field in ('price', 'quantity'):
            data = self.f[field].value()
        elif field == 'in_stock':
            data = self.f[field].isChecked()
        elif field in ('currency', 'category'):
            selected_index = self.f[field].currentIndex()
            if selected_index == -1:
                data = None
            else:
                data = self.f[field].itemData(selected_index)
        return (field, data)
    
    def setDataOnControl(self, field, data):
        if field in ('name', 'description', 'reference', 'code'):
            self.f[field].setText(data)
        elif field == 'in_stock':
            self.f[field].setChecked(data)
        elif field == 'currency':
            session = app.database.session()
            items = session.query(Currency.display, Currency).all()
            self.f[field].clear()
            for i, item in enumerate(items):
                self.f[field].addItem(*item)
                if item[1] == data:
                    self.f[field].setCurrentIndex(i)
        elif field == 'category':
            session = app.database.session()
            items = session.query(Category.display, Category).all()
            self.f[field].clear()
            self.f[field].addItem("", None)
            for i, item in enumerate(items):
                self.f[field].addItem(*item)
                if item[1] == data:
                    self.f[field].setCurrentIndex(i+1)
    
    def getDataFromItem(self, field, item):
        return getattr(item, field)
