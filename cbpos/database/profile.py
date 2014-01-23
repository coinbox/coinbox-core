__all__ = ('Profile', 'ProfileNotFoundError')

import cbpos
from .driver import Driver
import os

class Profile(object):
    def __init__(self, name, driver, host=None, port=None,
                 username=None, password=None, database=None,
                 query=None, drivername=None):
        self.__config_name = None
        self.__name = None
        self.name = name
        
        # Could be different than driver.name, e.g. "mysql" or "mysql+pymysql"
        self.drivername = drivername
        self.__driver = None
        self.driver = driver
        
        self.host = host
        self.port = port
        
        self.username = username
        self.password = password
        
        self.__database = None
        self.database = database
        
        self.query = query
        
        self.editable = True
        
        # Cache for future calls to Profile.get(name)
        self.__profiles[name] = self
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, n):
        self.__config_name = n if self.__name is None else self.__name
        self.__name = n
    
    @property
    def driver(self):
        return self.__driver
    
    @driver.setter
    def driver(self, d):
        self.__driver = d
        if d is not None and \
                (not self.drivername or \
                 self.drivername.split('+', 1)[0] != d.name):
            # No specific drivername is requested
            # Or the selected drivername does not match the driver
            # Then update the driver name to the default of the selected driver
            self.drivername = d.name
    
    @property
    def database(self):
        return self.__database
    
    @database.setter
    def database(self, d):
        if self.__driver.use_database_as_filename and \
                self.host is None and \
                d is not None and \
                not os.path.isabs(d):
            self.__database = os.path.join(cbpos.config.env.data_dir, d)
        else:
            self.__database = d
    
    def save(self):
        if not self.editable:
            return
        cbpos.config['db.'+self.__config_name] = dict(self)
        if self.__name != self.__config_name:
            # If the name changed from when it was created
            # Update the configuration
            cbpos.config['db.'+self.__name] = cbpos.config['db.'+self.__config_name]
            cbpos.config['db.'+self.__config_name] = None
            
            # And update the cache
            self.__profiles[self.__name] = self
            try:
                self.__profiles.pop(self.__config_name)
            except KeyError:
                pass
            
            # Update the config name
            self.__config_name = self.__name
        # And save it back to the config anyway
        cbpos.config.save()
    
    def use(self):
        cbpos.config['db', 'used'] = self.__config_name
        cbpos.config.save()
    
    def delete(self):
        if not self.editable:
            return
        cbpos.config['db.'+self.__config_name] = None
        try:
            self.__profiles.pop(self.__config_name)
        except KeyError:
            pass
        cbpos.config.save()
    
    __options = ('host', 'port', 'username', 'password', 'database', 'query', 'drivername')
    def __iter__(self):
        for s in self.__options:
            v = getattr(self, s)
            if v is not None and s not in self.driver.empty_fields:
                yield (s, v)
    
    def __repr__(self):
        return '<Profile %s>' % (self.name,)
    
    __profiles = {}
    @classmethod
    def get(cls, profile_name):
        if profile_name not in cls.__profiles:
            config = 'db.'+profile_name
            drivername = cbpos.config[config, 'drivername']
            if drivername is None:
                raise ProfileNotFoundError('Profile not found: {}'.format(repr(profile_name)))
            driver = Driver.get(drivername)
            
            kwargs = dict([(a, cbpos.config[config, a]) for a in cls.__options])
            p = cls(profile_name, driver, **kwargs) # It saves itself in the __profiles dict
        
        return cls.__profiles[profile_name]
    
    @classmethod
    def get_used(cls):
        profile_name = cbpos.config['db', 'used']
        return cls.get(profile_name)
    
    @classmethod
    def get_all_names(cls):
        return cls.__profiles.keys()
    
    @classmethod
    def get_all(cls):
        for section_name, s in cbpos.config:
            if section_name.startswith('db.'):
                Profile.get(section_name[3:]) 
        return cls.__profiles.values()

default = Profile(name='default', driver=Driver.get('sqlite'), database='default.sqlite')
default.editable = False

class ProfileNotFoundError(ValueError):
    pass
