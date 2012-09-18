import cbpos
from .driver import get_driver

class Profile(object):
    def __init__(self, name, driver, host=None, port=None,
                 username=None, password=None, database=None,
                 query=None):
        self.name = self._name = name
        self.driver = driver
        
        self.host = host
        self.port = port
        
        self.username = username
        self.password = password
        self.database = database
        
        self.query = query
        
        self.editable = True
        
        _profiles[name] = self
    
    def save(self):
        if not self.editable:
            return
        cbpos.config['db.'+self._name] = dict(self)
        if self.name != self._name:
            cbpos.config['db.'+self.name] = cbpos.config['db.'+self._name]
            cbpos.config['db.'+self._name] = None
            _profiles[self.name] = self
            try:
                _profiles.pop(self._name)
            except KeyError:
                pass
            self._name = self.name
        cbpos.config.save()
    
    def use(self):
        cbpos.config['db', 'used'] = self._name
        cbpos.config.save()
    
    def delete(self):
        if not self.editable:
            return
        cbpos.config['db.'+self._name] = None
        try:
            _profiles.pop(self._name)
        except KeyError:
            pass
        cbpos.config.save()
    
    _options = ('host', 'port', 'username', 'password', 'database', 'query')
    def __iter__(self):
        L = [('drivername', self.driver.name)]
        for s in self._options:
            v = getattr(self, s)
            if v is not None:
                L.append((s, v))
        return iter(L)
    
    def __repr__(self):
        return '<Profile %s>' % (self.name,)

_profiles = {}
default = Profile(name='default', driver=get_driver('sqlite'), database='default.sqlite')
default.editable = False

def get_profile(profile_name):
    if profile_name not in _profiles:
        config = 'db.'+profile_name
        driver_name = cbpos.config[config, 'drivername']
        if driver_name is None:
            return None
        driver = get_driver(driver_name)
        
        kwargs = dict([(a, cbpos.config[config, a]) for a in Profile._options])
        _profiles[profile_name] = Profile(profile_name, driver, **kwargs)
    return _profiles[profile_name]

def get_used_profile():
    profile_name = cbpos.config['db', 'used']
    return get_profile(profile_name)

def all_profiles(names=False):
    if not names:
        return [default]+[get_profile(section_name[3:]) for section_name, s in cbpos.config if section_name.startswith('db.')]
    else:
        return _profiles.keys()
