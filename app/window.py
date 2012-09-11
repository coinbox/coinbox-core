from PySide import QtCore, QtGui

import app

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabsClosable(False)
        self.tabs.setIconSize(QtCore.QSize(32, 32))
        self.tabs.setDocumentMode(True)
        
        self.setCentralWidget(self.tabs)
        
        self.statusBar().showMessage(app.tr._('Coinbox POS is ready.'))
        
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Coinbox')

    '''
    def OnShow(self, event):
        event.Skip()
        evt = app.Event('app', app.EVT_START)
        pos.event_queue.send(evt)

    def OnIdle(self, event):
        event.Skip()
        for evt in pos.event_queue.getall():
            for mod in pos.modules.all():
                if not mod.handle_event(evt):
                    break
    '''
    
    def loadMenu(self):
        """
        Load the menu "root" items and "items" into the toolbook with the appropriate pages. 
        """
        show_empty_root_items = app.config['menu', 'show_empty_root_items']
        show_disabled_items = app.config['menu', 'show_disabled_items']
        
        for root in app.menu.main.items:
            if not root.enabled and not show_disabled_items:
                continue
            enabled_children = [i for i in root.children if i.enabled]
            if show_disabled_items:
                children = root.children
            else:
                children = enabled_children
            # Hide empty menu root items
            if len(children) == 0 and not show_empty_root_items:
                continue
            widget = self.getTabWidget(children)
            icon = QtGui.QIcon(root.image)
            self.tabs.addTab(widget, icon, root.label)
            widget.setEnabled(root.enabled)# and len(enabled_children) != 0)

    def getTabWidget(self, items):
        """
        Returns the appropriate window to be placed in the main Toolbook depending on the items of a root menu item.
        """
        count = len(items)
        if count == 0:
            widget = QtGui.QWidget()
            widget.setEnabled(False)
            return widget
        elif count == 1:
            widget = items[0].page()
            widget.setEnabled(items[0].enabled)
            return widget
        else:
            tabs = QtGui.QTabWidget()

            for item in items:
                widget = item.page()
                icon = QtGui.QIcon(item.image)
                tabs.addTab(widget, icon, item.label)
                widget.setEnabled(item.enabled)
            return tabs
