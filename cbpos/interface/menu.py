class Menu:
    """
    Holds the hierarchy of the menu system.
    Root items are associated to it, and items associated to a root item.
    """
    def __init__(self):
        self.__by_name = {}
        self.items = []
        self.actions = []
        self.done = False

    def sort(self):
        """
        Sorts all the items and their children in the desired order, as close as possible
        to the one requested from the modules.
        """
        self.done = True
        self.items = self.__order(self.__by_name.values())
        for root in self.items:
            root.children = self.__order(root.children)

    def __order(self, items):
        grouped = [[] for j in range(len(items))]
        ordered = []
        for i in items:
            pos = min(i.rel, len(items)-1) if i.rel>=0 else max(i.rel, -len(items))
            grouped[pos].append(i)
        for L in grouped:
            L.sort(key=lambda i: (-i.priority if i.rel>=0 else i.priority))
            ordered.extend(L)
        return ordered
    
    def addRoot(self, item):
        if self.done:
            raise RuntimeError, 'Cannot add item to menu when already sorted'
        self.__by_name[item.name] = item
    
    def addAction(self, action):
        self.actions.append(action)
    
    def rootByName(self, name):
        return self.__by_name[name]
    
    def __repr__(self):
        return '<Menu %d items>' %  (len(self.__items),)
