import json
import os

class Config(object):
    """
    Main configuration class, a wrapper around the a json parser. 
    """
    def __init__(self, env):
        
        # Environment information
        self.env = env
        
        # Determine the full path to the config file
        self.filename = os.path.join(self.env.config_dir, 'coinbox.json')
        
        # Initialize config storage
        self.__config = None
        self.defaults = {}
        
        # Use pretty printing for JSON config files
        self.pretty = True
        
        self.read()
    
    def read(self):
        """
        Read configuration from a file, and load configuration from it.
        """
        try:
            with open(self.filename, 'r') as f:
                self.__config = json.load(f)
        except (IOError, OSError) as e:
            # File reading error
            if not os.path.exists(self.filename):
                self.__config = {}
            else:
                raise
        except ValueError:
            # JSON decoding error
            raise
    
    def save(self):
        """
        Save configuration to a file.
        """
        with open(self.filename, 'w') as f:
            if self.pretty:
                json.dump(self.__config, f, sort_keys=False,
                            indent=4, separators=(',', ': '))
            else:
                json.dump(self.__config, f)
    
    def save_defaults(self, overwrite=False):
        """
        Save the default values to a file.
        If overwrite is True, already present options are changed. Otherwise, they remain unchanged.
        Options that have no default values specified also remain unchanged.
        """
        for (section, option), value in self.defaults.iteritems():
            if value is None:
                continue
            if section not in self.__config:
                self.__config[section] = {}
            if overwrite or option not in self.__config[section]:
                self.__config[section][option] = value
        self.save()
    
    def clear(self):
        """
        Clears the configuration and saves to a file.
        This will reset the application to a "first run" configuration.
        """
        del self.__config
        self.__config = {}
        self.save()
    
    def empty(self):
        """
        Returns True if no section is present, meaning no configuration is defined.
        """
        return len(self.__config) == 0
    
    def set_default(self, section, option, value=None):
        """
        Sets a default value to a specific (section, option) pair, even if the section does not exist.
        """
        self.defaults[section, option] = value
    
    def __getitem__(self, k):
        """
        Implements the features:
        - pos.config[section, option] returns the value of the (section, option) pair or its default value
        - pos.config[section] returns a ConfigSection objects, so that this is enabled pos.config[section][option]
        Both return None if not found and no default is set.
        """
        if isinstance(k, (list, tuple)):
            try:
                return self.__config[k[0]][k[1]]
            except KeyError:
                return self.defaults.get(k, None)
        else:
            return self.__config.get(k, None)
    
    def __setitem__(self, k, v):
        """
        Implements the features:
        - pos.config[section, option] = None to delete the (section, option) pair
        - pos.config[section, option] = 'value' to set the (section, option) pair
        - pos.config[section] = None to delete the section
        - pos.config[section] = {'option': 'value'} to set the whole section
        - pos.config[section] = pos.config[section2] to replace the whole section
        """
        if isinstance(k, (list, tuple)):
            if v is None:
                del self.__config[k[0]][k[1]]
            else:
                try:
                    section = self.__config[k[0]]
                except KeyError:
                    section = {}
                    self.__config[k[0]] = section
                section[k[1]] = v
        elif isinstance(v, dict):
            self.__config[k] = dict(v)
        elif v is None:
            try:
                del self.__config[k]
            except KeyError:
                pass
    
    def __iter__(self):
        """
        Iterator to go through all the sections this way: (section_name, section_dict)
        """
        return self.__config.iteritems()
