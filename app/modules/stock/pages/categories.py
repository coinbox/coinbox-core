from PySide import QtGui

import app

from app.modules.stock.objects.category import Category
from app.modules.stock.objects.product import Product

from app.modules.base.pages import FormPage

class CategoriesPage(FormPage):
    itemClass = Category
    def fields(self):
        return [("name", "Name", QtGui.QLineEdit(), ""),
                ("parent", "Parent Category", QtGui.QComboBox(), None)
                ]
    
    def items(self):
        session = app.database.session()
        items = session.query(Category.display, Category).all()
        return items
    
    def canDeleteItem(self, item):
        session = app.database.session()
        category_count = session.query(Category).filter(Category.parent == item).count()
        if category_count != 0:
            return False
        product_count = session.query(Product).filter(Product.category == item).count()
        if product_count != 0:
            return False
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field in ('name', 'description', 'reference', 'code'):
            data = self.f[field].text()
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
        if field == 'name':
            self.f[field].setText(data)
        elif field == 'parent':
            session = app.database.session()
            query = session.query(Category.display, Category)
            if data is not None:
                query = query.filter(Category.id != data.id)
            items = query.all()
            self.f[field].clear()
            self.f[field].addItem("", None)
            for item in items:
                self.f[field].addItem(*item)
    
    def getDataFromItem(self, field, item):
        return getattr(item, field)
