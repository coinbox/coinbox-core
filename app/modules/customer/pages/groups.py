from PySide import QtGui

import app

from app.modules.customer.objects.group import CustomerGroup

from app.modules.base.pages import FormPage

class CustomerGroupsPage(FormPage):
    itemClass = CustomerGroup
    def fields(self):
        menu_restrictions = QtGui.QTreeWidget()
        menu_restrictions.setHeaderHidden(True)
        
        return [("name", "Name", QtGui.QLineEdit(), ""),
                ("comment", "Comment", QtGui.QTextEdit(), ""),
                ]
    
    def items(self):
        session = app.database.session()
        items = session.query(CustomerGroup.display, CustomerGroup).all()
        return items
    
    def canDeleteItem(self, item):
        return True
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field in ('name', 'comment'):
            data = self.f[field].text()
        return (field, data)
    
    def setDataOnControl(self, field, data):
        if field in ('name', 'comment'):
            self.f[field].setText(data)
    
    def getDataFromItem(self, field, item):
        return getattr(item, field)
