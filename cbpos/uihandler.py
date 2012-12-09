class BaseUIHandler(object):
    def init(self):
        raise NotImplementedError('No UI handler specified!')
        return False
    
    def start(self):
        return 1
