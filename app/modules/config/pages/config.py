from PySide import QtGui

import app

class MainConfigPage(QtGui.QWidget):
    def __init__(self):
        super(MainConfigPage, self).__init__()
        
        self.tabs = QtGui.QTabWidget()
        
        buttonBox = QtGui.QDialogButtonBox()
        
        self.okBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.cancelBtn.pressed.connect(self.onCancelButton)
        
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(10)
        
        layout.addWidget(self.tabs)
        layout.addWidget(buttonBox)
        
        self.setLayout(layout)
        
        self.populate()
    
    def populate(self):
        for mod in app.modules.all():
            try:
                pages = mod.config_pages()
            except AttributeError:
                continue
            for page_class in pages:
                page = page_class()
                label = page.label if hasattr(page, 'label') and page.label else '[%s]' % (mod.name,)
                self.tabs.addTab(page, label)
                page.populate()
    
    def onOkButton(self):
        for i in xrange(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.update()
        app.config.save()
        QtGui.QMessageBox.information(self, 'Configuration',
            "Configuration changes are saved.", QtGui.QMessageBox.Ok)
    
    def onCancelButton(self):
        for i in xrange(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.populate()
        QtGui.QMessageBox.information(self, 'Configuration',
            "Configuration changes are canceled.", QtGui.QMessageBox.Ok)
