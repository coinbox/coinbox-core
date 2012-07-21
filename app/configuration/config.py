import ConfigParser

class Config:
    """
    Main configuration class, a wrapper around the SafeConfigParser. 
    """
    def __init__(self, filename):
        self.filename = filename
        self._config = ConfigParser.SafeConfigParser()
        self.read()
        self._sections = {}
        self.defaults = {}
    
    def read(self):
        """
        Read configuration from a file, and load configuration from it.
        """
        self._config.read(self.filename)
    
    def save(self):
        """
        Save configuration to a file.
        """
        config_file = open(self.filename, 'w')
        try:
            self._config.write(config_file)
        except:
            raise
        finally:
            config_file.close()
    
    def save_defaults(self, overwrite=False):
        """
        Save the default values to a file.
        If overwrite is True, already present options are changed. Otherwise, they remain unchanged.
        Options that have no default values specified also remain unchanged.
        """
        for (section, option), value in self.defaults.iteritems():
            if value is None:
                continue
            if not self._config.has_section(section):
                self._config.add_section(section)
            if overwrite or not self._config.has_option(section, option):
                self._config.set(section, option, value)
        self.save()
    
    def clear(self):
        """
        Clears the configuration and saves to a file.
        This will reset the application to a "first run" configuration.
        """
        for section in self._config.sections():
            self._config.remove_section(section)
        self.save()
    
    def empty(self):
        """
        Returns True if no section is present, meaning no configuration is defined.
        """
        return len(self._config.sections()) == 0
    
    def set_default(self, section, option, value=None):
        """
        Sets a default value to a specific (section, option) pair, even if the section does not exist.
        """
        self.defaults[section, option] = value
    
    def _section(self, k):
        """
        Function that returns a ConfigSection object.
        It is used to not have more than one ConfigSection associated to one same section.
        """
        if k not in self._sections:
            self._sections[k] = ConfigSection(self, k)
        return self._sections[k]
    
    def __getitem__(self, k):
        """
        Implements the features:
        - pos.config[section, option] returns the value of the (section, option) pair or its default value
        - pos.config[section] returns a ConfigSection objects, so that this is enabled pos.config[section][option]
        Both return None if not found and no default is set.
        """
        if type(k) in (list, tuple):
            if self._config.has_section(k[0]):
                if self._config.has_option(k[0], k[1]):
                    return self._config.get(k[0], k[1])
                else:
                    try:
                        return self.defaults[k[0], k[1]]
                    except KeyError:
                        return None
            else:
                try:
                    return self.defaults[k[0], k[1]]
                except KeyError:
                    return None
        else:
            if self._config.has_section(k):
                return self._section(k)
            else:
                return None
    
    def __setitem__(self, k, v):
        """
        Implements the features:
        - pos.config[section, option] = None to delete the (section, option) pair
        - pos.config[section, option] = 'value' to set the (section, option) pair
        - pos.config[section] = None to delete the section
        - pos.config[section] = {'option': 'value'} to set the whole section
        - pos.config[section] = pos.config[section2] to replace the whole section
        """
        if type(k) in (list, tuple):
            if v is None:
                if self._config.has_option(k[0], k[1]):
                    self._config.remove_option(k[0], k[1])
            else:
                if not self._config.has_section(k[0]):
                    self._config.add_section(k[0])
                self._config.set(k[0], k[1], v)
        else:
            if type(v) == dict:
                self._config.remove_section(k)
                self._config.add_section(k)
                for _k, _v in v.iteritems():
                    self._config.set(k, _k, _v)
            elif isinstance(v, ConfigSection):
                self._config.remove_section(k)
                self._config.add_section(k)
                for _k, _v in v:
                    self._config.set(k, _k, _v)
            elif v is None and self._config.has_section(k):
                self._config.remove_section(k)
    
    def __iter__(self):
        """
        Iterator to go through all the sections this way: (section_name, ConfigSection_object)
        """
        return ((k, self._section(k)) for k in self._config.sections())

class ConfigSection:
    """
    Implements some way to set default values and get/set options for a specific section.
    Do not use this on its own. Use pos.config[section] instead.
    """
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self._config = self.config._config

    set_default = lambda self, option, value=None: self.config.set_default(self.section, option, value)
    
    def __getitem__(self, k):
        """
        Implements the feature: pos.config[section][option] that returns
        the value or the default for the (section, option) pair or None if not found.
        """
        return self.config[self.section, k]
    
    def __setitem__(self, k, v):
        """
        Implements the feature: pos.config[section][option] = value
        """
        self.config[self.section, k] = v
    
    def __iter__(self):
        """
        Iterator to go through all the section's options this way: (option_name, option_value)
        """
        return iter(self._config.items(self.section))
