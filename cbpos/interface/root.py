class MenuRoot:
    """
    Root menu item that groups together related children items.
    """
    def __init__(self, name, menu=None, label=None, icon=None, rel=0, priority=-1):
        self.name = name
        
        self.label = label
        self.icon = icon
        
        self.rel = rel
        self.priority = priority
        
        self.enabled = True
        
        self.children = []
        if menu is not None:
            self.attach(menu)
    
    def attach(self, menu):
        self.menu = menu
        self.menu.addRoot(self)
    
    def addChild(self, child):
        if self.menu.done:
            raise RuntimeError, 'Cannot add item to menu when already sorted'
        self.children.append(child)

    def __repr__(self):
        return '<MenuRoot %s (%d,%d)>' %  (self.name, self.rel, self.priority)
