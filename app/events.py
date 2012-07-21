__all__ = ['Event', 'event_queue',
           'EVT_START', 'EVT_EXIT',
           'EVT_ACTION', 'EVT_UPDATE',
           'EVT_LOG']

import datetime

class Event:
    def __init__(self, source, type_, target=None, *args, **kwargs):
        self.source = source
        self.target = target
        self.type = type_
        self.args = args
        self.kwargs = kwargs
    
    def IsTargetted(self, target):
        if type(self.target) in (list, dict, set):
            return target in self.target
        elif target is None:
            return True
        else:
            return self.target == target
    
    def __repr__(self):
        return '<pos.Event %s from=%s to=%s>' % (self.type, self.source, self.target)

EVT_ACTION, EVT_UPDATE, EVT_LOG, EVT_START, EVT_EXIT = range(5)

class EventQueue:
    def __init__(self):
        self.events = []
        self.processed = []
    
    def send(self, evt):
        self.events.append(evt)
    
    def get(self):
        now = datetime.datetime.now()
        try:
            evt = self.events.pop(0)
        except IndexError:
            return None
        else:
            self.processed.append((evt, now))
            return evt
    
    def getall(self):
        self.events.reverse()
        self.processed.extend(self.events)
        evts = self.events[:]
        self.events = []
        return evts

event_queue = EventQueue()
