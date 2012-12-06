import cbpos

import os

import logging
logger = logging.getLogger(__name__)

class Resource(object):
    
    def add(self, name):
        return setattr(self, name, ResourceGetter(name))

class ResourceGetter(object):
    def __init__(self, name):
        self.name = name
        self.mod = cbpos.modules.wrapper_by_name(self.name)
        mod_path = os.path.dirname(self.mod.top_module.__file__)
        self.path = os.path.join(mod_path, 'res')
    
    def __call__(self, path):
        full_path = os.path.join(self.path, path.strip('/'))
        real_path = os.path.realpath(full_path)
        if os.path.commonprefix([real_path, self.path]) != self.path:
            logger.warn('The resource requested points to a file outside of its scope: '+real_path)
        if not os.path.exists(real_path):
            logger.warn('The resource requested does not exist: '+real_path)
        return real_path
