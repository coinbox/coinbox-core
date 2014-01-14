import os
import sys
import platform
import warnings

class Environ(object):
    """
    Provides an interface to default directories
    for config, data and locale depending on the
    environment the application is running in.
    """
    default_config_dir = None
    default_data_dir = None
    default_locale_dir = None

class Win32Environ(Environ):
    def __app_data_path(self, sub):
        # Reads the app data path in Windows and returns that
        appDataPath = os.environ.get("APPDATA")
        if not appDataPath:
            import _winreg
            hkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders")
            appDataReg = _winreg.QueryValueEx(hkey, "AppData")
            appDataPath = appDataReg[0]
            _winreg.CloseKey(hkey)
        return os.path.join(appDataPath, 'Coinbox', sub)
    
    @property
    def default_config_dir(self):
        return self.__app_data_path('config')
    
    @property
    def default_data_dir(self):
        return self.__app_data_path('data')
    
    @property
    def default_locale_dir(self):
        # TODO: there has to be a better way. Probably in os.path.dirname(sys.executable) if frozen
        return self.__app_data_path('locale')

class LinuxEnviron(Environ):
    @property
    def default_config_dir(self):
        from xdg.BaseDirectory import save_config_path
        # TODO: Should we use save_config_path or load_first_config?
        return save_config_path('coinbox')
    
    @property
    def default_data_dir(self):
        from xdg.BaseDirectory import save_data_path
        # TODO: data dir? what should it be used for? resources? user data?
        return save_data_path('coinbox')
    
    @property
    def default_locale_dir(self):
        # TODO: the default locale directory should be determined in a better way
        #         some package it in the egg as resources (yuck)
        #         some have a $prefix set up, and from that determine the path to $prefix/share/locale
        #         some have it in the data directory
        return '/usr/share/locale'

class MacOsxEnviron(LinuxEnviron):
    # TODO: does it need anything more than a standard linux?
    pass

class FallbackEnviron(Environ):
    @property
    def default_config_dir(self):
        home = os.path.expanduser('~')
        return os.path.join(home, 'coinbox', 'config')
    
    @property
    def default_data_dir(self):
        home = os.path.expanduser('~')
        return os.path.join(home, 'coinbox', 'data')
    
    @property
    def default_locale_dir(self):
        home = os.path.expanduser('~')
        return os.path.join(home, 'coinbox', 'locale')

class EnvironHelper(Environ):
    """
    Helper to guess the environment on which we are running.
    """
    @classmethod
    def is_linux(cls):
        """Returns True on Linux"""
        return platform.system() == 'Linux'
    
    @classmethod
    def is_debian(cls):
        """Returns True on Debian"""
        return cls.is_linux() and platform.linux_distribution()[0].lower() == 'debian'
    
    @classmethod
    def is_fedora(cls):
        """Returns True on Fedora"""
        return cls.is_linux() and platform.linux_distribution()[0].lower() == 'fedora'
    
    @classmethod
    def is_osx(cls):
        """Return True on Mac OSX"""
        return platform.system() == "Darwin"
    is_darwin = is_osx
    
    @classmethod
    def is_windows(cls):
        """Return True on Windows"""
        return platform.system() in ('Windows', 'Microsoft')
    
    @classmethod
    def is_windows_vista():
        """Returns True on Windows Vista"""
        return platform.release() == "Vista"

def guess_environ():
    """
    Try to determine what enivronment we are running in
    and return an Environ object to determine the default
    directories to use.
    Return None if not enough information is available.
    """
    if EnvironHelper.is_linux():
        return LinuxEnviron()
    elif EnvironHelper.is_windows():
        # TODO: frozen or not?
        return Win32Environ()
    elif EnvironHelper.is_darwin():
        return MacOsxEnviron()
    else:
        # We couldn't guess. Too bad!
        return None

def get_fallback():
    """
    Return an Environ object to use if no other better option
    is available. Uses a directory in the user's HOME.
    """
    return FallbackEnviron()
