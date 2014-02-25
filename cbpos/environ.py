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
    config_dir = None
    data_dir = None
    locale_dir = None
    
    def __init__(self):
        pass
    
    def init(self):
        self.__make_dirs(self.config_dir)
        self.__make_dirs(self.data_dir)
        self.__make_dirs(self.locale_dir)

    def __make_dirs(self, d):
        if not os.path.exists(d):
            os.makedirs(d)
    
    def __str__(self):
        return '<{name} config: {s.config_dir}, ' \
                        'data: {s.data_dir}, ' \
                        'locale: {s.locale_dir}>'.format(s=self, name=type(self).__name__)

class FallbackEnviron(Environ):
    
    def __init__(self):
        home = os.path.expanduser('~')
        default_config_dir = os.path.join(home, 'coinbox', 'config')
        default_data_dir = os.path.join(home, 'coinbox', 'data')
        default_locale_dir = os.path.join(home, 'coinbox', 'locale')
        
        self.config_dir = os.environ.get(EnvironHelper.CONFIG_VAR, default_config_dir)
        self.data_dir = os.environ.get(EnvironHelper.DATA_VAR, default_data_dir)
        self.locale_dir = os.environ.get(EnvironHelper.LOCALE_VAR, default_locale_dir)

class Win32Environ(Environ):
    """
    Determine the right location to store the "app data" in Windows
    depending on whether there was an installer, and the path chosen
    in said installer, and whether we have access to global and/or
    user-specific locations, and if the environment variables
    are available (could be different than default).
    """
    ROAMING, LOCAL, COMMON = 1, 2, 4
    
    def __init__(self):
        # Find the Coinbox directory in Windows standard paths
        self.__find_app_data_path()
        
        self.config_dir = self.__get_path('config')
        self.data_dir = self.__get_path('data')
        self.locale_dir = self.__get_path('locale')
    
    def __nsis_registry_path(self, subkey):
        """
        Checks the registry keys made by the NSIS installer to check
        for the correct paths.
        """
        try:
            import _winreg
        except ImportError:
            return
        else:
            HKCU = _winreg.HKEY_CURRENT_USER
            HKLM = _winreg.HKEY_LOCAL_MACHINE
        
        try:
            reflect = _winreg.QueryReflectionKey(HKLM)
        except NotImplemented:
            flag = _winreg.KEY_READ
        else:
            if reflect:
                flag = _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY
            else:
                flag = _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY
        
        SOFTWARE_COINBOX = "Software\\Coinbox"
        # Search in HKCU, then HKLM
        for hkey in (HKCU, HKLM):
            try:
                with _winreg.OpenKey(hkey, SOFTWARE_COINBOX, 0, flag) as keyReg:
                    pathReg = _winreg.QueryValueEx(keyReg, subkey)
                    path = pathReg[0]
            except WindowsError as e:
                continue
            else:
                # Return as soon as any one is found
                return path
        
        # Not found in any of HKCU, HKLM
        return
    
    def __app_data_path_win32com(self, scope=ROAMING):
        """
        Get the standard "app data" paths using the recommended
        method of `SHGetFolderPath` using win32com.
        If not installed via the standard installer, it might not
        be available (not strictly a requirement except for
        PyInstaller)
        """
        try:
            from win32com.shell import shell, shellcon
        except ImportError:
            return
        
        if scope == Win32Environ.ROAMING:
            csidl = shellcon.CSIDL_APPDATA
        elif scope == Win32Environ.LOCAL:
            csidl = shellcon.CSIDL_LOCAL_APPDATA
        elif scope == Win32Environ.COMMON:
            csidl = shellcon.CSIDL_COMMON_APPDATA
        else:
            raise ValueError('Parameter scope has to be one of {ROAMING, LOCAL, COMMON}')
        
        return shell.SHGetFolderPath(0, csidl, None, 0)
    
    def __app_data_path_environ(self, scope=ROAMING):
        """
        Get the standard "app data" paths from the environment
        variables. This is the first method tried, since we
        assume the user might have changed the standard paths.
        """
        if scope == Win32Environ.ROAMING:
            return os.environ.get("APPDATA")
        elif scope == Win32Environ.LOCAL:
            return os.environ.get("LOCALAPPDATA")
        elif scope == Win32Environ.COMMON:
            return os.environ.get("PROGRAMDATA")
        else:
            raise ValueError('Parameter scope has to be one of {ROAMING, LOCAL, COMMON}')
    
    def __app_data_path_winreg(self, scope=ROAMING):
        """
        Get the standard "app data" paths from the registry
        keys. Although it should usually work, Microsoft
        recommends not to use these and use the win32com
        method.
        
        (A similar method is used by Deluge)
        """
        try:
            import _winreg
        except ImportError:
            return
        else:
            HKCU = _winreg.HKEY_CURRENT_USER
            HKLM = _winreg.HKEY_LOCAL_MACHINE
        
        try:
            reflect = _winreg.QueryReflectionKey(HKLM)
        except NotImplemented:
            flag = _winreg.KEY_READ
        else:
            if reflect:
                flag = _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY
            else:
                flag = _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY
        
        if scope == Win32Environ.ROAMING:
            subkey = "AppData"
            hkey = HKCU
        elif scope == Win32Environ.LOCAL:
            subkey = "Local AppData"
            hkey = HKCU
        elif scope == Win32Environ.COMMON:
            subkey = "Common AppData"
            hkey = HKLM
        else:
            raise ValueError('Parameter scope has to be one of {ROAMING, LOCAL, COMMON}')
        
        SHELL_FOLDERS = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders"
        try:
            with _winreg.OpenKey(hkey, SHELL_FOLDERS, 0, flag) as keyReg:
                pathReg = _winreg.QueryValueEx(keyReg, subkey)
                path = pathReg[0]
        except WindowsError as e:
            return
        else:
            return path
    
    def __find_app_data_path(self):
        """
        Find the Coinbox directory in Windows' "app data" standard paths
        using various methods, in the following order:
            (environment variables, SHGetFolderPath, registry)
        And the AppData paths in preferred order:
            (Roaming AppData, Common AppData / ProgramData, Local AppData)
        
        Depending on the installation method, it either finds the appropriate path
        via the "multiuser" option of the installer that created the directory
        or it falls back to the first valid "app data" path found: Roaming AppData.
        """
        self.__basepath = None
        self.__firstmatch = None
        
        for scope in (Win32Environ.ROAMING, Win32Environ.COMMON, Win32Environ.LOCAL):
            if self.__try_app_data_path(self.__app_data_path_environ(scope)):
                break
            if self.__try_app_data_path(self.__app_data_path_win32com(scope)):
                break
            if self.__try_app_data_path(self.__app_data_path_winreg(scope)):
                break
        else:
            # Didn't break -> Did not find existing -> Pick first one and create later
            self.__basepath = self.__firstmatch
            return False
        # Broke out and we did find one which exists
        return True

    def __try_app_data_path(self, p):
        """
        Checks if Coinbox has a directory at path `p`
        """
        basepath = os.path.join(p, 'Coinbox')
        
        # Only save the first match if the path `p` is a valid directory
        if self.__firstmatch is None and os.path.isdir(p):
            self.__firstmatch = basepath

        # If it exists, we found it; else we didn't
        if os.path.isdir(basepath):
            self.__basepath = basepath
            return True
        else:
            return False

    def __get_path(self, sub):
        """
        Return either the appropriate NSIS path or Windows standard path.
        """
        # Try to see if NSIS has the full path to use
        nsis = self.__nsis_registry_path(sub.title()+'Dir') # e.g. config -> ConfigDir
        if nsis:
            return nsis
        else:
            return os.path.join(self.__basepath, sub)

