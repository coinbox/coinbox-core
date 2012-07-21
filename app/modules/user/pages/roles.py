from PySide import QtCore, QtGui

import app

import app.modules.user.objects.user as user
from app.modules.user.objects.role import Role
from app.modules.user.objects.permission import Permission

from app.modules.base.pages import FormPage

class RolesPage(FormPage):
    itemClass = Role
    def fields(self):
        permissions = QtGui.QTreeWidget()
        permissions.setHeaderHidden(True)
        return [("name", "Name", QtGui.QLineEdit(), ""),
                ("permissions", "Permissions", permissions, [])
                ]
    
    def items(self):
        session = app.database.session()
        items = session.query(Role.display, Role).all()
        return items
    
    def canDeleteItem(self, item):
        return user.current.role != item
    
    def canEditItem(self, item):
        return user.current.role != item
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field == 'name':
            data = self.f[field].text()
        elif field == 'permissions':
            data = []
            for i in xrange(self.f[field].topLevelItemCount()):
                root = self.f[field].topLevelItem(i)
                if root.checkState(0) == QtCore.Qt.Checked:
                    item = root.data(0, QtCore.Qt.UserRole+1)
                    data.append(item)
        return (field, data)
    
    def setDataOnControl(self, field, data):
        if field == 'name':
            self.f[field].setText(data)
        elif field == 'permissions':
            session = app.database.session()
            items = session.query(Permission.display, Permission).all()
            self.f[field].clear()
            for item in items:
                root = QtGui.QTreeWidgetItem(self.f[field], [item[0]])
                root.setData(0, QtCore.Qt.UserRole+1, item[1])
                if item[1] in data:
                    root.setCheckState(0, QtCore.Qt.Checked)
                else:
                    root.setCheckState(0, QtCore.Qt.Unchecked)
    
    def getDataFromItem(self, field, item):
        return getattr(item, field)
