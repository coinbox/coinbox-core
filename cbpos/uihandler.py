class BaseUIHandler(object):
    def handle_first_run(self):
        pass
    
    def init(self):
        raise NotImplementedError('No UI handler specified!')
        return False
    
    def start(self):
        return 1
