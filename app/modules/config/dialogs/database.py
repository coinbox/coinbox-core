from PySide import QtGui

import app
from app.database.profile import all_profiles, get_used_profile, get_profile, Profile
from app.database.driver import all_drivers, get_driver

class DatabaseConfigDialog(QtGui.QMainWindow):
    
    def __init__(self):
        super(DatabaseConfigDialog, self).__init__()
        
        self.mainWidget = MainWidget()
        
        self.setCentralWidget(self.mainWidget)
        
        self.statusBar().showMessage('Select the database profile to use and configure it.')
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Database Configuration')

class MainWidget(QtGui.QWidget):
    
    def __init__(self):
        super(MainWidget, self).__init__()
        
        self.initUI()
        self.populate()
        
    def initUI(self):
        self.profiles = QtGui.QComboBox()
        self.profiles.activated[int].connect(self.onProfileActivated)
        self.profiles.editTextChanged.connect(self.onProfileTextChanged)
        
        self.addBtn = QtGui.QPushButton('+')
        self.addBtn.pressed.connect(self.onAddButton)
        self.removeBtn = QtGui.QPushButton('-')
        self.removeBtn.pressed.connect(self.onRemoveButton)
        
        self.forms = {}
        
        self.tabs = QtGui.QTabWidget()
        drivers = all_drivers()
        drivers.sort(key=lambda d: d.name)
        for driver in drivers:
            self.forms[driver.name] = form = DriverForm(driver)
            self.tabs.addTab(form, driver.display)

        buttonBox = QtGui.QDialogButtonBox()
        
        self.okBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.applyBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Apply)
        self.applyBtn.pressed.connect(self.onApplyButton)
        
        self.cancelBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.cancelBtn.pressed.connect(self.onCancelButton)

        profileLayout = QtGui.QHBoxLayout()
        profileLayout.addWidget(self.profiles, 1)
        profileLayout.addWidget(self.addBtn)
        profileLayout.addWidget(self.removeBtn)

        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        rows = [[profileLayout],
                [self.tabs],
                [buttonBox]
                ]

        [form.addRow(*row) for row in rows]
        self.setLayout(form)
    
    def populate(self):
        self._last_profile = None
        self._last_profile_values = None
        self._last_profile_name = None
        self._tmp_profile_name = None
        self.profiles.clear()
        for profile in all_profiles():
            self.profiles.addItem(profile.name, profile)
        profile = get_used_profile()
        self.setProfile(get_profile('default') if profile is None else profile)
    
    def onProfileActivated(self, index):
        self._last_profile_name = self._tmp_profile_name
        profile = self.profiles.itemData(index)
        self.setProfile(profile)
    
    def onProfileTextChanged(self, profile_name):
        self._tmp_profile_name = self._last_profile_name
        self._last_profile_name = profile_name
    
    def onAddButton(self):
        n = 0
        while get_profile("profile%d" % (n,)) is not None:
            n += 1
        profile = Profile(name="profile%d" % (n,), driver=get_driver('sqlite'))
        profile.save()
        self.saveProfile(auto=True)
        self.populate()
        self.setProfile(profile)
    
    def onRemoveButton(self):
        if not self._last_profile.editable:
            return
        self._last_profile.delete()
        self.populate()
    
    def onOkButton(self):
        self.saveProfile(auto=False)
        self._last_profile.use()
        self.parent().close()
        self.continueProcess()
    
    def onApplyButton(self):
        self.saveProfile(auto=False)
        self.populate()
    
    def onCancelButton(self):
        self.parent().close()
    
    def changed(self, other=None):
        if other is not None and self._last_profile == other:
            return True
        if self._last_profile_name is not None and self._last_profile_name != self._last_profile.name:
            return True
        form = self.tabs.currentWidget()
        if form.values() != self._last_profile_values:
            return True
    
    def setProfile(self, profile):
        if self._last_profile and self.changed(other=profile):
            if not self.saveProfile(auto=True):
                return
            self.populate()
        else:
            #TODO: self.profiles.findData(profile) is not working...
            index = self.profiles.findText(profile.name)
            self.profiles.setCurrentIndex(index)
        for f in self.forms.itervalues():
            f.clear()
        form = self.forms[profile.driver.name]
        self.tabs.setCurrentWidget(form)
        form.setProfile(profile)
        
        self.tabs.setEnabled(profile.editable)
        self.profiles.setEditable(profile.editable)
        self.removeBtn.setEnabled(profile.editable)
        
        self._last_profile = profile
        self._tmp_profile_name = profile.name
        self._last_profile_name = profile.name
        self._last_profile_values = form.values()
    
    def saveProfile(self, auto=False):
        if not self.changed():
            return True
        if auto:
            reply = QtGui.QMessageBox.question(self, 'Save Profile?',
                                               "Changes to this profile have not been saved. Save now?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                self.profiles.setEditText(self._last_profile_name)
                return False
            elif reply == QtGui.QMessageBox.No:
                return True
        if self._last_profile_name != self._last_profile.name and self._last_profile_name in all_profiles(names=True):
            QtGui.QMessageBox.information(self, 'Save Profile',
                "A profile with this name already exists. Choose another name.", QtGui.QMessageBox.Ok)
            return False
        form = self.tabs.currentWidget()
        self._last_profile.name = self._last_profile_name
        return form.save(self._last_profile)

    def continueProcess(self):
        # Start the database AFTER potential changes in the configuration 
        if not app.database.init():
            return
        # Load database objects of every module
        app.modules.loadDB()
        
        # Prompt the user to completely flush the chosen database and recreate the structure
        reply = QtGui.QMessageBox.question(self, "Database configuration",
                                           "Reconfigure Database?\nThis will drop the tables in the database you chose and recreate it.", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            app.modules.configDB()
        else:
            return
        
        # Prompt the user to add initial testing values, just to see it working immediately
        reply = QtGui.QMessageBox.question(self, "Database configuration", "Insert test values?",
                                           QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            app.modules.configTestDB()

class DriverForm(QtGui.QWidget):
    def __init__(self, driver):
        super(DriverForm, self).__init__()
        
        self.driver = driver
        self.rows = self.driver.form.copy()
        self.initUI()
        
    def initUI(self):
        if "host" in self.rows:
            self.rows["host"]["widget"] = QtGui.QLineEdit()
        if "port" in self.rows:
            self.rows["port"]["widget"] = widget = QtGui.QSpinBox()
            widget.setRange(0, 65535)
            widget.setSingleStep(1)
        if "username" in self.rows:
            self.rows["username"]["widget"] = QtGui.QLineEdit()
        if "password" in self.rows:
            self.rows["password"]["widget"] = widget = QtGui.QLineEdit()
            widget.setEchoMode(QtGui.QLineEdit.Password)
        if "database" in self.rows:
            self.rows["database"]["widget"] = QtGui.QLineEdit()
        if "query" in self.rows:
            self.rows["query"]["widget"] = QtGui.QLineEdit()

        form = QtGui.QFormLayout()
        form.setSpacing(10)

        rows_order = ('host', 'port', 'username', 'password', 'database', 'query')
        for field in rows_order:
            if field in self.rows:
                row = self.rows[field]
            else:
                continue
            row["checkbox"] = checkbox = QtGui.QCheckBox(row["label"])
            checkbox.setEnabled(not row["required"])
            checkbox.stateChanged.connect(lambda state, widget=row["widget"]: widget.setEnabled(bool(state)))
            row["widget"].setEnabled(row["required"])
            self.setField(field, None)
            form.addRow(checkbox, row["widget"])
        self.setLayout(form)

    def setField(self, field, value):
        if field not in self.rows:
            return
        self.rows[field]["checkbox"].setChecked(self.rows[field]["required"] or bool(value))
        value = value if value is not None else self.rows[field]["default"]
        if field in ('host', 'username', 'password', 'database', 'query'):
            self.rows[field]["widget"].setText(value)
        elif field == 'port':
            self.rows["port"]["widget"].setValue(int(value) if value is not None else 0)
    
    def getField(self, field):
        if field not in self.rows:
            return None
        if not self.rows[field]["checkbox"].isChecked():
            return None
        if field in ('host', 'username', 'password', 'database', 'query'):
            return self.rows[field]["widget"].text()
        elif field == 'port':
            return str(self.rows["port"]["widget"].value())

    def setProfile(self, profile):
        if profile.driver != self.driver:
            return
        for field in self.rows:
            self.setField(field, getattr(profile, field))

    def clear(self):
        for field in self.rows:
            self.setField(field, None)

    def values(self):
        v = {}
        v["driver"] = self.driver
        for field in self.rows:
            v[field] = self.getField(field)
        return v
    
    def save(self, profile):
        for k, v in self.values().iteritems():
            setattr(profile, k, v)
        profile.save()
        return True
