from PySide import QtGui

import app

import app.modules.user.objects.user as user
from app.modules.user.objects.user import User
from app.modules.user.objects.role import Role

from app.modules.base.pages import FormPage

class UsersPage(FormPage):
    itemClass = User
    def fields(self):
        username = QtGui.QLineEdit()
        username.setEnabled(False)
        
        role = QtGui.QComboBox()
        role.setEditable(False)
        role.currentIndexChanged[int].connect(self.onRoleChanged)
        
        password1 = QtGui.QLineEdit()
        password1.setEchoMode(QtGui.QLineEdit.Password)
        password1.setEnabled(False)
        
        password2 = QtGui.QLineEdit()
        password2.setEchoMode(QtGui.QLineEdit.Password)
        password2.setEnabled(False)

        password_check = QtGui.QCheckBox("Change Password")
        password_check.stateChanged.connect(self.onCheckPassword)

        return [("username", "Username", username, ""),
                ("role", "Role", role, None),
                ("permissions", "Permissions", QtGui.QListWidget(), []),
                ("hidden", "Show in Login Box", QtGui.QCheckBox("Is Hidden"), False),
                ("password_check", "", password_check, False),
                ("password1", "Password", password1, ""),
                ("password2", "Confirm Password", password2, "")
                ]
    
    def onCheckPassword(self):
        checked = self.f['password_check'].isChecked()
        self.f['password1'].setEnabled(checked)
        self.f['password2'].setEnabled(checked)
    
    def onRoleChanged(self):
        field, data = self.getDataFromControl('role')
        if data is not None:
            self.setDataOnControl('permissions', data.permissions)
        else:
            self.setDataOnControl('permissions', [])
    
    def items(self):
        session = app.database.session()
        items = session.query(User.display, User).all()
        return items
    
    def canDeleteItem(self, item):
        return user.current != item
    
    def canEditItem(self, item):
        return user.current != item
    
    def canAddItem(self):
        return True
    
    def getDataFromControl(self, field):
        if field == 'username':
            data = self.f[field].text()
        elif field == 'hidden':
            data = self.f[field].isChecked()
        elif field == 'role':
            selected_index = self.f[field].currentIndex()
            if selected_index == -1:
                data = None
            else:
                data = self.f[field].itemData(selected_index)
        elif field in ('password1', 'password2'):
            # TODO: validation
            data = self.f[field].text()
            field = 'password'
        elif field in ('permissions', 'password_check'):
            data = None
            field = None
        return (field, data)
    
    def setDataOnControl(self, field, data):
        if field == 'username':
            self.f[field].setText(data)
        elif field == 'hidden':
            self.f[field].setChecked(data)
        elif field == 'role':
            session = app.database.session()
            items = session.query(Role.display, Role).all()
            self.f[field].clear()
            self.f[field].addItem("", None)
            for i, item in enumerate(items):
                self.f[field].addItem(*item)
                if item[1] == data:
                    self.f[field].setCurrentIndex(i+1) 
        elif field == 'permissions':
            self.f[field].clear()
            self.f[field].addItems([i.display for i in data])
        elif field in ('password1', 'password2'):
            self.f[field].setText(data)
        elif field == 'password_check':
            self.f[field].setChecked(data)
    
    def getDataFromItem(self, field, item):
        if field in ('username', 'role', 'hidden'):
            return getattr(item, field)
        elif field == 'permissions':
            return item.role.permissions if item.role is not None else []
        elif field in ('password1', 'password2'):
            return ""
        elif field == 'password_check':
            return False
