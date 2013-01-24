class MenuItem:
    """
    Menu item which has a page associated to it and belongs under a MenuRoot,
    together with other related pages.
    """
    def __init__(self, name, parent, menu=None, label=None, page=None, icon=None, rel=0, priority=-1):
        self.name = name
        self.parent = parent
        
        self.label = label
        self.icon = icon
        
        self.rel = rel
        self.priority = priority
        
        self.enabled = True
        
        self.page = page
        
        if menu is not None:
            self.attach(menu)
    
    def attach(self, menu):
        self.menu = menu
        root = self.menu.rootByName(self.parent)
        root.addChild(self)

    def __repr__(self):
        return '<MenuItem %s parent=%s>' %  (self.name, self.parent)
