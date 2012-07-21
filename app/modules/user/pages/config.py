from PySide import QtGui

import app

class UserConfigPage(QtGui.QWidget):
    label = 'User'
    
    def __init__(self):
        super(UserConfigPage, self).__init__()
        
        self.allow_empty_password = QtGui.QCheckBox()
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        form.addRow('Allow empty passwords', self.allow_empty_passwords)
        
        self.setLayout(form)

    def populate(self):
        self.allow_empty_password.setChecked(app.config['mod.user', 'allow_empty_passwords'] != '')
    
    def update(self):
        checked = self.allow_empty_password.isChecked()
        app.config['mod.user', 'allow_empty_passwords'] = '1' if checked else ''
