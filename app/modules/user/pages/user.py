from PySide import QtCore, QtGui

import app

import app.modules.user.objects.user as user

class IndividualUserPage(QtGui.QWidget):
    
    def __init__(self):
        super(IndividualUserPage, self).__init__()

        self.username = QtGui.QLineEdit()
        self.username.setReadOnly(True)
        
        self.role = QtGui.QLineEdit()
        self.role.setReadOnly(True)
        
        self.changePassword = QtGui.QCheckBox("Change Password")
        self.changePassword.stateChanged.connect(self.onChangePasswordCheck)
        
        self.password1 = QtGui.QLineEdit()
        self.password1.setEchoMode(QtGui.QLineEdit.Password)
        
        self.password2 = QtGui.QLineEdit()
        self.password2.setEchoMode(QtGui.QLineEdit.Password)
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.okBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.cancelBtn.pressed.connect(self.onCancelButton)
        
        rows = [["Username", self.username],
                ["Role", self.role],
                ["", self.changePassword],
                ["Password", self.password1],
                ["Confirm Password", self.password2],
                [buttonBox]]
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        [form.addRow(*row) for row in rows]
        
        self.setLayout(form)
        
        self.populate()
    
    def populate(self):
        self.username.setText(user.current.username)
        self.role.setText(user.current.role.name if user.current.role is not None else '')
        self.changePassword.setChecked(False)
        self.password1.setText('')
        self.password1.setEnabled(False)
        self.password2.setText('')
        self.password2.setEnabled(False)
    
    def onChangePasswordCheck(self):
        enabled = self.changePassword.isChecked()
        self.password1.setEnabled(enabled)
        self.password2.setEnabled(enabled)
    
    def onOkButton(self):
        if self.changePassword.isChecked():
            if self.password1.text() != self.password2.text():
                QtGui.QMessageBox.information(self, 'User',
                    "Passwords do not match.", QtGui.QMessageBox.Ok)
            else:
                user.current.update(password=self.password1.text())
                self.populate()
    
    def onCancelButton(self):
        self.populate()
