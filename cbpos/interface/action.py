from pydispatch import dispatcher

class Action(object):
    """
    Action that is triggered by a particular event (e.g. toolbar button pressed) to trigger
    a certain function.
    """
    def __init__(self, name, menu=None, label=None, icon=None, shortcut=None, callback=None, signal=None):
        self.name = name
        
        self.label = label
        self.icon = icon
        self.shortcut = shortcut
        
        if callback is not None:
            self.trigger = callback
        elif signal is not None:
            self.signal = signal
            self.trigger = self.__sendSignal
        else:
            self.trigger = lambda: None
        
        if menu is not None:
            self.attach(menu)
    
    def __sendSignal(self):
        dispatcher.send(signal=self.signal, sender='action')
    
    def attach(self, menu):
        self.menu = menu
        self.menu.addAction(self)

    def __repr__(self):
        return '<Action %s (%s)>' %  (self.name, self.signal)