class XdgEnviron(Environ):
    def __init__(self):
        from xdg.BaseDirectory import save_config_path, save_data_path
        # TODO: Should we use save_config_path or load_first_config?
        self.config_dir = save_config_path('coinbox')
        
        self.data_dir = save_data_path('coinbox')
        
        # TODO: the default locale directory should be determined in a better way
        #         some package it in the egg as resources (yuck)
        #         some have a $prefix set up, and from that determine the path to $prefix/share/locale
        #         some have it in the data directory
        self.locale_dir = '/usr/share/locale'

class LinuxEnviron(XdgEnviron, FallbackEnviron):
    def __init__(self):
        if EnvironHelper.has_xdg():
            XdgEnviron.__init__(self)
        else:
            FallbackEnviron.__init__(self)

class MacOsxEnviron(LinuxEnviron):
    # TODO: does it need anything more than a standard linux?
    pass

class EnvironHelper(Environ):
    """
    Helper to guess the environment on which we are running.
    """
    
    CONFIG_VAR = 'COINBOX_CONFIG_DIR'
    DATA_VAR = 'COINBOX_DATA_DIR'
    LOCALE_VAR = 'COINBOX_LOCALE_DIR'
    
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
    def is_windows_vista(cls):
        """Returns True on Windows Vista"""
        return platform.release() == "Vista"
    
    @classmethod
    def has_xdg(cls):
        """Returns True if the Python XDG package is installed"""
        try:
            from xdg.BaseDirectory import save_config_path, save_data_path
        except ImportError as e:
            return False
        else:
            return True
    
    @classmethod
    def has_env_vars(cls):
        """Returns True if all environment variables needed for Coinbox directories are present"""
        return  cls.CONFIG_VAR in os.environ and \
                cls.DATA_VAR in os.environ and \
                cls.LOCALE_VAR in os.environ

def guess_environ():
    """
    Try to determine what enivronment we are running in
    and return an Environ object to determine the default
    directories to use.
    """
    if EnvironHelper.has_env_vars():
        return FallbackEnviron()
    elif EnvironHelper.is_windows():
        return Win32Environ()
    elif EnvironHelper.is_linux():
        return LinuxEnviron()
    elif EnvironHelper.is_darwin():
        return MacOsxEnviron()
    else:
        # We couldn't guess. Too bad!
        return FallbackEnviron()
