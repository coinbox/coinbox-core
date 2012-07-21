from PySide import QtGui

import app

from sqlalchemy.orm import exc

import app.modules.user.objects.user as user
from app.modules.user.objects.user import User

#from pos.modules.user.windows import UserCatalog

class LoginDialog(QtGui.QWidget):
    def __init__(self):
        super(LoginDialog, self).__init__()
        self.setWindowTitle(app.tr.user._('Login'))
        
        self.user = QtGui.QComboBox()
        self.user.setEditable(True)
        
        self.password = QtGui.QLineEdit()
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.loginBtn = buttonBox.addButton(app.tr.user._("Login"), QtGui.QDialogButtonBox.AcceptRole)
        self.loginBtn.pressed.connect(self.onOkButton)
        
        self.exitBtn = buttonBox.addButton(app.tr.user._("Exit"), QtGui.QDialogButtonBox.RejectRole)
        self.exitBtn.pressed.connect(self.onExitButton)
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        rows = [[app.tr.user._("User"), self.user],
                [app.tr.user._("Password"), self.password],
                [buttonBox]
                ]
        
        [form.addRow(*row) for row in rows]
         
        self.setLayout(form)
        
        self.populate()
    
    def populate(self):
        session = app.database.session()
        users = session.query(User.display, User).filter_by(hidden=False).all()
        for user in users:
            self.user.addItem(*user)
    
    def onOkButton(self):
        username = self.user.currentText()
        password = self.password.text()
        
        session = app.database.session()
        try:
            u = session.query(User).filter(User.username == username).one()
        except exc.NoResultFound, exc.MultipleResultsFound:
            QtGui.QMessageBox.information(self, 'Login',
                            "Invalid username/password.", QtGui.QMessageBox.Ok)
            user.current = None
        else:
            if u.login(password):
                user.current = u
                if not user.current.super:
                    # Filter menu items to display according to permissions
                    restrictions = [(mr.root, mr.item) for mr in user.current.menu_restrictions] 
                    for root in app.menu.main.items:
                        for item in root.children:
                            item.enabled = ((root.label, item.label) in restrictions)
                self.close()
                app.start()
            else:
                QtGui.QMessageBox.information(self, 'Login',
                                "Invalid username/password.", QtGui.QMessageBox.Ok)
                user.current = None
    
    def onExitButton(self):
        user.current = None
        self.close()
    
    """
    def OnF3Command(self, event):
        dlg = HiddenUserLoginDialog(None)
        dlg.ShowModal()
        if dlg.success:
            user.current = dlg.user
            self.Close()
    """

"""
class HiddenUserLoginDialog(wx.Dialog):
    def __init_ctrls(self):
        self.panel = wx.Panel(self, -1)

        # User
        self.usernameLbl = wx.StaticText(self.panel, -1, label='Username')
        self.usernameTxt = wx.TextCtrl(self.panel, -1)
        
        # Password
        self.passwordLbl = wx.StaticText(self.panel, -1, label='Password')
        self.passwordTxt = wx.TextCtrl(self.panel, -1, style=wx.TE_PASSWORD)

        # Controls
        self.okBtn = wx.Button(self, wx.ID_OK, label='OK')
        self.okBtn.Bind(wx.EVT_BUTTON, self.OnOkButton)
        self.cancelBtn = wx.Button(self, wx.ID_CANCEL, label='Cancel')
    
    def __init_sizers(self):
        self.panelSizer = wx.GridSizer(hgap=5, vgap=5, cols=2)
        self.panelSizer.Add(self.usernameLbl, 0, flag=wx.ALL | wx.ALIGN_LEFT)
        self.panelSizer.Add(self.usernameTxt, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        self.panelSizer.Add(self.passwordLbl, 0, flag=wx.ALL | wx.ALIGN_LEFT)
        self.panelSizer.Add(self.passwordTxt, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        self.panel.SetSizerAndFit(self.panelSizer)

        self.controlSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.controlSizer.Add(wx.Size(0, 0), 1, flag=wx.EXPAND | wx.ALL)
        self.controlSizer.Add(self.okBtn, 0, flag=wx.CENTER | wx.ALL)
        self.controlSizer.Add(wx.Size(0, 0), 1, flag=wx.EXPAND | wx.ALL)
        self.controlSizer.Add(self.cancelBtn, 0, flag=wx.CENTER | wx.ALL)
        self.controlSizer.Add(wx.Size(0, 0), 1, flag=wx.EXPAND | wx.ALL) 
        
        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.mainSizer.Add(self.panel, 1, border=10, flag=wx.ALL | wx.EXPAND)
        self.mainSizer.AddSizer(self.controlSizer, 0, border=10, flag=wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND)
        self.SetSizerAndFit(self.mainSizer)
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title='Login')

        self.__init_ctrls()
        self.__init_sizers()
        
        self.success = False
        self.user = None
    
    def OnOkButton(self, event):
        username = self.usernameTxt.GetValue()
        password = self.passwordTxt.GetValue()
        session = pos.database.session()
        try:
            self.user = session.query(User).filter(User.username == username).one()
        except exc.NoResultFound, exc.MultipleResultsFound:
            pass
        if self.user is not None and self.user.login(password):
            self.success = True
            event.Skip()
        else:
            wx.MessageBox('Invalid username/password.', 'Error', style=wx.OK | wx.ICON_EXCLAMATION)
            self.usernameTxt.SetFocus()
            self.usernameTxt.SelectAll()

class LoginValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.user = None

    Clone = lambda self: LoginValidator()

    def Validate(self, parent):
        password = parent.passwordTxt.GetValue()
        u = parent.userList.GetValue()
        
        password_valid = True
        username_valid = u is not None
        
        if not username_valid:
            wx.MessageBox(message='Select a user', caption='Failure',
                                style=wx.OK, parent=None)
            return False
        elif not password_valid:
            wx.MessageBox(message='Invalid password', caption='Failure',
                                style=wx.OK, parent=None)
            return False
        else:
            if not u.login(password):
                wx.MessageBox(message='Wrong username/password', caption='Failure',
                                    style=wx.OK, parent=None)
                return False
            else:
                self.user = u
                return True

    def TransferToWindow(self):
        user.current = None
        return True

    def TransferFromWindow(self):
        user.current = self.user
        return True
"""